
import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# Configuration
# --------------------------------------------------

API = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Business Intelligence AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Business Intelligence AI")
st.caption("Local-first agentic business operations assistant")


# --------------------------------------------------
# Dashboard Data
# --------------------------------------------------

try:
    dashboard_data = requests.get(
        f"{API}/api/dashboard/summary",
        timeout=10
    )
    dashboard_data.raise_for_status()
    dashboard_data = dashboard_data.json()

except requests.RequestException:
    st.error("Backend unavailable. Run: uvicorn app.main:app --reload")
    st.stop()


# --------------------------------------------------
# KPI Metrics
# --------------------------------------------------

k = dashboard_data["kpis"]

cols = st.columns(5)

metrics = [
    ("Revenue", f"₹{k['revenue']:,.0f}"),
    ("Orders", f"{k['orders']:,}"),
    ("Units sold", f"{k['units']:,}"),
    ("Customers", f"{k['customers']:,}"),
    ("Support tickets", f"{k['tickets']:,}")
]

for col, (label, value) in zip(cols, metrics):
    col.metric(label, value)


# --------------------------------------------------
# Revenue and Product Charts
# --------------------------------------------------

a, b = st.columns(2)

with a:
    st.subheader("Monthly revenue")

    monthly_df = pd.DataFrame(
        dashboard_data["monthly_revenue"]
    )

    if not monthly_df.empty:
        fig = px.line(
            monthly_df,
            x="month",
            y="revenue",
            markers=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    else:
        st.info("No monthly revenue data available.")


with b:
    st.subheader("Top products")

    products_df = pd.DataFrame(
        dashboard_data["top_products"]
    )

    if not products_df.empty:
        fig = px.bar(
            products_df,
            x="revenue",
            y="product_name",
            orientation="h"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    else:
        st.info("No product data available.")


# --------------------------------------------------
# AI Business Agent
# --------------------------------------------------

st.divider()
st.subheader("Ask your business agent")

question = st.text_input(
    "Ask a business question",
    placeholder="Which products generated the most revenue?"
)

if st.button(
    "Ask AI",
    type="primary",
    disabled=not question.strip()
):

    with st.spinner("Analyzing..."):

        try:
            response = requests.post(
                f"{API}/api/chat",
                json={"question": question},
                timeout=180
            )

            response.raise_for_status()
            result = response.json()

            # AI Answer
            st.markdown(result.get("answer", "No answer generated."))

            st.caption(
                f"Workflow: {result.get('intent', 'unknown')}"
            )

            # Generated SQL
            if result.get("sql"):
                with st.expander("Generated SQL"):
                    st.code(
                        result["sql"],
                        language="sql"
                    )

            # Structured Data
            response_data = result.get("data")

            if response_data:
                with st.expander("Data", expanded=True):

                    if isinstance(response_data, dict):

                        # Customer Complaint Categories
                        if "top_categories" in response_data:
                            st.subheader("Complaint Categories")

                            categories_df = pd.DataFrame(
                                response_data["top_categories"]
                            )

                            st.dataframe(
                                categories_df,
                                use_container_width=True
                            )

                            if not categories_df.empty:
                                fig = px.bar(
                                    categories_df,
                                    x="count",
                                    y="category",
                                    orientation="h",
                                    title="Most Common Customer Complaints"
                                )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                        # Customer Sentiment
                        if "sentiment" in response_data:
                            st.subheader("Customer Sentiment")

                            sentiment_df = pd.DataFrame(
                                list(response_data["sentiment"].items()),
                                columns=["Sentiment", "Count"]
                            )

                            st.dataframe(
                                sentiment_df,
                                use_container_width=True
                            )

                            if not sentiment_df.empty:
                                fig = px.pie(
                                    sentiment_df,
                                    names="Sentiment",
                                    values="Count",
                                    title="Customer Sentiment Distribution"
                                )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                        # Sample Tickets
                        if "examples" in response_data:
                            st.subheader("Sample Support Tickets")

                            st.dataframe(
                                pd.DataFrame(response_data["examples"]),
                                use_container_width=True
                            )

                        # Total Tickets
                        if "ticket_count" in response_data:
                            st.metric(
                                "Total Support Tickets",
                                response_data["ticket_count"]
                            )

                        # Fallback for other dictionaries
                        if not any(
                            key in response_data
                            for key in [
                                "top_categories",
                                "sentiment",
                                "examples",
                                "ticket_count"
                            ]
                        ):
                            st.json(response_data)

                    elif isinstance(response_data, list):

                        st.dataframe(
                            pd.DataFrame(response_data),
                            use_container_width=True
                        )

                    else:
                        st.json(response_data)

            # Knowledge Sources
            if result.get("sources"):
                with st.expander("Knowledge sources"):

                    for source in result["sources"]:
                        st.markdown(
                            f"**{source.get('source', 'Unknown')}** "
                            f"· Score: {source.get('score', 'N/A')}"
                        )

                        st.write(
                            source.get("text", "")
                        )

        except requests.RequestException as e:
            st.error(f"API request failed: {e}")

        except ValueError as e:
            st.error(f"Invalid API response: {e}")


# --------------------------------------------------
# Knowledge Base
# --------------------------------------------------

st.divider()
st.subheader("Knowledge Base")

uploaded_file = st.file_uploader(
    "Upload PDF, TXT, MD, CSV or XLSX",
    type=["pdf", "txt", "md", "csv", "xlsx"]
)

if uploaded_file and st.button("Index document"):

    try:
        response = requests.post(
            f"{API}/api/knowledge/upload",
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue()
                )
            },
            timeout=180
        )

        response.raise_for_status()

        st.success(
            f"Indexed {response.json()['chunks_indexed']} chunks."
        )

    except requests.RequestException as e:
        st.error(f"Document upload failed: {e}")


# --------------------------------------------------
# Customer Complaint Overview
# --------------------------------------------------

with st.expander("Customer complaint overview"):

    customer_insights = dashboard_data.get(
        "customer_insights",
        {}
    )

    st.json(customer_insights)
