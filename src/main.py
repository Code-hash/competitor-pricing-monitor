from apify import Actor
import requests

async def main():
    async with Actor:
        # Get input
        input_data = await Actor.get_input() or {}
        urls = input_data.get("urls", [])

        if not urls:
            raise ValueError("No URLs provided. Please provide URLs in the input.")

        results = []
        for url in urls:
            response = requests.get(
                url, 
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0 (PricingMonitorBot/1.0)"
                }
            )
            response.raise_for_status()
            results.append({
                "url": url,
                "statusCode": response.status_code,
                "htmlLength": len(response.text)
            })

        await Actor.push_data(results)
