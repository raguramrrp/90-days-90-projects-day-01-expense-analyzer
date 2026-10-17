"""
Personal Expense Intelligence & Spending Analyzer
Main Streamlit Application
"""

from __future__ import annotations

import io
import os
import sys
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root and src to path for module resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.database import (
    DEFAULT_DB_PATH,
    init_db,
    insert_transaction,
    bulk_insert_transactions,
    get_all_transactions,
    update_transaction,
    delete_transaction,
    clear_all_transactions,
    get_budgets,
    set_budget,
    get_transaction_stats,
)
from src.categorizer import get_categorizer, CATEGORIES
from src.anomaly_detector import ExpenseAnomalyDetector, get_anomalies_summary
from src.analytics import (
    calculate_kpis,
    get_monthly_summary,
    get_category_breakdown,
    get_daily_trend,
    get_budget_comparison,
    get_top_merchants,
)

# Page configuration
st.set_page_config(
    page_title="Personal Expense Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database schema
init_db()

# Custom Styling
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #1E232F;
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 16px 20px;
        color: white;
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F7FAFC;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #48BB78;
        margin-top: 4px;
    }
    .badge-anomaly {
        background-color: #FEB2B2;
        color: #9B2C2C;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-normal {
        background-color: #C6F6D5;
        color: #22543D;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_sidebar():
    """Render the sidebar with navigation and quick database metrics."""
    with st.sidebar:
        st.title("💳 ExpenseIQ")
        st.caption("Personal Expense Intelligence & Spending Analyzer")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📥 Upload & Ingest", "📑 Transactions", "📈 Reports & Budgets"],
            index=0,
        )

        st.markdown("---")
        st.subheader("Database Overview")
        stats = get_transaction_stats()
        st.write(f"**Total Records:** `{stats['total_count']}`")
        st.write(f"**Total Spent:** `${stats['total_spent']:,.2f}`")
        if stats["min_date"] and stats["max_date"]:
            st.write(f"**Date Span:** `{stats['min_date']}` to `{stats['max_date']}`")

        st.markdown("---")
        # Quick Sample Data Loader
        sample_file_path = os.path.join(PROJECT_ROOT, "data", "sample_expenses.csv")
        if os.path.exists(sample_file_path):
            if st.button("🚀 Load Sample Dataset", use_container_width=True, help="Load 100+ realistic categorized transactions for instant demonstration"):
                df_sample = pd.read_csv(sample_file_path)
                categorizer = get_categorizer()
                records = []
                for _, r in df_sample.iterrows():
                    desc = str(r["description"])
                    cat = str(r.get("category", "")).strip()
                    if not cat or cat == "nan" or cat not in CATEGORIES:
                        cat, _, _ = categorizer.predict(desc)
                    records.append({
                        "date": str(r["date"]),
                        "description": desc,
                        "category": cat,
                        "amount": float(r["amount"]),
                        "payment_method": str(r.get("payment_method", "Card")),
                        "notes": str(r.get("notes", "")),
                    })
                count = bulk_insert_transactions(records)
                st.success(f"Successfully loaded {count} sample transactions!")
                st.rerun()

        if stats["total_count"] > 0:
            if st.button("🗑️ Reset Database", use_container_width=True, help="Delete all stored transactions"):
                clear_all_transactions()
                st.warning("Database cleared!")
                st.rerun()

        st.markdown("---")
        st.caption("90 Days – 90 Projects Challenge | Day 1")
        return page


