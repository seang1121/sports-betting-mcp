# sports-betting-mcp

**MCP server exposing AI-powered sports betting predictions, live odds, and analysis tools to AI agents.**

![Status](https://img.shields.io/badge/status-active-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![PyPI](https://img.shields.io/pypi/v/sports-betting-mcp)

mcp-name: `io.github.seang1121/sports-betting-mcp`

Give AI agents live access to sports betting intelligence -- picks, odds, injuries, line movement, win rates, and visual bet slip cards. Backed by real data: 1,353+ resolved picks with a 59.6% documented win rate across NBA, NHL, and NCAAB.

## What It Does

An MCP (Model Context Protocol) server that connects AI assistants to a production sports betting analyzer. Agents can query today's top picks, pull live odds from FanDuel/BetMGM, check injury reports, and track line movement -- all through structured tool calls that return data and visual bet slip images.

## Features

- **7 MCP tools** -- top pick, daily picks, live odds, win rate, pending picks, injury report, line movement
- **Visual bet slip cards** -- rich images rendered directly in chat showing pick analysis, key stats, and edges
- **Live odds** -- moneyline, spread, and totals from major sportsbooks
- **AI predictions** -- confidence scores, probability edges, and full analysis per pick
- **Injury tracking** -- active injuries affecting today's lines
- **Line movement** -- significant shifts since market open

## Tech Stack

- **Python 3.10+** with MCP SDK (`mcp>=1.0.0`)
- **Hatchling** build system
- **MCP Protocol** for AI agent integration

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

### MCP Client Setup

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

## Available Tools (9)

| Tool | Description |
|------|-------------|
| `get_top_pick` | Highest-confidence pick of the day with visual bet slip image |
| `get_todays_picks` | All AI picks with confidence, edges, and bet slip cards per sport |
| `get_live_odds` | Live moneyline, spread, and totals from FanDuel/BetMGM |
| `get_win_rate` | Documented win rate with full record breakdown |
| `get_pending_picks` | Currently unresolved logged picks |
| `get_injury_report` | Active injuries affecting today's lines |
| `get_line_movement` | Significant line shifts since market open |
| `analyze_game` | Full 12-agent analysis on a specific game — consensus pick + edge breakdown |
| `get_system_status` | Health check — uptime, DB status, scheduler health |

## Get Your API Key

Free access at [sportsbettingaianalyzer.com/account/api-keys](https://sportsbettingaianalyzer.com/account/api-keys)

## License

MIT
