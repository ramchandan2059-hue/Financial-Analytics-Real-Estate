"""
Buyer Segmentation and Investment Profiling - Streamlit dashboard
Run from the project root:  streamlit run app.py
Data: client_segmentation.csv (one row per client, K-Means label in `cluster`)
"""
from pathlib import Path

import importlib

import numpy as np
import pandas as pd
import plotly.express as px  # type: ignore[import-not-found]
import streamlit as st  # type: ignore[import-not-found]

st.set_page_config(page_title="Buyer Segmentation", page_icon="🏢", layout="wide")

ROOT = Path(__file__).parent
CANDIDATES = [
    ROOT / "data" / "processed" / "client_segmentation.csv",
    ROOT / "data" / "processed" / "client_segments.csv",
    ROOT / "notebooks" / "data" / "processed" / "client_segmentation.csv",
    ROOT / "client_segmentation.csv",
]

# Names derived from the cluster profiles in the data.
DATA_NAMES = {0: "Value Buyers", 1: "Satisfied Mid-Market", 2: "Bulk Multi-Unit Buyers", 3: "Premium Buyers"}
DATA_DESC = {
    "Value Buyers": "Lowest spend, price and unit size; lowest satisfaction.",
    "Satisfied Mid-Market": "Mid-range spend and size; clearly the happiest clients.",
    "Bulk Multi-Unit Buyers": "Small group buying about twice as many units; oldest; mostly website-referred.",
    "Premium Buyers": "Highest average price and largest units; below-average satisfaction.",
}
# Names assigned as in PRD .
NOTEBOOK_NAMES = {0: "Corporate Buyers", 1: "First-Time Buyers", 2: "Luxury Investors", 3: "Global Investors"}

ISO3 = {"usa": "USA", "uk": "GBR", "canada": "CAN", "germany": "DEU", "france": "FRA",
        "belgium": "BEL", "mexico": "MEX", "australia": "AUS", "russia": "RUS", "denmark": "DNK"}
LABELS = {"usa": "USA", "uk": "UK"}


def nice(v):
    """Display label for lowercase category values."""
    return LABELS.get(v, str(v).replace("_", " ").title())


@st.cache_data
def load(source) -> pd.DataFrame:
    df = pd.read_csv(source)
    df["Loan"] = df["loan_applied"].map({1: "Loan applied", 0: "No loan"})
    df["is_investment"] = (df["acquisition_purpose"] == "investment").astype(int)
    df["is_company"] = (df["client_type"] == "company").astype(int)
    df["country_label"] = df["country"].map(nice)
    df["iso"] = df["country"].map(ISO3)

    
    if "country_freq" not in df.columns:
        df["country_freq"] = df["country"].map(df["country"].value_counts())
    if "log_total_spend" not in df.columns:
        df["log_total_spend"] = np.log1p(df["total_spend"])
    if "log_avg_price" not in df.columns:
        df["log_avg_price"] = np.log1p(df["avg_price"])
    return df


df = None
for p in CANDIDATES:
    if p.exists():
        df = load(p)
        break
if df is None:
    st.warning("client_segmentation.csv not found in the project. Upload it below.")
    up = st.file_uploader("Upload client_segmentation.csv", type="csv")
    if up:
        df = load(up)
if df is None:
    st.error("No client segmentation data is available.")
    st.stop()
assert df is not None

#  sidebar
st.sidebar.header("Filters")
naming = st.sidebar.radio(
    "Segment names",
    ["Data-driven (recommended)", "Notebook names"],
    help="The notebook names (Corporate, First-Time, Luxury, Global) do not match the cluster "
         "profiles: only about 5% of every cluster is a company, and ages and loan rates are the "
         "same across clusters. Data-driven names follow what each cluster actually shows.",
)
names = DATA_NAMES if naming.startswith("Data") else NOTEBOOK_NAMES
df = df.assign(Segment=df["cluster"].map(names))
order = [names[k] for k in sorted(names)]


def pick(label, col):
    assert df is not None
    return st.sidebar.multiselect(label, sorted(df[col].unique()), format_func=nice)


