from collections import defaultdict


def compute_dashboard(signals):
    stats = {
        "wins": 0,
        "losses": 0,
        "profit": 0,
        "best": -999,
        "worst": 999,
    }

    by_signal = defaultdict(lambda: {"wins": 0, "losses": 0})

    for s in signals:
        if not s.get("evaluated"):
            continue

        p = s.get("profit", 0)
        sig = s.get("signal")

        stats["profit"] += p
        stats["best"] = max(stats["best"], p)
        stats["worst"] = min(stats["worst"], p)

        if p > 0:
            stats["wins"] += 1
            by_signal[sig]["wins"] += 1
        else:
            stats["losses"] += 1
            by_signal[sig]["losses"] += 1

    total = stats["wins"] + stats["losses"]

    return {
        "trades": total,
        "winrate": round((stats["wins"] / total) * 100, 2) if total else 0,
        "profit": round(stats["profit"] * 100, 2),
        "best": round(stats["best"] * 100, 2),
        "worst": round(stats["worst"] * 100, 2),
        "by_signal": by_signal,
    }