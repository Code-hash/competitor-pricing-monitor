# Competitor Pricing Change Monitor
## Overview

Competitor Pricing Change Monitor is an Apify actor that continuously monitors product or pricing pages and emits events only when a meaningful price change occurs.

It is designed to be:

- Cost-efficient

- Memory-safe under Apify limits

- Production-ready

- Reusable across multiple websites

This actor is ideal for teams that need reliable competitor pricing intelligence without noisy data or high operational cost.

## What Problem This Actor Solves

Teams frequently need to:

- Track competitor price changes

- Detect increases or discounts quickly

- Avoid manually checking websites

- Prevent false alerts from unchanged prices

Most scraping solutions either:

- Store full HTML snapshots

- Emit data on every run

- Consume unnecessary storage and RAM

This actor solves the problem by tracking only what matters.

## How It Works (Architecture)

For each monitored item:

- Fetches the page using lightweight HTTP requests (no browser)

- Extracts the price using a user-provided CSS selector

- Normalizes the price into a numeric value

- Reads the last known price from Apify’s Key-Value Store

- Compares old vs new price in memory

- Overwrites the stored price

- Emits a dataset record only if a meaningful event occurs

### Change Types Emitted

- `first_seen`
- `increase`
- `decrease`
- `price_not_found`

Events with `no_change` are intentionally not written to the dataset.

## Storage & Cost Model (Important)

### Key-Value Store (State)

- Stores only the latest price per URL

- One key per monitored item

- Constant size (does not grow over time)

### Dataset (Events)

- Append-only

- Stores only meaningful changes

- No data written when prices remain unchanged

## Input Format

```json
{
  "items": [
    {
      "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
      "priceSelector": ".price_color"
    }
  ]
}
Output Format (Dataset):
{
  "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "oldPrice": 51.77,
  "newPrice": 45.00,
  "changeType": "decrease"
}

