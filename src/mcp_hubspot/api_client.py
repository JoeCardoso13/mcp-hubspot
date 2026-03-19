"""Async HTTP client for HubSpot CRM API."""

import os
from typing import Any

import aiohttp
from aiohttp import ClientError

from .api_models import CrmListResponse, CrmObject


class HubspotAPIError(Exception):
    """Exception raised for HubSpot API errors."""

    def __init__(self, status: int, message: str, details: dict[str, Any] | None = None) -> None:
        self.status = status
        self.message = message
        self.details = details
        super().__init__(f"HubSpot API Error {status}: {message}")


class HubspotClient:
    """Async client for HubSpot CRM API."""

    BASE_URL = "https://api.hubapi.com"

    def __init__(
        self,
        access_token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.access_token = access_token or os.environ.get("HUBSPOT_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("HUBSPOT_ACCESS_TOKEN is required")
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "HubspotClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _ensure_session(self) -> None:
        if not self._session:
            headers = {
                "User-Agent": "mcp-server-hubspot/0.1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            }
            self._session = aiohttp.ClientSession(
                headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: Any | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the HubSpot API."""
        await self._ensure_session()
        url = f"{self.BASE_URL}{path}"

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            if not self._session:
                raise RuntimeError("Session not initialized")

            kwargs: dict[str, Any] = {}
            if json_data is not None:
                kwargs["json"] = json_data
            if params:
                kwargs["params"] = params

            async with self._session.request(method, url, **kwargs) as response:
                if response.status == 204:
                    return {}

                result = await response.json()

                if response.status >= 400:
                    error_msg = "Unknown error"
                    if isinstance(result, dict):
                        error_msg = result.get("message", str(result))

                    raise HubspotAPIError(response.status, error_msg, result)

                return result

        except ClientError as e:
            raise HubspotAPIError(500, f"Network error: {str(e)}") from e

    # ========================================================================
    # Contacts
    # ========================================================================

    async def list_contacts(
        self,
        limit: int = 10,
        after: str | None = None,
        properties: list[str] | None = None,
    ) -> CrmListResponse:
        """List contacts."""
        params: dict[str, Any] = {"limit": limit}
        if after:
            params["after"] = after
        if properties:
            params["properties"] = ",".join(properties)
        data = await self._request("GET", "/crm/v3/objects/contacts", params=params)
        return CrmListResponse(**data)

    async def get_contact(
        self,
        contact_id: str,
        properties: list[str] | None = None,
        id_property: str | None = None,
    ) -> CrmObject:
        """Get a single contact by ID or email."""
        params: dict[str, Any] = {}
        if properties:
            params["properties"] = ",".join(properties)
        if id_property:
            params["idProperty"] = id_property
        data = await self._request("GET", f"/crm/v3/objects/contacts/{contact_id}", params=params)
        return CrmObject(**data)

    async def create_contact(self, properties: dict[str, str]) -> CrmObject:
        """Create a new contact."""
        data = await self._request(
            "POST", "/crm/v3/objects/contacts", json_data={"properties": properties}
        )
        return CrmObject(**data)

    async def update_contact(self, contact_id: str, properties: dict[str, str]) -> CrmObject:
        """Update a contact."""
        data = await self._request(
            "PATCH",
            f"/crm/v3/objects/contacts/{contact_id}",
            json_data={"properties": properties},
        )
        return CrmObject(**data)

    # ========================================================================
    # Companies
    # ========================================================================

    async def list_companies(
        self,
        limit: int = 10,
        after: str | None = None,
        properties: list[str] | None = None,
    ) -> CrmListResponse:
        """List companies."""
        params: dict[str, Any] = {"limit": limit}
        if after:
            params["after"] = after
        if properties:
            params["properties"] = ",".join(properties)
        data = await self._request("GET", "/crm/v3/objects/companies", params=params)
        return CrmListResponse(**data)

    async def get_company(
        self,
        company_id: str,
        properties: list[str] | None = None,
    ) -> CrmObject:
        """Get a single company by ID."""
        params: dict[str, Any] = {}
        if properties:
            params["properties"] = ",".join(properties)
        data = await self._request("GET", f"/crm/v3/objects/companies/{company_id}", params=params)
        return CrmObject(**data)

    async def create_company(self, properties: dict[str, str]) -> CrmObject:
        """Create a new company."""
        data = await self._request(
            "POST", "/crm/v3/objects/companies", json_data={"properties": properties}
        )
        return CrmObject(**data)

    async def update_company(self, company_id: str, properties: dict[str, str]) -> CrmObject:
        """Update a company."""
        data = await self._request(
            "PATCH",
            f"/crm/v3/objects/companies/{company_id}",
            json_data={"properties": properties},
        )
        return CrmObject(**data)

    # ========================================================================
    # Deals
    # ========================================================================

    async def list_deals(
        self,
        limit: int = 10,
        after: str | None = None,
        properties: list[str] | None = None,
    ) -> CrmListResponse:
        """List deals."""
        params: dict[str, Any] = {"limit": limit}
        if after:
            params["after"] = after
        if properties:
            params["properties"] = ",".join(properties)
        data = await self._request("GET", "/crm/v3/objects/deals", params=params)
        return CrmListResponse(**data)

    async def create_deal(self, properties: dict[str, str]) -> CrmObject:
        """Create a new deal."""
        data = await self._request(
            "POST", "/crm/v3/objects/deals", json_data={"properties": properties}
        )
        return CrmObject(**data)
