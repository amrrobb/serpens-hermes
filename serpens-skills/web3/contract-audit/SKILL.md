---
name: contract-audit
description: "Audit smart contracts for security vulnerabilities. Use when user asks to audit, review, or analyze a contract address for security issues, vulnerabilities, or code quality."
version: 1.0.0
author: serpens
license: MIT
metadata:
  hermes:
    tags: [Web3, Security, Smart Contracts, Audit, Solidity]
---

# Smart Contract Security Auditor

Deep security analysis of smart contracts combining source code review, GoPlus intelligence, and vulnerability pattern detection.

## When to Use

- User asks to "audit this contract" or "check this contract"
- User provides a contract address and asks about security
- User mentions smart contract vulnerabilities or exploits
- User wants to verify if a contract is safe to interact with

## Procedure

1. **Analyze contract security** — Use `analyze_contract_security` tool with the contract address and chain
   - This tool internally:
     - Fetches source code from Etherscan (if verified)
     - Runs GoPlus security scan
     - Performs regex-based vulnerability detection on source code
   - Returns: risk_level, goplus_risks, source_vulnerabilities, is_verified, contract_name, recommendations

2. **If you want deeper analysis**, use `delegate_task` to spawn parallel subagents:
   - Subagent 1: "Analyze the GoPlus security data for contract {address} using scan_token_security and check_address_risk tools. Focus on ownership, proxy, and permission risks."
   - Subagent 2: "Get the contract source using get_contract_source tool for {address}. Analyze the code for reentrancy, access control, and economic vulnerabilities. Report specific function names and line patterns."
   - Subagent 3: "Analyze the transaction history of contract {address} using analyze_wallet tool. Look for suspicious patterns, large withdrawals, or unusual activity."

3. **Format audit report**:
```
SMART CONTRACT AUDIT
=====================
Contract: {name}
Address: {address}
Chain: {chain}
Verified: {yes/no}
Risk Level: {CRITICAL/HIGH/MEDIUM/LOW}

CRITICAL FINDINGS:
{severity-ranked vulnerabilities}

SOURCE CODE ANALYSIS:
{patterns detected with descriptions}

GOPLUS FLAGS:
{security flags from GoPlus}

ON-CHAIN ACTIVITY:
{transaction patterns if analyzed}

RECOMMENDATIONS:
{numbered list of actionable items}

DISCLAIMER: This is an automated analysis. A professional manual audit is recommended for contracts handling significant value.
```

4. **Save to memory** — Store key findings for future reference

5. **Suggest next steps** — "Want me to check the deployer's wallet?" or "Should I scan the tokens associated with this contract?"

## Pitfalls

- Not all contracts are verified on Etherscan. Unverified contracts get a reduced analysis.
- Source code analysis uses pattern matching, not formal verification. It catches common patterns but may miss novel vulnerabilities.
- Proxy contracts may have their logic in a separate implementation contract. If detected, suggest analyzing the implementation address too.
- ETHERSCAN_API_KEY must be set for source code retrieval.

## Verification

- Audit should always include both GoPlus data AND source analysis (when available)
- Each finding should have a severity level
- Recommendations should be specific and actionable
