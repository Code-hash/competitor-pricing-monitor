from apify import Actor
import requests
import asyncio

async def main():
    async with Actor:
        Actor.log.info("Actor started")

        input_data = await Actor.get_input() or {}
        urls = input_data.get("urls", [])

        Actor.log.info(f"Received URLs: {urls}")

        if not urls:
            Actor.log.error("No URLs provided")
            return

        results = []

        for url in urls:
            try:
                Actor.log.info(f"Fetching {url}")

                response = requests.get(
                    url,
                    timeout=30,
                    headers={
                        "User-Agent": "Mozilla/5.0 (PricingMonitorBot/1.0)"
                    }
                )

                Actor.log.info(f"{url} → {response.status_code}")

                results.append({
                    "url": url,
                    "statusCode": response.status_code,
                    "htmlLength": len(response.text)
                })

            except Exception as e:
                Actor.log.error(f"Error fetching {url}: {e}")

        Actor.log.info(f"Pushing {len(results)} items to dataset")
        await Actor.push_data(results)

if __name__ == "__main__":
    asyncio.run(main())
