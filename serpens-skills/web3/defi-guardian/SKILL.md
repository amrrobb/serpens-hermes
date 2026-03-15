---
name: defi-guardian
description: "Monitor DeFi positions, track yield opportunities, and set up liquidation alerts. Use when user asks about DeFi yields, protocol TVL, position monitoring, or wants automated DeFi alerts."
version: 1.0.0
author: serpens
license: MIT
metadata:
  hermes:
    tags: [Web3, DeFi, Monitoring, Liquidation, Yields, Alerts]
---

# DeFi Guardian

Autonomous DeFi position monitoring with yield tracking, protocol analysis, and Telegram alerts via cron scheduling.

## When to Use

- User asks about best yield opportunities
- User wants to monitor their DeFi positions
- User asks about protocol TVL or safety
- User wants liquidation alerts
- User mentions Aave, Compound, Uniswap, or other DeFi protocols

## Procedure

1. **For yield queries** — Use `get_defi_positions` tool
   - Returns top yield pools by APY with TVL > $1M
   - Present as ranked table with protocol, chain, APY, and TVL

2. **For protocol research** — Use `get_protocol_tvl` tool with protocol slug
   - Common slugs: aave, uniswap, lido, compound, curve, makerdao, gmx
   - Returns: TVL, chain breakdown, category

3. **For monitoring setup** — Use `schedule_cronjob` tool:
   - Prompt: "Use get_token_price to check price of {token} on {chain}. Current price was ${price}. If price changed more than {threshold}%, send alert with old price, new price, and percentage change."
   - Schedule: "every 5m" for urgent monitoring, "every 30m" for casual
   - Delivery: "origin" (sends to the chat where monitoring was requested)

4. **Format yield report**:
```
TOP YIELD OPPORTUNITIES
========================
Chain: {chain or "All Chains"}

| # | Protocol | Pool | APY | TVL |
|---|----------|------|-----|-----|
| 1 | {name}   | {pool}| {apy}% | ${tvl} |
...

NOTE: APYs are variable and change frequently. Higher APY often means higher risk.
```

5. **Format monitoring confirmation**:
```
MONITORING ACTIVE
==================
Asset: {token} on {chain}
Current Price: ${price}
Alert Threshold: {threshold}% change
Check Interval: every {interval}
Delivery: Telegram

To stop: "remove the {token} price monitoring cron job"
```

## Pitfalls

- DeFiLlama yields data is aggregated and may be delayed by up to 30 minutes
- Protocol slugs must be exact (lowercase). If unsure, try common variations.
- Cron prompts are self-contained — they don't have access to conversation context
- Very short monitoring intervals (< 5m) may hit API rate limits

## Verification

- Yield data should include both base APY and reward APY
- Monitoring crons should be confirmable via `list_cronjobs` tool
- Protocol TVL should show chain-level breakdown
