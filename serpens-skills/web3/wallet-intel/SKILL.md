---
name: wallet-intel
description: "Analyze any wallet address for activity patterns, holdings, risk indicators, and transaction history. Use when user provides a wallet address for investigation, asks to analyze/investigate a wallet, wants to dig deeper on an address, or wants to track/watch an address."
version: 1.0.0
author: serpens
license: MIT
metadata:
  hermes:
    tags: [Web3, Wallet, Intelligence, Analysis, Monitoring, Whale]
---

# Wallet Intelligence Analyzer

Comprehensive wallet profiling combining on-chain activity analysis, balance checks, risk scoring, and behavioral pattern detection.

## When to Use

- User asks to "analyze this wallet" or "check this address"
- User says "investigate this address" or "dig deeper on this wallet"
- User wants to know what a wallet has been doing
- User asks about whale wallets or large holders
- User wants to "watch" or "monitor" an address
- User provides an Ethereum/EVM address for investigation

## Procedure

1. **Analyze wallet activity** — Use `analyze_wallet` tool with the address and chain
   - Returns: tx_count, wallet age, unique contracts, risk indicators, recent transactions

2. **Check balance** — Use `get_eth_balance` tool with the address and chain
   - Returns: native balance in ETH and USD

3. **Check address risk** — Use `check_address_risk` tool with the address
   - Returns: whether the address is flagged as malicious by GoPlus

4. **Generate wallet profile**:
```
WALLET INTELLIGENCE REPORT
============================
Address: {address}
Chain: {chain}
Type: {EOA / Contract}

BALANCE:
- Native: {balance} {native_token} (${usd_value})

ACTIVITY PROFILE:
- Wallet age: {days} days
- Total transactions: {count}
- First activity: {date}
- Last activity: {date}
- Unique contracts: {count}

RISK INDICATORS:
{list risk flags with explanations}

SECURITY STATUS:
- GoPlus: {clean / flagged}
{details if flagged}

RECENT TRANSACTIONS:
{last 5-10 txs with value and target}

ASSESSMENT:
{overall risk assessment and behavioral pattern analysis}
```

5. **Investigate mode** — If user says "investigate", "dig deeper", or the standard analysis reveals risk flags, perform deep investigation:

   a. **Deployer investigation** — If the address is a contract (Type = Contract from step 1):
      - Use `get_contract_source` tool on the address to check verification status
      - Identify the creator/deployer address from the `analyze_wallet` results (look at the contract creation tx)
      - Use `analyze_wallet` on the creator address to inspect their deployment history
      - Flag if the creator has deployed multiple similar contracts — this is a serial scammer pattern (rug factories, honeypot deployers)

   b. **Connected address mapping** — From the recent transactions returned in step 1:
      - Identify the most frequent counterparty addresses (sort by tx count)
      - Identify addresses that received large outflows from the target wallet (potential fund extraction)
      - Use `check_address_risk` on each of the top 3-5 counterparties to check GoPlus flags
      - Note any addresses that appear in both high-frequency AND high-value outflow categories

   c. **Cross-reference with memory** — Check if any connected addresses (deployer, counterparties) were previously analyzed or flagged in memory. Surface any prior assessments.

   d. **Generate network analysis section** — Append to the standard report:
   ```
   NETWORK ANALYSIS
   ================
   Deployer: 0x... (age: X days, deployed Y contracts)
   Top counterparties:
     → 0x... (15 txs, net flow: -5 ETH) ⚠️ GoPlus: flagged
     → 0x... (8 txs, net flow: +2 ETH) ✅ Clean
   Connections to watched addresses: [list or "none"]
   ```

   - For the deployer line: show the deployer address, how old it is, and how many contracts it has deployed. If not a contract, show "N/A (EOA wallet)".
   - For counterparties: list top 3-5 by transaction count. Show tx count, net ETH flow direction (positive = inflow, negative = outflow), and GoPlus status.
   - For watched connections: cross-reference all discovered addresses against memory for any previously watched or flagged wallets.

6. **Handle "watch" requests** — If user says "watch this wallet" or "monitor this address":
   - Save to memory: "Watching wallet {address} on {chain} — requested {date}"
   - Optionally set up a cron job: Use `schedule_cronjob` with prompt:
     "Check wallet {address} on {chain} using analyze_wallet and get_eth_balance tools. Compare with previous balance. If significant changes detected (>10% balance change or unusual transactions), report the changes."
   - Set interval: "every 30m" or as requested by user
   - Delivery: to origin chat

7. **Cross-reference with history** — If this wallet was analyzed before (check memory), compare current state with previous analysis and highlight changes.

## Pitfalls

- Etherscan API rate limits may affect tx history retrieval. If API returns error, still report balance and risk data.
- Very active wallets (>10K txs) — only latest 50 txs are fetched. Note this limitation.
- Contract wallets (multisigs, smart accounts) have different activity patterns — don't flag as suspicious.
- ENS names (.eth) are not resolved by our tools. If user provides ENS name, ask for the hex address.
- Investigate mode calls `check_address_risk` on multiple counterparties — batch these where possible to avoid rate limits. If GoPlus returns errors for some, still report the ones that succeeded.
- Deployer investigation only applies to contract addresses. Do not attempt `get_contract_source` on EOA wallets.

## Verification

- Report should always include balance, activity metrics, and risk assessment
- "Watch" requests should be confirmed with what's being monitored and how often
- Memory entries should be queryable: "What wallets am I watching?"
- "Investigate" mode should always produce the NETWORK ANALYSIS section with deployer info, top counterparties with GoPlus status, and watched address connections
