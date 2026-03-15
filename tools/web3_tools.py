"""EVM blockchain tools for Hermes Agent.

Provides on-chain reads (token info, balances) and price lookups via
DeFiLlama. Registers tools with the central registry at import time.

Dependencies: web3, requests (both in requirements already).
"""

import json
import logging
import os
from typing import Any, Dict

import requests
from web3 import Web3

from tools.registry import registry

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

CHAIN_NAMES_LLAMA = {
    "ethereum": "ethereum",
    "polygon": "polygon",
    "arbitrum": "arbitrum",
    "base": "base",
    "bsc": "bsc",
}

SUPPORTED_CHAINS = list(RPCS.keys())

ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
]

# Native token coingecko-style IDs used by DeFiLlama for native prices
NATIVE_PRICE_IDS = {
    "ethereum": "coingecko:ethereum",
    "polygon": "coingecko:matic-network",
    "arbitrum": "coingecko:ethereum",
    "base": "coingecko:ethereum",
    "bsc": "coingecko:binancecoin",
}

HTTP_TIMEOUT = 5

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_w3(chain: str) -> Web3:
    """Return a Web3 instance connected to the given chain."""
    rpc = RPCS.get(chain)
    if not rpc:
        raise ValueError(f"Unsupported chain: {chain}. Supported: {SUPPORTED_CHAINS}")
    return Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": HTTP_TIMEOUT}))


def _checksum(address: str) -> str:
    """Validate and return checksummed address."""
    return Web3.to_checksum_address(address)


def _llama_price(chain: str, token_address: str) -> Dict[str, Any]:
    """Fetch price from DeFiLlama coins API. Returns dict with price info or empty."""
    llama_chain = CHAIN_NAMES_LLAMA.get(chain, chain)
    coin_id = f"{llama_chain}:{token_address}"
    url = f"https://coins.llama.fi/prices/current/{coin_id}"
    try:
        resp = requests.get(url, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        coin_data = data.get("coins", {}).get(coin_id, {})
        return coin_data
    except Exception as e:
        logger.debug("DeFiLlama price fetch failed for %s: %s", coin_id, e)
        return {}


def _native_price(chain: str) -> float | None:
    """Fetch native token price via DeFiLlama."""
    price_id = NATIVE_PRICE_IDS.get(chain)
    if not price_id:
        return None
    url = f"https://coins.llama.fi/prices/current/{price_id}"
    try:
        resp = requests.get(url, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        coin_data = data.get("coins", {}).get(price_id, {})
        return coin_data.get("price")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


def _handle_get_token_info(args: dict, **kwargs) -> str:
    """Get ERC-20 token metadata and price."""
    try:
        token_address = _checksum(args["token_address"])
        chain = args.get("chain", "ethereum")

        w3 = _get_w3(chain)
        contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)

        # Read on-chain data — each call can fail independently
        name = None
        symbol = None
        decimals = None
        total_supply_raw = None

        try:
            name = contract.functions.name().call()
        except Exception:
            name = "Unknown"

        try:
            symbol = contract.functions.symbol().call()
        except Exception:
            symbol = "Unknown"

        try:
            decimals = contract.functions.decimals().call()
        except Exception:
            decimals = 18

        try:
            total_supply_raw = contract.functions.totalSupply().call()
        except Exception:
            total_supply_raw = 0

        total_supply = total_supply_raw / (10 ** decimals)

        # Price from DeFiLlama
        price_data = _llama_price(chain, token_address)
        price_usd = price_data.get("price")
        market_cap_estimate = (price_usd * total_supply) if price_usd and total_supply else None

        result = {
            "name": name,
            "symbol": symbol,
            "decimals": decimals,
            "total_supply": total_supply,
            "price_usd": price_usd,
            "market_cap_estimate": market_cap_estimate,
            "chain": chain,
            "address": token_address,
        }
        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"get_token_info failed: {type(e).__name__}: {e}"})


