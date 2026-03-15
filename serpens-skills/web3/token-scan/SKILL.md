---
name: token-scan
description: "Scan any ERC-20 token for rug pull signals, honeypot risk, tax analysis, and safety. Use when user asks 'is this token safe', 'check this token', 'scan token', or provides a token contract address for safety analysis."
version: 1.0.0
author: serpens
license: MIT
metadata:
  hermes:
    tags: [Web3, Security, Token, Rug Pull, Honeypot, DeFi]
---

# Token Safety Scanner

Comprehensive token security analysis combining on-chain data, GoPlus security intelligence, and price data.

## When to Use

- User asks "is this token safe?" or "check this token"
- User provides a token contract address for analysis
- User mentions rug pull, honeypot, scam, or token safety
- User wants to evaluate a new token before buying

## Procedure

1. **Get token metadata** — Use `get_token_info` tool with the token address and chain
   - Extract: name, symbol, decimals, total supply, current price

2. **Run security scan** — Use `scan_token_security` tool with the token address
   - Chain IDs: ethereum=1, bsc=56, polygon=137, arbitrum=42161, base=8453
   - Extract: honeypot status, buy/sell tax, ownership risks, holder data

3. **Calculate risk score (0-100)**:
   - Honeypot detected: +40 points
   - Sell tax > 10%: +20 points
   - Sell tax > 5%: +10 points
   - Not open source: +15 points
   - Hidden owner: +10 points
   - Can take back ownership: +10 points
   - Top holder > 50%: +15 points
   - Top holder > 20%: +5 points
   - Is proxy/upgradeable: +5 points
   - Self-destruct capability: +30 points

4. **Determine rating**:
   - Score 0-15: SAFE (green)
   - Score 16-40: CAUTION (yellow)
   - Score 41-70: DANGER (orange)
   - Score 71-100: CRITICAL (red)

5. **Format report**:
```
TOKEN SAFETY REPORT
====================
Token: {name} ({symbol})
Chain: {chain}
Price: ${price_usd}
Risk Score: {score}/100 — {rating}

FINDINGS:
{list each risk with severity}

HOLDER ANALYSIS:
- Total holders: {count}
- Top holder: {pct}%
- LP holders: {count}

TAX ANALYSIS:
- Buy tax: {buy_tax}%
- Sell tax: {sell_tax}%

RECOMMENDATION:
{actionable advice based on findings}
```

6. **Save to memory** — Store the scan result so you can reference it later if the user asks about previously scanned tokens

7. **Suggest next steps** — "Want me to also check the deployer wallet?" or "Want me to audit the contract source code?"

## Pitfalls

- GoPlus may not have data for very new tokens (< 24h old). If no data, warn the user.
- A "LOW" risk score does NOT mean the token is guaranteed safe — it means no obvious red flags were detected.
- Always disclaim: "This analysis is automated and should not be considered financial advice."

## Verification

- The report should include specific risk flags, not just a score
- Price data should be current (within last 5 minutes)
- Holder count and tax data should be present
