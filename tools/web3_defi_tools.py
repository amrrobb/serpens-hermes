"""
Web3 & DeFi Tools for Hermes Agent

Provides wallet analysis, whale movement detection, DeFi position lookup,
and protocol TVL data using public APIs (Etherscan, DeFiLlama) and web3.py.

Tools:
- analyze_wallet: Comprehensive on-chain wallet analysis with risk indicators
- get_whale_movements: Detect large token transfers via explorer APIs
- get_defi_positions: Top DeFi yield opportunities via DeFiLlama
- get_protocol_tvl: Protocol TVL breakdown via DeFiLlama
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RPCS = {
    "ethereum": "https://eth.llamarpc.com",
    "polygon": "https://polygon-rpc.com",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "base": "https://mainnet.base.org",
    "bsc": "https://bsc-dataseed.binance.org",
}

EXPLORER_APIS = {
    "ethereum": "https://api.etherscan.io/v2/api?chainid=1",
    "polygon": "https://api.etherscan.io/v2/api?chainid=137",
    "arbitrum": "https://api.etherscan.io/v2/api?chainid=42161",
    "base": "https://api.etherscan.io/v2/api?chainid=8453",
    "bsc": "https://api.etherscan.io/v2/api?chainid=56",
}

HTTP_TIMEOUT = 10  # seconds


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_web3(chain: str):
    """Lazy-import web3 and return a Web3 instance for the given chain."""
    from web3 import Web3
    rpc = RPCS.get(chain)
    if not rpc:
        raise ValueError(f"Unsupported chain: {chain}. Supported: {list(RPCS.keys())}")
    return Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": HTTP_TIMEOUT}))


def _checksum(address: str) -> str:
    from web3 import Web3
    return Web3.to_checksum_address(address)


def _unix_to_iso(ts) -> str:
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()


def _explorer_get(chain: str, params: dict) -> dict:
    """Make a GET request to the block explorer API for *chain*."""
    base_url = EXPLORER_APIS.get(chain)
    if not base_url:
        raise ValueError(f"No explorer API for chain: {chain}")
    api_key = os.getenv("ETHERSCAN_API_KEY", "")
    if api_key:
        params["apikey"] = api_key
    resp = requests.get(base_url, params=params, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data


# ---------------------------------------------------------------------------
# 1. analyze_wallet
# ---------------------------------------------------------------------------

def _handle_analyze_wallet(args: dict, **kwargs) -> str:
    try:
        address = _checksum(args["address"])
        chain = args.get("chain", "ethereum")

        w3 = _get_web3(chain)

        # Native balance
        balance_wei = w3.eth.get_balance(address)
        native_balance = float(w3.from_wei(balance_wei, "ether"))

        # Is contract?
        code = w3.eth.get_code(address)
        is_contract = len(code) > 0

        # Transaction history from explorer
        txs: List[dict] = []
        explorer_error: Optional[str] = None
        try:
            data = _explorer_get(chain, {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": 50,
                "sort": "desc",
            })
            if data.get("status") == "1" and isinstance(data.get("result"), list):
                txs = data["result"]
            elif isinstance(data.get("result"), str):
                explorer_error = data["result"]
        except Exception as e:
            explorer_error = str(e)

        # Derived metrics
        tx_count = len(txs)
        now = datetime.now(tz=timezone.utc)

        first_tx_date = None
        last_tx_date = None
        wallet_age_days = 0
        unique_contracts: set = set()
        recent_30d_count = 0
        contract_freq: Dict[str, int] = {}

        if txs:
            # txs are sorted desc — last element is earliest
            first_ts = int(txs[-1].get("timeStamp", 0))
            last_ts = int(txs[0].get("timeStamp", 0))
            if first_ts:
                first_tx_date = _unix_to_iso(first_ts)
                wallet_age_days = (now - datetime.fromtimestamp(first_ts, tz=timezone.utc)).days
            if last_ts:
                last_tx_date = _unix_to_iso(last_ts)

            thirty_days_ago = now.timestamp() - (30 * 86400)
            for tx in txs:
                to_addr = tx.get("to", "")
                ts = int(tx.get("timeStamp", 0))
                if to_addr:
                    unique_contracts.add(to_addr.lower())
                    contract_freq[to_addr.lower()] = contract_freq.get(to_addr.lower(), 0) + 1
                if ts > thirty_days_ago:
                    recent_30d_count += 1

        # Risk indicators
        risk_indicators: List[str] = []
        if wallet_age_days < 7 and txs:
            risk_indicators.append("NEW_WALLET")
        if recent_30d_count > 100:
            risk_indicators.append("HIGH_FREQUENCY")
        if contract_freq and txs:
            max_freq = max(contract_freq.values())
            if max_freq / len(txs) > 0.8:
                risk_indicators.append("SINGLE_TOKEN_FOCUS")

        # Recent transactions (last 10)
        recent_transactions = []
        for tx in txs[:10]:
            value_wei = int(tx.get("value", 0))
            recent_transactions.append({
                "hash": tx.get("hash", ""),
                "to": tx.get("to", ""),
                "value_eth": float(w3.from_wei(value_wei, "ether")),
                "timestamp": _unix_to_iso(tx.get("timeStamp", 0)),
                "method_id": tx.get("input", "0x")[:10] if tx.get("input") else "0x",
            })

        result = {
            "address": address,
            "chain": chain,
            "native_balance_eth": native_balance,
            "tx_count": tx_count,
            "first_tx_date": first_tx_date,
            "last_tx_date": last_tx_date,
            "wallet_age_days": wallet_age_days,
            "unique_contracts_interacted": len(unique_contracts),
            "is_contract": is_contract,
            "risk_indicators": risk_indicators,
            "recent_transactions": recent_transactions,
        }
        if explorer_error:
            result["explorer_note"] = explorer_error

        return json.dumps(result)

    except Exception as e:
        logger.exception("analyze_wallet error")
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


# ---------------------------------------------------------------------------
# 2. get_whale_movements
# ---------------------------------------------------------------------------

def _handle_get_whale_movements(args: dict, **kwargs) -> str:
    try:
        token_address = _checksum(args["token_address"])
        chain = args.get("chain", "ethereum")
        min_value = float(args.get("min_value", 100000))

        data = _explorer_get(chain, {
            "module": "account",
            "action": "tokentx",
            "contractaddress": token_address,
            "page": 1,
            "offset": 100,
            "sort": "desc",
        })

        transfers: List[dict] = []
        token_symbol = ""

        if data.get("status") == "1" and isinstance(data.get("result"), list):
            for tx in data["result"]:
                decimals = int(tx.get("tokenDecimal", 18))
                raw_value = int(tx.get("value", 0))
                value = raw_value / (10 ** decimals)

                if not token_symbol:
                    token_symbol = tx.get("tokenSymbol", "UNKNOWN")

                if value >= min_value:
                    transfers.append({
                        "from": tx.get("from", ""),
                        "to": tx.get("to", ""),
                        "value": value,
                        "value_formatted": f"{value:,.2f} {token_symbol}",
                        "tx_hash": tx.get("hash", ""),
                        "timestamp": _unix_to_iso(tx.get("timeStamp", 0)),
                    })

        return json.dumps({
            "token_address": token_address,
            "token_symbol": token_symbol or "UNKNOWN",
            "chain": chain,
            "min_value_filter": min_value,
            "whale_transfers": transfers,
            "total_found": len(transfers),
        })

    except Exception as e:
        logger.exception("get_whale_movements error")
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


# ---------------------------------------------------------------------------
# 3. get_defi_positions
# ---------------------------------------------------------------------------

def _handle_get_defi_positions(args: dict, **kwargs) -> str:
    try:
        address = _checksum(args["address"])

        # Fetch top yield opportunities from DeFiLlama
        resp = requests.get("https://yields.llama.fi/pools", timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        pools = resp.json().get("data", [])

        # Filter: TVL > $1M, sort by APY desc, take top 20
        filtered = [
            p for p in pools
            if p.get("tvlUsd", 0) and p["tvlUsd"] > 1_000_000
            and p.get("apy") is not None
        ]
        filtered.sort(key=lambda p: p.get("apy", 0), reverse=True)
        top = filtered[:20]

        top_yields = []
        for p in top:
            top_yields.append({
                "protocol": p.get("project", ""),
                "chain": p.get("chain", ""),
                "pool": p.get("symbol", ""),
                "tvl_usd": round(p.get("tvlUsd", 0), 2),
                "apy": round(p.get("apy", 0), 2),
                "apy_base": round(p.get("apyBase", 0) or 0, 2),
                "apy_reward": round(p.get("apyReward", 0) or 0, 2),
            })

        return json.dumps({
            "address": address,
            "top_yields": top_yields,
            "note": "Full position tracking requires protocol-specific integration",
        })

    except Exception as e:
        logger.exception("get_defi_positions error")
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


# ---------------------------------------------------------------------------
# 4. get_protocol_tvl
# ---------------------------------------------------------------------------

def _handle_get_protocol_tvl(args: dict, **kwargs) -> str:
    try:
        slug = args["protocol"].lower().strip()

        resp = requests.get(
            f"https://api.llama.fi/protocol/{slug}",
            timeout=HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        # Extract chain TVLs from the latest entry in chainTvls
        chain_tvls: Dict[str, float] = {}
        for chain_name, chain_data in (data.get("chainTvls") or {}).items():
            tvl_entries = chain_data.get("tvl", [])
            if tvl_entries:
                chain_tvls[chain_name] = round(tvl_entries[-1].get("totalLiquidityUSD", 0), 2)

        return json.dumps({
            "name": data.get("name", slug),
            "total_tvl": round(data.get("currentChainTvls", {}).get("total", 0) or sum(
                v for v in (data.get("currentChainTvls") or {}).values()
            ), 2),
            "chain_tvls": chain_tvls or data.get("currentChainTvls", {}),
            "category": data.get("category", ""),
            "url": data.get("url", ""),
        })

    except Exception as e:
        logger.exception("get_protocol_tvl error")
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


# ---------------------------------------------------------------------------
# Availability check
# ---------------------------------------------------------------------------

def _web3_available() -> bool:
    """Return True if web3 can be imported (soft dependency)."""
    try:
        import web3  # noqa: F401
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Register with Hermes tool registry
# ---------------------------------------------------------------------------

from tools.registry import registry

registry.register(
    name="analyze_wallet",
    toolset="web3",
    schema={
        "name": "analyze_wallet",
        "description": (
            "Comprehensive on-chain wallet analysis. Returns native balance, "
            "transaction history, wallet age, unique contracts interacted with, "
            "risk indicators (NEW_WALLET, HIGH_FREQUENCY, SINGLE_TOKEN_FOCUS), "
            "and recent transactions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Wallet address (0x...)",
                },
                "chain": {
                    "type": "string",
                    "description": "Blockchain network (ethereum, polygon, arbitrum, base, bsc)",
                    "default": "ethereum",
                },
            },
            "required": ["address"],
        },
    },
    handler=lambda args, **kw: _handle_analyze_wallet(args, **kw),
    check_fn=_web3_available,
    is_async=False,
)

registry.register(
    name="get_whale_movements",
    toolset="web3",
    schema={
        "name": "get_whale_movements",
        "description": (
            "Detect large token transfers (whale movements) for a given ERC-20 token. "
            "Queries the block explorer for recent transfers and filters by minimum value."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "ERC-20 token contract address (0x...)",
                },
                "chain": {
                    "type": "string",
                    "description": "Blockchain network (ethereum, polygon, arbitrum, base, bsc)",
                    "default": "ethereum",
                },
                "min_value": {
                    "type": "number",
                    "description": "Minimum transfer value in token units to qualify as a whale movement",
                    "default": 100000,
                },
            },
            "required": ["token_address"],
        },
    },
    handler=lambda args, **kw: _handle_get_whale_movements(args, **kw),
    check_fn=lambda: True,
    is_async=False,
)

registry.register(
    name="get_defi_positions",
    toolset="web3",
    schema={
        "name": "get_defi_positions",
        "description": (
            "Get top DeFi yield opportunities across protocols via DeFiLlama. "
            "Returns the top 20 pools by APY with TVL > $1M. "
            "Full position tracking for a specific address requires protocol-specific integration."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Wallet address to check (used for future position tracking)",
                },
            },
            "required": ["address"],
        },
    },
    handler=lambda args, **kw: _handle_get_defi_positions(args, **kw),
    check_fn=_web3_available,
    is_async=False,
)

registry.register(
    name="get_protocol_tvl",
    toolset="web3",
    schema={
        "name": "get_protocol_tvl",
        "description": (
            "Get Total Value Locked (TVL) data for a DeFi protocol via DeFiLlama. "
            "Returns total TVL, per-chain breakdown, category, and protocol URL. "
            "Use protocol slugs like 'aave', 'uniswap', 'lido', 'makerdao'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "protocol": {
                    "type": "string",
                    "description": "Protocol slug (e.g. 'aave', 'uniswap', 'lido')",
                },
            },
            "required": ["protocol"],
        },
    },
    handler=lambda args, **kw: _handle_get_protocol_tvl(args, **kw),
    check_fn=lambda: True,
    is_async=False,
)
