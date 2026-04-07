"""
sports-betting-mcp — MCP server for AI-powered sports betting analysis
Backed by real data: 1,353+ resolved picks, 59.6% win rate
"""

import base64
import os
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional
from mcp.server.fastmcp import FastMCP, Image

BASE_URL = os.environ.get("SPORTS_BETTING_API_URL", "http://localhost:5000")
API_KEY = os.environ.get("SPORTS_BETTING_API_KEY", "")

mcp = FastMCP(
    "sports-betting-mcp",
    instructions=(
        "AI-powered sports betting analysis server. "
        "Provides picks, odds, win rates, injury data, and line movement "
        "from a live betting analyzer with 1,353+ resolved picks and a 59.6% win rate. "
        "Supports NBA, NHL, and NCAAB. Always check win rate and injuries before placing picks."
    )
)

# ── API request helper ────────────────────────────────────────────────────────

def _api_get(path: str, params: Optional[dict] = None) -> dict:
    """Authenticated GET request using X-API-Key header."""
    if not API_KEY:
        raise RuntimeError(
            "Set SPORTS_BETTING_API_KEY environment variable. "
            "Get your key at https://sportsbettingaianalyzer.com/account/api-keys"
        )

    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, headers={"X-API-Key": API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RuntimeError(
                "Free tier rate limit reached (10 req/day). "
                "Upgrade to Pro at https://sportsbettingaianalyzer.com/pricing"
            )
        if e.code == 401:
            raise RuntimeError("Invalid API key. Check SPORTS_BETTING_API_KEY.")
        body = e.read().decode()
        raise RuntimeError(f"API error {e.code}: {body[:200]}") from e


def _api_post(path: str, body: dict) -> dict:
    """Authenticated POST request using X-API-Key header."""
    if not API_KEY:
        raise RuntimeError(
            "Set SPORTS_BETTING_API_KEY environment variable. "
            "Get your key at https://sportsbettingaianalyzer.com/account/api-keys"
        )
    url = f"{BASE_URL}{path}"
    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        raise RuntimeError(f"API error {e.code}: {body_text[:200]}") from e


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_todays_picks(sport: str = "all") -> list:
    """
    Get today's AI-generated picks with confidence and edge scores.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', or 'all' (default)

    Returns:
        List of picks with pick name, bet type, line, odds, confidence, and edge score.
    """
    try:
        data = _api_get("/api/picks/ai-today")
        # ai-today returns {success, pending_picks, finished_picks}
        pending = data.get("pending_picks", [])
        finished = data.get("finished_picks", [])
        picks = pending + finished

        # Filter by sport if specified
        if sport.lower() != "all":
            picks = [p for p in picks if (p.get("sport") or "").upper() == sport.upper()]

        if not picks:
            return [f"No picks available for {sport} today."]

        lines = [f"TODAY'S AI PICKS ({sport.upper() if sport != 'all' else 'ALL SPORTS'})\n"]
        for p in picks[:20]:
            confidence = p.get("confidence", "?")
            edge = p.get("edge_score") or p.get("edge", "?")
            bet_type = (p.get("bet_type") or "?").upper()
            line = p.get("line_value") or p.get("line") or ""
            odds = p.get("odds", "")
            pick_name = p.get("pick_name") or p.get("team") or "?"
            sport_tag = (p.get("sport") or "").upper()

            line_str = f" {line}" if line else ""
            odds_str = f" ({odds})" if odds else ""
            edge_str = f" | edge: {edge}" if edge and edge != "?" else ""
            lines.append(
                f"  [{sport_tag}] {pick_name} {bet_type}{line_str}{odds_str} — {confidence} confidence{edge_str}"
            )

        lines.append("\n---\nPowered by sportsbettingaianalyzer.com — free access, real AI picks.")
        return ["\n".join(lines)]
    except Exception as e:
        return [f"Error fetching picks: {e}"]


@mcp.tool()
def get_top_pick(sport: str = "all") -> list:
    """
    Get the single highest-confidence pick available today.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', or 'all' (default)

    Returns:
        The best pick with full analysis details.
    """
    try:
        data = _api_get("/api/picks/ai-today")
        pending = data.get("pending_picks", [])
        picks = pending  # Only pending (unresolved) picks

        if sport.lower() != "all":
            picks = [p for p in picks if (p.get("sport") or "").upper() == sport.upper()]

        if not picks:
            return ["No picks available today."]

        # Sort by confidence tier then edge score
        confidence_order = {"high": 0, "medium": 1, "low": 2}
        def sort_key(p):
            conf = confidence_order.get((p.get("confidence") or "low").lower(), 2)
            edge = float(p.get("edge_score") or p.get("edge") or 0)
            return (conf, -edge)

        best = sorted(picks, key=sort_key)[0]
        pick_name = best.get("pick_name") or best.get("team") or "?"
        sport_tag = (best.get("sport") or "?").upper()

        lines = [
            "TOP PICK TODAY",
            f"  Pick:       {pick_name}",
            f"  Sport:      {sport_tag}",
            f"  Bet Type:   {(best.get('bet_type') or '?').upper()}",
            f"  Line:       {best.get('line_value') or best.get('line') or 'N/A'}",
            f"  Odds:       {best.get('odds') or 'N/A'}",
            f"  Confidence: {best.get('confidence') or '?'}",
            f"  Edge Score: {best.get('edge_score') or best.get('edge') or 'N/A'}",
            f"  Game:       {best.get('game') or 'N/A'}",
            "\nFree picks at sportsbettingaianalyzer.com",
        ]
        return ["\n".join(lines)]
    except Exception as e:
        return [f"Error fetching top pick: {e}"]


@mcp.tool()
def get_live_odds(sport: str) -> str:
    """
    Get current live odds for a sport from FanDuel and BetMGM.

    Args:
        sport: Sport to fetch — 'nba', 'nhl', or 'ncaab'

    Returns:
        Live moneyline, spread, and total odds for today's games.
    """
    if sport.lower() not in ("nba", "nhl", "ncaab"):
        return "Invalid sport. Use: nba, nhl, or ncaab"

    try:
        data = _api_get(f"/api/odds/{sport.upper()}")
        games = data.get("data", [])

        if not games:
            return f"No live odds available for {sport.upper()} right now."

        lines = [f"LIVE ODDS — {sport.upper()}\n"]
        for g in games[:15]:
            home = g.get("home_team") or g.get("home") or "?"
            away = g.get("away_team") or g.get("away") or "?"
            ml_home = g.get("home_ml") or g.get("moneyline_home") or "N/A"
            ml_away = g.get("away_ml") or g.get("moneyline_away") or "N/A"
            spread = g.get("spread") or g.get("home_spread") or "N/A"
            total = g.get("total") or g.get("over_under") or "N/A"
            game_time = g.get("commence_time") or g.get("game_time") or ""
            time_str = f" @ {game_time[:16]}" if game_time else ""

            lines.append(f"  {away} @ {home}{time_str}")
            lines.append(f"    ML: {away} {ml_away} / {home} {ml_home}")
            lines.append(f"    Spread: {spread} | Total: {total}")
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching odds: {e}"


@mcp.tool()
def get_win_rate(period: str = "all") -> str:
    """
    Get the betting analyzer's documented win rate with real resolved picks.

    Args:
        period: Time period — 'all', '30d', or '90d'

    Returns:
        Win rate, record, and breakdown by sport.
    """
    try:
        data = _api_get("/api/stats/performance")
        if not data:
            return "Analytics data not available."

        recent_picks = data.get("recent_picks", 0)
        by_bet_type = data.get("by_bet_type", {})
        by_sport = data.get("by_sport", {})

        lines = [
            "BETTING ANALYZER WIN RATES",
            f"  Recent picks tracked: {recent_picks}",
        ]

        if by_sport:
            lines.append("\n  By Sport:")
            for sport, stats in by_sport.items():
                s_wins = stats.get("wins", 0)
                s_total = stats.get("total", 0)
                s_pct = round(s_wins / s_total * 100, 1) if s_total > 0 else 0
                lines.append(f"    {sport.upper()}: {s_wins}W / {s_total - s_wins}L ({s_pct}%)")

        if by_bet_type:
            lines.append("\n  By Bet Type:")
            for bt, stats in by_bet_type.items():
                bt_wins = stats.get("wins", 0)
                bt_total = stats.get("total", 0)
                bt_pct = round(bt_wins / bt_total * 100, 1) if bt_total > 0 else 0
                lines.append(f"    {bt.upper()}: {bt_wins}W / {bt_total - bt_wins}L ({bt_pct}%)")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching analytics: {e}"


@mcp.tool()
def get_pending_picks() -> str:
    """
    Get all currently unresolved (pending) picks waiting for game results.

    Returns:
        List of pending picks with pick details and how long they've been pending.
    """
    try:
        data = _api_get("/api/picks/pending")
        picks = data.get("picks", [])

        if not picks:
            return "No pending picks — all picks are resolved."

        lines = [f"PENDING PICKS ({len(picks)} total)\n"]
        for p in picks[:25]:
            sport = (p.get("sport") or "?").upper()
            pick_name = p.get("pick_name") or "?"
            bet_type = (p.get("bet_type") or "?").upper()
            line = p.get("line_value") or ""
            created = p.get("created_at") or p.get("logged_at") or ""
            created_str = f" (logged {created[:10]})" if created else ""

            line_str = f" {line}" if line else ""
            lines.append(f"  [{sport}] {pick_name} {bet_type}{line_str}{created_str}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching pending picks: {e}"


@mcp.tool()
def get_completed_picks(limit: int = 20) -> str:
    """
    Get recently completed (resolved) picks with results.

    Args:
        limit: Number of recent completed picks to return (default 20, max 50)

    Returns:
        List of completed picks with results (W/L) and details.
    """
    try:
        data = _api_get("/api/picks/completed")
        picks = data.get("picks", [])

        if not picks:
            return "No completed picks found."

        # Take most recent N
        picks = picks[-min(limit, 50):]
        picks.reverse()

        wins = sum(1 for p in picks if p.get("result") in ("W", "WIN"))
        losses = sum(1 for p in picks if p.get("result") in ("L", "LOSS"))

        lines = [f"COMPLETED PICKS (showing {len(picks)}, {wins}W-{losses}L)\n"]
        for p in picks:
            sport = (p.get("sport") or "?").upper()
            pick_name = p.get("pick_name") or "?"
            bet_type = (p.get("bet_type") or "?").upper()
            result = p.get("result", "?")
            icon = "W" if result in ("W", "WIN") else "L" if result in ("L", "LOSS") else result
            lines.append(f"  [{sport}] {pick_name} {bet_type} — {icon}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching completed picks: {e}"


@mcp.tool()
def get_model_stats() -> str:
    """
    Get model performance statistics — win rates by confidence level, total picks, discipline.

    Returns:
        Model stats including total picks, last 20 win rate, and confidence tier breakdown.
    """
    try:
        data = _api_get("/api/stats/model")
        stats = data.get("stats", {})

        if not stats:
            return "Model stats not available."

        lines = [
            "MODEL STATISTICS",
            f"  Total picks: {stats.get('total_picks', 0)}",
            f"  Last 20 win rate: {stats.get('last_20_win_rate', 'N/A')}%",
            f"  Discipline score: {stats.get('discipline_score', 'N/A')}",
        ]

        confidence = stats.get("confidence_stats", {})
        if confidence:
            lines.append("\n  By Confidence:")
            for level in ("high", "medium", "low"):
                tier = confidence.get(level, {})
                lines.append(
                    f"    {level.title()}: {tier.get('wins', 0)}W / "
                    f"{tier.get('total', 0)} total ({tier.get('win_rate', 0)}%)"
                )

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching model stats: {e}"


@mcp.tool()
def analyze_game(sport: str, game_id: str) -> str:
    """
    Run full multi-agent analysis on a specific game.
    Uses 12 specialized agents to evaluate every angle.

    Args:
        sport: Sport — 'nba', 'nhl', or 'ncaab'
        game_id: Game ID from the get_live_odds tool

    Returns:
        Complete multi-agent analysis with consensus pick, confidence, and edge breakdown.
    """
    if sport.lower() not in ("nba", "nhl", "ncaab"):
        return "Invalid sport. Use: nba, nhl, or ncaab"

    try:
        data = _api_post("/api/analyze", {"sport": sport.upper(), "game_id": game_id})

        if not data.get("success", True):
            return f"Analysis failed: {data.get('error', 'Unknown error')}"

        lines = [f"FULL GAME ANALYSIS — {sport.upper()}\n"]

        pick = data.get("pick") or data.get("recommendation") or {}
        if pick:
            lines.append(f"  Pick:       {pick.get('pick_name', 'N/A')}")
            lines.append(f"  Bet Type:   {pick.get('bet_type', 'N/A')}")
            lines.append(f"  Confidence: {pick.get('confidence', 'N/A')}")
            lines.append(f"  Edge Score: {pick.get('edge_score', 'N/A')}")

        analysis = data.get("analysis") or data.get("details") or ""
        if analysis:
            lines.append(f"\n{analysis[:1500]}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error analyzing game: {e}"


@mcp.tool()
def get_system_status() -> str:
    """
    Health check — uptime, database status, API key status, and scheduler health.

    Returns:
        Current system status including uptime, DB connectivity, and service health.
    """
    try:
        data = _api_get("/api/health")

        lines = ["SYSTEM STATUS\n"]
        lines.append(f"  Status:   {data.get('status', 'unknown')}")
        lines.append(f"  Uptime:   {data.get('uptime', 'N/A')}")
        lines.append(f"  Database: {data.get('database', 'N/A')}")

        schedulers = data.get("schedulers") or {}
        if schedulers:
            lines.append("\n  Schedulers:")
            for name, status in schedulers.items():
                icon = "OK" if status in ("success", "ok", True) else "FAIL"
                lines.append(f"    {name}: {icon}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error checking status: {e}"


@mcp.tool()
def get_alerts() -> str:
    """
    Get active alerts from the multi-agent system (line movements, injury impacts, etc.).

    Returns:
        List of current alerts with severity and details.
    """
    try:
        data = _api_get("/api/alerts")
        alerts = data.get("alerts", [])

        if not alerts:
            return "No active alerts."

        lines = [f"ACTIVE ALERTS ({len(alerts)})\n"]
        for a in alerts[:20]:
            alert_type = a.get("alert_type", "?")
            message = a.get("message", "?")
            severity = a.get("severity", "info").upper()
            created = (a.get("created_at") or "")[:16]
            lines.append(f"  [{severity}] {alert_type}: {message} ({created})")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching alerts: {e}"


@mcp.tool()
def get_leaderboard() -> str:
    """
    Get the pick leaderboard showing user rankings by win rate.

    Returns:
        Leaderboard with rankings, win rates, and total picks per user.
    """
    try:
        data = _api_get("/api/leaderboard")
        users = data.get("leaderboard", [])

        if not users:
            return "No leaderboard data available."

        lines = ["LEADERBOARD\n"]
        for i, u in enumerate(users[:15], 1):
            name = u.get("username", "?")
            wins = u.get("wins", 0)
            total = u.get("total_picks", 0)
            pct = u.get("win_rate", 0)
            lines.append(f"  #{i} {name}: {wins}W / {total} picks ({pct}%)")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching leaderboard: {e}"
