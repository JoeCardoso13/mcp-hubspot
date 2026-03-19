"""Unit tests for the HubSpot API client."""

import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from mcp_hubspot.api_client import HubspotAPIError, HubspotClient
from mcp_hubspot.api_models import CrmListResponse, CrmObject


@pytest_asyncio.fixture
async def mock_client():
    """Create a HubspotClient with mocked session."""
    client = HubspotClient(access_token="test_key")
    client._session = AsyncMock()
    yield client
    await client.close()


class TestClientInitialization:
    """Test client creation and configuration."""

    def test_init_with_explicit_token(self):
        client = HubspotClient(access_token="explicit_token")
        assert client.access_token == "explicit_token"

    def test_init_with_env_var(self):
        os.environ["HUBSPOT_ACCESS_TOKEN"] = "env_token"
        try:
            client = HubspotClient()
            assert client.access_token == "env_token"
        finally:
            del os.environ["HUBSPOT_ACCESS_TOKEN"]

    def test_init_without_token_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("HUBSPOT_ACCESS_TOKEN", None)
            with pytest.raises(ValueError, match="HUBSPOT_ACCESS_TOKEN is required"):
                HubspotClient()

    def test_custom_timeout(self):
        client = HubspotClient(access_token="key", timeout=60.0)
        assert client.timeout == 60.0

    def test_base_url(self):
        assert HubspotClient.BASE_URL == "https://api.hubapi.com"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        async with HubspotClient(access_token="test") as client:
            assert client._session is not None
        assert client._session is None


class TestContactMethods:
    """Test contact API methods."""

    @pytest.mark.asyncio
    async def test_list_contacts(self, mock_client):
        mock_response = {
            "results": [{"id": "1", "properties": {"email": "a@b.com"}}],
            "paging": {"next": {"after": "2"}},
        }
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.list_contacts(limit=10)
        assert isinstance(result, CrmListResponse)
        assert len(result.results) == 1

    @pytest.mark.asyncio
    async def test_list_contacts_with_properties(self, mock_client):
        mock_response = {"results": [], "paging": None}
        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            await mock_client.list_contacts(properties=["email", "firstname"])
        call_args = mock_req.call_args
        assert "email,firstname" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_contact(self, mock_client):
        mock_response = {"id": "1", "properties": {"email": "a@b.com"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.get_contact("1")
        assert isinstance(result, CrmObject)
        assert result.id == "1"

    @pytest.mark.asyncio
    async def test_get_contact_by_email(self, mock_client):
        mock_response = {"id": "1", "properties": {"email": "a@b.com"}}
        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            await mock_client.get_contact("a@b.com", id_property="email")
        call_args = mock_req.call_args
        assert "idProperty" in str(call_args)

    @pytest.mark.asyncio
    async def test_create_contact(self, mock_client):
        mock_response = {"id": "2", "properties": {"email": "new@b.com"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.create_contact({"email": "new@b.com"})
        assert isinstance(result, CrmObject)
        assert result.id == "2"

    @pytest.mark.asyncio
    async def test_update_contact(self, mock_client):
        mock_response = {"id": "1", "properties": {"phone": "555-1234"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.update_contact("1", {"phone": "555-1234"})
        assert isinstance(result, CrmObject)


class TestCompanyMethods:
    """Test company API methods."""

    @pytest.mark.asyncio
    async def test_list_companies(self, mock_client):
        mock_response = {"results": [{"id": "1", "properties": {"name": "Acme"}}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.list_companies()
        assert isinstance(result, CrmListResponse)
        assert len(result.results) == 1

    @pytest.mark.asyncio
    async def test_get_company(self, mock_client):
        mock_response = {"id": "1", "properties": {"name": "Acme"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.get_company("1")
        assert isinstance(result, CrmObject)

    @pytest.mark.asyncio
    async def test_create_company(self, mock_client):
        mock_response = {"id": "2", "properties": {"name": "NewCo"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.create_company({"name": "NewCo"})
        assert isinstance(result, CrmObject)

    @pytest.mark.asyncio
    async def test_update_company(self, mock_client):
        mock_response = {"id": "1", "properties": {"industry": "Tech"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.update_company("1", {"industry": "Tech"})
        assert isinstance(result, CrmObject)


class TestDealMethods:
    """Test deal API methods."""

    @pytest.mark.asyncio
    async def test_list_deals(self, mock_client):
        mock_response = {"results": [{"id": "1", "properties": {"dealname": "Big"}}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.list_deals()
        assert isinstance(result, CrmListResponse)

    @pytest.mark.asyncio
    async def test_create_deal(self, mock_client):
        mock_response = {"id": "2", "properties": {"dealname": "New Deal"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.create_deal({"dealname": "New Deal", "dealstage": "new"})
        assert isinstance(result, CrmObject)


class TestErrorHandling:
    """Test error handling for API errors."""

    @pytest.mark.asyncio
    async def test_401_unauthorized(self, mock_client):
        with patch.object(
            mock_client, "_request", side_effect=HubspotAPIError(401, "Invalid API key")
        ):
            with pytest.raises(HubspotAPIError) as exc_info:
                await mock_client.list_contacts()
            assert exc_info.value.status == 401

    @pytest.mark.asyncio
    async def test_429_rate_limit(self, mock_client):
        with patch.object(
            mock_client, "_request", side_effect=HubspotAPIError(429, "Rate limit exceeded")
        ):
            with pytest.raises(HubspotAPIError) as exc_info:
                await mock_client.list_contacts()
            assert exc_info.value.status == 429

    @pytest.mark.asyncio
    async def test_network_error(self, mock_client):
        with patch.object(
            mock_client,
            "_request",
            side_effect=HubspotAPIError(500, "Network error: Connection failed"),
        ):
            with pytest.raises(HubspotAPIError) as exc_info:
                await mock_client.list_contacts()
            assert exc_info.value.status == 500
            assert "Network error" in exc_info.value.message

    def test_error_string_representation(self):
        err = HubspotAPIError(401, "Unauthorized", {"id": "auth_error"})
        assert "401" in str(err)
        assert "Unauthorized" in str(err)
        assert err.details == {"id": "auth_error"}
