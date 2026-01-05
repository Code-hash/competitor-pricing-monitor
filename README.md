# Competitor Pricing Change Monitor

## Overview

Competitor Pricing Change Monitor is an Apify actor that continuously monitors product or pricing pages and emits events only when a meaningful price change occurs.

It is designed to be:

- Cost-efficient
- Memory-safe under Apify limits
- Production-ready
- Reusable across multiple websites

This actor is ideal for teams that need reliable competitor pricing intelligence without noisy data or high operational cost.

---

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

---

## How It Works (Architecture)

For each monitored item:

- Fetches the page using lightweight HTTP requests (no browser)
- Extracts the price using a user-provided CSS selector
- Normalizes the price into a numeric value
- Loads the previously observed price from storage
- Compares old vs new price in memory
- Emits a dataset record only if a meaningful event occurs

### Change Types Emitted

- `first_seen`
- `increase`
- `decrease`
- `price_not_found`

Events with `no_change` are intentionally not written to the dataset.

---

## Storage & Cost Model (Important)

### Dataset (State + Events)

- Stores the last known price per monitored URL
- Acts as persistent state across executions
- Also acts as an event log when changes occur
- Grows only when a meaningful change is detected

This design ensures:

- Predictable storage usage
- Constant memory usage
- Safe execution for frequent scheduled runs

---

## Execution Mode & State Persistence (Important)

This actor is **stateful by design** and intended for **monitoring use cases**.

### Correct way to run this actor

To ensure proper change detection, the actor should be executed using one of the following methods:

- **Scheduled or manual runs via an Apify Task**
- **Resurrecting a previous run** (recommended for testing and validation)

These execution modes preserve run storage and allow the actor to compare current prices with previously observed values.

### Important note about fresh runs

A fresh run (starting a new run without resurrecting or without a task context) starts with empty storage.  
In this case, all monitored items will be treated as `first_seen`.

This behavior is expected and intentional.

---

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
