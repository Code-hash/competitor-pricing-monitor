from apify import Actor
import requests
import asyncio
import hashlib
from bs4 import BeautifulSoup


def normalize_price(price_text):
    if not price_text:
        return None
    cleaned = (
        price_text.replace("£", "")
        .replace("$", "")
        .replace(",", "")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return None


async def main():
    async with Actor:
        Actor.log.info("Pricing monitor started")

        input_data = await Actor.get_input() or {}
        urls = input_data.get("urls", [])

        if not urls:
            Actor.log.error("No URLs provided in input")
            return

        results = []

        for url in urls:
            Actor.log.info(f"Checking price for {url}")

            response = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0 (PricingMonitorBot/1.0)"
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            price_el = soup.select_one(".price_color")

            current_price_text = price_el.text.strip() if price_el else None
            current_price = normalize_price(current_price_text)

            # SAFE KEY FOR APIFY STORAGE
            url_hash = hashlib.sha256(url.encode()).hexdigest()
            store_key = f"PRICE_{url_hash}"

            previous_price = await Actor.get_value(
                store_key, default_value=None
            )

            if previous_price is None:
                change_type = "first_seen"
            elif current_price is None:
                change_type = "price_not_found"
            elif current_price > previous_price:
                change_type = "increase"
            elif current_price < previous_price:
                change_type = "decrease"
            else:
                change_type = "no_change"

            # STORE ONLY LATEST PRICE (OVERWRITE)
            await Actor.set_value(store_key, current_price)

            result = {
                "url": url,
                "oldPrice": previous_price,
                "newPrice": current_price,
                "changeType": change_type,
            }

            results.append(result)

            Actor.log.info(
                f"{url} | old={previous_price} new={current_price} change={change_type}"
            )

        # OUTPUT RESULT
        await Actor.push_data(results)


if __name__ == "__main__":
    asyncio.run(main())
