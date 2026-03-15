# SERPENS Demo Guide & Narration Script

## Pre-Recording Checklist

- [ ] Gateway running: `hermes gateway run --replace`
- [ ] Test: send "hi" to @serpens_telegram_bot — should respond
- [ ] Telegram Desktop open (not mobile — better for screen recording)
- [ ] Screen recorder ready (OBS or macOS Cmd+Shift+5)
- [ ] Clear chat history: send `/new` to bot for fresh session
- [ ] Have these addresses ready to copy-paste:
  - PEPE (safe-ish): `0x6982508145454Ce325dDbE47a25d4ec3d2311933`
  - Known scam token: `0x000000000000000000000000000000000000dead` (or any zero-liquidity token)
  - Vitalik wallet: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`
  - Uniswap V2 Router: `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D`

## Video Structure (2:30 - 3:00 total)

---

### Part 1: Pitch Intro (0:00 - 0:25)
**Show: Pitch slide (pitch/index.html) in browser**

**Narration:**
> "In 2024, over 2 billion dollars was lost to rug pulls, scams, and smart contract exploits. Existing tools are reactive — you check AFTER you lose money. What if your security guard never slept?"
>
> "Meet SERPENS — an autonomous Web3 intelligence agent built on Hermes Agent by Nous Research. It scans tokens, audits contracts, profiles wallets, and monitors your positions around the clock."

**Action:** Scroll through pitch slides briefly (problem → what it does → architecture)

---

### Part 2: Token Scan (0:25 - 0:55)
**Show: Switch to Telegram Desktop — @serpens_telegram_bot**

**Narration:**
> "Let's see it in action. I'll ask SERPENS to check if PEPE token is safe."

**Send to bot:**
```
Is this token safe? 0x6982508145454Ce325dDbE47a25d4ec3d2311933
```

**Wait for response** (should take 3-5 seconds)

**Narration (while response appears):**
> "SERPENS loads the token-scan skill, calls two tools — GoPlus security API for honeypot detection and DeFiLlama for price data — and generates a risk score."
>
> "Risk score 20 out of 100 — CAUTION. It found a blacklist function and anti-whale mechanism, but no honeypot, zero taxes, open source. For a meme token, that's actually reasonable."

---

### Part 3: Contract Audit (0:55 - 1:25)
**Narration:**
> "Now let's audit a smart contract. I'll give it the Uniswap V2 Router address."

**Send to bot:**
```
Audit this contract: 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
```

**Wait for response**

**Narration:**
> "It fetches the verified source code from Etherscan, runs GoPlus security analysis, and checks for common vulnerability patterns like reentrancy, delegatecall, and selfdestruct."
>
> "Uniswap V2 Router comes back clean — as expected for one of the most audited contracts in DeFi."

---

### Part 4: Wallet Intelligence + Watch (1:25 - 1:55)
**Narration:**
> "Now the really interesting part. Let's analyze Vitalik's wallet and set up monitoring."

**Send to bot:**
```
Analyze wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

**Wait for response**

**Narration:**
> "Full wallet profile — balance, transaction count, wallet age, unique contracts interacted with, and risk indicators."

**Then send:**
```
Watch this wallet and alert me of any changes
```

**Narration:**
> "And here's where Hermes Agent's cron scheduling shines. SERPENS sets up autonomous monitoring — every 30 minutes, it checks this wallet and sends me a Telegram alert if anything significant changes. This runs 24/7 without any human intervention."

---

### Part 5: Memory & Intelligence (1:55 - 2:15)
**Narration:**
> "SERPENS remembers everything across sessions. Watch this."

**Send to bot:**
```
What have I analyzed today?
```

**Wait for response — should recall PEPE scan, Uniswap audit, Vitalik wallet**

**Narration:**
> "It recalls every analysis from this session. And this memory persists — next time I open Telegram, SERPENS still knows my watchlist and past scans. That's Hermes Agent's persistent memory system at work."

---

### Part 6: Closing (2:15 - 2:45)
**Show: Switch back to pitch slide (architecture section)**

**Narration:**
> "Under the hood, SERPENS uses 10 Hermes Agent features: 11 custom tools registered in the tool registry, 5 skills including the built-in Solana blockchain skill, a custom SOUL.md persona, persistent memory, cron scheduling for autonomous monitoring, Telegram gateway, subagent delegation for parallel analysis, session search for cross-session intelligence, and programmatic tool calling."
>
> "All of this runs on real APIs — GoPlus for security data, DeFiLlama for prices, Etherscan for contract source, and free public RPCs for on-chain reads. No mocks, no fakes."
>
> "SERPENS. The on-chain serpent that never sleeps. Link in the tweet."

---

## Recording Tips

1. **Resolution**: 1920x1080 minimum
2. **Telegram window**: Make it large, dark theme, text readable
3. **Pace**: Don't rush. Let the bot responses fully render before narrating
4. **If bot is slow**: You can speed up the waiting parts 1.5x in CapCut
5. **If bot errors**: Send `/new` and retry — errors happen
6. **Narration**: Record separately in CapCut with TTS, overlay on screen recording
7. **Music**: Optional — subtle lo-fi or ambient electronic

## Narration Script (for CapCut TTS — copy-paste this)

```
In 2024, over 2 billion dollars was lost to rug pulls, scams, and smart contract exploits. Existing tools are reactive. You check after you lose money. What if your security guard never slept?

Meet SERPENS. An autonomous Web3 intelligence agent built on Hermes Agent by Nous Research.

Watch this. I ask it to check if PEPE token is safe. Instantly, it loads the token scan skill, calls GoPlus security API and DeFi Llama for price data, and generates a risk score. 20 out of 100. Caution. Blacklist function detected, but no honeypot, zero taxes, open source.

Now let's audit a smart contract. The Uniswap V2 Router. SERPENS fetches the verified source code from Etherscan, runs security analysis, and checks for vulnerability patterns. Clean. As expected.

Wallet intelligence. Give it Vitalik's address and it builds a complete profile. Balance, transaction history, risk indicators. Then say watch this wallet. SERPENS sets up a cron job. Every 30 minutes, it checks for changes and alerts me on Telegram. Fully autonomous.

What have I analyzed today? It remembers everything. Persistent memory across sessions. That's Hermes Agent's memory system.

Under the hood, SERPENS uses 10 Hermes features. 11 custom tools. 5 skills. Custom persona. Persistent memory. Cron scheduling. Telegram gateway. Subagent delegation. Session search. All running on real APIs. No mocks.

SERPENS. The on-chain serpent that never sleeps.
```

## Tweet Template

```
SERPENS — Autonomous Web3 Intelligence Agent 🐍

Built with @NousResearch Hermes Agent for the hackathon.

Your 24/7 on-chain security guard:
🔍 Token scanning — rug pull & honeypot detection
📋 Contract auditing — source code vulnerability analysis
👁️ Wallet intelligence — activity profiling & monitoring
⏰ DeFi guardian — autonomous cron-based alerts

Uses 10+ Hermes features: custom tools, skills, SOUL.md, memory, cron, Telegram gateway, subagents, session search.

Real APIs. No mocks. Try it: t.me/serpens_telegram_bot

[VIDEO]

GitHub: [LINK]
```

## Discord Submission Message

```
🐍 SERPENS — Autonomous Web3 Intelligence Agent

What it does: Token scanning, contract auditing, wallet intelligence, and autonomous DeFi monitoring via Telegram. Uses 10+ Hermes features (custom tools, skills, SOUL.md, memory, cron, subagents).

Tweet: [LINK]
GitHub: [LINK]
Try it live: t.me/serpens_telegram_bot
```
