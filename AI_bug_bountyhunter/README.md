# AI Bug Bounty Hunter

**Version:** 1.0.0 (God Tier Prototype)

## Overview
AI Bug Bounty Hunter is a "Self-Healing" security tool that finds and fixes vulnerabilities automatically. It combines:
- **SAST (Regex & AST):** Finds secrets, SQLi, and dangerous functions.
- **Auto-Fixer:** Automatically patches code (SQLi to parameterized queries, Secrets to .env).
- **GUI Dashboard:** Interactive vulnerability management.

## Installation
You can install this tool directly from the source:

```bash
cd AI_bug_bountyhunter
pip install .
```

## Usage

### 1. CLI Mode
Scan and fix vulnerabilities in a directory:
```bash
ai-bug-hunter --scan-type sast --target ./tests --fix
```

### 2. GUI Mode
Launch the visual dashboard:
```bash
ai-bug-hunter-gui
```

## Features
- **Fixes SQL Injection:** Handles string concatenation and f-strings.
- **Fixes Secrets:** Moves hardcoded secrets to `.env`.
- **Fixes RCE:** Replaces `eval()` with `ast.literal_eval()`.
- **Hybrid Scanning:** Combines Regex speed with AST accuracy.

## Disclaimer
**EDUCATIONAL USE ONLY.** This tool is for authorized security testing and research.