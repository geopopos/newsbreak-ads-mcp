"""
Pydantic models for NewsBreak Business API
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# Enums and Constants
class OnlineStatus(str):
    """Campaign online status values"""
    WARNING = "WARNING"
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


class OSType(str):
    """Operating system types for event filtering"""
    IOS = "IOS"
    ANDROID = "ANDROID"
    WEB = ""  # Empty string for web events


class EventType(str):
    """Event tracking types"""
    PIXEL = "PIXEL"
    POSTBACK = "POSTBACK"


class MobilePartner(str):
    """Supported mobile attribution partners"""
    APPSFLYER = "AppsFlyer"
    ADJUST = "Adjust"
    SINGULAR = "Singular"
    KOCHAVA = "Kochava"
    TENJIN = "Tenjin"
    ADVERTISER_S2S = "Advertiser S2S"


# Response Models
class BaseResponse(BaseModel):
    """Base response model for all API calls"""
    code: Optional[int] = Field(None, description="Status code, 0 for success (may be missing in some responses)")
    errMsg: Optional[str] = Field(None, description="Error message when code is non-zero")
    message: Optional[str] = Field(None, description="Alternative error message field")
    error: Optional[str] = Field(None, description="Another alternative error message field")
    timestamp: Optional[str] = Field(None, description="Error timestamp (present in error responses)")
    url: Optional[str] = Field(None, description="Request URL (present in error responses)")


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    pageNo: int
    pageSize: int
    total: int
    hasNext: bool


# Ad Account Models
class AdAccount(BaseModel):
    """Ad account information"""
    id: str = Field(description="Ad account ID")
    name: str = Field(description="Ad account name")
    createTime: int = Field(description="Creation timestamp")


class Organization(BaseModel):
    """Organization with ad accounts"""
    id: str = Field(description="Organization ID")
    name: str = Field(description="Organization name")
    adAccounts: List[AdAccount] = Field(default_factory=list)


class AdAccountsResponse(BaseResponse):
    """Response for get ad accounts endpoint"""
    data: Optional[dict] = None

    @property
    def organizations(self) -> List[Organization]:
        """Extract organizations from data.list"""
        if self.data and "list" in self.data:
            return [Organization(**org) for org in self.data["list"]]
        return []


# Campaign Models
class Campaign(BaseModel):
    """Campaign information"""
    id: str = Field(description="Campaign ID")
    name: str = Field(description="Campaign name")
    orgId: str = Field(description="Organization ID")
    adAccountId: str = Field(description="Ad account ID")
    objective: Optional[str] = Field(None, description="Campaign objective")
    budget: Optional[float] = Field(None, description="Campaign budget")
    status: Optional[str] = Field(None, description="Campaign status")
    onlineStatus: Optional[str] = Field(None, description="Online status")
    createTime: Optional[int] = Field(None, description="Creation timestamp")
    updateTime: Optional[int] = Field(None, description="Update timestamp")


class CampaignsData(BaseModel):
    """Campaigns list with pagination"""
    list: List[Campaign] = Field(default_factory=list)
    pageNo: int
    pageSize: int
    total: int
    hasNext: bool


class CampaignsResponse(BaseResponse):
    """Response for get campaigns endpoint"""
    data: Optional[CampaignsData] = None


# Event Models
class Event(BaseModel):
    """Tracking event information"""
    id: str = Field(description="Event ID")
    name: str = Field(description="Event name")
    orgId: str = Field(description="Organization ID")
    type: str = Field(description="Event type: PIXEL or POSTBACK")
    eventType: Optional[str] = Field(None, description="Specific event type")
    url: Optional[str] = Field(None, description="Event URL")
    os: Optional[str] = Field(None, description="Operating system")
    appEvent: Optional[bool] = Field(None, description="Is app event")
    mobilePartner: Optional[str] = Field(None, description="Mobile attribution partner")
    clickTrackingUrl: Optional[str] = Field(None, description="Click tracking URL")
    impressionTrackingUrl: Optional[str] = Field(None, description="Impression tracking URL")
    eventParams: Optional[dict] = Field(None, description="Additional event parameters")
    version: Optional[int] = Field(None, description="Event version")
    createTime: Optional[int] = Field(None, description="Creation timestamp")
    updateTime: Optional[int] = Field(None, description="Update timestamp")


class EventsData(BaseModel):
    """Events list"""
    list: List[Event] = Field(default_factory=list)


class EventsResponse(BaseResponse):
    """Response for get events endpoint"""
    data: Optional[EventsData] = None


# Report Models
class ReportRequest(BaseModel):
    """Request model for synchronous reports"""
    adAccountId: str = Field(description="Ad account ID")
    dateFrom: str = Field(description="Start date (YYYY-MM-DD)")
    dateTo: str = Field(description="End date (YYYY-MM-DD)")
    dimensions: Optional[List[str]] = Field(None, description="Report dimensions")
    metrics: Optional[List[str]] = Field(None, description="Report metrics")
    filters: Optional[dict] = Field(None, description="Report filters")
    level: Optional[Literal["campaign", "ad_set", "ad"]] = Field(None, description="Reporting level")


class ReportRow(BaseModel):
    """Single row in report data - API returns flat structure with dimensions and metrics at same level"""
    # Dimension fields (optional based on what was requested)
    date: Optional[str] = Field(None, description="Date (YYYY-MM-DD)")
    hour: Optional[str] = Field(None, description="Hour")
    adAccountId: Optional[str] = Field(None, description="Ad account ID")
    adAccount: Optional[str] = Field(None, description="Ad account name")
    orgId: Optional[str] = Field(None, description="Organization ID")
    organization: Optional[str] = Field(None, description="Organization name")
    campaignId: Optional[str] = Field(None, description="Campaign ID")
    campaign: Optional[str] = Field(None, description="Campaign name")
    adSetId: Optional[str] = Field(None, description="Ad set ID")
    adSet: Optional[str] = Field(None, description="Ad set name")
    adId: Optional[str] = Field(None, description="Ad ID")
    ad: Optional[str] = Field(None, description="Ad name")

    # Metric fields (optional based on what was requested)
    cost: Optional[float] = Field(None, description="Cost/Spend")
    impression: Optional[int] = Field(None, description="Impressions")
    click: Optional[int] = Field(None, description="Clicks")
    conversion: Optional[int] = Field(None, description="Conversions")
    value: Optional[float] = Field(None, description="Conversion value")
    cpm: Optional[float] = Field(None, description="Cost per mille (CPM)")
    cpc: Optional[float] = Field(None, description="Cost per click (CPC)")
    cpa: Optional[float] = Field(None, description="Cost per acquisition (CPA)")
    ctr: Optional[float] = Field(None, description="Click-through rate (CTR)")
    cvr: Optional[float] = Field(None, description="Conversion rate (CVR)")
    vpa: Optional[float] = Field(None, description="Value per acquisition")
    roas: Optional[float] = Field(None, description="Return on ad spend (ROAS)")

    # Allow additional fields the API might return
    class Config:
        extra = "allow"


class ReportData(BaseModel):
    """Report data structure"""
    rows: List[ReportRow] = Field(default_factory=list)
    total: Optional[int] = Field(None, description="Total rows")


class ReportResponse(BaseResponse):
    """Response for report endpoints"""
    data: Optional[ReportData] = None


# Ad Set Models
class AdSet(BaseModel):
    """Ad set information"""
    id: str = Field(description="Ad set ID")
    name: str = Field(description="Ad set name")
    campaignId: str = Field(description="Parent campaign ID")
    status: Optional[str] = Field(None, description="Ad set status")
    budget: Optional[float] = Field(None, description="Ad set budget")
    createTime: Optional[int] = Field(None, description="Creation timestamp")
    updateTime: Optional[int] = Field(None, description="Update timestamp")


class AdSetsData(BaseModel):
    """Ad sets list with pagination"""
    list: List[AdSet] = Field(default_factory=list)
    pageNo: int
    pageSize: int
    total: int
    hasNext: bool


class AdSetsResponse(BaseResponse):
    """Response for get ad sets endpoint"""
    data: Optional[AdSetsData] = None


# Ad Models
class Ad(BaseModel):
    """Ad information"""
    id: str = Field(description="Ad ID")
    name: str = Field(description="Ad name")
    adSetId: str = Field(description="Parent ad set ID")
    status: Optional[str] = Field(None, description="Ad status")
    creativeType: Optional[str] = Field(None, description="Creative type")
    createTime: Optional[int] = Field(None, description="Creation timestamp")
    updateTime: Optional[int] = Field(None, description="Update timestamp")


class AdsData(BaseModel):
    """Ads list with pagination"""
    list: List[Ad] = Field(default_factory=list)
    pageNo: int
    pageSize: int
    total: int
    hasNext: bool


class AdsResponse(BaseResponse):
    """Response for get ads endpoint"""
    data: Optional[AdsData] = None
