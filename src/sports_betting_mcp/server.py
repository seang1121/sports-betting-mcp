"""
sports-betting-mcp — MCP server for AI-powered sports betting analysis
Live picks, odds, injuries, and line movement across NBA, NHL, NCAAB, MLB
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
        "Live sports betting analysis server. "
        "Query real-time AI picks, live odds, injury reports, and line movement "
        "across NBA, NHL, NCAAB, and MLB. "
        "12 tools: today's picks with confidence scores, live odds from FanDuel/BetMGM, "
        "injury flags, sharp money line movement, full multi-agent game analysis, "
        "win rate tracking, leaderboard, and pick logging. "
        "Data updates continuously throughout game day."
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
                "Free tier rate limit reached (12 req/day). "
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


def _fetch_slip(pick_name: str, sport: str, probability: float) -> Optional[Image]:
    """Fetch a Nimrod bet slip image from the API. Returns FastMCP Image or None."""
    try:
        slip = _api_post("/xk/slip", {
            "pick_name": pick_name,
            "sport": sport,
            "probability": int(probability),
        })
        img_b64 = slip.get("image_b64")
        if img_b64:
            return Image(data=base64.b64decode(img_b64), format="png")
    except Exception:
        pass
    return None


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_todays_picks(sport: str = "all") -> list:
    """
    Get today's AI-generated picks with confidence and edge scores.
    Includes a visual bet slip card for the top pick per sport.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', 'mlb', or 'all' (default)

    Returns:
        List of picks with pick name, bet type, line, odds, confidence, and edge score.
        Visual bet slip cards are included for the top pick per sport.
    """
    try:
        data = _api_get("/xk/p", {"sport": sport} if sport != "all" else None)
        picks = data if isinstance(data, list) else data.get("picks", [])

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

        content = ["\n".join(lines)]

        # Top pick per sport — attach bet slip image
        seen_sports = set()
        confidence_order = {"high": 0, "medium": 1, "low": 2}
        sorted_picks = sorted(
            picks,
            key=lambda p: (
                confidence_order.get((p.get("confidence") or "low").lower(), 2),
                -float(p.get("edge_score") or 0)
            )
        )
        for p in sorted_picks:
            sport_tag = (p.get("sport") or "").upper()
            if sport_tag in seen_sports or sport_tag not in ("NBA", "NHL", "NCAAB", "MLB"):
                continue
            pick_name = p.get("pick_name") or p.get("team") or ""
            prob = float(p.get("edge_score") or 0) + 50
            if pick_name:
                img = _fetch_slip(pick_name, sport_tag, prob)
                if img:
                    content.append(img)
            seen_sports.add(sport_tag)
            if len(seen_sports) == 4:
                break

        return content
    except Exception as e:
        return [f"Error fetching picks: {e}"]


@mcp.tool()
def get_top_pick(sport: str = "all") -> list:
    """
    Get the single highest-confidence pick available today with a visual bet slip card.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', 'mlb', or 'all' (default)

    Returns:
        The best pick with full analysis details and a visual bet slip image.
    """
    try:
        data = _api_get("/xk/p", {"sport": sport} if sport != "all" else None)
        picks = data if isinstance(data, list) else data.get("picks", [])

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
        prob = float(best.get("edge_score") or 0) + 50

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
        content = ["\n".join(lines)]

        img = _fetch_slip(pick_name, sport_tag, prob)
        if img:
            content.append(img)

        return content
    except Exception as e:
        return [f"Error fetching top pick: {e}"]


@mcp.tool()
def get_live_odds(sport: str) -> str:
    """
    Get current live odds for a sport from FanDuel and BetMGM.

    Args:
        sport: Sport to fetch — 'nba', 'nhl', 'ncaab', or 'mlb'

    Returns:
        Live moneyline, spread, and total odds for today's games.
    """
    if sport.lower() not in ("nba", "nhl", "ncaab", "mlb"):
        return "Invalid sport. Use: nba, nhl, ncaab, or mlb"

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
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', 'mlb', or 'all'

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
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', 'mlb', or 'all'

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


@mcp.tool()
def analyze_game(sport: str, game_id: str) -> str:
    """
    Run full 12-agent analysis on a specific game — Pro tier only.
    Free and comp API keys receive a preview with upgrade instructions.

    Args:
        sport: Sport — 'nba', 'nhl', 'ncaab', or 'mlb'
        game_id: Game ID from the get_live_odds tool

    Returns:
        Pro: Complete multi-agent analysis with consensus pick, confidence, and edge breakdown.
        Free: Preview message with upgrade link.
    """
    if sport.lower() not in ("nba", "nhl", "ncaab", "mlb"):
        return "Invalid sport. Use: nba, nhl, ncaab, or mlb"

    pro_upsell = (
        f"GAME ANALYSIS — {sport.upper()} (Pro Feature)\n\n"
        "Full 12-agent analysis is available to Pro subscribers. "
        "Each game is evaluated by 12 specialized agents covering "
        "momentum, matchups, injuries, rest, sharp money, and more — "
        "then synthesized into a consensus pick with edge breakdown.\n\n"
        "What you get with Pro:\n"
        "  - Full multi-agent analysis on any game\n"
        "  - Unlimited API requests\n"
        "  - Priority pick delivery\n\n"
        "Upgrade at https://sportsbettingaianalyzer.com/pricing\n\n"
        "Free tools available now: get_todays_picks, get_top_pick, "
        "get_live_odds, get_injury_report, get_win_rate"
    )

    try:
        data = _api_post("/api/analyze", {"sport": sport.upper(), "game_id": game_id})
    except Exception:
        return pro_upsell

    if not isinstance(data, dict) or not data.get("success", True):
        return pro_upsell

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


@mcp.tool()
def log_pick(
    pick_name: str,
    sport: str,
    bet_type: str,
    odds: int,
    wager_amount: float = 4.0,
    game: str = "",
    line_value: float = 0,
    reasoning: str = "",
    odds_api_game_id: str = "",
) -> str:
    """
    Log a pick to the betting analyzer. Your pick enters the learning loop
    and gets resolved automatically when the game finishes.

    Args:
        pick_name: Team or player name (e.g. 'Lakers', 'O225.5')
        sport: Sport — 'nba', 'nhl', 'ncaab', or 'mlb'
        bet_type: Type of bet — 'moneyline', 'spread', or 'total'
        odds: American odds (e.g. -110, +150)
        wager_amount: Wager in dollars, $1-$100 (default $4)
        game: Game description (e.g. 'Lakers vs Celtics')
        line_value: Spread or total line (e.g. -3.5 or 225.5)
        reasoning: Why you're making this pick
        odds_api_game_id: Game ID from get_live_odds for duplicate prevention

    Returns:
        Confirmation with pick ID, wager, and potential profit.
    """
    try:
        data = _api_post("/xk/log", {
            "pick_name": pick_name,
            "sport": sport.upper(),
            "bet_type": bet_type,
            "odds": odds,
            "wager_amount": wager_amount,
            "game": game,
            "line_value": line_value,
            "reasoning": reasoning,
            "odds_api_game_id": odds_api_game_id,
        })

        if data.get("success"):
            return (
                f"PICK LOGGED\n"
                f"  Pick:     {data.get('pick_name', pick_name)}\n"
                f"  Sport:    {data.get('sport', sport).upper()}\n"
                f"  Odds:     {data.get('odds', odds)}\n"
                f"  Wager:    ${data.get('wager_amount', wager_amount):.2f}\n"
                f"  Profit:   ${data.get('potential_profit', 0):.2f} (if win)\n"
                f"  Pick ID:  {data.get('pick_id', 'N/A')}\n\n"
                f"Pick will auto-resolve when the game finishes."
            )
        else:
            error = data.get("error", "Unknown error")
            if data.get("duplicate"):
                return f"Already logged a {bet_type} pick for this game today."
            return f"Failed to log pick: {error}"
    except Exception as e:
        return f"Error logging pick: {e}"


@mcp.tool()
def get_completed_picks(sport: str = "all", limit: int = 50) -> str:
    """
    Get recently completed picks with W/L results.
    Use this to verify the track record or analyze historical performance.

    Args:
        sport: Filter by sport — 'nba', 'nhl', 'ncaab', 'mlb', or 'all' (default)
        limit: Number of picks to return, max 100 (default 50)

    Returns:
        Recent completed picks with results, bet type, odds, and date.
    """
    try:
        params = {"limit": min(limit, 100)}
        if sport != "all":
            params["sport"] = sport.upper()

        data = _api_get("/xk/c", params)
        picks = data.get("picks", [])

        if not picks:
            return f"No completed picks found for {sport.upper() if sport != 'all' else 'any sport'}."

        wins = sum(1 for p in picks if p.get("result") == "W")
        losses = sum(1 for p in picks if p.get("result") == "L")
        pct = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0

        lines = [
            f"COMPLETED PICKS — {sport.upper() if sport != 'all' else 'ALL SPORTS'} "
            f"(last {len(picks)}: {wins}W-{losses}L, {pct:.1f}%)\n"
        ]

        for p in picks:
            result = p.get("result", "?")
            icon = "W" if result == "W" else "L"
            sport_tag = (p.get("sport") or "").upper()
            pick_name = p.get("pick_name", "?")
            bet_type = (p.get("bet_type") or "?").upper()
            odds = p.get("odds", "")
            date = p.get("date", "")

            odds_str = f" ({odds})" if odds else ""
            lines.append(f"  [{icon}] [{sport_tag}] {pick_name} {bet_type}{odds_str} — {date}")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching completed picks: {e}"


@mcp.tool()
def get_leaderboard() -> str:
    """
    Get the current leaderboard — all users ranked by win rate,
    including the AI model's performance.

    Returns:
        Rankings with username, record, win rate, and whether the entry is AI or human.
    """
    try:
        data = _api_get("/xk/lb")
        rankings = data.get("rankings", [])

        if not rankings:
            return "Leaderboard not available."

        lines = [f"LEADERBOARD — {data.get('total_users', len(rankings))} participants\n"]

        for r in rankings:
            rank = r.get("rank", "?")
            name = r.get("username", "?")
            wins = r.get("wins", 0)
            losses = r.get("losses", 0)
            total = r.get("total_picks", 0)
            pct = r.get("win_rate", 0)
            tag = " [AI]" if r.get("is_ai") else ""

            lines.append(f"  #{rank} {name}{tag} — {wins}W-{losses}L ({pct}%) | {total} picks")

        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching leaderboard: {e}"


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
