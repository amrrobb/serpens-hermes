"""Web3 security tools for Hermes Agent.

Provides token security scanning, address risk checks, contract source
retrieval, and combined security analysis using GoPlus and Etherscan APIs.
"""

import json
import logging
import os
import re
from typing import Any, Dict

import requests

from tools.registry import registry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GOPLUS_BASE = "https://api.gopluslabs.io/api/v1"
GOPLUS_TIMEOUT = 10
ETHERSCAN_TIMEOUT = 5

CHAIN_IDS_GOPLUS = {
    "ethereum": 1,
    "bsc": 56,
    "polygon": 137,
    "arbitrum": 42161,
    "base": 8453,
}

EXPLORER_APIS = {
    "ethereum": "https://api.etherscan.io/api",
    "polygon": "https://api.polygonscan.com/api",
    "arbitrum": "https://api.arbiscan.io/api",
    "base": "https://api.basescan.org/api",
    "bsc": "https://api.bscscan.com/api",
}

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def _scan_token_security(args: dict, **kw: Any) -> str:
    """GoPlus token security analysis."""
    try:
        address = args["token_address"].strip().lower()
        chain_id = int(args.get("chain_id", 1))

        resp = requests.get(
            f"{GOPLUS_BASE}/token_security/{chain_id}",
            params={"contract_addresses": address},
            timeout=GOPLUS_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        result_map = data.get("result", {})
        token_data = result_map.get(address, {})
        if not token_data:
            return json.dumps({"error": f"No data returned for {address} on chain {chain_id}"})

        # Collect risks
        risks = []
        is_honeypot = str(token_data.get("is_honeypot", "0")) == "1"
        has_selfdestruct = str(token_data.get("selfdestruct", "0")) == "1"
        is_mintable = str(token_data.get("is_mintable", "0")) == "1"
        hidden_owner = str(token_data.get("hidden_owner", "0")) == "1"
        can_take_back = str(token_data.get("can_take_back_ownership", "0")) == "1"
        external_call = str(token_data.get("external_call", "0")) == "1"
        is_blacklisted = str(token_data.get("is_blacklisted", "0")) == "1"
        is_whitelisted = str(token_data.get("is_whitelisted", "0")) == "1"
        anti_whale = str(token_data.get("is_anti_whale", "0")) == "1"
        trading_cooldown = str(token_data.get("trading_cooldown", "0")) == "1"
        transfer_pausable = str(token_data.get("transfer_pausable", "0")) == "1"
        cannot_sell_all = str(token_data.get("cannot_sell_all", "0")) == "1"

        if is_honeypot:
            risks.append("HONEYPOT")
        if has_selfdestruct:
            risks.append("SELFDESTRUCT")
        if is_mintable:
            risks.append("MINTABLE")
        if hidden_owner:
            risks.append("HIDDEN_OWNER")
        if can_take_back:
            risks.append("CAN_TAKE_BACK_OWNERSHIP")
        if external_call:
            risks.append("EXTERNAL_CALL")
        if is_blacklisted:
            risks.append("BLACKLISTED")
        if is_whitelisted:
            risks.append("WHITELISTED")
        if anti_whale:
            risks.append("ANTI_WHALE")
        if trading_cooldown:
            risks.append("TRADING_COOLDOWN")
        if transfer_pausable:
            risks.append("TRANSFER_PAUSABLE")
        if cannot_sell_all:
            risks.append("CANNOT_SELL_ALL")

        # Risk level
        if is_honeypot or has_selfdestruct:
            risk_level = "CRITICAL"
        elif len(risks) >= 3:
            risk_level = "HIGH"
        elif len(risks) >= 1:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Tax parsing
        buy_tax = float(token_data.get("buy_tax", 0) or 0) * 100
        sell_tax = float(token_data.get("sell_tax", 0) or 0) * 100

        # Holder info
        holders = token_data.get("holders", [])
        top_holder_pct = 0.0
        if holders:
            top_holder_pct = float(holders[0].get("percent", 0) or 0) * 100

        result = {
            "risk_level": risk_level,
            "risks": risks,
            "is_honeypot": is_honeypot,
            "buy_tax_pct": round(buy_tax, 2),
            "sell_tax_pct": round(sell_tax, 2),
            "is_open_source": str(token_data.get("is_open_source", "0")) == "1",
            "is_proxy": str(token_data.get("is_proxy", "0")) == "1",
            "holder_count": str(token_data.get("holder_count", "0")),
            "top_holder_pct": round(top_holder_pct, 2),
            "lp_holder_count": str(token_data.get("lp_holder_count", "0")),
            "owner_address": token_data.get("owner_address", ""),
            "creator_address": token_data.get("creator_address", ""),
        }
        return json.dumps(result)

    except Exception as e:
        logger.exception("scan_token_security error: %s", e)
        return json.dumps({"error": f"scan_token_security failed: {type(e).__name__}: {e}"})


def _check_address_risk(args: dict, **kw: Any) -> str:
    """GoPlus address security check."""
    try:
        address = args["address"].strip()

        resp = requests.get(
            f"{GOPLUS_BASE}/address_security/{address}",
            timeout=GOPLUS_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        result_data = data.get("result", {})
        if not result_data:
            return json.dumps({"error": f"No data returned for address {address}"})

        # Determine if malicious based on any positive flag
        risk_flags = [
            "cybercrime", "money_laundering", "number_of_malicious_contracts_created",
            "financial_crime", "darkweb_transactions", "phishing_activities",
            "fake_kyc", "blacklist_doubt", "stealing_attack",
            "blackmail_activities", "sanctioned", "malicious_mining_activities",
            "mixer_usage", "honeypot_related_address",
        ]

        detected_risks = []
        for flag in risk_flags:
            val = result_data.get(flag)
            if val and str(val) == "1":
                detected_risks.append(flag)

        is_malicious = len(detected_risks) > 0
        risk_type = detected_risks[0] if detected_risks else None

        return json.dumps({
            "is_malicious": is_malicious,
            "risk_type": risk_type,
            "details": detected_risks,
            "data_source": result_data.get("data_source", ""),
        })

    except Exception as e:
        logger.exception("check_address_risk error: %s", e)
        return json.dumps({"error": f"check_address_risk failed: {type(e).__name__}: {e}"})


def _get_contract_source(args: dict, **kw: Any) -> str:
    """Fetch contract source code from Etherscan-compatible explorers."""
    try:
        api_key = os.getenv("ETHERSCAN_API_KEY")
        if not api_key:
            return json.dumps({"error": "ETHERSCAN_API_KEY not set"})

        address = args["contract_address"].strip()
        chain = args.get("chain", "ethereum").lower()

        base_url = EXPLORER_APIS.get(chain)
        if not base_url:
            return json.dumps({"error": f"Unsupported chain: {chain}. Supported: {list(EXPLORER_APIS.keys())}"})

        resp = requests.get(
            base_url,
            params={
                "module": "contract",
                "action": "getsourcecode",
                "address": address,
                "apikey": api_key,
            },
            timeout=ETHERSCAN_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "1" or not data.get("result"):
            return json.dumps({"error": f"Etherscan returned: {data.get('message', 'Unknown error')}"})

        contract = data["result"][0]
        source_code = contract.get("SourceCode", "")
        # Truncate to 5000 chars
        truncated = source_code[:5000] if source_code else ""

        return json.dumps({
            "contract_name": contract.get("ContractName", ""),
            "source_code": truncated,
            "compiler_version": contract.get("CompilerVersion", ""),
            "is_verified": bool(contract.get("SourceCode")),
            "optimization_used": contract.get("OptimizationUsed", "0") == "1",
            "abi_available": bool(contract.get("ABI") and contract["ABI"] != "Contract source code not verified"),
        })

    except Exception as e:
        logger.exception("get_contract_source error: %s", e)
        return json.dumps({"error": f"get_contract_source failed: {type(e).__name__}: {e}"})


def _analyze_contract_security(args: dict, **kw: Any) -> str:
    """Combined security analysis: GoPlus + source code pattern checks."""
    try:
        address = args["contract_address"].strip()
        chain = args.get("chain", "ethereum").lower()
        chain_id = CHAIN_IDS_GOPLUS.get(chain, 1)

        # 1. GoPlus token scan
        goplus_raw = _scan_token_security({"token_address": address, "chain_id": chain_id})
        goplus_result = json.loads(goplus_raw)
        goplus_risks = goplus_result.get("risks", [])
        goplus_risk_level = goplus_result.get("risk_level", "LOW")
        goplus_error = goplus_result.get("error")

        # 2. Source code retrieval
        source_raw = _get_contract_source({"contract_address": address, "chain": chain})
        source_result = json.loads(source_raw)
        source_code = source_result.get("source_code", "")
        is_verified = source_result.get("is_verified", False)
        contract_name = source_result.get("contract_name", "")
        source_error = source_result.get("error")

        # 3. Source code pattern analysis
        source_vulns = []
        recommendations = []

        if source_code:
            if re.search(r'\bselfdestruct\b', source_code):
                source_vulns.append({"severity": "CRITICAL", "pattern": "selfdestruct", "description": "Contract contains selfdestruct — can be permanently destroyed"})
            if re.search(r'\bdelegatecall\b', source_code):
                source_vulns.append({"severity": "HIGH", "pattern": "delegatecall", "description": "Uses delegatecall — risk of storage collision or malicious logic injection"})
            if not re.search(r'ReentrancyGuard|nonReentrant', source_code):
                source_vulns.append({"severity": "MEDIUM", "pattern": "missing_reentrancy_guard", "description": "No ReentrancyGuard or nonReentrant modifier detected"})
            if re.search(r'\btx\.origin\b', source_code):
                source_vulns.append({"severity": "HIGH", "pattern": "tx.origin", "description": "Uses tx.origin for authorization — vulnerable to phishing attacks"})
            if re.search(r'approve\s*\(.*(?:type\s*\(\s*uint256\s*\)\s*\.max|0xf{64}|2\*\*256)', source_code):
                source_vulns.append({"severity": "MEDIUM", "pattern": "unlimited_approval", "description": "Contains unlimited token approval pattern"})
        elif not source_error:
            recommendations.append("Source code not available — contract may be unverified")

        # 4. Determine combined risk level
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        combined_level = severity_order.get(goplus_risk_level, 1)

        for vuln in source_vulns:
            sev = severity_order.get(vuln["severity"], 1)
            if sev > combined_level:
                combined_level = sev

        level_names = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW"}
        risk_level = level_names.get(combined_level, "LOW")

        # 5. Build recommendations
        if "HONEYPOT" in goplus_risks:
            recommendations.append("CRITICAL: Token detected as honeypot — do NOT interact")
        if "SELFDESTRUCT" in goplus_risks or any(v["pattern"] == "selfdestruct" for v in source_vulns):
            recommendations.append("CRITICAL: Contract can self-destruct — funds at risk")
        if not is_verified:
            recommendations.append("Contract source code is not verified — higher risk")
        if any(v["pattern"] == "delegatecall" for v in source_vulns):
            recommendations.append("Review delegatecall usage — ensure proxy implementation is safe")
        if any(v["pattern"] == "tx.origin" for v in source_vulns):
            recommendations.append("tx.origin used for auth — susceptible to phishing via intermediary contracts")

        result = {
            "risk_level": risk_level,
            "goplus_risks": goplus_risks,
            "source_vulnerabilities": source_vulns,
            "is_verified": is_verified,
            "contract_name": contract_name,
            "recommendations": recommendations,
        }

        if goplus_error:
            result["goplus_error"] = goplus_error
        if source_error:
            result["source_error"] = source_error

        return json.dumps(result)

    except Exception as e:
        logger.exception("analyze_contract_security error: %s", e)
        return json.dumps({"error": f"analyze_contract_security failed: {type(e).__name__}: {e}"})


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

registry.register(
    name="scan_token_security",
    toolset="web3",
    schema={
        "name": "scan_token_security",
        "description": "Scan a token contract for security risks using GoPlus API. Returns risk level, honeypot detection, tax rates, holder concentration, and other red flags.",
        "parameters": {
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "The token contract address to scan",
                },
                "chain_id": {
                    "type": "integer",
                    "description": "Chain ID (1=Ethereum, 56=BSC, 137=Polygon, 42161=Arbitrum, 8453=Base). Default: 1",
                    "default": 1,
                },
            },
            "required": ["token_address"],
        },
    },
    handler=lambda args, **kw: _scan_token_security(args, **kw),
    check_fn=lambda: True,
    is_async=False,
)

registry.register(
    name="check_address_risk",
    toolset="web3",
    schema={
        "name": "check_address_risk",
        "description": "Check if a wallet or contract address is associated with malicious activity using GoPlus API. Detects phishing, money laundering, sanctions, and other risks.",
        "parameters": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "The wallet or contract address to check",
                },
            },
            "required": ["address"],
        },
    },
    handler=lambda args, **kw: _check_address_risk(args, **kw),
    check_fn=lambda: True,
    is_async=False,
)

