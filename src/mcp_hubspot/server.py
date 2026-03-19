"""HubSpot MCP Server - FastMCP Implementation."""

import logging
import os
import sys
from importlib.resources import files

from fastmcp import Context, FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_hubspot.api_client import HubspotAPIError, HubspotClient
from mcp_hubspot.api_models import CrmListResponse, CrmObject

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_hubspot")

SKILL_CONTENT = files("mcp_hubspot").joinpath("SKILL.md").read_text()

mcp = FastMCP(
    "HubSpot",
    instructions=(
        "Before using tools, read the skill://hubspot/usage resource "
        "for tool selection guidance and workflow patterns."
    ),
)

_client: HubspotClient | None = None


def get_client(ctx: Context | None = None) -> HubspotClient:
    """Get or create the API client instance."""
    global _client
    if _client is None:
        access_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
        if not access_token:
            msg = "HUBSPOT_ACCESS_TOKEN environment variable is required"
            raise ValueError(msg)
        _client = HubspotClient(access_token=access_token)
    return _client


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-hubspot"})


# ============================================================================
# Contacts
# ============================================================================


@mcp.tool()
async def list_contacts(
    limit: int = 10,
    after: str | None = None,
    properties: list[str] | None = None,
    ctx: Context | None = None,
) -> CrmListResponse:
    """List contacts from HubSpot CRM.

    Args:
        limit: Maximum number of contacts to return (1-100, default 10)
        after: Pagination cursor for the next page of results
        properties: Specific properties to include (e.g. ["email", "firstname", "lastname"])
        ctx: MCP context
    """
    client = get_client(ctx)
    try:
        return await client.list_contacts(limit=limit, after=after, properties=properties)
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def get_contact(
    contact_id: str,
    properties: list[str] | None = None,
    id_property: str | None = None,
    ctx: Context | None = None,
) -> CrmObject:
    """Get a single contact by ID or by a unique property like email.

    Args:
        contact_id: The contact's HubSpot ID, or a unique property value (e.g. email address)
        properties: Specific properties to include (e.g. ["email", "firstname", "phone"])
        id_property: Use a unique property as the lookup key (e.g. "email")
        ctx: MCP context
    """
    client = get_client(ctx)
    try:
        return await client.get_contact(contact_id, properties=properties, id_property=id_property)
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def create_contact(
    email: str,
    firstname: str | None = None,
    lastname: str | None = None,
    phone: str | None = None,
    company: str | None = None,
    extra_properties: dict[str, str] | None = None,
    ctx: Context | None = None,
) -> CrmObject:
    """Create a new contact in HubSpot CRM.

    Args:
        email: Contact email address (required)
        firstname: Contact first name
        lastname: Contact last name
        phone: Contact phone number
        company: Company name
        extra_properties: Additional HubSpot properties as key-value pairs
        ctx: MCP context
    """
    client = get_client(ctx)
    props: dict[str, str] = {"email": email}
    if firstname:
        props["firstname"] = firstname
    if lastname:
        props["lastname"] = lastname
    if phone:
        props["phone"] = phone
    if company:
        props["company"] = company
    if extra_properties:
        props.update(extra_properties)

    try:
        return await client.create_contact(props)
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def update_contact(
    contact_id: str,
    properties: dict[str, str] | None = None,
    ctx: Context | None = None,
) -> CrmObject:
    """Update an existing contact's properties.

    Args:
        contact_id: The HubSpot contact ID to update
        properties: Properties to update as key-value pairs (e.g. {"phone": "555-1234"})
        ctx: MCP context
    """
    client = get_client(ctx)
    try:
        return await client.update_contact(contact_id, properties or {})
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


# ============================================================================
# Companies
# ============================================================================


