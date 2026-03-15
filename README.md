# SERPENS

**Autonomous Web3 Intelligence Agent** powered by [Hermes Agent](https://github.com/NousResearch/hermes-agent)

Your always-on crypto security guard — smart contract auditing, rug pull detection, wallet intelligence, and DeFi monitoring. Accessible via Telegram or CLI.

> Named after the Serpens constellation — the celestial serpent entwined around Hermes's staff. It sees everything on-chain.

## What It Does

| Capability | Description |
|---|---|
| **Token Scanner** | Scan any ERC-20 for honeypot risk, sell tax, holder concentration, and ownership flags |
| **Contract Auditor** | Fetch verified source code, detect vulnerability patterns, run GoPlus security analysis |
| **Wallet Intelligence** | Profile any wallet — activity patterns, holdings, risk indicators, transaction history |
| **DeFi Guardian** | Monitor positions, track yields, set up automated alerts via cron |
| **Solana Support** | Built-in Solana skill for wallet portfolios, token info, and whale detection |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SERPENS                              │
│               Hermes Agent + SOUL.md Persona                 │
├─────────────────────────────────────────────────────────────┤
│  11 Custom Tools                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ GoPlus   │ │ DeFiLlama│ │Etherscan │ │ web3.py  │       │
│  │ Security │ │ Prices   │ │ Source   │ │ EVM RPC  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│  5 Skills: token-scan, contract-audit, wallet-intel,         │
│            defi-guardian, blockchain/solana                   │
├─────────────────────────────────────────────────────────────┤
│  Hermes Platform: Memory | Cron | Telegram | Subagents       │
│                   Session Search | SOUL.md | Skills Hub       │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone
git clone --recurse-submodules https://github.com/AmmGo/serpens.git
cd serpens

# Install
uv venv venv --python 3.11
source venv/bin/activate
uv pip install -e ".[all]"
uv pip install -e "./mini-swe-agent"
uv pip install web3 requests

# Configure (~/.hermes/.env)
ANTHROPIC_API_KEY=your_key          # or use Claude Code OAuth auto-detect
TELEGRAM_BOT_TOKEN=your_bot_token   # from @BotFather
ETHERSCAN_API_KEY=your_key          # free at etherscan.io
GATEWAY_ALLOW_ALL_USERS=true

# Install skills
cp -r optional-skills/blockchain ~/.hermes/skills/
# Copy the web3 skills from skills/web3/ to ~/.hermes/skills/web3/

# Run CLI
hermes chat --provider anthropic

# Run Telegram bot
hermes gateway
```

## Custom Tools

All tools register with the Hermes tool registry under the `web3` toolset:

| Tool | API Source | Description |
|---|---|---|
| `get_token_info` | web3.py + DeFiLlama | Token metadata, price, market cap |
| `get_token_price` | DeFiLlama | Quick price lookup |
| `get_eth_balance` | web3.py | Native + token balances |
| `scan_token_security` | GoPlus | Honeypot, tax, ownership risk analysis |
| `check_address_risk` | GoPlus | Malicious address detection |
| `get_contract_source` | Etherscan | Verified source code retrieval |
| `analyze_contract_security` | GoPlus + Etherscan + regex | Combined security audit |
| `analyze_wallet` | Etherscan + web3.py | Wallet activity profiling |
| `get_whale_movements` | Etherscan | Large transfer detection |
| `get_defi_positions` | DeFiLlama | Yield opportunities |
| `get_protocol_tvl` | DeFiLlama | Protocol TVL data |

## Hermes Features Used

- **Custom Tool Registry** — 11 tools in `web3` toolset
- **Skills System** — 4 custom + 1 built-in skill
- **SOUL.md** — Web3 security analyst persona
- **Persistent Memory** — Watched wallets survive restarts
- **Cron Scheduling** — Automated position monitoring
- **Telegram Gateway** — Interactive bot
- **Subagent Delegation** — Parallel contract analysis
- **Session Search** — Cross-session intelligence recall

## Example Usage

```
You: Is this token safe? 0x6982508145454Ce325dDbE47a25d4ec3d2311933

SERPENS: TOKEN SAFETY REPORT
Token: Pepe (PEPE)
Chain: Ethereum
Risk Score: 22/100 — CAUTION

FINDINGS:
- MEDIUM: Blacklisted function detected
- MEDIUM: Anti-whale mechanism present
- LOW: Top holder owns 13.34%

TAX: Buy 0% | Sell 0%
Holders: 511,368

RECOMMENDATION: Generally safe to trade. The blacklist and anti-whale
functions are common in large-cap meme tokens. Monitor holder concentration.

Want me to audit the contract source code?
```

## Supported Chains

| Chain | RPC | Explorer |
|---|---|---|
| Ethereum | eth.llamarpc.com | etherscan.io |
| Polygon | polygon-rpc.com | polygonscan.com |
| Arbitrum | arb1.arbitrum.io/rpc | arbiscan.io |
| Base | mainnet.base.org | basescan.org |
| BSC | bsc-dataseed.binance.org | bscscan.com |
| Solana | (built-in skill) | — |

## Use Your Own API Key

SERPENS skills are portable. You can run them with your own LLM key — no dependency on our infrastructure.

**Option 1: Full install (Hermes Agent)**
```bash
git clone https://github.com/AmmGo/serpens.git
cd serpens
# Install hermes + deps (see Quick Start above)
# Set YOUR api key:
echo "ANTHROPIC_TOKEN=your-key-here" > ~/.hermes/.env
# Copy skills
cp -r skills/web3/ ~/.hermes/skills/web3/
hermes chat --provider anthropic
```

**Option 2: Skills only (any AgentSkills.io-compatible agent)**

Our `SKILL.md` files follow the open [AgentSkills.io](https://agentskills.io) standard. They work with:
- Claude Code
- Cursor
- Gemini CLI
- OpenAI Codex
- VS Code Copilot
- Any agent that reads SKILL.md

Just copy the `skills/web3/` directory into your agent's skills folder.

**Option 3: Tools only (Python)**
```python
# Use our tools standalone — they're just Python functions
from tools.web3_security_tools import handle_scan_token_security
result = handle_scan_token_security({"token_address": "0x...", "chain_id": 1})
```

## License

MIT — Built on [Hermes Agent](https://github.com/NousResearch/hermes-agent) by [Nous Research](https://nousresearch.com)