s_country = pick("Country", "country")
s_region = pick("Region", "region")
s_purpose = pick("Acquisition purpose", "acquisition_purpose")
s_type = pick("Client type", "client_type")
s_seg = st.sidebar.multiselect("Segment", order)
age_rng = st.sidebar.slider("Age range", int(df.age.min()), int(df.age.max()),
                            (int(df.age.min()), int(df.age.max())))

f = df[df.age.between(*age_rng)]
for col, sel in [("country", s_country), ("region", s_region), ("acquisition_purpose", s_purpose),
                 ("client_type", s_type), ("Segment", s_seg)]:
    if sel:
        f = f[f[col].isin(sel)]

st.sidebar.download_button("Download filtered data", f.to_csv(index=False).encode(),
                           "filtered_clients.csv", "text/csv")

#  header
st.title("Buyer Segmentation and Investment Profiling")
st.caption("K-Means segmentation of 2,000 real estate buyers (K = 4) on behavior, spend and demographics")
if f.empty:
    st.warning("No clients match the current filters.")
    st.stop()

m = st.columns(5)
m[0].metric("Clients", f"{len(f):,}", f"{len(f) / len(df):.0%} of all")
m[1].metric("Total spend", f"{f.total_spend.sum() / 1e6:,.1f}M")
m[2].metric("Avg satisfaction", f"{f.satisfaction_score.mean():.2f} / 5")
m[3].metric("Investment share", f"{f.is_investment.mean():.0%}")
m[4].metric("Loan rate", f"{f.loan_applied.mean():.0%}")

t1, t2, t3, t4 = st.tabs(["Segmentation Overview", "Investor Behavior",
                          "Geographic Analysis", "Segment Insights"])
color_args = dict(category_orders={"Segment": order})

# 1. overview : The distribution about the segment,  features like total spend, units_bought, satisfaction_score ....
with t1:
    cnt = f.Segment.value_counts().reindex(order).dropna().rename_axis("Segment").reset_index(name="Clients")
    a, b = st.columns(2)
    a.plotly_chart(px.pie(cnt, names="Segment", values="Clients", hole=0.45,
                          title="Cluster distribution", **color_args), width="stretch")
    b.plotly_chart(px.bar(cnt, x="Segment", y="Clients", color="Segment", text="Clients",
                          title="Clients per segment", **color_args), width="stretch")
    st.plotly_chart(px.scatter(f, x="total_spend", y="satisfaction_score", color="Segment",
                               size="units_bought", opacity=0.6, hover_data=["client_id"],
                               title="Total spend vs satisfaction (bubble = units bought)",
                               **color_args), width="stretch")

#  2. investor behavior :- Shows the behaviour of investors into different features based on segmentation.
with t2:
    a, b = st.columns(2)
    a.plotly_chart(px.histogram(f, x="Segment", color="acquisition_purpose", barmode="group",
                                title="Acquisition purpose by segment", **color_args),
                   width="stretch")
    b.plotly_chart(px.histogram(f, x="Segment", color="Loan", barmode="group",
                                title="Loan behavior by segment", **color_args),
                   width="stretch")
    a, b = st.columns(2)
    a.plotly_chart(px.box(f, x="Segment", y="total_spend", color="Segment",
                          title="Total spend by segment", **color_args), width="stretch")
    b.plotly_chart(px.box(f, x="Segment", y="avg_price", color="Segment",
                          title="Average unit price by segment", **color_args), width="stretch")
    a, b = st.columns(2)
    ref = f.groupby(["Segment", "referral_channel"]).size().reset_index(name="Clients")
    a.plotly_chart(px.bar(ref, x="Segment", y="Clients", color="referral_channel", barmode="relative",
                          title="Referral channel by segment", **color_args), width="stretch")
    b.plotly_chart(px.histogram(f, x="units_bought", color="Segment", nbins=13,
                                title="Units bought per client", **color_args), width="stretch")

