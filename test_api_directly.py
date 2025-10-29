#!/usr/bin/env python3
"""
Test the NewsBreak API directly to compare with what the MCP server sends
"""
import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client import NewsBreakClient

load_dotenv()


async def test_report():
    """Test the exact same request format that worked with curl"""

    print("Testing NewsBreak API with the format that worked in curl...\n")

    ad_account_id = "1892675572611006465"
    date_from = "2025-10-22"
    date_to = "2025-10-29"

    async with NewsBreakClient() as client:
        try:
            response = await client.run_synchronous_report(
                ad_account_id=ad_account_id,
                date_from=date_from,
                date_to=date_to,
                dimensions=None,  # Will use defaults: ["DATE", "CAMPAIGN"]
                metrics=None,  # Will use defaults
                level="campaign",  # Same as Claude passed
            )

            print("✅ SUCCESS!")
            print(f"\nResponse code: {response.code}")
            print(f"Response data: {json.dumps(response.dict(), indent=2)}")

        except Exception as e:
            print(f"❌ FAILED!")
            print(f"\nError: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_report())
