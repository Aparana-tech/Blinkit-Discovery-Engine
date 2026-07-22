import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pathlib import Path

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Blinkit Discovery Engine",
    page_icon="🛒",
    layout="wide"
)

# --- DATA LOADING ---
@st.cache_data
def load_clusters():
    # Load the most recent clusters JSON
    processed_dir = Path("data/processed")
    if not processed_dir.exists():
        return []
    
    files = list(processed_dir.glob("clusters_*.json"))
    if not files:
        return []
        
    # Get the latest file
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    with open(latest_file, "r") as f:
        data = json.load(f)
        
    # Filter out the noise cluster (-1)
    return [d for d in data if d.get("cluster_id", -1) != -1]

@st.cache_data
def load_report():
    insights_dir = Path("data/insights")
    if not insights_dir.exists():
        return "No reports found."
        
    files = list(insights_dir.glob("report_*.md"))
    if not files:
        return "No reports found."
        
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    with open(latest_file, "r") as f:
        return f.read()

# --- MAIN APP ---
st.title("🛒 Blinkit AI Discovery Engine")
st.markdown("Automated intelligence from App Store, Play Store, and Reddit reviews.")

clusters = load_clusters()
report_md = load_report()

if not clusters:
    st.warning("No data found! Please run `python src/main.py` to generate insights.")
    st.stop()

# Build DataFrame for visuals
df = pd.DataFrame(clusters)

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Visual Analytics", "📄 Monthly Insight Report"])

with tab1:
    st.header("Discovery Pillars Breakdown")
    
    # Top Level Metrics
    col1, col2, col3 = st.columns(3)
    total_reviews = sum(df["size"]) if "size" in df else 0
    total_themes = len(df)
    col1.metric("Total Problem Themes", total_themes)
    col2.metric("Affected Users", total_reviews)
    col3.metric("Data Sources", "3 (App, Play, Reddit)")
    
    st.markdown("---")
    
    # Charts
    colA, colB = st.columns(2)
    
    with colA:
        st.subheader("Themes by Impact")
        # Bar chart with custom styling
        fig_bar = px.bar(
            df.sort_values(by="size", ascending=True), 
            x="size", 
            y="theme_name", 
            color="pillar",
            orientation='h',
            title="Top Friction Points",
            labels={"size": "Number of Users", "theme_name": ""},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        # Make background transparent to match Streamlit theme
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=40, b=0),
            clickmode="event+select"
        )
        bar_event = st.plotly_chart(fig_bar, use_container_width=True, on_select="rerun", key="bar_chart")
        
    with colB:
        st.subheader("Pillar Distribution")
        # Pie Chart with custom styling
        pillar_counts = df.groupby("pillar")["size"].sum().reset_index()
        fig_pie = px.pie(
            pillar_counts, 
            values="size", 
            names="pillar",
            title="Where is the friction happening?",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
            clickmode="event+select"
        )
        pie_event = st.plotly_chart(fig_pie, use_container_width=True, on_select="rerun", key="pie_chart")

    st.markdown("---")
    st.subheader("Deep Dive: AI Insights")
    
    # Filter raw data based on chart clicks!
    df_sorted = df.sort_values(by="size", ascending=False)
    
    # Extract selection data safely
    selected_theme = None
    selected_pillar = None
    
    if bar_event and bar_event.selection.get("points"):
        selected_theme = bar_event.selection["points"][0].get("y")
        
    if pie_event and pie_event.selection.get("points"):
        # For pie charts, Plotly returns the label of the slice
        selected_pillar = pie_event.selection["points"][0].get("label")

    if selected_theme:
        st.success(f"🔍 Filtering insights by Theme: **{selected_theme}**")
        df_sorted = df_sorted[df_sorted["theme_name"] == selected_theme]
    elif selected_pillar:
        st.success(f"🔍 Filtering insights by Pillar: **{selected_pillar}**")
        df_sorted = df_sorted[df_sorted["pillar"] == selected_pillar]
    else:
        st.markdown("💡 *Click on any bar or pie slice above to filter these results! Click again to clear.*")
    
    for _, row in df_sorted.iterrows():
        # Create a beautiful expanding card for each problem theme
        with st.expander(f"🔴 **{row['theme_name']}** — {row['size']} users affected ({row['pillar']})"):
            st.markdown(f"**🗣️ User Quote:** \n> *\"{row['best_quote']}\"*")
            st.markdown(f"**💡 AI Recommendation:** \n{row['actionable_insight']}")


with tab2:
    st.header("Automated One-Pager")
    st.info("This report was automatically generated by the Groq LLM based on the cluster data.")
    
    with st.container(border=True):
        st.markdown(report_md)
    
    st.download_button(
        label="📥 Download Report as Markdown",
        data=report_md,
        file_name="blinkit_insights_report.md",
        mime="text/markdown"
    )
