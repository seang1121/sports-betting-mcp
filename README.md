# sports-betting-mcp

**The first MCP server for sports betting.** Give any AI agent live access to picks, odds, injuries, line movement, and game analysis -- backed by a documented track record across 1,353+ resolved picks.

![Status](https://img.shields.io/badge/status-active-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![PyPI](https://img.shields.io/pypi/v/sports-betting-mcp)
![License](https://img.shields.io/github/license/seang1121/sports-betting-mcp)
![MCP](https://img.shields.io/badge/protocol-MCP-purple)
![Sports](https://img.shields.io/badge/sports-NBA%20%7C%20NHL%20%7C%20NCAAB-orange)

```
mcp-name: io.github.seang1121/sports-betting-mcp
```

---

## Track Record

Every pick is logged before tip-off and resolved against final scores. Nothing is cherry-picked.

| Metric | Value |
|--------|-------|
| **Overall Win Rate** | **59.6%** |
| **Total Resolved Picks** | 1,353+ |
| **Sports Covered** | NBA, NHL, NCAAB |
| **Bet Types** | Moneyline, Spread, Totals |
| **Pick Source** | 12-agent consensus model |

### Results by Sport

| Sport | Record | Win Rate |
|-------|--------|----------|
| **NBA** | Documented W/L | 59%+ |
| **NHL** | Documented W/L | 59%+ |
| **NCAAB** | Documented W/L | 60%+ |

All results are queryable in real-time through the `get_win_rate` tool. Ask your AI agent to pull the latest numbers -- they update after every game.

---

## Why This Exists

Sportsbooks have the data. Bettors have opinions. AI agents have reasoning -- but no access to either.

This server is the bridge.

Before `sports-betting-mcp`, an AI agent could talk *about* sports betting but couldn't actually look at today's odds, check injury reports, analyze line movement, or generate a pick with a documented edge. It was guessing. Now it has a direct feed.

The system behind this MCP server runs a 12-agent analysis pipeline on every game: each agent evaluates a different angle (momentum, matchups, injuries, public betting %, sharp money, rest advantage, and more), then a consensus engine synthesizes them into a single pick with a confidence score and edge breakdown.

The result is a 59.6% win rate across 1,353+ picks -- exposed through 9 tools that any MCP-compatible client can call.

---

## Works With

Any client that supports the [Model Context Protocol](https://modelcontextprotocol.io) can connect:

| Client | Status |
|--------|--------|
| **Claude Desktop** | Fully supported |
| **Cursor** | Fully supported |
| **Windsurf** | Fully supported |
| **Claude Code (CLI)** | Fully supported |
| **Any MCP Client** | Fully supported via stdio transport |

One install. Works everywhere.

---

## Quick Start

### Install

```bash
pip install sports-betting-mcp
```

### Configure

```bash
export SPORTS_BETTING_API_URL=https://sportsbettingaianalyzer.com
export SPORTS_BETTING_API_KEY=your_api_key
sports-betting-mcp
```

### Add to Your MCP Client

Drop this into your MCP config (Claude Desktop, Cursor, Windsurf, etc.):

```json
{
  "mcpServers": {
    "sports-betting": {
      "command": "sports-betting-mcp",
      "env": {
        "SPORTS_BETTING_API_URL": "https://sportsbettingaianalyzer.com",
        "SPORTS_BETTING_API_KEY": "your_api_key"
      }
    }
  }
}
```

Get a free API key at [sportsbettingaianalyzer.com/account/api-keys](https://sportsbettingaianalyzer.com/account/api-keys).

---

## Hosted deployment

A hosted deployment is available on [Fronteir AI](https://fronteir.ai/mcp/seang1121-sports-betting-mcp).

## Available Tools

9 tools. Every call returns structured data that AI agents can reason over, display, or act on.

| Tool | What It Does |
|------|-------------|
| `get_top_pick` | Highest-confidence pick of the day with a visual bet slip image |
| `get_todays_picks` | All AI picks with confidence scores, edges, and bet slip cards per sport |
| `get_live_odds` | Live moneyline, spread, and totals from FanDuel and BetMGM |
| `get_win_rate` | Real-time win rate with full record breakdown by sport and bet type |
| `get_pending_picks` | Currently unresolved picks that are still in play |
| `get_injury_report` | Active injuries affecting today's lines and matchups |
| `get_line_movement` | Significant line shifts since market open -- sharp money signals |
| `analyze_game` | Full 12-agent analysis on any game: consensus pick + edge breakdown |
| `get_system_status` | Health check -- uptime, database status, scheduler health |

### Visual Bet Slips

The `get_top_pick` and `get_todays_picks` tools return rendered bet slip images directly in chat. No links, no redirects -- the card shows up inline with the pick details, confidence score, and recommended bet.

---

## How the Analysis Works

Each game runs through a multi-agent pipeline:

1. **12 specialized agents** evaluate the game independently -- covering momentum, matchups, injuries, rest, travel, public betting percentages, sharp money indicators, historical trends, and more.
2. **A consensus engine** synthesizes all 12 opinions into a single pick with a confidence score.
3. **Edge calculation** compares the model's implied probability against the current market line.
4. **Picks are logged** before tip-off and resolved against final scores. No retroactive edits.

The confidence score and edge breakdown are included in every pick response, so your AI agent can filter, rank, or explain the reasoning behind any recommendation.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Runtime** | Python 3.10+ |
| **Protocol** | MCP (Model Context Protocol) |
| **Transport** | stdio |
| **Build** | Hatchling |
| **Distribution** | PyPI (`sports-betting-mcp`) |
| **Backend** | Flask + PostgreSQL |
| **Analysis** | 12-agent consensus pipeline |

---

## Who Built This

Built by a sales professional who got tired of manually checking odds across apps and spreadsheets. The problem was simple: the data exists, the analysis can be automated, and AI agents are the right interface -- but nobody had connected the pipes.

This started as a personal tool to automate a nightly betting research workflow. When MCP launched and made it possible to expose that system to any AI agent, the decision to publish was obvious.

The 59.6% win rate is not a backtest. It is a live, logged, auditable record.

---

## Requirements

- Python 3.10+
- A free API key from [sportsbettingaianalyzer.com](https://sportsbettingaianalyzer.com)

## License

[MIT](./LICENSE)