@mcp.tool()
async def list_companies(
    limit: int = 10,
    after: str | None = None,
    properties: list[str] | None = None,
    ctx: Context | None = None,
) -> CrmListResponse:
    """List companies from HubSpot CRM.

    Args:
        limit: Maximum number of companies to return (1-100, default 10)
        after: Pagination cursor for the next page of results
        properties: Specific properties to include (e.g. ["name", "domain", "industry"])
        ctx: MCP context
    """
    client = get_client(ctx)
    try:
        return await client.list_companies(limit=limit, after=after, properties=properties)
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def get_company(
    company_id: str,
    properties: list[str] | None = None,
    ctx: Context | None = None,
) -> CrmObject:
    """Get a single company by ID.

    Args:
        company_id: The HubSpot company ID
        properties: Specific properties to include (e.g. ["name", "domain", "industry"])
        ctx: MCP context
    """
    client = get_client(ctx)
    try:
        return await client.get_company(company_id, properties=properties)
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def create_company(
    name: str,
    domain: str | None = None,
    industry: str | None = None,
    extra_properties: dict[str, str] | None = None,
    ctx: Context | None = None,
) -> CrmObject:
    """Create a new company in HubSpot CRM.

    Args:
        name: Company name (required)
        domain: Company website domain (e.g. "example.com")
        industry: Industry category
        extra_properties: Additional HubSpot properties as key-value pairs
        ctx: MCP context
    """
    client = get_client(ctx)
    props: dict[str, str] = {"name": name}
    if domain:
        props["domain"] = domain
    if industry:
        props["industry"] = industry
    if extra_properties:
        props.update(extra_properties)

    try:
        return await client.create_company(props)
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def update_company(
    company_id: str,
    properties: dict[str, str] | None = None,
    ctx: Context | None = None,
) -> CrmObject:
    """Update an existing company's properties.

    Args:
        company_id: The HubSpot company ID to update
        properties: Properties to update as key-value pairs (e.g. {"industry": "Technology"})
        ctx: MCP context
    """
    client = get_client(ctx)
    try:
        return await client.update_company(company_id, properties or {})
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


# ============================================================================
# Deals
# ============================================================================


@mcp.tool()
async def list_deals(
    limit: int = 10,
    after: str | None = None,
    properties: list[str] | None = None,
    ctx: Context | None = None,
) -> CrmListResponse:
    """List deals from HubSpot CRM.

    Args:
        limit: Maximum number of deals to return (1-100, default 10)
        after: Pagination cursor for the next page of results
        properties: Specific properties to include (e.g. ["dealname", "amount", "dealstage"])
        ctx: MCP context
    """
    client = get_client(ctx)
    try:
        return await client.list_deals(limit=limit, after=after, properties=properties)
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def create_deal(
    dealname: str,
    dealstage: str,
    pipeline: str = "default",
    amount: str | None = None,
    closedate: str | None = None,
    extra_properties: dict[str, str] | None = None,
    ctx: Context | None = None,
) -> CrmObject:
    """Create a new deal in HubSpot CRM.

    Args:
        dealname: Name of the deal (required)
        dealstage: Deal stage internal ID (required, e.g. "appointmentscheduled")
        pipeline: Pipeline ID (defaults to "default")
        amount: Deal amount as a string (e.g. "1500.00")
        closedate: Expected close date in ISO format (e.g. "2026-06-15T00:00:00Z")
        extra_properties: Additional HubSpot properties as key-value pairs
        ctx: MCP context
    """
    client = get_client(ctx)
    props: dict[str, str] = {
        "dealname": dealname,
        "dealstage": dealstage,
        "pipeline": pipeline,
    }
    if amount:
        props["amount"] = amount
    if closedate:
        props["closedate"] = closedate
    if extra_properties:
        props.update(extra_properties)

    try:
        return await client.create_deal(props)
    except HubspotAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


# ============================================================================
# Resources
# ============================================================================


@mcp.resource("skill://hubspot/usage")
def skill_usage() -> str:
    """Usage guide for the HubSpot MCP server tools."""
    return SKILL_CONTENT


# ============================================================================
# Entrypoints
# ============================================================================

app = mcp.http_app()

if __name__ == "__main__":
    mcp.run()
