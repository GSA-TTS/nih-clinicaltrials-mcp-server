from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class ResponseFormat(str, Enum):
    """Response format for ClinicalTrials.gov API calls."""
    JSON = "json"
    CSV = "csv"


class MarkupFormat(str, Enum):
    """Markup format for text fields in ClinicalTrials.gov API responses."""
    MARKDOWN = "markdown"
    LEGACY = "legacy"


class OverallStatus(str, Enum):
    """Overall recruitment status of a clinical study."""
    RECRUITING = "RECRUITING"
    NOT_YET_RECRUITING = "NOT_YET_RECRUITING"
    ACTIVE_NOT_RECRUITING = "ACTIVE_NOT_RECRUITING"
    COMPLETED = "COMPLETED"
    ENROLLING_BY_INVITATION = "ENROLLING_BY_INVITATION"
    TERMINATED = "TERMINATED"
    WITHDRAWN = "WITHDRAWN"
    SUSPENDED = "SUSPENDED"
    UNKNOWN = "UNKNOWN"


class GetStudyInput(BaseModel):
    """Input parameters for the GET /studies/{nctId} endpoint."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    nct_id: str = Field(
        ...,
        description="NCT identifier for the clinical study (e.g., 'NCT00000102'). Must start with 'NCT' followed by digits.",
        pattern=r"^NCT\d+$",
    )
    format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Response format: 'json' (default) for structured data or 'csv' for tabular output.",
    )
    markup_format: MarkupFormat = Field(
        default=MarkupFormat.MARKDOWN,
        description="Markup format for text fields: 'markdown' (default) or 'legacy'.",
    )
    fields: Optional[str] = Field(
        default=None,
        description=(
            "Comma-separated list of specific fields to include in the response "
            "(e.g., 'NCTId,BriefTitle,OverallStatus,Phase'). "
            "If omitted, all fields are returned."
        ),
    )

    @field_validator("nct_id")
    @classmethod
    def normalize_nct_id(cls, v: str) -> str:
        return v.upper()


class SearchStudiesInput(BaseModel):
    """Input parameters for the GET /studies (search) endpoint."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    # --- Query parameters (at least one required) ---
    query_cond: Optional[str] = Field(
        default=None,
        description="Search by condition or disease (e.g., 'diabetes', 'breast cancer').",
    )
    query_term: Optional[str] = Field(
        default=None,
        description="General keyword search across all study fields (e.g., 'mRNA vaccine').",
    )
    query_intr: Optional[str] = Field(
        default=None,
        description="Search by intervention or treatment name (e.g., 'insulin', 'pembrolizumab').",
    )
    query_titles: Optional[str] = Field(
        default=None,
        description="Search within study titles only (e.g., 'long COVID fatigue').",
    )
    query_id: Optional[str] = Field(
        default=None,
        description="Search by study ID, including NCT IDs and other secondary identifiers.",
    )
    query_spons: Optional[str] = Field(
        default=None,
        description="Search by sponsor or collaborator name (e.g., 'NIH', 'Pfizer').",
    )
    query_locn: Optional[str] = Field(
        default=None,
        description="Search by location terms such as facility name or city (e.g., 'Boston', 'Mayo Clinic').",
    )
    query_patient: Optional[str] = Field(
        default=None,
        description="Patient-friendly search using plain language (e.g., 'cancer survivor exercise program').",
    )

    # --- Filters ---
    filter_overall_status: Optional[List[OverallStatus]] = Field(
        default=None,
        description=(
            "Filter by recruitment status. Accepted values: RECRUITING, NOT_YET_RECRUITING, "
            "ACTIVE_NOT_RECRUITING, COMPLETED, ENROLLING_BY_INVITATION, TERMINATED, "
            "WITHDRAWN, SUSPENDED, UNKNOWN."
        ),
    )
    filter_geo: Optional[str] = Field(
        default=None,
        description=(
            "Filter studies to those with a location within a geographic radius. "
            "Format: 'distance(lat,lon,radius)' where radius uses 'mi' or 'km' "
            "(e.g., 'distance(39.0,-77.0,50mi)')."
        ),
    )
    filter_ids: Optional[List[str]] = Field(
        default=None,
        description="Filter to a specific list of NCT IDs (e.g., ['NCT04280705', 'NCT00000102']).",
    )
    post_filter_overall_status: Optional[List[OverallStatus]] = Field(
        default=None,
        description=(
            "Same as filter_overall_status but applied after aggregation counts are computed, "
            "so counts reflect the full result set rather than the filtered subset."
        ),
    )
    post_filter_geo: Optional[str] = Field(
        default=None,
        description=(
            "Same as filter_geo but applied after aggregation counts are computed. "
            "Format: 'distance(lat,lon,radius)' (e.g., 'distance(42.36,-71.06,25mi)')."
        ),
    )
    agg_filters: Optional[str] = Field(
        default=None,
        description=(
            "Aggregation filters as a comma-separated string. "
            "Phase values: '0' (early phase 1), '1', '2', '3', '4', 'na' (not applicable). "
            "Study type values: 'int' (interventional), 'obs' (observational). "
            "Example: 'phase:2 3,studyType:int' for phase 2 or 3 interventional studies."
        ),
    )

    # --- Sorting & pagination ---
    sort: Optional[str] = Field(
        default=None,
        description=(
            "Sort order as 'field:direction'. Direction is 'asc' or 'desc'. "
            "Common sort fields: 'LastUpdatePostDate', 'StudyFirstPostDate', 'EnrollmentCount'. "
            "Example: 'LastUpdatePostDate:desc'."
        ),
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Number of studies to return per page (1–1000, default 20).",
    )
    page_token: Optional[str] = Field(
        default=None,
        description=(
            "Pagination cursor returned as 'nextPageToken' in a previous response. "
            "Pass this to retrieve the next page of results."
        ),
    )
    count_total: bool = Field(
        default=False,
        description="If true, include the total number of matching studies in the response.",
    )

    # --- Output format ---
    format: ResponseFormat = Field(
        default=ResponseFormat.JSON,
        description="Response format: 'json' (default) for structured data or 'csv' for tabular output.",
    )
    markup_format: MarkupFormat = Field(
        default=MarkupFormat.MARKDOWN,
        description="Markup format for text fields: 'markdown' (default) or 'legacy'.",
    )
    fields: Optional[str] = Field(
        default=None,
        description=(
            "Comma-separated list of specific fields to return "
            "(e.g., 'NCTId,BriefTitle,OverallStatus,Phase'). "
            "If omitted, all fields are returned."
        ),
    )

    @model_validator(mode="after")
    def require_at_least_one_query_or_filter(self) -> "SearchStudiesInput":
        query_fields = [
            self.query_cond, self.query_term, self.query_intr, self.query_titles,
            self.query_id, self.query_spons, self.query_locn, self.query_patient,
            self.filter_ids,
        ]
        if not any(query_fields):
            raise ValueError(
                "At least one query parameter (query_cond, query_term, query_intr, "
                "query_titles, query_id, query_spons, query_locn, query_patient) "
                "or filter_ids must be provided."
            )
        return self
