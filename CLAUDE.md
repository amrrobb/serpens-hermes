# SERPENS — Autonomous Web3 Intelligence Agent

## Overview

SERPENS is an autonomous Web3 security and intelligence agent built on [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research. It provides smart contract auditing, token safety scanning, wallet intelligence, and DeFi monitoring via Telegram or CLI.

Named after Hermes's staff — the ancient symbol of commerce and protection.

## Hackathon

- **Event**: Nous Research Hermes Agent Hackathon
- **Deadline**: March 16, 2026 EOD
- **Submission**: Tweet + video demo + Discord #submissions
- **Judging**: Creativity, usefulness, presentation
- **Prize**: $7,500 / $2,500 / $1,000 / $500 / $250

## Architecture

```
Hermes Agent (forked) + SOUL.md persona
├── Custom Tools (tools/web3_*.py) — 11 tools registered to "web3" toolset
│   ├── web3_tools.py         — get_token_info, get_eth_balance, get_token_price
│   ├── web3_security_tools.py — scan_token_security, check_address_risk, get_contract_source, analyze_contract_security
│   └── web3_defi_tools.py    — analyze_wallet, get_whale_movements, get_defi_positions, get_protocol_tvl
├── Skills (~/.hermes/skills/web3/) — 4 SKILL.md files
│   ├── token-scan        — Rug pull / honeypot detection with risk scoring
│   ├── contract-audit    — Smart contract security analysis (with subagent delegation)
│   ├── wallet-intel      — Wallet profiling, monitoring, and watch lists
│   └── defi-guardian     — DeFi position monitoring via cron alerts
├── Built-in Solana skill (~/.hermes/skills/blockchain/solana/) — multi-chain
└── SOUL.md (~/.hermes/SOUL.md) — Elite Web3 security analyst persona
```

## External APIs

| API | Purpose | Auth |
|---|---|---|
| GoPlus Labs | Token security, address risk, honeypot detection | No key needed |
| DeFiLlama | Token prices, protocol TVL, yield data | No key needed |
| Etherscan | Contract source, tx history, token transfers | `ETHERSCAN_API_KEY` |
| Free public RPCs | On-chain reads via web3.py | No key needed |

## Hermes Features Used

1. **Custom Tool Registry** — 11 tools in `web3` toolset
2. **Skills System** — 4 SKILL.md + 1 built-in Solana skill
3. **SOUL.md** — Custom Web3 security analyst persona
4. **Memory** — Watched wallets persist across sessions
5. **Session Search** — Recall past analyses
6. **Cron Scheduling** — DeFi position monitoring
7. **Telegram Gateway** — Interactive bot at @caduceus_telegram_bot
8. **Subagent Delegation** — Parallel contract analysis
9. **Programmatic Tool Calling** — Agent chains tools via code execution

## Key Files

| File | Purpose |
|---|---|
| `tools/web3_tools.py` | Core EVM tools (token info, balance, price) |
| `tools/web3_security_tools.py` | Security tools (GoPlus, Etherscan, pattern analysis) |
| `tools/web3_defi_tools.py` | Wallet analysis, DeFi, whale tracking |
| `toolsets.py` | Modified to include `web3` toolset in core tools |
| `tools/__init__.py` | Modified to import web3 tool modules |
| `~/.hermes/SOUL.md` | SERPENS persona |
| `~/.hermes/skills/web3/` | 4 custom skills |
| `~/.hermes/skills/blockchain/solana/` | Built-in Solana skill (copied from optional-skills) |
| `~/.hermes/config.yaml` | Provider config (Anthropic OAuth or Groq) |
| `~/.hermes/.env` | API keys and bot tokens |

## LLM Provider

- **Dev/Telegram**: Anthropic Claude via OAuth (`~/.claude.json` auto-detect)
- **VPS fallback**: Groq free tier (Llama 3.3 70B)

## Commands

```bash
# Activate venv
cd /Users/ammar.robb/Documents/Web3/hackathons/serpens
source venv/bin/activate

# CLI chat (limited toolsets for faster response)
hermes chat --provider anthropic --toolsets web3,skills,memory

# Full CLI with all tools
hermes chat --provider anthropic

# Telegram gateway
hermes gateway

# Quick test a tool
python -c "
import sys; sys.path.insert(0, '.')
from tools.registry import registry
import tools.web3_tools
result = registry.dispatch('get_token_price', {'token_address': '0xdAC17F958D2ee523a2206206994597C13D831ec7'})
print(result)
"
```

## Demo Flow

1. Token scan: "Is this token safe? 0x6982508145454Ce325dDbE47a25d4ec3d2311933" (PEPE)
2. Contract audit: "Audit contract 0x..."
3. Wallet intel: "Analyze wallet 0x..." + "Watch this wallet"
4. Memory recall: "What have I analyzed today?"
5. Cron: "Alert me if ETH drops below $2000"

## Telegram Bot

- **Username**: @caduceus_telegram_bot
- **Your Telegram ID**: 5839244281 (home channel)
- **Gateway**: `hermes gateway` starts polling

## Modified Files (diff from upstream hermes-agent)

- `tools/__init__.py` — Added web3 tool imports
- `toolsets.py` — Added web3 tools to `_HERMES_CORE_TOOLS` and `TOOLSETS` dict
- `tools/web3_tools.py` — NEW
- `tools/web3_security_tools.py` — NEW
- `tools/web3_defi_tools.py` — NEW

## Critical Bug: ANTHROPIC_API_KEY vs ANTHROPIC_TOKEN

**NEVER set `ANTHROPIC_API_KEY` in `.env` when using OAuth tokens (`sk-ant-oat01-...`).**

The Anthropic Python SDK auto-reads `ANTHROPIC_API_KEY` from the environment and sends it as `x-api-key` header. OAuth tokens need `Bearer` auth via `auth_token` parameter. When both are set, the SDK uses `x-api-key` (wrong) instead of `Bearer` (correct), causing `invalid x-api-key` errors.

**Correct:** Only set `ANTHROPIC_TOKEN` in `.env` — Hermes reads this first (priority 1 in `resolve_anthropic_token()`).

## Anti-Patterns

- Do NOT set `ANTHROPIC_API_KEY` in `.env` for OAuth tokens — causes auth header conflict
- Do NOT add more tools without testing TPM limits on Groq
- Do NOT modify registry.py — our tools self-register
- Do NOT hardcode API keys in tool files — use os.getenv()
- Skills go in `~/.hermes/skills/`, NOT in the repo's `skills/` dir (those are built-in)
- Clear `__pycache__` after modifying `.py` files: `find . -name __pycache__ -not -path ./venv/\* -exec rm -rf {} +`
