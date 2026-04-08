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
| **Total Picks** | 3,859+ resolved |
| **Platform Users** | 30 |
| **Tools** | 12 MCP tools |
| **Auth** | API key (X-API-Key header) |

### Results by Sport

| Sport | Picks | Wins | Win Rate |
|-------|-------|------|----------|
| **NBA** | 1,267 | 762 | **60.1%** |
| **NHL** | 1,148 | 656 | **57.1%** |
| **NCAAB** | 1,149 | 549 | 47.8% |
| **MLB** | 283 | 109 | 38.5% *(launched Apr 2026)* |

All results are queryable in real-time via the `get_win_rate` tool. Numbers update after every game.

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

12 tools. Every call returns structured data that AI agents can reason over, display, or act on.

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

## Full API — 22 Endpoints

The API has two tiers: **Free** (any API key) and **Pro** (approved access).

### Free Tier (available to all API key holders)

| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/xk/p` | GET | Today's AI picks with confidence scores |
| `/xk/o/{sport}` | GET | Live odds from FanDuel/BetMGM |
| `/xk/w` | GET | Win rate breakdown by sport and bet type |
| `/xk/i` | GET | Active injury report from Covers.com |
| `/xk/m` | GET | Significant line movement (sharp money signals) |
| `/xk/games` | GET | Today's full schedule with odds snapshot and AI pick flags |
| `/xk/stats` | GET | Model performance by sport, bet type, confidence tier |
| `/xk/lb` | GET | Leaderboard — AI vs human win rates |
| `/xk/news` | GET | Sports news feed from RSS sources |
| `/xk/q` | GET | Currently pending (unresolved) picks |

### Pro Tier (requires approved access)

| Endpoint | Method | What It Does |
|----------|--------|-------------|
| `/xk/full` | GET | Full structured picks — complete edge breakdowns, positive/negative edges, reasoning, scorecard, opposing side with odds, line movement, quality flags |
| `/xk/analyze` | POST | On-demand 12-agent analysis for any game — send team names, get full consensus |
| `/xk/results` | GET | Resolved picks with W/L, actual scores, profit, top contributing edges |
| `/xk/clv` | GET | Closing Line Value analysis — did the line move in our favor? |
| `/xk/search` | GET | Search all picks by team name with W/L record |
| `/xk/log` | POST | Log a pick (supports flip flag, pick source tracking) |
| `/xk/log/batch` | POST | Batch log up to 20 picks with per-pick success/duplicate/error status |
| `/xk/history` | GET | Your pick history — pending, resolved, win rate |
| `/xk/slip` | POST | Generate Nimrod bet slip image |
| `/xk/webhook` | POST/GET/DELETE | Register webhooks for pick events |
| `/xk/full` | GET | Includes fade/flip data for every pick — opposing side, line, odds |

### Pro Pick Payload

Every pick from `/xk/full` includes:

```json
{
  "ai_pick": "Lakers -5.5",
  "ai_verdict": "STRONG BET",
  "ai_probability": "65%",
  "ai_reasoning": "Lakers defense ranks top 5, opponent on B2B...",
  "edges": [13 individual edge factors],
  "top_edges": [top 5 positive],
  "negative_edges": [top 3 negative],
  "scorecard": [3 model scores],
  "fade_pick": "Celtics +5.5",
  "fade_team": "Celtics",
  "fade_odds": "+105",
  "fade_note": "Betting AGAINST the AI — take Celtics +5.5",
  "line_moved": true,
  "flags": ["line_moved"],
  "data_quality": "good"
}
```

### Pick Source Tracking (for learning)

When logging picks, include `pick_source` to track decision types:
- `model_agree` — following the AI's pick
- `flip` — fading/betting against the AI
- `manual_override` — custom pick

This enables win rate comparison between model-agree vs flip picks over time.

---

## API Authentication

Authenticate with `X-API-Key` header. Get a free key at [sportsbettingaianalyzer.com](https://sportsbettingaianalyzer.com). Pro access requires admin approval.

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
| **Sports** | NBA, NHL, NCAAB, MLB |

---

## Related Projects

- **[Mortgage Rates MCP Server](https://github.com/seang1121/mortgage-rates-mcp)** -- 17 lenders, 13 tools, real-time mortgage rate intelligence
- **[March Madness Bracket Predictor](https://github.com/seang1121/ncaab-MarchMadness-Trend-analysis)** -- 5-model ensemble, 14-year backtest, 77% accuracy, correctly predicted 2026 champion
- **[Agent Command Center](https://github.com/seang1121/acc-agent-command-center)** -- Dashboard that auto-discovers MCP servers, agents, hooks, cron jobs, and repos

## License

[MIT](./LICENSE)
