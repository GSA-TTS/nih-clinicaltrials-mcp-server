# ClinicalTrials.gov MCP Server

An MCP (Model Context Protocol) server that exposes the [ClinicalTrials.gov v2 API](https://clinicaltrials.gov/data-api/api) as tools for LLM agents. Supports searching, retrieving, and analyzing clinical study data from the full registry of 570,000+ studies.

## Tools

### `clinicaltrials_get_study`
Retrieve a single study record by NCT ID.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `nct_id` | string | Yes | NCT identifier, e.g. `NCT00000102` |
| `fields` | `StudyField[]` | No | Specific fields to return; omit for all fields |
| `format` | `json` \| `csv` | No | Response format (default: `json`) |
| `markup_format` | `markdown` \| `legacy` | No | Text markup format (default: `markdown`) |

### `clinicaltrials_search_studies`
Search studies by condition, intervention, sponsor, location, and more. Returns paginated results.

**Query parameters** (at least one required):

| Parameter | Description |
|---|---|
| `query_cond` | Condition or disease (e.g. `diabetes`) |
| `query_term` | General keyword search |
| `query_intr` | Intervention or treatment name |
| `query_titles` | Search within study titles only |
| `query_id` | NCT ID or other study identifier |
| `query_spons` | Sponsor or collaborator name |
| `query_locn` | Location name or city |
| `query_patient` | Plain-language patient-friendly search |

**Filters:**

| Parameter | Description |
|---|---|
| `filter_overall_status` | List of recruitment statuses (e.g. `[RECRUITING, NOT_YET_RECRUITING]`) |
| `filter_geo` | Geographic radius, e.g. `distance(39.0,-77.0,50mi)` |
| `filter_ids` | List of specific NCT IDs |
| `post_filter_overall_status` | Status filter applied after aggregation counts |
| `post_filter_geo` | Geo filter applied after aggregation counts |
| `agg_filters` | Aggregation filters string, e.g. `phase:2 3,studyType:int` |

**Pagination & output:**

| Parameter | Default | Description |
|---|---|---|
| `sort` | — | Sort field and direction, e.g. `LastUpdatePostDate:desc` |
| `page_size` | `20` | Results per page (1–1000) |
| `page_token` | — | Cursor from previous response's `nextPageToken` |
| `count_total` | `false` | Include total match count in response |
| `fields` | all | Specific `StudyField` values to return |
| `format` | `json` | `json` or `csv` |
| `markup_format` | `markdown` | `markdown` or `legacy` |

### `clinicaltrials_get_field_values`
Get the distribution of values across all studies for one or more fields. Useful for understanding what values exist and how common they are (e.g. study counts per phase, per country, per status).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `fields` | `StudyField[]` | Yes | Fields to get distributions for |

Works best with enumerable fields: `Phase`, `OverallStatus`, `StudyType`, `Sex`, `StdAge`, `LeadSponsorClass`, `InterventionType`, `LocationCountry`, `DesignAllocation`, `IsFDARegulatedDrug`, `HasResults`, `IPDSharing`.

## Field Selection

All three tools accept a `fields` parameter typed as `List[StudyField]`. The `StudyField` enum contains all 342 valid field names sourced from the ClinicalTrials.gov metadata API, grouped by section:

- **Identification**: `NCTId`, `BriefTitle`, `OfficialTitle`, `Acronym`, `OrgFullName`, ...
- **Status**: `OverallStatus`, `StartDate`, `CompletionDate`, `LastUpdatePostDate`, ...
- **Sponsor**: `LeadSponsorName`, `LeadSponsorClass`, `CollaboratorName`, ...
- **Design**: `Phase`, `StudyType`, `DesignAllocation`, `DesignMasking`, `EnrollmentCount`, ...
- **Arms / Interventions**: `InterventionType`, `InterventionName`, `ArmGroupLabel`, ...
- **Outcomes**: `PrimaryOutcomeMeasure`, `SecondaryOutcomeMeasure`, ...
- **Eligibility**: `EligibilityCriteria`, `Sex`, `MinimumAge`, `MaximumAge`, `StdAge`, ...
- **Locations**: `LocationFacility`, `LocationCity`, `LocationState`, `LocationCountry`, ...
- **Results**: participant flow, baseline characteristics, outcome measures, adverse events
- **MeSH / Browse**: `ConditionMeshTerm`, `InterventionMeshTerm`, ...

## Setup

### Prerequisites
- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

### Install

```bash
git clone https://github.com/your-org/nih-clinicaltrials-mcp-server
cd nih-clinicaltrials-mcp-server
uv sync
uv pip install -e .
```

### Run locally (stdio)

```bash
uv run python src/clinicaltrials/app.py
```

### Run as HTTP server

```bash
PORT=8000 uv run python src/clinicaltrials/app.py
# or
uv run uvicorn clinicaltrials.app:app --port 8000
```

### Connect from Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clinicaltrials": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/nih-clinicaltrials-mcp-server",
        "python", "src/clinicaltrials/app.py"
      ]
    }
  }
}
```

## Project Structure

```
src/clinicaltrials/
├── app.py       # FastMCP server init and transport config
├── tools.py     # Tool implementations (register_tools)
├── models.py    # Pydantic models and enums (StudyField, OverallStatus, ...)
├── utils.py     # Shared HTTP client (Chrome TLS impersonation) and error handling
├── prompts.py   # MCP prompts
└── routes.py    # Custom HTTP routes (/health)
```

## Implementation Notes

**TLS fingerprinting:** The ClinicalTrials.gov CDN blocks standard Python HTTP clients via JA3 TLS fingerprint detection. This server uses [`curl-cffi`](https://github.com/yifeikong/curl-cffi) to impersonate Chrome's TLS handshake, which resolves the 403 errors that `httpx` and `requests` produce.

**No authentication required:** The ClinicalTrials.gov API is public and requires no API key.

**API version:** ClinicalTrials.gov v2 (`https://clinicaltrials.gov/api/v2`). Data is refreshed daily.
