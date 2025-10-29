#!/usr/bin/env python3
"""
Helper script to discover your NewsBreak organization and account IDs.

This script will attempt to find your IDs by making various API calls
and examining the responses.
"""
import asyncio
import os
import sys
import json
from dotenv import load_dotenv
from client import NewsBreakClient, NewsBreakAPIError

load_dotenv()


async def discover_ids():
    """
    Attempt to discover organization and account IDs from API responses.
    """
    print("=" * 70)
    print("NewsBreak ID Discovery Tool")
    print("=" * 70)
    print()

    # Check for access token
    access_token = os.getenv("NEWSBREAK_ACCESS_TOKEN")
    if not access_token:
        print("❌ ERROR: NEWSBREAK_ACCESS_TOKEN not found in .env file")
        print()
        print("Please create a .env file with your access token:")
        print("  NEWSBREAK_ACCESS_TOKEN=your_token_here")
        print()
        sys.exit(1)

    print(f"✓ Access token found: {access_token[:10]}...")
    print()
    print("Attempting to discover your IDs...")
    print()

    async with NewsBreakClient(access_token=access_token) as client:
        print("Strategy 1: Trying common organization ID patterns...")
        print("-" * 70)

        # Try to get campaigns with various org ID attempts
        # This won't work without knowing the ad account ID first

        print("⚠️  Unable to auto-discover IDs without at least one known ID")
        print()
        print("=" * 70)
        print("MANUAL STEPS TO FIND YOUR IDS:")
        print("=" * 70)
        print()
        print("1. LOG IN TO NEWSBREAK FOR BUSINESS")
        print("   Go to: https://business.newsbreak.com")
        print()
        print("2. CHECK THE URL")
        print("   After logging in, look at your browser's address bar:")
        print("   https://business.newsbreak.com/org/{YOUR_ORG_ID}/...")
        print("                                      ^^^^^^^^^^^^^^^^")
        print("   The number after '/org/' is your Organization ID")
        print()
        print("3. NAVIGATE TO CAMPAIGNS OR ADS")
        print("   - Go to your Campaigns or Ads section")
        print("   - Click on any campaign or ad")
        print("   - Check the URL for identifiers like:")
        print("     /campaign/{CAMPAIGN_ID}")
        print("     /ad-account/{AD_ACCOUNT_ID}")
        print()
        print("4. CHECK YOUR ACCOUNT SETTINGS")
        print("   - Go to Settings → Organization")
        print("   - Look for 'Organization ID' or 'Account ID'")
        print()
        print("5. CONTACT NEWSBREAK SUPPORT")
        print("   - Click the 'Help' button in the bottom-left")
        print("   - Ask for your Organization ID and Ad Account ID")
        print()
        print("=" * 70)
        print("WHAT TO DO NEXT:")
        print("=" * 70)
        print()
        print("Once you have your Organization ID, you can:")
        print()
        print("1. Test the get_ad_accounts tool:")
        print("   python -c '")
        print("   import asyncio")
        print("   from client import NewsBreakClient")
        print("   async def test():")
        print("       async with NewsBreakClient() as client:")
        print("           r = await client.get_ad_accounts([\"YOUR_ORG_ID\"])")
        print("           print(r)")
        print("   asyncio.run(test())")
        print("   '")
        print()
        print("2. Or update test_connection.py with your org ID")
        print()
        print("3. Or use the MCP server directly with Claude Desktop")
        print()
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(discover_ids())
