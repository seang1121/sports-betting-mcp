"""
sports-betting-mcp — MCP server for AI-powered sports betting analysis
Backed by real data: 1,353+ resolved picks, 59.6% win rate
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional
from mcp.server.fastmcp import FastMCP

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


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_todays_picks(sport: str = "all") -> str:
    """
    Get today's AI-generated picks with confidence and edge scores.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', or 'all' (default)

    Returns:
        List of picks with pick name, bet type, line, odds, confidence, and edge score.
    """
    try:
        data = _api_get("/xk/p", {"sport": sport} if sport != "all" else None)
        picks = data if isinstance(data, list) else data.get("picks", [])

        if not picks:
            return f"No picks available for {sport} today."

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

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching picks: {e}"


@mcp.tool()
def get_top_pick(sport: str = "all") -> str:
    """
    Get the single highest-confidence pick available today.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', or 'all' (default)

    Returns:
        The best pick with full analysis details.
    """
    try:
        data = _api_get("/xk/p", {"sport": sport} if sport != "all" else None)
        picks = data if isinstance(data, list) else data.get("picks", [])

        if not picks:
            return "No picks available today."

        # Sort by confidence tier then edge score
        confidence_order = {"high": 0, "medium": 1, "low": 2}
        def sort_key(p):
            conf = confidence_order.get((p.get("confidence") or "low").lower(), 2)
            edge = float(p.get("edge_score") or p.get("edge") or 0)
            return (conf, -edge)

        best = sorted(picks, key=sort_key)[0]

        lines = [
            "TOP PICK TODAY",
            f"  Pick:       {best.get('pick_name') or best.get('team') or '?'}",
            f"  Sport:      {(best.get('sport') or '?').upper()}",
            f"  Bet Type:   {(best.get('bet_type') or '?').upper()}",
            f"  Line:       {best.get('line_value') or best.get('line') or 'N/A'}",
            f"  Odds:       {best.get('odds') or 'N/A'}",
            f"  Confidence: {best.get('confidence') or '?'}",
            f"  Edge Score: {best.get('edge_score') or best.get('edge') or 'N/A'}",
            f"  Game:       {best.get('game') or 'N/A'}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching top pick: {e}"


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
        data = _api_get(f"/xk/o/{sport.lower()}")
        games = data if isinstance(data, list) else data.get("games", data.get("odds", []))

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
        data = _api_get("/xk/w")
        if not data:
            return "Analytics data not available."

        overall = data.get("overall") or data
        total = overall.get("total_picks") or overall.get("total") or 0
        wins = overall.get("wins") or 0
        losses = overall.get("losses") or 0
        win_pct = overall.get("win_rate") or overall.get("win_pct") or 0

        lines = [
            "BETTING ANALYZER WIN RATES",
            f"  Overall: {wins}W / {losses}L ({win_pct}%) — {total} picks",
        ]

        # By sport if available
        by_sport = data.get("by_sport") or {}
        if by_sport:
            lines.append("\n  By Sport:")
            for sport, stats in by_sport.items():
                s_wins = stats.get("wins", 0)
                s_total = stats.get("total", 0)
                s_pct = stats.get("win_rate") or (round(s_wins / s_total * 100, 1) if s_total > 0 else 0)
                lines.append(f"    {sport.upper()}: {s_wins}W / {s_total - s_wins}L ({s_pct}%)")

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
        data = _api_get("/xk/q")
        picks = data if isinstance(data, list) else data.get("picks", [])

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
def get_injury_report(sport: str = "all") -> str:
    """
    Get current injury flags that may affect today's picks.
    Data refreshes at 5am and 5pm EST from Covers.com.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', or 'all'

    Returns:
        Active injury reports with player names, status, and impact assessment.
    """
    try:
        params = {"sport": sport} if sport != "all" else None
        data = _api_get("/xk/i", params)
        injuries = data if isinstance(data, list) else data.get("injuries", [])

        if not injuries:
            return f"No active injury flags for {sport.upper() if sport != 'all' else 'any sport'}."

        lines = [f"INJURY REPORT — {sport.upper() if sport != 'all' else 'ALL SPORTS'}\n"]
        for inj in injuries[:30]:
            player = inj.get("player") or inj.get("player_name") or "?"
            team = inj.get("team") or "?"
            status = inj.get("status") or "?"
            sport_tag = (inj.get("sport") or "").upper()
            impact = inj.get("impact") or inj.get("note") or ""
            impact_str = f" — {impact}" if impact else ""
            lines.append(f"  [{sport_tag}] {player} ({team}): {status}{impact_str}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching injuries: {e}"


@mcp.tool()
def get_line_movement(sport: str = "all") -> str:
    """
    Get significant line movements detected since market open.
    Sharp money often signals where to bet.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', or 'all'

    Returns:
        Games with notable line shifts, direction, and magnitude.
    """
    try:
        params = {"sport": sport} if sport != "all" else None
        data = _api_get("/xk/m", params)
        movements = data if isinstance(data, list) else data.get("movements", data.get("line_history", []))

        if not movements:
            return f"No significant line movement detected for {sport.upper() if sport != 'all' else 'any sport'} today."

        lines = [f"LINE MOVEMENT — {sport.upper() if sport != 'all' else 'ALL SPORTS'}\n"]
        for m in movements[:20]:
            game = m.get("game") or f"{m.get('away_team','?')} @ {m.get('home_team','?')}"
            bet_type = (m.get("bet_type") or "?").upper()
            old_line = m.get("old_line") or m.get("open_line") or "?"
            new_line = m.get("new_line") or m.get("current_line") or "?"
            sport_tag = (m.get("sport") or "").upper()
            direction = ""
            try:
                diff = float(new_line) - float(old_line)
                direction = f" ({'up' if diff > 0 else 'down'} {abs(diff):.1f})"
            except (TypeError, ValueError):
                pass

            lines.append(f"  [{sport_tag}] {game}")
            lines.append(f"    {bet_type}: {old_line} → {new_line}{direction}")
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching line movement: {e}"