def _handle_get_eth_balance(args: dict, **kwargs) -> str:
    """Get native balance for an address."""
    try:
        address = _checksum(args["address"])
        chain = args.get("chain", "ethereum")

        w3 = _get_w3(chain)
        balance_wei = w3.eth.get_balance(address)
        balance_eth = float(Web3.from_wei(balance_wei, "ether"))

        # Get native price for USD conversion
        native_usd = _native_price(chain)
        balance_usd = (balance_eth * native_usd) if native_usd else None

        native_symbol = {
            "ethereum": "ETH",
            "polygon": "MATIC",
            "arbitrum": "ETH",
            "base": "ETH",
            "bsc": "BNB",
        }.get(chain, "ETH")

        result = {
            "address": address,
            "chain": chain,
            "native_balance": balance_eth,
            "native_symbol": native_symbol,
            "native_balance_usd": round(balance_usd, 2) if balance_usd else None,
            "native_price_usd": native_usd,
        }

        # Optional: Etherscan token list (only for ethereum, if key available)
        etherscan_key = os.getenv("ETHERSCAN_API_KEY")
        if etherscan_key and chain == "ethereum":
            try:
                url = (
                    f"https://api.etherscan.io/api"
                    f"?module=account&action=tokentx&address={address}"
                    f"&page=1&offset=20&sort=desc&apikey={etherscan_key}"
                )
                resp = requests.get(url, timeout=HTTP_TIMEOUT)
                resp.raise_for_status()
                data = resp.json()
                if data.get("status") == "1" and data.get("result"):
                    # Deduplicate token contracts from recent transfers
                    seen_tokens = {}
                    for tx in data["result"]:
                        ca = tx.get("contractAddress", "")
                        if ca and ca not in seen_tokens:
                            seen_tokens[ca] = {
                                "symbol": tx.get("tokenSymbol", "?"),
                                "name": tx.get("tokenName", "?"),
                                "contract": ca,
                            }
                    result["recent_tokens"] = list(seen_tokens.values())[:10]
            except Exception as e:
                logger.debug("Etherscan token lookup failed: %s", e)

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"get_eth_balance failed: {type(e).__name__}: {e}"})


def _handle_get_token_price(args: dict, **kwargs) -> str:
    """Quick token price lookup via DeFiLlama."""
    try:
        token_address = _checksum(args["token_address"])
        chain = args.get("chain", "ethereum")

        price_data = _llama_price(chain, token_address)

        if not price_data:
            return json.dumps({
                "error": "Price not found on DeFiLlama",
                "chain": chain,
                "address": token_address,
            })

        result = {
            "price_usd": price_data.get("price"),
            "confidence": price_data.get("confidence", None),
            "timestamp": price_data.get("timestamp", None),
            "symbol": price_data.get("symbol", None),
            "chain": chain,
            "address": token_address,
        }
        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": f"get_token_price failed: {type(e).__name__}: {e}"})


# ---------------------------------------------------------------------------
# Availability check
# ---------------------------------------------------------------------------


def _web3_available() -> bool:
    """Check if web3 is importable (it's already imported at top, so True)."""
    return True


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

registry.register(
    name="get_token_info",
    toolset="web3",
    schema={
        "name": "get_token_info",
        "description": (
            "Get ERC-20 token metadata (name, symbol, decimals, total supply) "
            "and current price from on-chain data + DeFiLlama."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "The ERC-20 token contract address.",
                },
                "chain": {
                    "type": "string",
                    "enum": ["ethereum", "polygon", "arbitrum", "base", "bsc"],
                    "description": "The blockchain to query. Defaults to ethereum.",
                },
            },
            "required": ["token_address"],
        },
    },
    handler=_handle_get_token_info,
    check_fn=_web3_available,
    is_async=False,
)

registry.register(
    name="get_eth_balance",
    toolset="web3",
    schema={
        "name": "get_eth_balance",
        "description": (
            "Get the native token balance (ETH/MATIC/BNB) and USD value for an address. "
            "Optionally discovers recent ERC-20 tokens via Etherscan if API key is set."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "The wallet address to check.",
                },
                "chain": {
                    "type": "string",
                    "enum": ["ethereum", "polygon", "arbitrum", "base", "bsc"],
                    "description": "The blockchain to query. Defaults to ethereum.",
                },
            },
            "required": ["address"],
        },
    },
    handler=_handle_get_eth_balance,
    check_fn=_web3_available,
    is_async=False,
)

registry.register(
    name="get_token_price",
    toolset="web3",
    schema={
        "name": "get_token_price",
        "description": (
            "Quick token price lookup via DeFiLlama. Returns USD price, "
            "confidence score, and timestamp."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "The ERC-20 token contract address.",
                },
                "chain": {
                    "type": "string",
                    "enum": ["ethereum", "polygon", "arbitrum", "base", "bsc"],
                    "description": "The blockchain to query. Defaults to ethereum.",
                },
            },
            "required": ["token_address"],
        },
    },
    handler=_handle_get_token_price,
    check_fn=_web3_available,
    is_async=False,
)
