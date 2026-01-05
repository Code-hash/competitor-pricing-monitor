from apify import Actor
import requests
import asyncio
import hashlib
import re
from bs4 import BeautifulSoup


def normalize_price(text):
    if not text:
        return None
    m = re.search(r"[\d,.]+", text)
    return float(m.group().replace(",", "")) if m else None


async def main():
    async with Actor:
        Actor.log.info("Pricing monitor started")

        input_data = await Actor.get_input() or {}
        items = input_data.get("items", [])

        if not items:
            Actor.log.error("No items provided")
            return

        # Load existing state from dataset
        dataset = await Actor.open_dataset()
        existing = {}

        async for row in dataset.iterate_items():
            if "key" in row:
                existing[row["key"]] = row

        for item in items:
            url = item["url"]
            selector = item["priceSelector"]
            key = hashlib.sha256(url.encode()).hexdigest()

            Actor.log.info(f"Checking price for {url}")

            response = requests.get(
                url,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0 (PricingMonitorBot/1.0)"},
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            el = soup.select_one(selector)
            current = normalize_price(el.text.strip() if el else None)

            prev = existing.get(key, {}).get("newPrice")

            if prev is None:
                change = "first_seen"
            elif current is None:
                change = "price_not_found"
            elif current > prev:
                change = "increase"
            elif current < prev:
                change = "decrease"
            else:
                change = "no_change"

            Actor.log.info(
                f"{url} | old={prev} new={current} change={change}"
            )

            # Emit only meaningful events
            if change != "no_change":
                await Actor.push_data({
                    "key": key,
                    "url": url,
                    "oldPrice": prev,
                    "newPrice": current,
                    "changeType": change,
                })


if __name__ == "__main__":
    asyncio.run(main())
