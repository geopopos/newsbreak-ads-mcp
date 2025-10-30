"""
Quick test script to debug the get_ads API call
"""
import asyncio
import os
import json
from dotenv import load_dotenv
from client import NewsBreakClient

load_dotenv()

async def test_get_ads():
    """Test getting ads and see what the API returns"""
    ad_account_id = "1894430718948372481"

    async with NewsBreakClient(access_token=os.getenv("NEWSBREAK_ACCESS_TOKEN")) as client:
        print("Calling get_ads API...")
        response = await client.get_ads(
            ad_account_id=ad_account_id,
            page_size=5,
            online_status="ACTIVE"
        )

        print(f"\n=== API Response ===")
        print(f"Code: {response.code}")
        print(f"Has data: {response.data is not None}")

        if response.data:
            print(f"Data type: {type(response.data)}")
            print(f"Rows count: {len(response.data.rows)}")
            print(f"Total: {response.data.total}")
            print(f"PageNo: {response.data.pageNo}")
            print(f"PageSize: {response.data.pageSize}")
            print(f"HasNext: {response.data.hasNext}")

            if response.data.rows:
                print(f"\n=== First Ad ===")
                first_ad = response.data.rows[0]
                print(f"ID: {first_ad.id}")
                print(f"Name: {first_ad.name}")
                print(f"Status: {first_ad.status}")
                print(f"Has creative: {first_ad.creative is not None}")

                if first_ad.creative:
                    print(f"\n=== Creative Details ===")
                    print(f"Type: {first_ad.creative.type}")
                    if first_ad.creative.content:
                        print(f"Headline: {first_ad.creative.content.headline}")
                        print(f"Description: {first_ad.creative.content.description}")
                        print(f"CTA: {first_ad.creative.content.callToAction}")
                        print(f"Asset URL: {first_ad.creative.content.assetUrl}")
                        print(f"Landing Page: {first_ad.creative.content.clickThroughUrl}")

                print(f"\n=== Full Ad JSON ===")
                print(json.dumps(first_ad.model_dump(), indent=2))
        else:
            print("No data in response!")
            print(f"ErrMsg: {response.errMsg}")

if __name__ == "__main__":
    asyncio.run(test_get_ads())
