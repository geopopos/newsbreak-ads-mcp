"""
NewsBreak Business API Client
"""
import os
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
from functools import wraps

from models import (
    AdAccountsResponse,
    CampaignsResponse,
    EventsResponse,
    ReportResponse,
    AdSetsResponse,
    AdsResponse,
)


class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, calls_per_second: int = 10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Wait if necessary to respect rate limit"""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            time_since_last = now - self.last_call
            if time_since_last < self.min_interval:
                await asyncio.sleep(self.min_interval - time_since_last)
            self.last_call = asyncio.get_event_loop().time()


class NewsBreakAPIError(Exception):
    """Custom exception for NewsBreak API errors"""

    def __init__(self, code: int, message: str, response: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.response = response
        super().__init__(f"NewsBreak API Error (code={code}): {message}")


class NewsBreakClient:
    """Client for NewsBreak Business API"""

    BASE_URL = "https://business.newsbreak.com/business-api/v1"

    def __init__(
        self,
        access_token: Optional[str] = None,
        rate_limit: int = 10,
        timeout: float = 30.0,
    ):
        """
        Initialize NewsBreak API client

        Args:
            access_token: NewsBreak access token (or set NEWSBREAK_ACCESS_TOKEN env var)
            rate_limit: Maximum requests per second
            timeout: Request timeout in seconds
        """
        self.access_token = access_token or os.getenv("NEWSBREAK_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError(
                "Access token required. Set NEWSBREAK_ACCESS_TOKEN environment "
                "variable or pass access_token parameter."
            )

        self.rate_limiter = RateLimiter(calls_per_second=rate_limit)
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "Access-Token": self.access_token,
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        retry_count: int = 3,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to NewsBreak API with rate limiting and retries

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON request body
            retry_count: Number of retries on failure

        Returns:
            Response data as dict

        Raises:
            NewsBreakAPIError: If API returns error response
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        await self.rate_limiter.acquire()

        for attempt in range(retry_count):
            try:
                response = await self._client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=json,
                )

                # Check HTTP status first
                if response.status_code >= 400:
                    # Try to parse error response
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message") or error_data.get("errMsg") or error_data.get("error") or f"HTTP {response.status_code}"
                        raise NewsBreakAPIError(
                            code=response.status_code,
                            message=error_msg,
                            response=error_data,
                        )
                    except ValueError:
                        # Not JSON, use status text
                        raise NewsBreakAPIError(
                            code=response.status_code,
                            message=f"HTTP {response.status_code}: {response.text[:200]}",
                        )

                # Parse response
                data = response.json()

                # Check if response has 'code' field (standard NewsBreak format)
                if "code" in data:
                    if data["code"] != 0:
                        error_msg = data.get("errMsg", "Unknown error")
                        raise NewsBreakAPIError(
                            code=data["code"],
                            message=error_msg,
                            response=data,
                        )
                    return data

                # Check for error response without 'code' field
                # (timestamp + url format usually indicates an error)
                if "timestamp" in data and "url" in data and "code" not in data:
                    error_msg = data.get("message") or data.get("error") or "API returned error response"
                    raise NewsBreakAPIError(
                        code=response.status_code,
                        message=f"{error_msg} (timestamp: {data.get('timestamp')})",
                        response=data,
                    )

                # Return data even if no 'code' field (might be valid response)
                return data

            except httpx.HTTPError as e:
                if attempt == retry_count - 1:
                    raise NewsBreakAPIError(
                        code=-1,
                        message=f"HTTP error: {str(e)}",
                    )

                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

        raise NewsBreakAPIError(code=-1, message="Max retries exceeded")

    # Ad Account Methods
    async def get_ad_accounts(self, org_ids: List[str]) -> AdAccountsResponse:
        """
        Get ad accounts for organizations

        Args:
            org_ids: List of organization IDs

        Returns:
            AdAccountsResponse with ad accounts grouped by organization
        """
        params = {"orgIds": org_ids}
        data = await self._request("GET", "/ad-account/getGroupsByOrgIds", params=params)
        return AdAccountsResponse(**data)

    # Campaign Methods
    async def get_campaigns(
        self,
        ad_account_id: str,
        page_no: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        online_status: Optional[str] = None,
    ) -> CampaignsResponse:
        """
        Get campaigns for an ad account

        Args:
            ad_account_id: Ad account ID
            page_no: Page number (1-indexed)
            page_size: Results per page (5, 10, 20, 50, 100, 200, 500)
            search: Search query
            online_status: Filter by status (WARNING, INACTIVE, ACTIVE, DELETED)

        Returns:
            CampaignsResponse with campaign list and pagination
        """
        params = {
            "adAccountId": ad_account_id,
            "pageNo": page_no,
            "pageSize": page_size,
        }

        if search:
            params["search"] = search
        if online_status:
            params["onlineStatus"] = online_status

        data = await self._request("GET", "/campaign/getList", params=params)
        return CampaignsResponse(**data)

    # Event Methods
    async def get_events(
        self,
        ad_account_id: str,
        os: Optional[str] = None,
    ) -> EventsResponse:
        """
        Get tracking events for an ad account

        Args:
            ad_account_id: Ad account ID
            os: Filter by OS (IOS, ANDROID, or empty string for web)

        Returns:
            EventsResponse with event list
        """
        params = {}
        if os is not None:
            params["os"] = os

        data = await self._request(
            "GET",
            f"/event/getList/{ad_account_id}",
            params=params if params else None,
        )
        return EventsResponse(**data)

    # Report Methods
    async def run_synchronous_report(
        self,
        ad_account_id: str,
        date_from: str,
        date_to: str,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        level: Optional[str] = None,
    ) -> ReportResponse:
        """
        Run a synchronous report

        Args:
            ad_account_id: Ad account ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            dimensions: Report dimensions (e.g., ['date', 'campaign_id'])
            metrics: Report metrics (e.g., ['impressions', 'clicks', 'spend'])
            filters: Additional filters
            level: Reporting level (campaign, ad_set, ad)

        Returns:
            ReportResponse with report data
        """
        # Build request in the CORRECT format per NewsBreak API documentation
        # See: https://business.newsbreak.com/business-api-doc/docs/api-reference/reporting/run-a-synchronous-report

        # Map our parameter names to API's uppercase enum values
        dimension_map = {
            "date": "DATE",
            "hour": "HOUR",
            "org": "ORG",
            "organization": "ORG",
            "ad_account": "AD_ACCOUNT",
            "ad_account_id": "AD_ACCOUNT",
            "campaign": "CAMPAIGN",
            "campaign_id": "CAMPAIGN",  # Common alias
            "ad_set": "AD_SET",
            "ad_set_id": "AD_SET",  # Common alias
            "ad": "AD",
            "ad_id": "AD",  # Common alias
        }

        metric_map = {
            "cost": "COST",
            "spend": "COST",  # Alias
            "impression": "IMPRESSION",
            "impressions": "IMPRESSION",  # Alias
            "click": "CLICK",
            "clicks": "CLICK",  # Alias
            "conversion": "CONVERSION",
            "conversions": "CONVERSION",  # Alias
            "value": "VALUE",
            "cpm": "CPM",
            "cpc": "CPC",
            "cpa": "CPA",
            "ctr": "CTR",
            "cvr": "CVR",
            "vpa": "VPA",
        }

        # Convert dimensions to uppercase API format
        api_dimensions = []
        if dimensions:
            for dim in dimensions:
                api_dimensions.append(dimension_map.get(dim.lower(), dim.upper()))
        else:
            # Default dimensions if none provided
            api_dimensions = ["DATE", "CAMPAIGN"]

        # Convert metrics to uppercase API format
        api_metrics = []
        if metrics:
            for metric in metrics:
                api_metrics.append(metric_map.get(metric.lower(), metric.upper()))
        else:
            # Default metrics if none provided
            api_metrics = ["COST", "IMPRESSION", "CLICK", "CTR", "CPC"]

        # Build request matching the exact format from API documentation
        request_body = {
            "name": f"report_{date_from}_{date_to}",  # Simplified name
            "dateRange": "FIXED",
            "startDate": date_from,
            "endDate": date_to,
            "dimensions": api_dimensions,
            "metrics": api_metrics,
            "filter": "AD_ACCOUNT",
            "filterIds": [int(ad_account_id)],
            "dataSource": "HOURLY",
        }

        # Debug logging - log the request we're about to send
        import sys
        import json
        print(f"\nDEBUG: Sending report request:", file=sys.stderr)
        print(f"DEBUG: Request body: {json.dumps(request_body, indent=2)}", file=sys.stderr)
        print(f"DEBUG: Original params - date_from: {date_from}, date_to: {date_to}", file=sys.stderr)
        print(f"DEBUG: Original dimensions: {dimensions}, metrics: {metrics}", file=sys.stderr)
        print(f"DEBUG: Mapped dimensions: {api_dimensions}, metrics: {api_metrics}\n", file=sys.stderr)

        # Use the correct endpoint: /reports/getIntegratedReport (not /report/runSync)
        data = await self._request("POST", "/reports/getIntegratedReport", json=request_body)

        # Add debug logging for report responses
        try:
            return ReportResponse(**data)
        except Exception as e:
            # Log the raw response for debugging
            import sys
            import json
            print(f"DEBUG: Raw API response for /reports/getIntegratedReport:", file=sys.stderr)
            print(f"DEBUG: {json.dumps(data, indent=2)}", file=sys.stderr)
            print(f"DEBUG: Validation error: {str(e)}", file=sys.stderr)

            # Re-raise with better context
            raise NewsBreakAPIError(
                code=-1,
                message=f"Failed to parse report response: {str(e)}. Raw response logged to stderr.",
                response=data,
            )

    # Ad Set Methods
    async def get_ad_sets(
        self,
        campaign_id: str,
        page_no: int = 1,
        page_size: int = 50,
    ) -> AdSetsResponse:
        """
        Get ad sets for a campaign

        Args:
            campaign_id: Campaign ID
            page_no: Page number (1-indexed)
            page_size: Results per page

        Returns:
            AdSetsResponse with ad set list and pagination
        """
        params = {
            "campaignId": campaign_id,
            "pageNo": page_no,
            "pageSize": page_size,
        }

        data = await self._request("GET", "/ad-set/getList", params=params)
        return AdSetsResponse(**data)

    # Ad Methods
    async def get_ads(
        self,
        ad_account_id: str,
        page_no: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        online_status: Optional[str] = None,
        campaign_ids: Optional[List[str]] = None,
        ad_set_ids: Optional[List[str]] = None,
    ) -> AdsResponse:
        """
        Get ads for an ad account with full creative asset details

        Args:
            ad_account_id: Ad account ID (required)
            page_no: Page number (1-indexed)
            page_size: Results per page (5, 10, 20, 50, 100, 200, 500)
            search: Search query to filter ads
            online_status: Filter by status (WARNING, INACTIVE, ACTIVE, DELETED, PENDING, REJECTED)
            campaign_ids: Filter by specific campaign IDs
            ad_set_ids: Filter by specific ad set IDs

        Returns:
            AdsResponse with complete ad details including creative assets (headlines, images,
            descriptions, CTAs, landing page URLs, etc.) and pagination info
        """
        params = {
            "adAccountId": ad_account_id,
            "pageNo": page_no,
            "pageSize": page_size,
        }

        if search:
            params["search"] = search
        if online_status:
            params["onlineStatus"] = online_status
        if campaign_ids:
            params["campaignIds"] = campaign_ids
        if ad_set_ids:
            params["adSetIds"] = ad_set_ids

        data = await self._request("GET", "/ad/getList", params=params)
        return AdsResponse(**data)
