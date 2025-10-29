"""
NewsBreak Ads MCP Server
A Model Context Protocol server for NewsBreak Business API
Focus: Analytics and Reporting
"""
import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from client import NewsBreakClient, NewsBreakAPIError
from models import (
    AdAccountsResponse,
    CampaignsResponse,
    EventsResponse,
    ReportResponse,
)

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(
    name="newsbreak-ads-mcp",
    version="1.0.0",
    instructions=(
        "MCP server for NewsBreak Business API with focus on analytics and reporting. "
        "Provides tools to query campaigns, events, and generate reports for ad performance analysis."
    ),
)


def get_client() -> NewsBreakClient:
    """Get configured NewsBreak API client"""
    access_token = os.getenv("NEWSBREAK_ACCESS_TOKEN")
    if not access_token:
        raise ToolError(
            "NEWSBREAK_ACCESS_TOKEN environment variable not set. "
            "Please set your NewsBreak access token."
        )
    return NewsBreakClient(access_token=access_token)


# =============================================================================
# TOOLS - Analytics & Reporting (Priority)
# =============================================================================


@mcp.tool()
async def get_ad_accounts(org_ids: List[str]) -> str:
    """
    Get all ad accounts for specified organization IDs.

    This retrieves ad account IDs and names grouped by organization,
    filtered by user access permissions.

    Args:
        org_ids: List of organization IDs to fetch ad accounts for

    Returns:
        JSON string with organizations and their ad accounts
    """
    try:
        async with get_client() as client:
            response = await client.get_ad_accounts(org_ids)

            if response.code != 0:
                raise ToolError(f"API error: {response.errMsg}")

            result = {
                "organizations": [
                    {
                        "id": org.id,
                        "name": org.name,
                        "ad_accounts": [
                            {
                                "id": acc.id,
                                "name": acc.name,
                                "create_time": acc.createTime,
                            }
                            for acc in org.adAccounts
                        ],
                    }
                    for org in response.organizations
                ]
            }

            return json.dumps(result, indent=2)

    except NewsBreakAPIError as e:
        raise ToolError(f"NewsBreak API error: {e.message}")
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")


@mcp.tool()
async def get_campaigns(
    ad_account_id: str,
    page_no: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    online_status: Optional[str] = None,
) -> str:
    """
    Get campaigns for an ad account with optional filtering.

    Args:
        ad_account_id: The ad account ID to fetch campaigns for
        page_no: Page number (default: 1)
        page_size: Results per page - options: 5, 10, 20, 50, 100, 200, 500 (default: 50)
        search: Optional search query to filter campaigns by name
        online_status: Optional status filter - values: WARNING, INACTIVE, ACTIVE, DELETED

    Returns:
        JSON string with campaigns list and pagination info
    """
    try:
        async with get_client() as client:
            response = await client.get_campaigns(
                ad_account_id=ad_account_id,
                page_no=page_no,
                page_size=page_size,
                search=search,
                online_status=online_status,
            )

            if response.code != 0:
                raise ToolError(f"API error: {response.errMsg}")

            if not response.data:
                return json.dumps({"campaigns": [], "pagination": {}}, indent=2)

            result = {
                "campaigns": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "org_id": c.orgId,
                        "ad_account_id": c.adAccountId,
                        "objective": c.objective,
                        "budget": c.budget,
                        "status": c.status,
                        "online_status": c.onlineStatus,
                        "create_time": c.createTime,
                        "update_time": c.updateTime,
                    }
                    for c in response.data.list
                ],
                "pagination": {
                    "page_no": response.data.pageNo,
                    "page_size": response.data.pageSize,
                    "total": response.data.total,
                    "has_next": response.data.hasNext,
                },
            }

            return json.dumps(result, indent=2)

    except NewsBreakAPIError as e:
        raise ToolError(f"NewsBreak API error: {e.message}")
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")


