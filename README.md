# sports-betting-mcp

**The first MCP server for sports betting.** Give any AI agent live access to picks, odds, game analysis, and performance tracking across NBA, NHL, NCAAB, and MLB.

![Status](https://img.shields.io/badge/status-active-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![PyPI](https://img.shields.io/pypi/v/sports-betting-mcp)
![License](https://img.shields.io/github/license/seang1121/sports-betting-mcp)
![MCP](https://img.shields.io/badge/protocol-MCP-purple)
![Sports](https://img.shields.io/badge/sports-NBA%20%7C%20NHL%20%7C%20NCAAB%20%7C%20MLB-orange)

```
mcp-name: io.github.seang1121/sports-betting-mcp
```

---

## What It Does

Connects any MCP-compatible AI agent to a live sports betting analysis system. Every pick is logged before tip-off and resolved against final scores. Nothing is cherry-picked.

| Metric | Value |
|--------|-------|
| **Sports Covered** | NBA, NHL, NCAAB, MLB |
| **Bet Types** | Moneyline, Spread, Totals |
| **Pick Source** | 12-agent consensus model |
| **Tools** | 11 MCP tools |
| **Auth** | API key (X-API-Key header) |

All results are queryable in real-time. Ask your AI agent to pull the latest numbers -- they update after every game.

---

## Quick Start

### Install

```bash
pip install sports-betting-mcp
```

### Add to Your MCP Client

Drop this into your MCP config (Claude Desktop, Cursor, Windsurf, Claude Code, etc.):

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

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SPORTS_BETTING_API_KEY` | Yes | Your API key for authentication |
| `SPORTS_BETTING_API_URL` | No | API base URL (defaults to `http://localhost:5000`) |

---

## Works With

Any client that supports the [Model Context Protocol](https://modelcontextprotocol.io):

| Client | Status |
|--------|--------|
| **Claude Desktop** | Fully supported |
| **Cursor** | Fully supported |
| **Windsurf** | Fully supported |
| **Claude Code (CLI)** | Fully supported |
| **Any MCP Client** | Fully supported via stdio transport |

---

## Available Tools

11 tools. Every call returns structured data that AI agents can reason over, display, or act on.

### Picks & Analysis

| Tool | What It Does |
|------|-------------|
| `get_todays_picks` | All AI picks with confidence scores and edge breakdowns, filterable by sport |
| `get_top_pick` | Single highest-confidence pick of the day |
| `get_pending_picks` | Currently unresolved picks that are still in play |
| `get_completed_picks` | Recently resolved picks with W/L results -- verify the track record |
| `analyze_game` | Full 12-agent analysis on any game: consensus pick + edge breakdown |

### Odds & Market Data

| Tool | What It Does |
|------|-------------|
| `get_live_odds` | Live moneyline, spread, and totals for today's games |
| `get_alerts` | Active alerts from the multi-agent system (line moves, injury impacts) |

### Performance & Stats

| Tool | What It Does |
|------|-------------|
| `get_win_rate` | Win rate with breakdown by sport and bet type |
| `get_model_stats` | Model performance: total picks, last-20 win rate, confidence tier breakdown |
| `get_leaderboard` | User rankings by win rate |
| `get_system_status` | Health check -- uptime, database, scheduler status |

---

## How the Analysis Works

Each game runs through a multi-agent pipeline:

1. **12 specialized agents** evaluate the game independently -- covering momentum, matchups, injuries, rest, travel, public betting percentages, sharp money indicators, historical trends, and more.
2. **A consensus engine** synthesizes all 12 opinions into a single pick with a confidence score.
3. **Edge calculation** compares the model's implied probability against the current market line.
4. **Picks are logged** before tip-off and resolved against final scores. No retroactive edits.

The confidence score and edge breakdown are included in every pick response, so your AI agent can filter, rank, or explain the reasoning behind any recommendation.

---

## API Authentication

The server authenticates using the `X-API-Key` header. All tool calls go through authenticated endpoints -- no session cookies or browser login required.

**Endpoint map** (what each tool calls under the hood):

| Tool | Endpoint | Method |
|------|----------|--------|
| `get_todays_picks` | `/api/picks/ai-today` | GET |
| `get_top_pick` | `/api/picks/ai-today` | GET |
| `get_live_odds` | `/api/odds/{sport}` | GET |
| `get_win_rate` | `/api/stats/performance` | GET |
| `get_pending_picks` | `/api/picks/pending` | GET |
| `get_completed_picks` | `/api/picks/completed` | GET |
| `get_model_stats` | `/api/stats/model` | GET |
| `analyze_game` | `/api/analyze` | POST |
| `get_system_status` | `/api/health` | GET |
| `get_alerts` | `/api/alerts` | GET |
| `get_leaderboard` | `/api/leaderboard` | GET |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Runtime** | Python 3.10+ |
| **Protocol** | MCP (Model Context Protocol) |
| **Transport** | stdio |
| **Build** | Hatchling |
| **Distribution** | PyPI (`sports-betting-mcp`) |
| **Backend** | Flask + SQLite |
| **Analysis** | 12-agent consensus pipeline |

---

## Related Projects

- **[March Madness Bracket Predictor](https://github.com/seang1121/ncaab-MarchMadness-Trend-analysis)** -- 5-model ensemble, 14-year backtest, 77% accuracy
- **[Multi-Lender Mortgage Rate Lookup](https://github.com/seang1121/Multi-Lender-Mortgage-Rate-Lookup)** -- One command, 10 lenders, sorted best to worst
- **[Agent Command Center](https://github.com/seang1121/acc-agent-command-center)** -- Dashboard that auto-discovers MCP servers, agents, hooks, cron jobs, and repos

## License

[MIT](./LICENSE)
