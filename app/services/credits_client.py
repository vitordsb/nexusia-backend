"""Cliente HTTP para sincronizar créditos com o backendAuth."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class CreditsClient:
    """Encapsula chamadas ao backendAuth para consultar e atualizar créditos."""

    def __init__(self) -> None:
        self.base_url = settings.BACKEND_AUTH_BASE_URL.rstrip("/")
        self.service_token = settings.INTERNAL_SERVICE_TOKEN
        timeout_env = os.getenv("BACKEND_AUTH_TIMEOUT", "10")
        try:
            self.timeout = float(timeout_env)
        except ValueError:
            self.timeout = 10.0
        self._client = httpx.AsyncClient(timeout=self.timeout)

    def _headers(self) -> Dict[str, str]:
        return {"x-service-token": self.service_token}

    async def get_balance(self, user_id: str) -> Dict[str, Any]:
        """Retorna o saldo disponível do usuário."""
        try:
            response = await self._client.get(
                f"{self.base_url}/internal/users/{user_id}/credits",
                headers=self._headers(),
            )
        except httpx.HTTPError as exc:  # pragma: no cover
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Não foi possível consultar o saldo de créditos.",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado ao consultar créditos.",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Serviço de autenticação rejeitou a consulta de créditos.",
            )

        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Resposta inválida do serviço de autenticação.",
            ) from exc

    async def ensure_minimum_balance(self, user_id: str, min_credits: int = 1) -> Dict[str, Any]:
        """Valida se o usuário possui o saldo mínimo exigido."""
        if settings.ENABLE_CREDIT_SIMULATION:
            # Em modo de simulação, ignoramos o saldo real e retornamos um valor alto
            return {
                "credits": max(min_credits, 1000),
                "simulated": True,
            }
        summary = await self.get_balance(user_id)
        credits = int(summary.get("credits", 0))
        if credits < min_credits:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Saldo insuficiente. Recarregue seus créditos para continuar usando a IA.",
            )
        return summary

    async def debit(
        self,
        user_id: str,
        amount: int,
        reference: str,
        reason: str,
        metadata: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """Debita créditos através do backendAuth."""
        if amount <= 0:
            return {}

        if settings.ENABLE_CREDIT_SIMULATION:
            # Não faz chamadas externas quando a simulação está ativa
            return {}

        payload = {
            "amount": amount,
            "operation": "debit",
            "reference": reference,
            "reason": reason,
            "metadata": metadata or {},
        }

        try:
            response = await self._client.post(
                f"{self.base_url}/internal/users/{user_id}/credits",
                json=payload,
                headers=self._headers(),
            )
        except httpx.HTTPError as exc:  # pragma: no cover
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Não foi possível debitar créditos do usuário.",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado para débito de créditos.",
            )
        if response.status_code == 422:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Saldo insuficiente para concluir a operação.",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Serviço de autenticação rejeitou o débito de créditos.",
            )

        try:
            return response.json()
        except ValueError:
            return {}

    async def aclose(self) -> None:
        """Encerra a sessão HTTP."""
        await self._client.aclose()


credits_client = CreditsClient()