@mcp.tool()
async def get_tracking_events(
    ad_account_id: str,
    os_filter: Optional[str] = None,
) -> str:
    """
    Get all tracking events for an ad account.

    Retrieves pixel and postback tracking events configured for the account.

    Args:
        ad_account_id: The ad account ID to fetch events for
        os_filter: Optional OS filter - values: "IOS", "ANDROID", or "" (empty string for web)

    Returns:
        JSON string with tracking events list
    """
    try:
        async with get_client() as client:
            response = await client.get_events(
                ad_account_id=ad_account_id,
                os=os_filter,
            )

            if response.code != 0:
                raise ToolError(f"API error: {response.errMsg}")

            if not response.data:
                return json.dumps({"events": []}, indent=2)

            result = {
                "events": [
                    {
                        "id": e.id,
                        "name": e.name,
                        "org_id": e.orgId,
                        "type": e.type,
                        "event_type": e.eventType,
                        "url": e.url,
                        "os": e.os,
                        "app_event": e.appEvent,
                        "mobile_partner": e.mobilePartner,
                        "click_tracking_url": e.clickTrackingUrl,
                        "impression_tracking_url": e.impressionTrackingUrl,
                        "event_params": e.eventParams,
                        "version": e.version,
                        "create_time": e.createTime,
                        "update_time": e.updateTime,
                    }
                    for e in response.data.list
                ]
            }

            return json.dumps(result, indent=2)

    except NewsBreakAPIError as e:
        raise ToolError(f"NewsBreak API error: {e.message}")
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")


