"""
Core tools integration tests.

Tests basic API functionality with real API calls against the HubSpot CRM API.
Requires HUBSPOT_ACCESS_TOKEN environment variable.
"""

import time

import pytest

from mcp_hubspot.api_client import HubspotClient
from mcp_hubspot.api_models import CrmListResponse, CrmObject

# ============================================================================
# Contacts
# ============================================================================


class TestListContacts:
    @pytest.mark.asyncio
    async def test_list_contacts(self, client: HubspotClient):
        result = await client.list_contacts(limit=5)
        assert isinstance(result, CrmListResponse)
        assert isinstance(result.results, list)
        print(f"Found {len(result.results)} contacts")


class TestContactCRUD:
    @pytest.mark.asyncio
    async def test_contact_lifecycle(self, client: HubspotClient):
        """Create a contact, get it, update it, then archive it."""
        ts = int(time.time())
        contact = None
        try:
            # Create
            contact = await client.create_contact(
                {
                    "firstname": "IntegTest",
                    "lastname": f"Contact-{ts}",
                    "email": f"integ-test-{ts}@example.com",
                }
            )
            assert isinstance(contact, CrmObject)
            assert contact.id
            assert contact.properties["firstname"] == "IntegTest"
            print(f"Created contact {contact.id}")

            # Get
            fetched = await client.get_contact(
                contact.id, properties=["firstname", "lastname", "email"]
            )
            assert fetched.id == contact.id
            assert fetched.properties["email"] == f"integ-test-{ts}@example.com"
            print(f"Fetched contact {fetched.id}")

            # Update
            updated = await client.update_contact(
                contact.id, {"lastname": f"Updated-{ts}"}
            )
            assert updated.id == contact.id
            assert updated.properties["lastname"] == f"Updated-{ts}"
            print(f"Updated contact {updated.id}")
        finally:
            # Archive (no delete method in client, use _request directly)
            if contact:
                await client._request(
                    "DELETE", f"/crm/v3/objects/contacts/{contact.id}"
                )
                print(f"Archived contact {contact.id}")


# ============================================================================
# Companies
# ============================================================================


class TestListCompanies:
    @pytest.mark.asyncio
    async def test_list_companies(self, client: HubspotClient):
        result = await client.list_companies(limit=5)
        assert isinstance(result, CrmListResponse)
        assert isinstance(result.results, list)
        print(f"Found {len(result.results)} companies")


class TestCompanyCRUD:
    @pytest.mark.asyncio
    async def test_company_lifecycle(self, client: HubspotClient):
        """Create a company, get it, update it, then archive it."""
        ts = int(time.time())
        company = None
        try:
            # Create
            company = await client.create_company(
                {"name": f"IntegTest Company {ts}"}
            )
            assert isinstance(company, CrmObject)
            assert company.id
            assert "IntegTest Company" in company.properties["name"]
            print(f"Created company {company.id}")

            # Get
            fetched = await client.get_company(
                company.id, properties=["name"]
            )
            assert fetched.id == company.id
            print(f"Fetched company {fetched.id}")

            # Update
            updated = await client.update_company(
                company.id, {"name": f"IntegTest Updated {ts}"}
            )
            assert updated.id == company.id
            assert "Updated" in updated.properties["name"]
            print(f"Updated company {updated.id}")
        finally:
            if company:
                await client._request(
                    "DELETE", f"/crm/v3/objects/companies/{company.id}"
                )
                print(f"Archived company {company.id}")


# ============================================================================
# Deals
# ============================================================================


class TestListDeals:
    @pytest.mark.asyncio
    async def test_list_deals(self, client: HubspotClient):
        result = await client.list_deals(limit=5)
        assert isinstance(result, CrmListResponse)
        assert isinstance(result.results, list)
        print(f"Found {len(result.results)} deals")


class TestCreateDeal:
    @pytest.mark.asyncio
    async def test_create_deal(self, client: HubspotClient):
        """Create a deal then archive it."""
        ts = int(time.time())
        deal = None
        try:
            deal = await client.create_deal(
                {
                    "dealname": f"IntegTest Deal {ts}",
                    "pipeline": "default",
                    "dealstage": "appointmentscheduled",
                }
            )
            assert isinstance(deal, CrmObject)
            assert deal.id
            assert "IntegTest Deal" in deal.properties["dealname"]
            print(f"Created deal {deal.id}")
        finally:
            if deal:
                await client._request(
                    "DELETE", f"/crm/v3/objects/deals/{deal.id}"
                )
                print(f"Archived deal {deal.id}")
