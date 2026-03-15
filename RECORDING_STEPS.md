# SERPENS — Shot-by-Shot Recording Guide

## Setup (do this BEFORE hitting record)

1. Open **Terminal 1** (for CLI demo):
```bash
cd /Users/ammar.robb/Documents/Web3/hackathons/caduceus
source venv/bin/activate
set -a; source ~/.hermes/.env; set +a
unset ANTHROPIC_API_KEY
```
Make terminal full screen, increase font size (Cmd+Plus until readable at 1080p)

2. Open **Terminal 2** (for gateway — keep in background):
```bash
cd /Users/ammar.robb/Documents/Web3/hackathons/caduceus
source venv/bin/activate
set -a; source ~/.hermes/.env; set +a
unset ANTHROPIC_API_KEY
hermes gateway run --replace
```

3. Open **Telegram Desktop** — go to @serpens_telegram_bot, send `/new`
4. Open **Browser** — `file:///Users/ammar.robb/Documents/Web3/hackathons/caduceus/pitch/index.html`
5. Open **Notes** with these addresses ready to copy:
```
0x6982508145454Ce325dDbE47a25d4ec3d2311933
0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

6. Screen resolution: 1920x1080
7. Start recording: **Cmd + Shift + 5** → Record Entire Screen

---

## SHOT 1: Pitch Slides (0:00 — 0:20)
**Screen:** Browser with pitch/index.html

| Action | Caption |
|---|---|
| Show Slide 1 — SERPENS hero | `$2B+ lost to rug pulls & exploits in 2024` |
| Scroll to Slide 2 — The Problem | `Existing tools are reactive` |
| Scroll to Slide 3 — What It Does | `Token scanning · Contract auditing · Wallet intel · DeFi monitoring` |
| Scroll to Slide 4 — Architecture | `11 custom tools · 5 skills · Hermes Agent` |
| Hold 2 sec, then switch to Terminal | — |

**TTS Narration:**
> "In 2024, over 2 billion dollars was lost to rug pulls, scams, and smart contract exploits. Existing tools are reactive. You check after you lose money. What if your security guard never slept? Meet SERPENS."

---

## SHOT 2: Terminal — Token Scan (0:20 — 0:55)
**Screen:** Terminal 1 (full screen)

| Action | Caption |
|---|---|
| Type: `hermes chat --provider anthropic --model claude-sonnet-4-6 --toolsets web3,skills,memory` | — |
| Wait for TUI banner to load (ASCII art + 95 skills + tool list) | `SERPENS — 15 tools · 95 skills loaded` |
| **Pause 3 sec on the banner — let viewer read it** | — |
| Type: `Is this token safe? 0x6982508145454Ce325dDbE47a25d4ec3d2311933` | `Scanning PEPE token...` |
| Terminal shows: `skill_view: "token-scan"` → `get_token_info...` → `scan_token_security...` | `Loading skill → calling GoPlus + DeFiLlama` |
| TOKEN SAFETY REPORT appears | `Risk Score: 20/100 — CAUTION` |
| **Pause 3 sec — let viewer read the findings** | `✅ No honeypot · 0% tax · Open source` |

**TTS Narration:**
> "An autonomous Web3 intelligence agent built on Hermes Agent. Watch the terminal. It loads the token scan skill, calls GoPlus security API and DeFi Llama, and generates a risk score. 20 out of 100. Caution. Blacklist function detected, but no honeypot, zero taxes, open source."

---

## SHOT 3: Terminal — Contract Audit (0:55 — 1:25)
**Screen:** Same terminal session

| Action | Caption |
|---|---|
| Type: `Audit contract 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` | `Auditing Uniswap V2 Router...` |
| Terminal shows: `skill_view: "contract-audit"` → `analyze_contract_security...` → `get_contract_source...` | `Fetching source from Etherscan → vulnerability scan` |
| SMART CONTRACT AUDIT appears | `Risk Level: LOW — verified & clean` |
| **Pause 3 sec on findings** | `Checks: reentrancy, delegatecall, selfdestruct, access control` |

**TTS Narration:**
> "Now let's audit a smart contract. The Uniswap V2 Router. SERPENS fetches verified source code from Etherscan, runs security analysis, checks for vulnerability patterns like reentrancy and selfdestruct. Clean. As expected for one of the most audited contracts in DeFi."

---

## SHOT 4: Telegram — Wallet Watch (1:25 — 2:00)
**Screen:** Switch to Telegram Desktop — @serpens_telegram_bot

| Action | Caption |
|---|---|
| Type: `Analyze wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045` | `Analyzing Vitalik's wallet...` |
| Bot shows tool calls: `analyze_wallet` → `get_eth_balance` → `check_address_risk` | `3 tools firing in sequence` |
| WALLET INTELLIGENCE REPORT appears | `Balance · Tx count · Wallet age · Risk assessment` |
| **Pause 2 sec** | — |
| Type: `Watch this wallet and alert me of any changes` | `Setting up autonomous monitoring...` |
| Bot shows: `schedule_cronjob` + `memory` tool calls | `Cron + Memory — two Hermes features at once` |
| WALLET WATCH ACTIVE appears with Job ID, thresholds | `Every 30 min · Alerts on Telegram · Fully autonomous` |