@mcp.tool()
async def run_performance_report(
    ad_account_id: str,
    date_from: str,
    date_to: str,
    dimensions: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
    level: Optional[str] = None,
) -> str:
    """
    Run a synchronous performance report for campaigns, ad sets, or ads.

    This generates immediate reports on auction and reservation ads data.

    Args:
        ad_account_id: The ad account ID to generate report for
        date_from: Start date in YYYY-MM-DD format (e.g., "2024-01-01")
        date_to: End date in YYYY-MM-DD format (e.g., "2024-01-31")
        dimensions: Optional list of dimensions (e.g., ["date", "campaign_id"])
        metrics: Optional list of metrics (e.g., ["impressions", "clicks", "spend", "conversions"])
        level: Optional reporting level - values: "campaign", "ad_set", "ad"

    Returns:
        JSON string with report data
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError:
            raise ToolError("Invalid date format. Use YYYY-MM-DD (e.g., 2024-01-01)")

        async with get_client() as client:
            response = await client.run_synchronous_report(
                ad_account_id=ad_account_id,
                date_from=date_from,
                date_to=date_to,
                dimensions=dimensions,
                metrics=metrics,
                level=level,
            )

            if response.code != 0:
                raise ToolError(f"API error: {response.errMsg}")

            if not response.data:
                return json.dumps(
                    {
                        "report": {
                            "ad_account_id": ad_account_id,
                            "date_from": date_from,
                            "date_to": date_to,
                            "level": level,
                            "rows": [],
                            "total": 0,
                        }
                    },
                    indent=2,
                )

            result = {
                "report": {
                    "ad_account_id": ad_account_id,
                    "date_from": date_from,
                    "date_to": date_to,
                    "level": level,
                    "dimensions": dimensions,
                    "metrics": metrics,
                    "rows": [
                        {
                            "dimensions": row.dimensions,
                            "metrics": row.metrics,
                        }
                        for row in response.data.rows
                    ],
                    "total": response.data.total or len(response.data.rows),
                }
            }

            return json.dumps(result, indent=2)

    except NewsBreakAPIError as e:
        raise ToolError(f"NewsBreak API error: {e.message}")
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")


@mcp.tool()
async def get_campaign_summary(
    ad_account_id: str,
    days: int = 7,
) -> str:
    """
    Get a quick summary of recent campaign performance.

    This is a convenience tool that fetches active campaigns and provides
    a high-level overview of account activity.

    Args:
        ad_account_id: The ad account ID
        days: Number of days to look back (default: 7)

    Returns:
        JSON string with campaign summary
    """
    try:
        async with get_client() as client:
            # Get active campaigns
            campaigns_response = await client.get_campaigns(
                ad_account_id=ad_account_id,
                page_size=100,
                online_status="ACTIVE",
            )

            if campaigns_response.code != 0:
                raise ToolError(f"API error: {campaigns_response.errMsg}")

            campaigns_data = campaigns_response.data
            active_campaigns = campaigns_data.list if campaigns_data else []

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            result = {
                "summary": {
                    "ad_account_id": ad_account_id,
                    "period": {
                        "from": start_date.strftime("%Y-%m-%d"),
                        "to": end_date.strftime("%Y-%m-%d"),
                        "days": days,
                    },
                    "active_campaigns": {
                        "count": len(active_campaigns),
                        "campaigns": [
                            {
                                "id": c.id,
                                "name": c.name,
                                "objective": c.objective,
                                "budget": c.budget,
                                "status": c.status,
                            }
                            for c in active_campaigns[:10]  # Limit to top 10
                        ],
                    },
                },
                "note": "Use run_performance_report for detailed metrics and conversions",
            }

            return json.dumps(result, indent=2)

    except NewsBreakAPIError as e:
        raise ToolError(f"NewsBreak API error: {e.message}")
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")


# =============================================================================
# RESOURCES - Read-only data access
# =============================================================================


@mcp.resource("accounts://{org_id}/ad-accounts")
async def get_org_ad_accounts_resource(org_id: str) -> str:
    """
    Resource to access ad accounts for a specific organization.

    URI: accounts://{org_id}/ad-accounts
    """
    try:
        async with get_client() as client:
            response = await client.get_ad_accounts([org_id])

            if response.code != 0:
                return f"Error: {response.errMsg}"

            orgs = response.organizations
            if not orgs:
                return "No organizations found"

            org = orgs[0]
            return json.dumps(
                {
                    "organization": {
                        "id": org.id,
                        "name": org.name,
                        "ad_accounts": [
                            {"id": acc.id, "name": acc.name, "create_time": acc.createTime}
                            for acc in org.adAccounts
                        ],
                    }
                },
                indent=2,
            )

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.resource("campaigns://{ad_account_id}/active")
async def get_active_campaigns_resource(ad_account_id: str) -> str:
    """
    Resource to access active campaigns for an ad account.

    URI: campaigns://{ad_account_id}/active
    """
    try:
        async with get_client() as client:
            response = await client.get_campaigns(
                ad_account_id=ad_account_id,
                page_size=100,
                online_status="ACTIVE",
            )

            if response.code != 0:
                return f"Error: {response.errMsg}"

            if not response.data:
                return json.dumps({"campaigns": []}, indent=2)

            return json.dumps(
                {
                    "campaigns": [
                        {
                            "id": c.id,
                            "name": c.name,
                            "objective": c.objective,
                            "budget": c.budget,
                            "status": c.status,
                        }
                        for c in response.data.list
                    ]
                },
                indent=2,
            )

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.resource("events://{ad_account_id}/tracking")
async def get_tracking_events_resource(ad_account_id: str) -> str:
    """
    Resource to access tracking events for an ad account.

    URI: events://{ad_account_id}/tracking
    """
    try:
        async with get_client() as client:
            response = await client.get_events(ad_account_id=ad_account_id)

            if response.code != 0:
                return f"Error: {response.errMsg}"

            if not response.data:
                return json.dumps({"events": []}, indent=2)

            return json.dumps(
                {
                    "events": [
                        {
                            "id": e.id,
                            "name": e.name,
                            "type": e.type,
                            "os": e.os,
                            "mobile_partner": e.mobilePartner,
                        }
                        for e in response.data.list
                    ]
                },
                indent=2,
            )

    except Exception as e:
        return f"Error: {str(e)}"


# =============================================================================
# Server Lifecycle
# =============================================================================


if __name__ == "__main__":
    # Run the server
    mcp.run()
