# sports-betting-mcp

Published MCP server for AI-powered sports betting analysis -- NBA, NHL, NCAAB.

![Status](https://img.shields.io/badge/status-active-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![PyPI](https://img.shields.io/pypi/v/sports-betting-mcp)
![License](https://img.shields.io/github/license/seang1121/sports-betting-mcp)

mcp-name: `io.github.seang1121/sports-betting-mcp`

## What It Does

The first MCP server for AI-powered sports betting analysis. Gives Claude and other AI agents live access to sports betting intelligence -- picks, odds, injuries, line movement, win rates, and visual bet slip cards. Backed by real data: 1,353+ resolved picks with a 59.6% documented win rate across NBA, NHL, and NCAAB.

## Features

- **9 MCP Tools** -- picks, odds, injuries, line movement, game analysis, and more
- **Visual Bet Slip Cards** -- rich images rendered directly in Claude chat
- **Multi-Sport Coverage** -- NBA, NHL, NCAAB
- **Live Odds** -- moneyline, spread, and totals from FanDuel/BetMGM
- **12-Agent Game Analysis** -- consensus pick with edge breakdown
- **Documented Track Record** -- 1,353+ resolved picks, 59.6% win rate

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Runtime** | Python 3.10+ |
| **Protocol** | MCP (Model Context Protocol) |
| **Build** | Hatchling |
| **Distribution** | PyPI (`sports-betting-mcp`) |

## Quick Start

```bash
pip install sports-betting-mcp
```

Set credentials and run:

```bash
export SPORTS_BETTING_API_URL=https://sportsbettingaianalyzer.com
export SPORTS_BETTING_API_KEY=your_api_key
sports-betting-mcp
```

### Claude Desktop / Claude Code Setup

Add to your MCP config:

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

## Available Tools

| Tool | Description |
|------|-------------|
| `get_top_pick` | Highest-confidence pick of the day with visual bet slip image |
| `get_todays_picks` | All AI picks with confidence, edges, and bet slip cards per sport |
| `get_live_odds` | Live moneyline, spread, and totals from FanDuel/BetMGM |
| `get_win_rate` | Documented win rate with full record breakdown |
| `get_pending_picks` | Currently unresolved logged picks |
| `get_injury_report` | Active injuries affecting today's lines |
| `get_line_movement` | Significant line shifts since market open |
| `analyze_game` | Full 12-agent analysis on a specific game -- consensus pick + edge breakdown |
| `get_system_status` | Health check -- uptime, DB status, scheduler health |

## Get Your API Key

Free access at [sportsbettingaianalyzer.com/account/api-keys](https://sportsbettingaianalyzer.com/account/api-keys)

## Requirements

- Python 3.10+
- A free API key from [sportsbettingaianalyzer.com](https://sportsbettingaianalyzer.com)

## License

[MIT](./LICENSE)