def render_dashboard(df: pd.DataFrame):
    """Render main executive analytics dashboard."""
    st.title("📊 Financial Intelligence Dashboard")
    st.markdown("Comprehensive overview of personal cash outflow, trends, and spending patterns.")

    if df.empty:
        st.info("👋 Welcome! No transactions found in your database. Click **'🚀 Load Sample Dataset'** in the sidebar or head over to **'📥 Upload & Ingest'** to import your bank/credit card CSV.")
        return

    # Calculate KPIs
    kpis = calculate_kpis(df)
    detector = ExpenseAnomalyDetector()
    df_anom = detector.detect_anomalies(df)
    anom_summary = get_anomalies_summary(df_anom)

    # Top Metric KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Spending</div>
                <div class="metric-value">${kpis['total_spend']:,.2f}</div>
                <div class="metric-subtitle">Across {kpis['transaction_count']} transactions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Daily Burn Rate</div>
                <div class="metric-value">${kpis['daily_burn_rate']:,.2f}</div>
                <div class="metric-subtitle">Average over {kpis['active_days']} days</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Top Expense Category</div>
                <div class="metric-value">{kpis['top_category']}</div>
                <div class="metric-subtitle">${kpis['top_category_spend']:,.2f} accumulated</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Unusual Expenses (AI)</div>
                <div class="metric-value">{anom_summary['anomaly_count']} Flagged</div>
                <div class="metric-subtitle">${anom_summary['total_anomaly_amount']:,.2f} total variance</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Visualizations Row 1: Monthly Trends and Category Breakdown
    col_chart1, col_chart2 = st.columns([6, 5])

    with col_chart1:
        st.subheader("📅 Monthly Spending Trend")
        monthly_df = get_monthly_summary(df)
        if not monthly_df.empty:
            fig_month = go.Figure()
            fig_month.add_trace(
                go.Bar(
                    x=monthly_df["year_month"],
                    y=monthly_df["total_spend"],
                    name="Monthly Total ($)",
                    marker_color="#3182CE",
                    text=monthly_df["total_spend"].apply(lambda v: f"${v:,.0f}"),
                    textposition="auto",
                )
            )
            fig_month.add_trace(
                go.Scatter(
                    x=monthly_df["year_month"],
                    y=monthly_df["avg_spend"],
                    name="Avg per Transaction ($)",
                    yaxis="y2",
                    mode="lines+markers",
                    line=dict(color="#DD6B20", width=3),
                )
            )
            fig_month.update_layout(
                yaxis=dict(title="Total Outflow ($)"),
                yaxis2=dict(title="Average ($)", overlaying="y", side="right"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=30, b=20),
                height=350,
            )
            st.plotly_chart(fig_month, use_container_width=True)

    with col_chart2:
        st.subheader("🍩 Category Distribution")
        cat_df = get_category_breakdown(df)
        if not cat_df.empty:
            fig_pie = px.pie(
                cat_df,
                values="total_spend",
                names="category",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

    # Visualizations Row 2: Daily Spending Velocity & Top Merchants
    col_daily, col_top = st.columns([7, 5])

    with col_daily:
        st.subheader("📈 Daily Spending Velocity & 7-Day Moving Avg")
        daily_df = get_daily_trend(df)
        if not daily_df.empty:
            fig_daily = go.Figure()
            fig_daily.add_trace(
                go.Scatter(
                    x=daily_df["date"],
                    y=daily_df["daily_spend"],
                    mode="lines",
                    name="Daily Spend",
                    line=dict(color="#CBD5E0", width=1),
                    opacity=0.6,
                )
            )
            fig_daily.add_trace(
                go.Scatter(
                    x=daily_df["date"],
                    y=daily_df["rolling_7d_avg"],
                    mode="lines",
                    name="7-Day Rolling Avg",
                    line=dict(color="#38A169", width=3),
                )
            )
            fig_daily.update_layout(
                yaxis=dict(title="Amount ($)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=30, b=20),
                height=320,
            )
            st.plotly_chart(fig_daily, use_container_width=True)

    with col_top:
        st.subheader("🏆 Top Frequent Outflow Merchants")
        top_merchants = get_top_merchants(df, n=6)
        if not top_merchants.empty:
            fig_top = px.bar(
                top_merchants,
                x="total_spend",
                y="description",
                orientation="h",
                color="category",
                text="total_spend",
            )
            fig_top.update_layout(
                yaxis=dict(autorange="reversed", title=""),
                xaxis=dict(title="Total Spent ($)"),
                margin=dict(l=20, r=20, t=30, b=20),
                height=320,
            )
            fig_top.update_traces(texttemplate="$%{text:,.2f}", textposition="outside")
            st.plotly_chart(fig_top, use_container_width=True)


def render_upload_page():
    """Render CSV file ingestion, auto-categorization preview, and manual entry."""
    st.title("📥 Ingest & Add Transactions")
    st.markdown("Upload bank/credit card CSV statements or enter new transactions directly.")

    tab_upload, tab_manual = st.tabs(["📂 CSV Statement Upload", "✍️ Manual Transaction Entry"])

    with tab_upload:
        st.subheader("Upload Bank / Credit Card CSV")
        st.write("Upload any standard CSV statement containing Date, Description, and Amount columns.")

        uploaded_file = st.file_uploader("Select a CSV file", type=["csv"])

        if uploaded_file is not None:
            try:
                raw_df = pd.read_csv(uploaded_file)
                st.write(f"**Found {len(raw_df)} rows.** Map your columns below:")

                cols = list(raw_df.columns)
                col1, col2, col3, col4 = st.columns(4)

                # Intelligent column heuristic guessing
                def guess_col(options, keywords):
                    for opt in options:
                        if any(k in opt.lower() for k in keywords):
                            return opt
                    return options[0] if options else ""

                with col1:
                    date_col = st.selectbox("Date Column", cols, index=cols.index(guess_col(cols, ["date", "time", "day"])))
                with col2:
                    desc_col = st.selectbox("Description Column", cols, index=cols.index(guess_col(cols, ["desc", "name", "merchant", "memo", "title"])))
                with col3:
                    amt_col = st.selectbox("Amount Column", cols, index=cols.index(guess_col(cols, ["amount", "cost", "total", "price", "val"])))
                with col4:
                    cat_options = ["(Auto-Detect with AI/Rules)"] + cols
                    cat_col = st.selectbox("Category Column", cat_options, index=0)

                if st.button("🔍 Preview & Auto-Categorize Ingestion", type="primary"):
                    categorizer = get_categorizer()
                    prepared_rows = []

                    for _, row in raw_df.iterrows():
                        raw_date = str(row[date_col]).strip()
                        raw_desc = str(row[desc_col]).strip()

                        # Clean and normalize amount
                        amt_val = row[amt_col]
                        if isinstance(amt_val, str):
                            amt_val = re.sub(r"[^\d\.\-]", "", amt_val)
                        try:
                            amt_float = abs(float(amt_val))
                        except Exception:
                            amt_float = 0.0

                        # Determine category
                        if cat_col != "(Auto-Detect with AI/Rules)" and pd.notna(row[cat_col]):
                            cat_candidate = str(row[cat_col]).strip()
                            final_cat = cat_candidate if cat_candidate in CATEGORIES else categorizer.predict(raw_desc)[0]
                            method = "source"
                        else:
                            final_cat, method, conf = categorizer.predict(raw_desc)

                        prepared_rows.append({
                            "date": raw_date,
                            "description": raw_desc,
                            "category": final_cat,
                            "amount": amt_float,
                            "categorization_method": method,
                        })

                    preview_df = pd.DataFrame(prepared_rows)
                    st.session_state["pending_import_df"] = preview_df

                if "pending_import_df" in st.session_state:
                    p_df = st.session_state["pending_import_df"]
                    st.markdown("### Ingestion Preview")
                    st.dataframe(p_df.head(15), use_container_width=True)

                    c_save, c_cancel = st.columns([3, 1])
                    with c_save:
                        if st.button("💾 Confirm & Commit to Database", type="primary", use_container_width=True):
                            records = p_df.to_dict(orient="records")
                            inserted = bulk_insert_transactions(records)
                            st.success(f"🎉 Successfully imported {inserted} transactions into your database!")
                            del st.session_state["pending_import_df"]
                            st.rerun()
                    with c_cancel:
                        if st.button("Cancel", use_container_width=True):
                            del st.session_state["pending_import_df"]
                            st.rerun()

            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    with tab_manual:
        st.subheader("Record a Single Expense")
        with st.form("manual_expense_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                t_date = st.date_input("Date", value=date.today())
                t_desc = st.text_input("Merchant / Description", placeholder="e.g. Trader Joe's Groceries")
                t_amt = st.number_input("Amount ($)", min_value=0.01, max_value=100000.0, value=25.0, step=1.0)
            with f_col2:
                # Predictive category suggestion
                suggested_cat = "Miscellaneous"
                if t_desc:
                    suggested_cat, _, _ = get_categorizer().predict(t_desc)

                t_cat = st.selectbox(
                    "Category",
                    CATEGORIES,
                    index=CATEGORIES.index(suggested_cat) if suggested_cat in CATEGORIES else 0,
                    help="Auto-inferred from description; you can override anytime.",
                )
                t_payment = st.selectbox("Payment Method", ["Card", "Cash", "UPI", "Bank Transfer", "Other"])
                t_notes = st.text_input("Notes (Optional)", placeholder="e.g. Dinner with colleagues")

            submit = st.form_submit_button("➕ Save Transaction", type="primary")
            if submit:
                if not t_desc.strip():
                    st.error("Please enter a valid merchant or description.")
                else:
                    new_id = insert_transaction(
                        date=t_date.strftime("%Y-%m-%d"),
                        description=t_desc,
                        category=t_cat,
                        amount=t_amt,
                        payment_method=t_payment,
                        notes=t_notes,
                    )
                    st.success(f"Transaction #{new_id} saved successfully!")
                    st.rerun()


def render_transactions_page(df: pd.DataFrame):
    """Render transactions table with search, filters, anomaly tags, and data export."""
    st.title("📑 Transaction Ledger")
    st.markdown("Search, filter, inspect anomaly tags, and export your transaction records.")

    if df.empty:
        st.info("No transactions found in database.")
        return

    # Run Anomaly Detector
    detector = ExpenseAnomalyDetector()
    df_with_anom = detector.detect_anomalies(df)

    # Filters Toolbar
    with st.expander("🔍 Filter & Search Options", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)

        with f_col1:
            search_query = st.text_input("Search Description / Merchant", "")
        with f_col2:
            cat_list = ["All"] + sorted(list(df["category"].dropna().unique()))
            selected_cat = st.selectbox("Filter by Category", cat_list)
        with f_col3:
            min_val = float(df["amount"].min())
            max_val = float(df["amount"].max())
            amount_range = st.slider("Amount Range ($)", min_value=0.0, max_value=max(100.0, max_val), value=(min_val, max_val))
        with f_col4:
            anomaly_filter = st.selectbox("Anomaly Status", ["All Transactions", "Flagged Anomalies Only", "Normal Only"])

    # Apply filters
    filtered_df = df_with_anom.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["description"].str.contains(search_query, case=False, na=False)
            | filtered_df["notes"].str.contains(search_query, case=False, na=False)
        ]
    if selected_cat != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_cat]

    filtered_df = filtered_df[
        (filtered_df["amount"] >= amount_range[0]) & (filtered_df["amount"] <= amount_range[1])
    ]

    if anomaly_filter == "Flagged Anomalies Only":
        filtered_df = filtered_df[filtered_df["is_anomaly"] == True]
    elif anomaly_filter == "Normal Only":
        filtered_df = filtered_df[filtered_df["is_anomaly"] == False]

    st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** transactions (Total: **${filtered_df['amount'].sum():,.2f}**)")

    # Display Table
    display_cols = ["id", "date", "description", "category", "amount", "payment_method", "is_anomaly", "severity", "anomaly_reason"]
    st.dataframe(
        filtered_df[display_cols].sort_values("date", ascending=False),
        column_config={
            "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
            "is_anomaly": st.column_config.CheckboxColumn("Outlier?"),
            "severity": st.column_config.TextColumn("Severity"),
            "anomaly_reason": st.column_config.TextColumn("AI Diagnostic Note"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # Actions & Export
    col_exp1, col_exp2, col_del = st.columns([3, 3, 4])
    with col_exp1:
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "📥 Export Filtered to CSV",
            data=csv_buffer.getvalue(),
            file_name=f"expenses_export_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_exp2:
        json_buffer = filtered_df.to_json(orient="records", date_format="iso")
        st.download_button(
            "📥 Export to JSON",
            data=json_buffer,
            file_name=f"expenses_export_{date.today()}.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_del:
        with st.popover("🗑️ Delete a Transaction"):
            del_id = st.number_input("Transaction ID to delete", min_value=1, step=1)
            if st.button("Confirm Delete", type="primary"):
                if delete_transaction(del_id):
                    st.success(f"Transaction #{del_id} deleted!")
                    st.rerun()
                else:
                    st.error("Transaction ID not found.")


def render_reports_page(df: pd.DataFrame):
    """Render budget variance reports, Month-over-Month intelligence, and Anomaly Inspector."""
    st.title("📈 Reports & Budget Comparison")
    st.markdown("Detailed breakdown of monthly budget targets vs actual spending, plus deep AI anomaly diagnostics.")

    if df.empty:
        st.info("No data available for reports. Please add or import transactions.")
        return

    tab_budget, tab_mom, tab_anom = st.tabs([
        "🎯 Budget vs Actual Variance",
        "📊 Month-over-Month (MoM) Analysis",
        "🚨 AI Anomaly Inspector",
    ])

    with tab_budget:
        st.subheader("Monthly Budget Allocation & Variance")
        budgets = get_budgets()

        # Target Month selector
        df_parsed = df.copy()
        df_parsed["date"] = pd.to_datetime(df_parsed["date"])
        available_months = sorted(list(df_parsed["date"].dt.strftime("%Y-%m").unique()), reverse=True)

        sel_month = st.selectbox("Select Target Month", available_months, index=0)
        budget_df = get_budget_comparison(df, budgets, target_year_month=sel_month)

        # Budget vs Actual Grouped Bar Chart
        fig_budget = go.Figure()
        fig_budget.add_trace(go.Bar(
            x=budget_df["category"],
            y=budget_df["actual_spend"],
            name="Actual Spend ($)",
            marker_color="#E53E3E",
        ))
        fig_budget.add_trace(go.Bar(
            x=budget_df["category"],
            y=budget_df["budget"],
            name="Budget Target ($)",
            marker_color="#4A5568",
        ))
        fig_budget.update_layout(
            barmode="group",
            yaxis=dict(title="Amount ($)"),
            margin=dict(l=20, r=20, t=30, b=20),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_budget, use_container_width=True)

        st.markdown("### Budget Health Table")
        st.dataframe(
            budget_df,
            column_config={
                "actual_spend": st.column_config.NumberColumn("Actual Spend ($)", format="$%.2f"),
                "budget": st.column_config.NumberColumn("Budget ($)", format="$%.2f"),
                "remaining": st.column_config.NumberColumn("Variance / Remaining ($)", format="$%.2f"),
                "utilization_pct": st.column_config.ProgressColumn(
                    "Utilization %",
                    format="%.1f%%",
                    min_value=0,
                    max_value=150,
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("⚙️ Edit Monthly Category Budgets"):
            st.write("Update your personal target budgets for any category:")
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                edit_cat = st.selectbox("Category to Edit", CATEGORIES)
            with b_col2:
                curr_budget = budgets.get(edit_cat, 100.0)
                new_budget = st.number_input("Monthly Budget Target ($)", min_value=0.0, max_value=50000.0, value=curr_budget, step=25.0)
            with b_col3:
                st.write("")
                st.write("")
                if st.button("💾 Update Budget", type="primary"):
                    set_budget(edit_cat, new_budget)
                    st.success(f"Budget for {edit_cat} updated to ${new_budget:,.2f}!")
                    st.rerun()

    with tab_mom:
        st.subheader("Month-over-Month (MoM) Growth & Trends")
        mom_df = get_monthly_summary(df)
        st.dataframe(
            mom_df,
            column_config={
                "total_spend": st.column_config.NumberColumn("Total Spend ($)", format="$%.2f"),
                "avg_spend": st.column_config.NumberColumn("Avg Spend / Tx ($)", format="$%.2f"),
                "mom_change": st.column_config.NumberColumn("MoM $ Change", format="$%.2f"),
                "mom_growth_pct": st.column_config.NumberColumn("MoM Growth %", format="%.1f%%"),
            },
            use_container_width=True,
            hide_index=True,
        )

    with tab_anom:
        st.subheader("🚨 AI-Powered Outlier & Anomaly Inspector")
        detector = ExpenseAnomalyDetector()
        anom_df = detector.detect_anomalies(df)
        flagged = anom_df[anom_df["is_anomaly"] == True]

        if flagged.empty:
            st.success("✅ No unusual spending anomalies detected in your transaction history.")
        else:
            st.warning(f"⚠️ Detected **{len(flagged)} unusual spending outliers** that deviate significantly from your typical baseline.")
            st.dataframe(
                flagged[["date", "description", "category", "amount", "severity", "anomaly_score", "anomaly_reason"]],
                column_config={
                    "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
                    "anomaly_score": st.column_config.ProgressColumn("Anomaly Score (0-100)", min_value=0, max_value=100),
                },
                use_container_width=True,
                hide_index=True,
            )


def main():
    """Main application entry point."""
    page = render_sidebar()
    all_df = get_all_transactions()

    if page == "📊 Dashboard":
        render_dashboard(all_df)
    elif page == "📥 Upload & Ingest":
        render_upload_page()
    elif page == "📑 Transactions":
        render_transactions_page(all_df)
    elif page == "📈 Reports & Budgets":
        render_reports_page(all_df)


if __name__ == "__main__":
    main()
