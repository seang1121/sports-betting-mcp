# sports-betting-mcp

The first MCP server for AI-powered sports betting analysis.

**Backed by real data: 1,353+ resolved picks | 59.6% documented win rate | NBA, NHL, NCAAB**

Use this MCP server to give Claude and other AI agents live access to sports betting intelligence — picks, odds, injuries, line movement, and win rates.

## Install

```bash
pip install sports-betting-mcp
```

## Quick Start

```bash
# Set credentials
export SPORTS_BETTING_API_URL=https://sportsbettingaianalyzer.com
export SPORTS_BETTING_API_KEY=your_api_key

# Run server
sports-betting-mcp
```

## Claude Desktop / Claude Code Setup

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
| `get_todays_picks` | AI-generated picks for today with confidence and edge scores |
| `get_top_pick` | Single highest-confidence pick of the day |
| `get_live_odds` | Live moneyline, spread, and totals from FanDuel/BetMGM |
| `get_win_rate` | Documented win rate with full record breakdown |
| `get_pending_picks` | Currently unresolved logged picks |
| `get_injury_report` | Active injuries affecting today's lines |
| `get_line_movement` | Significant line shifts since market open |

## Requirements

- Python 3.10+
- An API key from [sportsbettingaianalyzer.com/account/api-keys](https://sportsbettingaianalyzer.com/account/api-keys)
