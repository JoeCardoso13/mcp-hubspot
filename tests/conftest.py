"""Shared fixtures for unit tests."""

from unittest.mock import AsyncMock

import pytest

from mcp_hubspot.api_models import CrmListResponse, CrmObject, Paging, PagingResponse
from mcp_hubspot.server import mcp

MOCK_CONTACT = CrmObject(
    id="101",
    properties={"email": "john@example.com", "firstname": "John", "lastname": "Doe"},
    createdAt="2026-01-01T00:00:00Z",
    updatedAt="2026-01-02T00:00:00Z",
)

MOCK_COMPANY = CrmObject(
    id="201",
    properties={"name": "Acme Corp", "domain": "acme.com", "industry": "Technology"},
    createdAt="2026-01-01T00:00:00Z",
    updatedAt="2026-01-02T00:00:00Z",
)

MOCK_DEAL = CrmObject(
    id="301",
    properties={"dealname": "Big Deal", "amount": "5000", "dealstage": "contractsent"},
    createdAt="2026-01-01T00:00:00Z",
    updatedAt="2026-01-02T00:00:00Z",
)

MOCK_LIST_RESPONSE = CrmListResponse(
    results=[MOCK_CONTACT],
    paging=PagingResponse(next=Paging(after="102")),
)

MOCK_LIST_RESPONSE_NO_PAGING = CrmListResponse(results=[MOCK_CONTACT])


@pytest.fixture
def mcp_server():
    """Return the MCP server instance."""
    return mcp


@pytest.fixture
def mock_client():
    """Create a mock API client."""
    client = AsyncMock()

    client.list_contacts = AsyncMock(return_value=MOCK_LIST_RESPONSE)
    client.get_contact = AsyncMock(return_value=MOCK_CONTACT)
    client.create_contact = AsyncMock(return_value=MOCK_CONTACT)
    client.update_contact = AsyncMock(return_value=MOCK_CONTACT)

    client.list_companies = AsyncMock(return_value=MOCK_LIST_RESPONSE)
    client.get_company = AsyncMock(return_value=MOCK_COMPANY)
    client.create_company = AsyncMock(return_value=MOCK_COMPANY)
    client.update_company = AsyncMock(return_value=MOCK_COMPANY)

    client.list_deals = AsyncMock(return_value=MOCK_LIST_RESPONSE)
    client.create_deal = AsyncMock(return_value=MOCK_DEAL)

    return client
