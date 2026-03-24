import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Telco Churn Analysis",
    page_icon="📡",
    layout="wide"
)

DB_PATH = r"dev.duckdb"

@st.cache_resource
def get_con():
    return duckdb.connect(DB_PATH, read_only=True)

@st.cache_data
def query(sql):
    return get_con().execute(sql).df()

st.title("📡 Telco Customer Churn Analysis")
st.caption("Built with dbt + DuckDB + Streamlit · IBM Telco Dataset · 7,043 customers")

# ── KPI row ───────────────────────────────────────────────────────────────────
total, churned, churn_rate, avg_monthly, avg_ltv = query("""
    SELECT
        COUNT(*)                                                    as total,
        COUNT(CASE WHEN has_churned THEN 1 END)                     as churned,
        ROUND(COUNT(CASE WHEN has_churned THEN 1 END)*100.0/COUNT(*),1) as churn_rate,
        ROUND(AVG(monthly_charges),2)                               as avg_monthly,
        ROUND(AVG(lifetime_value),2)                                as avg_ltv
    FROM dev.fct_churn
""").values[0]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Customers",   f"{int(total):,}")
k2.metric("Churned",           f"{int(churned):,}")
k3.metric("Churn Rate",        f"{churn_rate}%")
k4.metric("Avg Monthly Charge",f"${avg_monthly}")
k5.metric("Avg Lifetime Value",f"${avg_ltv:,.0f}")

st.divider()