# 3. geographic : Distribution based on Geography
with t3:
    geo = f.groupby(["country_label", "iso"]).size().reset_index(name="Clients")
    st.plotly_chart(px.choropleth(geo, locations="iso", color="Clients", hover_name="country_label",
                                  color_continuous_scale="Blues", title="Clients by country"),
                    width="stretch")
    a, b = st.columns(2)
    mix = f.groupby(["country_label", "Segment"]).size().reset_index(name="Clients")
    a.plotly_chart(px.bar(mix, x="country_label", y="Clients", color="Segment",
                          title="Segments by country (counts)", **color_args), width="stretch")
    pct = (pd.crosstab(f.country_label, f.Segment, normalize="index") * 100).round(1)
    b.plotly_chart(px.imshow(pct, text_auto=True, aspect="auto", color_continuous_scale="Blues",
                             title="Segment mix within each country (%)"), width="stretch")
    tree = f.groupby(["country_label", "region"]).size().reset_index(name="Clients")
    tree["region"] = tree["region"].map(nice)
    st.plotly_chart(px.treemap(tree, path=["country_label", "region"], values="Clients",
                               title="Country and region breakdown"), width="stretch")
    st.caption("Note: about 77% of clients are in the USA, so shares in small countries rest on few clients.")

#  4. insights
with t4:
    prof = f.groupby("Segment").agg(
        Clients=("client_id", "count"), Avg_age=("age", "mean"),
        Satisfaction=("satisfaction_score", "mean"), Units=("units_bought", "mean"),
        Total_spend=("total_spend", "mean"), Avg_price=("avg_price", "mean"),
        Avg_area_sqft=("avg_area", "mean"), Loan_rate=("loan_applied", "mean"),
        Investment_share=("is_investment", "mean"), Company_share=("is_company", "mean"),
    ).reindex(order).dropna().round(2)
    st.subheader("Descriptive statistics per segment")
    st.dataframe(prof, width="stretch")

    metrics = [c for c in prof.columns if c != "Clients"]
    overall = f[["age", "satisfaction_score", "units_bought", "total_spend", "avg_price", "avg_area",
                 "loan_applied", "is_investment", "is_company"]].mean()
    overall.index = metrics
    rel = (prof[metrics] / overall - 1) * 100
    st.plotly_chart(px.imshow(rel.round(0), text_auto=True, aspect="auto",
                              color_continuous_scale="RdBu_r", color_continuous_midpoint=0,
                              title="Difference from the average client (%)"),
                    width="stretch")

    st.subheader("What defines each segment")
    for seg in prof.index:
        row = rel.loc[seg]
        top = row.abs().sort_values(ascending=False).head(3).index
        bullets = ", ".join(
            f"{k.replace('_', ' ').lower()} {float(row[k]):+.0f}%" for k in top
        )
        segment_count = int(prof.at[seg, "Clients"])
        desc = DATA_DESC.get(seg, "") if naming.startswith("Data") else ""
        st.markdown(
            f"**{seg}** ({segment_count} clients): {desc}  \n"
            f"Biggest differences from average: {bullets}."
        )

    st.subheader("Segment drill-down")
    seg = st.selectbox("Choose a segment", list(prof.index))
    s = f[f.Segment == seg]
    d = st.columns(4)
    d[0].metric("Clients", len(s))
    d[1].metric("Avg age", f"{s.age.mean():.1f}")
    d[2].metric("Avg spend", f"{s.total_spend.mean():,.0f}")
    d[3].metric("Loan rate", f"{s.loan_applied.mean():.0%}")
    a, b, c = st.columns(3)
    for box, col, ttl in [(a, "country_label", "Top countries"), (b, "referral_channel", "Referral"),
                          (c, "acquisition_purpose", "Purpose")]:
        vc = s[col].value_counts().head(8).rename_axis(col).reset_index(name="Clients")
        box.plotly_chart(px.bar(vc, x="Clients", y=col, orientation="h", title=ttl)
                         .update_yaxes(autorange="reversed"), width="stretch")
    with st.expander("Client records"):
        st.dataframe(s.drop(columns=["first_name", "last_name", "Loan", "iso", "country_label",
                                     "is_investment", "is_company", "country_freq",
                                     "log_total_spend", "log_avg_price"], errors="ignore"),
                     width="stretch")

