"""Tests for HubSpot MCP Server tools and skill resource."""

from unittest.mock import patch

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_hubspot.api_client import HubspotAPIError
from mcp_hubspot.server import SKILL_CONTENT


class TestSkillResource:
    """Test the skill resource and server instructions."""

    @pytest.mark.asyncio
    async def test_initialize_returns_instructions(self, mcp_server):
        async with Client(mcp_server) as client:
            result = await client.initialize()
            assert result.instructions is not None
            assert "skill://hubspot/usage" in result.instructions

    @pytest.mark.asyncio
    async def test_skill_resource_listed(self, mcp_server):
        async with Client(mcp_server) as client:
            resources = await client.list_resources()
            uris = [str(r.uri) for r in resources]
            assert "skill://hubspot/usage" in uris

    @pytest.mark.asyncio
    async def test_skill_resource_readable(self, mcp_server):
        async with Client(mcp_server) as client:
            contents = await client.read_resource("skill://hubspot/usage")
            text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])
            assert "list_contacts" in text

    @pytest.mark.asyncio
    async def test_skill_content_matches_constant(self, mcp_server):
        async with Client(mcp_server) as client:
            contents = await client.read_resource("skill://hubspot/usage")
            text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])
            assert text == SKILL_CONTENT


class TestToolListing:
    """Test that all tools are registered and discoverable."""

    @pytest.mark.asyncio
    async def test_all_tools_listed(self, mcp_server):
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            names = {t.name for t in tools}
            expected = {
                "list_contacts",
                "get_contact",
                "create_contact",
                "update_contact",
                "list_companies",
                "get_company",
                "create_company",
                "update_company",
                "list_deals",
                "create_deal",
            }
            assert expected == names


class TestContactTools:
    """Test contact tools via FastMCP Client."""

    @pytest.mark.asyncio
    async def test_list_contacts(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_contacts", {"limit": 10})
            assert result is not None
            mock_client.list_contacts.assert_called_once_with(limit=10, after=None, properties=None)

    @pytest.mark.asyncio
    async def test_get_contact(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("get_contact", {"contact_id": "101"})
            assert result is not None
            mock_client.get_contact.assert_called_once_with(
                "101", properties=None, id_property=None
            )

    @pytest.mark.asyncio
    async def test_create_contact(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "create_contact",
                    {"email": "new@example.com", "firstname": "Jane"},
                )
            assert result is not None
            mock_client.create_contact.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_contact(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "update_contact",
                    {"contact_id": "101", "properties": {"phone": "555-1234"}},
                )
            assert result is not None
            mock_client.update_contact.assert_called_once_with("101", {"phone": "555-1234"})

    @pytest.mark.asyncio
    async def test_list_contacts_api_error(self, mcp_server, mock_client):
        mock_client.list_contacts.side_effect = HubspotAPIError(401, "Unauthorized")
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                with pytest.raises(ToolError, match="401"):
                    await client.call_tool("list_contacts", {})


class TestCompanyTools:
    """Test company tools via FastMCP Client."""

    @pytest.mark.asyncio
    async def test_list_companies(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_companies", {"limit": 5})
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_company(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("get_company", {"company_id": "201"})
            assert result is not None

    @pytest.mark.asyncio
    async def test_create_company(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "create_company",
                    {"name": "NewCo", "domain": "newco.com"},
                )
            assert result is not None

    @pytest.mark.asyncio
    async def test_update_company(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "update_company",
                    {"company_id": "201", "properties": {"industry": "Tech"}},
                )
            assert result is not None


class TestDealTools:
    """Test deal tools via FastMCP Client."""

    @pytest.mark.asyncio
    async def test_list_deals(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_deals", {})
            assert result is not None

    @pytest.mark.asyncio
    async def test_create_deal(self, mcp_server, mock_client):
        with patch("mcp_hubspot.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "create_deal",
                    {"dealname": "Big Deal", "dealstage": "contractsent", "amount": "5000"},
                )
            assert result is not None
            mock_client.create_deal.assert_called_once()