**TTS Narration:**
> "Wallet intelligence. Give it Vitalik's address and it builds a complete profile. Balance, transaction history, risk indicators. Then I say watch this wallet. SERPENS sets up a cron job. Every 30 minutes, it checks for changes and alerts me right here on Telegram. Fully autonomous. No human intervention needed."

---

## SHOT 5: Telegram — Memory Recall (2:00 — 2:15)
**Screen:** Same Telegram chat

| Action | Caption |
|---|---|
| Type: `What have I analyzed today?` | `Testing persistent memory...` |
| Bot recalls: PEPE scan, Uniswap audit, Vitalik wallet watch | `Remembers every analysis across sessions` |
| **Pause 3 sec on the recall** | `Hermes persistent memory system` |

**TTS Narration:**
> "What have I analyzed today? It remembers everything. Persistent memory across sessions. Next time I come back, SERPENS still knows my watchlist and every past scan."

---

## SHOT 6: Closing (2:15 — 2:35)
**Screen:** Switch to browser — pitch slides

| Action | Caption |
|---|---|
| Show architecture slide | `11 custom tools · 5 skills · SOUL.md persona` |
| Show Hermes features slide | `Memory · Cron · Telegram · Subagents · Session Search` |
| Show final slide | `All real APIs · No mocks · Try it: t.me/serpens_telegram_bot` |
| **Hold final slide 5 sec** | `SERPENS — the on-chain serpent that never sleeps` |
| Stop recording | — |

**TTS Narration:**
> "Under the hood. 11 custom tools. 5 skills. Custom SOUL dot MD persona. Persistent memory. Cron scheduling. Telegram gateway. All running on real APIs. GoPlus, DeFi Llama, Etherscan. No mocks, no fakes. SERPENS. The on-chain serpent that never sleeps."

---

## Post-Recording: CapCut Edit Steps

### Step 1: Import
- Drag screen recording into CapCut timeline

### Step 2: Speed Up Wait Times
- Find spots where bot is "thinking" (3+ seconds of no change)
- Speed those sections to 2-3x
- Target final length: 2:30 - 2:40

### Step 3: Add Captions
- Use CapCut's text tool
- Add the captions from the tables above at each section
- Style: white text, semi-transparent dark background, bottom-center
- Font: clean sans-serif (Inter, SF Pro, or similar)

### Step 4: Add TTS Narration
Create separate TTS clips for each segment. Copy-paste these one at a time:

**Clip 1 (over pitch slides, 0:00-0:20):**
```
In 2024, over 2 billion dollars was lost to rug pulls, scams, and smart contract exploits. Existing tools are reactive. You check after you lose money. What if your security guard never slept? Meet SERPENS.
```

**Clip 2 (over terminal token scan, 0:20-0:55):**
```
An autonomous Web3 intelligence agent built on Hermes Agent. Watch the terminal. It loads the token scan skill, calls GoPlus security API and DeFi Llama, and generates a risk score. 20 out of 100. Caution. Blacklist function detected, but no honeypot, zero taxes, open source.
```

**Clip 3 (over terminal contract audit, 0:55-1:25):**
```
Now let's audit a smart contract. The Uniswap V2 Router. SERPENS fetches verified source code from Etherscan, runs security analysis, checks for vulnerability patterns. Clean. As expected.
```

**Clip 4 (over Telegram wallet watch, 1:25-2:00):**
```
Wallet intelligence. Full profile. Balance, transaction history, risk indicators. Then I say watch this wallet. SERPENS sets up a cron job. Every 30 minutes, it checks for changes and alerts on Telegram. Fully autonomous.
```

**Clip 5 (over Telegram memory, 2:00-2:15):**
```
What have I analyzed today? It remembers everything. Persistent memory across sessions.
```

**Clip 6 (over closing slides, 2:15-2:35):**
```
11 custom tools. 5 skills. Custom persona. Persistent memory. Cron scheduling. Telegram gateway. All running on real APIs. No mocks. SERPENS. The on-chain serpent that never sleeps.
```

### Step 5: Background Music (optional)
- Add subtle lo-fi or ambient electronic
- Volume: 10-15% (narration should dominate)

### Step 6: Export
- MP4, 1080p, 30fps
- Target: 2:30 - 2:40

---

## Submission Checklist

- [ ] Video exported from CapCut
- [ ] Upload video to Twitter/X
- [ ] Tweet text (copy from DEMO_GUIDE.md)
- [ ] Tag @NousResearch in tweet
- [ ] Post tweet link in Nous Discord #submissions forum
- [ ] Verify @serpens_telegram_bot is running (gateway alive)
- [ ] Optional: push code to GitHub, add link to tweet