registry.register(
    name="get_contract_source",
    toolset="web3",
    schema={
        "name": "get_contract_source",
        "description": "Fetch verified contract source code from Etherscan-compatible block explorers. Supports Ethereum, Polygon, Arbitrum, Base, and BSC.",
        "parameters": {
            "type": "object",
            "properties": {
                "contract_address": {
                    "type": "string",
                    "description": "The contract address to fetch source for",
                },
                "chain": {
                    "type": "string",
                    "description": "Chain name: ethereum, polygon, arbitrum, base, bsc. Default: ethereum",
                    "default": "ethereum",
                    "enum": ["ethereum", "polygon", "arbitrum", "base", "bsc"],
                },
            },
            "required": ["contract_address"],
        },
    },
    handler=lambda args, **kw: _get_contract_source(args, **kw),
    check_fn=lambda: True,
    requires_env=["ETHERSCAN_API_KEY"],
    is_async=False,
)

registry.register(
    name="analyze_contract_security",
    toolset="web3",
    schema={
        "name": "analyze_contract_security",
        "description": "Comprehensive security analysis combining GoPlus token scanning with source code vulnerability detection. Checks for selfdestruct, delegatecall, reentrancy guards, tx.origin abuse, and unlimited approvals.",
        "parameters": {
            "type": "object",
            "properties": {
                "contract_address": {
                    "type": "string",
                    "description": "The contract address to analyze",
                },
                "chain": {
                    "type": "string",
                    "description": "Chain name: ethereum, polygon, arbitrum, base, bsc. Default: ethereum",
                    "default": "ethereum",
                    "enum": ["ethereum", "polygon", "arbitrum", "base", "bsc"],
                },
            },
            "required": ["contract_address"],
        },
    },
    handler=lambda args, **kw: _analyze_contract_security(args, **kw),
    check_fn=lambda: True,
    requires_env=["ETHERSCAN_API_KEY"],
    is_async=False,
)
