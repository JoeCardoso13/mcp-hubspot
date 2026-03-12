# HubSpot MCP Server — Skill Guide

## Tools

| Tool | Use when... |
|------|-------------|
| `list_contacts` | You need to browse contacts or paginate through them |
| `get_contact` | You have a contact ID or email and need full details |
| `create_contact` | You need to add a new contact to the CRM |
| `update_contact` | You need to change a contact's properties |
| `list_companies` | You need to browse companies |
| `get_company` | You have a company ID and need full details |
| `create_company` | You need to add a new company to the CRM |
| `update_company` | You need to change a company's properties |
| `list_deals` | You need to browse deals in the pipeline |
| `create_deal` | You need to create a new deal |

## Context Reuse

- Use the `id` from list results when calling get/update tools
- Use `id_property="email"` with `get_contact` to look up by email instead of ID
- Pass `properties` lists to control which fields are returned (saves tokens)

## Workflows

### 1. Look Up a Contact
1. `get_contact` with email via `id_property="email"` — or `list_contacts` to browse
2. Use returned `id` for any follow-up `update_contact` calls

### 2. Onboard a New Customer
1. `create_company` with name and domain
2. `create_contact` with email, name, and company
3. `create_deal` linking to the pipeline stage

### 3. Pipeline Review
1. `list_deals` with properties `["dealname", "amount", "dealstage", "closedate"]`
2. Page through using `after` cursor if more results exist
