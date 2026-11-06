
from typing import TypedDict, Any

from langgraph.graph import StateGraph, END
from sqlalchemy import text

from app.sql_analytics import answer_analytics
from app.customer_intelligence import customer_insights
from app.db import engine
from app.rag import rag
from app.llm import generate


# --------------------------------------------------
# Agent State
# --------------------------------------------------

class State(TypedDict, total=False):
    question: str
    intent: str
    answer: str
    sources: list
    sql: str | None
    data: Any


# --------------------------------------------------
# Intent Classification
# --------------------------------------------------

def classify(s):

    q = s["question"].lower()

    # Strategic questions must be checked first
    strategy_keywords = [
        "improve",
        "improvements",
        "prioritize",
        "priorities",
        "recommendation",
        "recommendations",
        "business strategy",
        "business performance",
        "business growth",
        "what should the business",
        "how can the business",
        "how can we improve",
        "areas of improvement",
        "biggest problems",
        "business problems",
        "what should we focus on",
    ]

    if any(word in q for word in strategy_keywords):
        return {"intent": "strategy"}

    if any(x in q for x in [
        "complaint",
        "ticket",
        "sentiment",
        "feedback",
        "support issue"
    ]):
        return {"intent": "customer"}

    if any(x in q for x in [
        "policy",
        "document",
        "manual",
        "according to",
        "return process",
        "knowledge base"
    ]):
        return {"intent": "knowledge"}

    return {"intent": "analytics"}


# --------------------------------------------------
# SQL Analytics Node
# --------------------------------------------------

def analytics(s):

    r = answer_analytics(s["question"])

    return {
        "answer": r["answer"],
        "sql": r["sql"],
        "data": r["data"],
        "sources": []
    }


# --------------------------------------------------
# Customer Intelligence Node
# --------------------------------------------------


def customer(s):

    info = customer_insights()

    if info["ticket_count"] == 0:
        return {
            "answer": "No customer support tickets were found.",
            "data": info,
            "sources": []
        }

    sentiments = {
        str(k).strip().lower(): v
        for k, v in info["sentiment"].items()
    }

    total = info["ticket_count"]
    negative = sentiments.get("negative", 0)
    neutral = sentiments.get("neutral", 0)
    positive = sentiments.get("positive", 0)

    negative_percentage = round(
        negative / total * 100, 2
    )

    # Find negative feedback examples
    negative_examples = [
        item for item in info["examples"]
        if str(item.get("sentiment", "")).strip().lower() == "negative"
    ]

    # Count negative feedback by category
    negative_categories = {}

    for item in info["examples"]:
        if str(item.get("sentiment", "")).strip().lower() == "negative":
            category = item.get("category") or "Uncategorized"
            negative_categories[category] = (
                negative_categories.get(category, 0) + 1
            )

    lines = [
        "NEGATIVE CUSTOMER FEEDBACK SUMMARY",
        "",
        f"Total support tickets: {total}",
        f"Negative feedback: {negative} ({negative_percentage}%)",
        f"Neutral feedback: {neutral}",
        f"Positive feedback: {positive}",
        "",
        "Key complaint categories:"
    ]

    for item in info["top_categories"][:5]:
        lines.append(
            f"- {item['category']}: {item['count']} tickets"
        )

    lines.extend([
        "",
        "Negative feedback examples:"
    ])

    if negative_examples:
        for item in negative_examples:
            lines.append(
                f"- [{item.get('category', 'Unknown')}] "
                f"{item.get('message', 'No message available')}"
            )
    else:
        lines.append("No negative examples available in the sample.")

    lines.extend([
        "",
        "Business recommendation:",
        "Investigate recurring customer complaints, "
        "prioritize the largest complaint categories, "
        "and monitor customer satisfaction."
    ])

    return {
        "answer": "\n".join(lines),
        "data": {
            **info,
            "negative_count": negative,
            "negative_percentage": negative_percentage,
            "negative_examples": negative_examples
        },
        "sources": []
    }

# --------------------------------------------------
# Knowledge Base / RAG Node
# --------------------------------------------------

def knowledge(s):

    hits = rag.search(s["question"])

    if not hits:

        return {
            "answer": (
                "No relevant documents were found. "
                "Please upload and index a relevant document."
            ),
            "sources": []
        }

    context = "\n\n".join(
        f"[{h['source']}] {h['text']}"
        for h in hits
    )

    answer = generate(
        f"""
Question: {s['question']}

Context:
{context}

Answer only using the provided context.
Mention the source filenames.
If the answer is not available in the context, say so.
""",
        "You are a grounded company knowledge assistant."
    )

    return {
        "answer": answer or "\n".join(
            f"{h['source']}: {h['text']}"
            for h in hits
        ),
        "sources": hits,
        "data": hits
    }


# --------------------------------------------------
# Business Strategy Node
# --------------------------------------------------

