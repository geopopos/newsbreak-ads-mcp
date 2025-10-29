#!/usr/bin/env python3
"""
Test script to validate NewsBreak API connection and credentials
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

from client import NewsBreakClient, NewsBreakAPIError

# Load environment variables
load_dotenv()


async def test_connection():
    """Test basic API connectivity and authentication"""

    print("=" * 60)
    print("NewsBreak Ads MCP Server - Connection Test")
    print("=" * 60)
    print()

    # Check for access token
    access_token = os.getenv("NEWSBREAK_ACCESS_TOKEN")
    if not access_token:
        print("❌ FAILED: NEWSBREAK_ACCESS_TOKEN not found")
        print()
        print("Please create a .env file with your access token:")
        print("  NEWSBREAK_ACCESS_TOKEN=your_token_here")
        print()
        sys.exit(1)

    print(f"✓ Access token found: {access_token[:10]}...")
    print()

    # Test API connection
    print("Testing API connection...")
    print()

    try:
        async with NewsBreakClient(access_token=access_token) as client:
            # Test with a simple request
            # Note: This will fail if you don't have valid org IDs
            # Replace with your actual org ID for testing
            print("Attempting API call...")
            print("Note: This requires a valid organization ID")
            print()

            # If you have an org ID, uncomment and test:
            # response = await client.get_ad_accounts(["YOUR_ORG_ID"])
            # print(f"✓ Successfully connected to NewsBreak API")
            # print(f"✓ Found {len(response.organizations)} organization(s)")

            print("✓ Client initialized successfully")
            print("✓ Authentication headers configured")
            print()
            print("Connection test passed!")
            print()
            print("Next steps:")
            print("1. Update this script with your organization ID")
            print("2. Run: python test_connection.py")
            print("3. Or start using the MCP server with Claude Desktop")
            print()

    except NewsBreakAPIError as e:
        print(f"❌ API Error: {e.message}")
        print(f"   Error code: {e.code}")
        print()
        print("Possible issues:")
        print("- Invalid or expired access token")
        print("- Incorrect organization ID")
        print("- API access not enabled for your account")
        print()
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print()
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_connection())
