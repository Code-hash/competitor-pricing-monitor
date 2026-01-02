from apify import Actor
import requests

async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        urls = input_data.get("urls", [])

        Actor.log.info(f"Received URLs: {urls}")

        if not urls:
            Actor.log.error("No URLs provided in input")
            return

        results = []

        for url in urls:
            try:
                Actor.log.info(f"Requesting {url}")

                response = requests.get(
                    url,
                    timeout=30,
                    headers={
                        "User-Agent": "Mozilla/5.0 (PricingMonitorBot/1.0)"
                    }
                )

                Actor.log.info(f"{url} → status {response.status_code}")

                response.raise_for_status()

                results.append({
                    "url": url,
                    "statusCode": response.status_code,
                    "htmlLength": len(response.text)
                })

            except Exception as e:
                Actor.log.error(f"Failed to fetch {url}: {e}")

        Actor.log.info(f"Pushing {len(results)} records to dataset")
        await Actor.push_data(results)
