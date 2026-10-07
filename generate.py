#!/usr/bin/env python3
"""Build the static verification report from data/snapshot.json into site/."""

import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))


def load_snapshot():
    with open(os.path.join(HERE, "data", "snapshot.json")) as f:
        return json.load(f)


def row_html(cells, header=False):
    tag = "th" if header else "td"
    return "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"


def main():
    snap = load_snapshot()
    generated = snap.get("generated_at", "")
    providers = snap.get("providers", [])
    rounds = snap.get("rounds", [])
    active = snap.get("active_models", [])
    inactive = snap.get("inactive_models", [])

    parts = [
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>Model Verification Report</title>",
        "<style>body{font-family:sans-serif;max-width:1000px;margin:2em auto;padding:0 1em}"
        "table{border-collapse:collapse;width:100%;margin:1em 0}"
        "th,td{border:1px solid #ccc;padding:6px 10px;text-align:left}"
        "th{background:#f0f0f0}</style></head><body>",
        "<h1>Model Verification Report</h1>",
        f"<p>Generated: {generated}</p>",
        "<h2>Providers</h2>",
        "<table>" + row_html(["Provider", "Registry total", "Active"], True)
        + "".join(row_html([p["provider"], p["total"], p["active"]]) for p in providers)
        + "</table>",
        "<h2>Latest rounds</h2>",
        "<table>"
        + row_html(["Round", "Provider", "Tested", "Successful", "Failed", "New", "Flagged inactive"], True)
        + "".join(
            row_html([r["run_id"], r["provider"], r["tested"], r["successful"], r["failed"], r["new"], r["inactive"]])
            for r in rounds
        )
        + "</table>",
        "<h2>Active models</h2>",
        "<table>" + row_html(["Model", "Provider", "Context window", "Last tested"], True)
        + "".join(row_html([m["model"], m["provider"], m.get("context_window", ""), m.get("last_tested", "")]) for m in active)
        + "</table>",
        "<h2>Inactive models</h2>",
        "<table>" + row_html(["Model", "Provider", "Consecutive failures"], True)
        + "".join(row_html([m["model"], m["provider"], m.get("failures", "")]) for m in inactive)
        + "</table>",
        f"<p>Report generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}.</p>",
        "</body></html>",
    ]

    os.makedirs(os.path.join(HERE, "site"), exist_ok=True)
    with open(os.path.join(HERE, "site", "index.html"), "w") as f:
        f.write("\n".join(parts))
    print(f"Wrote site/index.html ({len(active)} active, {len(inactive)} inactive)")


if __name__ == "__main__":
    main()
