# sports-betting-mcp

mcp-name: io.github.seang1121/sports-betting-mcp

**The first MCP server for AI-powered sports betting analysis.**

**Backed by real data: 1,353+ resolved picks | 59.6% documented win rate | NBA, NHL, NCAAB**

Give Claude and other AI agents live access to sports betting intelligence — picks, odds, injuries, line movement, win rates, and visual bet slip cards.

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
| `get_top_pick` | Highest-confidence pick of the day — returns full analysis + **visual bet slip image** |
| `get_todays_picks` | All AI picks for today with confidence, edges, and **bet slip cards per sport** |
| `get_live_odds` | Live moneyline, spread, and totals from FanDuel/BetMGM |
| `get_win_rate` | Documented win rate with full record breakdown |
| `get_pending_picks` | Currently unresolved logged picks |
| `get_injury_report` | Active injuries affecting today's lines |
| `get_line_movement` | Significant line shifts since market open |

## Visual Bet Slip Cards

`get_top_pick` and `get_todays_picks` return rich visual bet slip images alongside the pick data — showing the pick name, probability, matchup, WHY THIS PICK analysis, key stats, and all supporting edges. Renders directly in Claude chat.

## Get Your API Key

Free access at [sportsbettingaianalyzer.com/account/api-keys](https://sportsbettingaianalyzer.com/account/api-keys)

## Requirements

- Python 3.10+
- A free API key from [sportsbettingaianalyzer.com](https://sportsbettingaianalyzer.com/account/api-keys)