# ── Row 1: Churn by tenure bucket | Churn by contract ─────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Churn rate by tenure")
    df = query("""
        SELECT
            tenure_bucket,
            tenure_bucket_order,
            COUNT(*)                                                        as customers,
            COUNT(CASE WHEN has_churned THEN 1 END)                         as churned,
            ROUND(COUNT(CASE WHEN has_churned THEN 1 END)*100.0/COUNT(*),1) as churn_rate_pct
        FROM dev.fct_churn
        GROUP BY tenure_bucket, tenure_bucket_order
        ORDER BY tenure_bucket_order
    """)
    fig = px.bar(
        df, x="tenure_bucket", y="churn_rate_pct",
        text="churn_rate_pct",
        color="churn_rate_pct",
        color_continuous_scale="Reds",
        labels={"tenure_bucket": "Tenure", "churn_rate_pct": "Churn rate (%)"}
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, yaxis_range=[0, 65],
                      margin=dict(t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Customers in their first 6 months churn at 5x the rate of long-term customers.")

with c2:
    st.subheader("Churn rate by contract type")
    df = query("""
        SELECT
            contract_type,
            COUNT(*)                                                        as customers,
            COUNT(CASE WHEN has_churned THEN 1 END)                         as churned,
            ROUND(COUNT(CASE WHEN has_churned THEN 1 END)*100.0/COUNT(*),1) as churn_rate_pct
        FROM dev.fct_churn
        GROUP BY contract_type
        ORDER BY churn_rate_pct DESC
    """)
    fig = px.bar(
        df, x="contract_type", y="churn_rate_pct",
        text="churn_rate_pct",
        color="contract_type",
        color_discrete_sequence=["#E24B4A", "#EF9F27", "#639922"],
        labels={"contract_type": "Contract", "churn_rate_pct": "Churn rate (%)"}
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_range=[0, 55],
                      margin=dict(t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Month-to-month customers churn at nearly 10x the rate of two-year contract holders.")

st.divider()

# ── Row 2: Monthly charges distribution | Churn by internet service ────────────
c3, c4 = st.columns(2)

with c3:
    st.subheader("Monthly charges: churned vs retained")
    df = query("""
        SELECT
            monthly_charges,
            CASE WHEN has_churned THEN 'Churned' ELSE 'Retained' END as status
        FROM dev.fct_churn
    """)
    fig = px.histogram(
        df, x="monthly_charges", color="status",
        barmode="overlay", nbins=40, opacity=0.75,
        color_discrete_map={"Churned": "#E24B4A", "Retained": "#378ADD"},
        labels={"monthly_charges": "Monthly charges ($)", "count": "Customers"}
    )
    fig.update_layout(margin=dict(t=20, b=0), legend_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Churned customers skew toward higher monthly charges — pricing sensitivity is a real signal.")

with c4:
    st.subheader("Churn by internet service type")
    df = query("""
        SELECT
            internet_service_type,
            COUNT(*)                                                        as customers,
            COUNT(CASE WHEN has_churned THEN 1 END)                         as churned,
            ROUND(COUNT(CASE WHEN has_churned THEN 1 END)*100.0/COUNT(*),1) as churn_rate_pct
        FROM dev.fct_churn
        GROUP BY internet_service_type
        ORDER BY churn_rate_pct DESC
    """)
    fig = px.bar(
        df, x="internet_service_type", y="churn_rate_pct",
        text="churn_rate_pct",
        color="internet_service_type",
        color_discrete_sequence=["#E24B4A", "#EF9F27", "#639922"],
        labels={"internet_service_type": "Internet service", "churn_rate_pct": "Churn rate (%)"}
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_range=[0, 50],
                      margin=dict(t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Fiber optic customers churn at nearly double the rate of DSL — likely a pricing issue.")

st.divider()

# ── Row 3: High value churn | Add-on services vs churn ────────────────────────
c5, c6 = st.columns(2)

with c5:
    st.subheader("High value vs standard customers")
    df = query("""
        SELECT
            CASE WHEN is_high_value THEN 'High value' ELSE 'Standard' END  as segment,
            COUNT(*)                                                        as customers,
            COUNT(CASE WHEN has_churned THEN 1 END)                         as churned,
            ROUND(COUNT(CASE WHEN has_churned THEN 1 END)*100.0/COUNT(*),1) as churn_rate_pct,
            ROUND(AVG(monthly_charges),2)                                   as avg_monthly
        FROM dev.fct_churn
        GROUP BY is_high_value
    """)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Customers", x=df["segment"], y=df["customers"],
        marker_color=["#378ADD", "#7F77DD"], yaxis="y"
    ))
    fig.add_trace(go.Scatter(
        name="Churn rate %", x=df["segment"], y=df["churn_rate_pct"],
        mode="markers+lines", marker=dict(size=10, color="#E24B4A"),
        yaxis="y2"
    ))
    fig.update_layout(
        yaxis=dict(title="Customers"),
        yaxis2=dict(title="Churn rate (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=20, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("High value customers churn less — but losing one hurts more given their $91 avg monthly spend.")

with c6:
    st.subheader("Churn rate by add-on service count")
    df = query("""
        SELECT
            addon_service_count,
            COUNT(*)                                                        as customers,
            ROUND(COUNT(CASE WHEN has_churned THEN 1 END)*100.0/COUNT(*),1) as churn_rate_pct
        FROM dev.fct_churn
        GROUP BY addon_service_count
        ORDER BY addon_service_count
    """)
    fig = px.line(
        df, x="addon_service_count", y="churn_rate_pct",
        markers=True,
        labels={"addon_service_count": "Number of add-on services", "churn_rate_pct": "Churn rate (%)"},
        color_discrete_sequence=["#E24B4A"]
    )
    fig.update_layout(yaxis_range=[0, 55], margin=dict(t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("More add-ons = lower churn. Customers embedded in the ecosystem stay longer.")

st.divider()

# ── Row 4: Churn heatmap by tenure + contract ─────────────────────────────────
st.subheader("Churn rate heatmap — tenure vs contract type")
df = query("""
    SELECT
        tenure_bucket,
        tenure_bucket_order,
        contract_type,
        ROUND(COUNT(CASE WHEN has_churned THEN 1 END)*100.0/COUNT(*),1) as churn_rate_pct
    FROM dev.fct_churn
    GROUP BY tenure_bucket, tenure_bucket_order, contract_type
    ORDER BY tenure_bucket_order
""")
pivot = df.pivot(index="contract_type", columns="tenure_bucket", values="churn_rate_pct")
ordered_cols = df.sort_values("tenure_bucket_order")["tenure_bucket"].unique().tolist()
pivot = pivot[[c for c in ordered_cols if c in pivot.columns]]

fig = px.imshow(
    pivot,
    color_continuous_scale="Reds",
    text_auto=True,
    aspect="auto",
    labels=dict(x="Tenure bucket", y="Contract type", color="Churn %")
)
fig.update_layout(margin=dict(t=20, b=0))
st.plotly_chart(fig, use_container_width=True)
st.caption("The top-left cell is the danger zone: month-to-month customers in their first 6 months. This is where retention spend should be focused.")

st.divider()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
**Data pipeline:** `raw CSV` → `stg_telco__customers` → `int_customers_enriched` → `dim_customers` / `fct_churn`  
**Tests:** 22 passing · **Rows:** 7,043 · **Source:** IBM Telco Dataset via Kaggle
""")