def business_strategy(s):

    # 1. Customer insights
    customer_data = customer_insights()

    ticket_count = customer_data["ticket_count"]
    categories = customer_data["top_categories"]
    sentiment = customer_data["sentiment"]

    negative = sum(
        count for label, count in sentiment.items()
        if label.lower() == "negative"
    )

    negative_percentage = (
        round((negative / ticket_count) * 100, 2)
        if ticket_count else 0
    )

    # 2. Revenue and product performance
    with engine.connect() as conn:

        revenue = conn.execute(text("""
            SELECT
                COALESCE(
                    SUM(
                        quantity * unit_price *
                        (1 - COALESCE(discount, 0))
                    ), 0
                )
            FROM orders
            WHERE LOWER(status) NOT IN ('cancelled', 'refunded')
        """)).scalar_one()

        top_products = conn.execute(text("""
            SELECT
                p.product_name,
                ROUND(
                    SUM(
                        o.quantity * o.unit_price *
                        (1 - COALESCE(o.discount, 0))
                    ), 2
                ) AS revenue
            FROM orders o
            JOIN products p
                ON p.product_id = o.product_id
            WHERE LOWER(o.status) NOT IN ('cancelled', 'refunded')
            GROUP BY p.product_name
            ORDER BY revenue DESC
            LIMIT 5
        """)).mappings().all()

        unresolved = conn.execute(text("""
            SELECT COUNT(*)
            FROM tickets
            WHERE LOWER(status) IN ('open', 'in_progress')
        """)).scalar_one()

        high_priority = conn.execute(text("""
            SELECT COUNT(*)
            FROM tickets
            WHERE LOWER(priority) = 'high'
              AND LOWER(status) IN ('open', 'in_progress')
        """)).scalar_one()

    # 3. Generate evidence-based recommendations
    recommendations = []

    if categories:

        largest = categories[0]

        recommendations.append({
            "priority": "HIGH",
            "area": largest["category"],
            "evidence": f"{largest['count']} customer tickets",
            "recommendation": (
                f"Investigate and improve {largest['category'].lower()} "
                "operations. Identify recurring causes and track "
                "resolution time."
            )
        })

    if negative_percentage > 40:

        recommendations.append({
            "priority": "HIGH",
            "area": "Customer satisfaction",
            "evidence": (
                f"{negative_percentage}% negative customer sentiment"
            ),
            "recommendation": (
                "Review negative feedback, identify recurring issues, "
                "and introduce customer satisfaction monitoring."
            )
        })

    if high_priority > 0:

        recommendations.append({
            "priority": "HIGH",
            "area": "Support operations",
            "evidence": f"{high_priority} unresolved high-priority tickets",
            "recommendation": (
                "Create an escalation process for high-priority tickets "
                "and monitor resolution time."
            )
        })

    if unresolved > 0:

        recommendations.append({
            "priority": "MEDIUM",
            "area": "Ticket management",
            "evidence": f"{unresolved} unresolved tickets",
            "recommendation": (
                "Introduce ticket-age monitoring and regular follow-ups "
                "to reduce the unresolved backlog."
            )
        })

    # 4. Build final answer
    lines = [
        "BUSINESS PERFORMANCE AND STRATEGIC RECOMMENDATIONS",
        "",
        "1. BUSINESS OVERVIEW",
        f"- Total revenue: {float(revenue):,.2f}",
        f"- Customer support tickets: {ticket_count}",
        f"- Negative sentiment: {negative_percentage}%",
        f"- Unresolved tickets: {unresolved}",
        f"- High-priority unresolved tickets: {high_priority}",
        "",
        "2. TOP CUSTOMER COMPLAINTS"
    ]

    for item in categories[:5]:
        lines.append(
            f"- {item['category']}: {item['count']} tickets"
        )

    lines.extend([
        "",
        "3. TOP REVENUE-GENERATING PRODUCTS"
    ])

    for item in top_products:
        lines.append(
            f"- {item['product_name']}: {float(item['revenue']):,.2f}"
        )

    lines.extend([
        "",
        "4. RECOMMENDED BUSINESS IMPROVEMENTS"
    ])

    for i, item in enumerate(recommendations, start=1):

        lines.extend([
            "",
            f"{i}. {item['area']} - {item['priority']} PRIORITY",
            f"Evidence: {item['evidence']}",
            f"Action: {item['recommendation']}"
        ])

    if not recommendations:
        lines.append(
            "Insufficient evidence to identify a critical improvement area."
        )

    lines.extend([
        "",
        "5. KPIs TO MONITOR",
        "- Negative sentiment percentage",
        "- Delivery-related complaint volume",
        "- Average ticket resolution time",
        "- High-priority unresolved tickets",
        "- Monthly revenue growth",
        "- Product-wise revenue"
    ])

    answer = "\n".join(lines)

    return {
        "answer": answer,
        "intent": "strategy",
        "sql": None,
        "sources": [],
        "data": {
            "revenue": float(revenue),
            "ticket_count": ticket_count,
            "negative_sentiment_percentage": negative_percentage,
            "unresolved_tickets": unresolved,
            "high_priority_unresolved": high_priority,
            "top_categories": categories,
            "top_products": [dict(x) for x in top_products],
            "recommendations": recommendations
        }
    }


# --------------------------------------------------
# Build LangGraph Workflow
# --------------------------------------------------

def build():

    g = StateGraph(State)

    g.add_node("route", classify)
    g.add_node("analytics", analytics)
    g.add_node("customer", customer)
    g.add_node("knowledge", knowledge)
    g.add_node("strategy", business_strategy)

    g.set_entry_point("route")

    g.add_conditional_edges(
        "route",
        lambda s: s["intent"],
        {
            "analytics": "analytics",
            "customer": "customer",
            "knowledge": "knowledge",
            "strategy": "strategy"
        }
    )

    for node in [
        "analytics",
        "customer",
        "knowledge",
        "strategy"
    ]:
        g.add_edge(node, END)

    return g.compile()


agent = build()


def ask(question):
    return agent.invoke({"question": question})
