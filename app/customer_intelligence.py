
from collections import Counter

from sqlalchemy import text
from app.db import engine


def customer_insights():
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT category, sentiment, priority, status, message
                FROM tickets
            """)
        ).mappings().all()

    if not rows:
        return {
            "ticket_count": 0,
            "top_categories": [],
            "sentiment": {},
            "examples": [],
        }

    categories = Counter(
        (row["category"] or "Uncategorized").strip()
        for row in rows
    )

    sentiments = Counter(
        (row["sentiment"] or "Unknown").strip()
        for row in rows
    )

    return {
        "ticket_count": len(rows),
        "top_categories": [
            {"category": category, "count": count}
            for category, count in categories.most_common(8)
        ],
        "sentiment": dict(sentiments),
        "examples": [dict(row) for row in rows[:8]],
    }
