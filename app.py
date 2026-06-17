import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="음주운전 사고 분석 대시보드",
    page_icon="🚨",
    layout="wide",
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e, #2d2d44);
        border: 1px solid #3d3d5c;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-label {
        color: #aaa;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #fff;
        font-size: 32px;
        font-weight: bold;
    }
    .metric-delta-neg {
        color: #ff6b6b;
        font-size: 13px;
    }
    .metric-delta-pos {
        color: #51cf66;
        font-size: 13px;
    }
    h1 { color: #ffffff; }
    .stApp { background-color: #0f0f1a; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("data/drunk_driving_accidents.csv")
    return df


df = load_data()

# ── 사이드바 필터 ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 필터")
    years = sorted(df["사고년도"].unique(), reverse=True)
    selected_year = st.selectbox("연도", years)

    regions = ["전체"] + sorted(df["시도"].unique().tolist())
    selected_region = st.selectbox("시도", regions)

    st.markdown("---")
    st.markdown("**데이터 출처**")
    st.markdown("TAAS 교통사고분석시스템")
    st.caption("※ 현재 샘플 데이터입니다.\nAPI 연동 후 실제 데이터로 교체 예정")

# ── 데이터 필터링 ──────────────────────────────────────────────
df_year = df[df["사고년도"] == selected_year].copy()
df_prev = df[df["사고년도"] == selected_year - 1].copy()

if selected_region != "전체":
    df_year = df_year[df_year["시도"] == selected_region]
    df_prev = df_prev[df_prev["시도"] == selected_region]

# ── 헤더 ──────────────────────────────────────────────────────
st.markdown(f"# 🚨 음주운전 사고 분석 대시보드")
st.markdown(f"**{selected_year}년** {'· ' + selected_region if selected_region != '전체' else '· 전국'}")
st.markdown("---")

# ── 핵심 지표 카드 ────────────────────────────────────────────
total_accidents = int(df_year["사고건수"].sum())
total_deaths = int(df_year["사망자수"].sum())
total_injuries = int(df_year["부상자수"].sum())

prev_accidents = int(df_prev["사고건수"].sum()) if not df_prev.empty else 0
prev_deaths = int(df_prev["사망자수"].sum()) if not df_prev.empty else 0

def delta_str(current, prev):
    if prev == 0:
        return ""
    diff = current - prev
    pct = diff / prev * 100
    sign = "▲" if diff > 0 else "▼"
    cls = "metric-delta-neg" if diff > 0 else "metric-delta-pos"
    return f'<span class="{cls}">{sign} {abs(diff):,}건 ({abs(pct):.1f}%)</span>'

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">총 사고건수</div>
        <div class="metric-value">{total_accidents:,}</div>
        {delta_str(total_accidents, prev_accidents)}
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">사망자수</div>
        <div class="metric-value" style="color:#ff6b6b">{total_deaths:,}</div>
        {delta_str(total_deaths, prev_deaths)}
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">부상자수</div>
        <div class="metric-value" style="color:#ffd43b">{total_injuries:,}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    rate = total_deaths / total_accidents * 100 if total_accidents > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">사고 치사율</div>
        <div class="metric-value" style="color:#ff6b6b">{rate:.2f}%</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 지도 + 시도별 차트 ────────────────────────────────────────
map_col, chart_col = st.columns([6, 4])

with map_col:
    st.markdown("### 📍 사고 위치 지도")

    center_lat = df_year["위도"].mean() if not df_year.empty else 36.5
    center_lon = df_year["경도"].mean() if not df_year.empty else 127.5

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7 if selected_region == "전체" else 11,
        tiles="CartoDB dark_matter",
    )

    for _, row in df_year.iterrows():
        radius = max(6, min(30, row["사고건수"] / 5))
        color = "#ff6b6b" if row["사망자수"] >= 3 else "#ffd43b" if row["사망자수"] >= 1 else "#74c0fc"

        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"""<b>{row['시도']} {row['시군구']}</b><br>
                사고건수: {row['사고건수']:,}건<br>
                사망자: {row['사망자수']}명<br>
                부상자: {row['부상자수']}명""",
                max_width=200,
            ),
            tooltip=f"{row['시군구']} {row['사고건수']}건",
        ).add_to(m)

    # 범례
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: rgba(0,0,0,0.75); padding: 10px 14px; border-radius: 8px;
                color: white; font-size: 13px;">
        <b>사망자 수</b><br>
        <span style="color:#ff6b6b">●</span> 3명 이상<br>
        <span style="color:#ffd43b">●</span> 1~2명<br>
        <span style="color:#74c0fc">●</span> 0명<br>
        <i style="font-size:11px">원 크기 = 사고건수</i>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=500)

with chart_col:
    st.markdown("### 📊 시도별 사고 현황")

    region_df = df_year.groupby("시도").agg(
        사고건수=("사고건수", "sum"),
        사망자수=("사망자수", "sum"),
    ).reset_index().sort_values("사고건수", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=region_df["시도"],
        x=region_df["사고건수"],
        name="사고건수",
        orientation="h",
        marker_color="#74c0fc",
    ))
    fig.add_trace(go.Bar(
        y=region_df["시도"],
        x=region_df["사망자수"],
        name="사망자수",
        orientation="h",
        marker_color="#ff6b6b",
    ))
    fig.update_layout(
        barmode="overlay",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(gridcolor="#333"),
        yaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── 연도별 추이 ───────────────────────────────────────────────
st.markdown("### 📈 연도별 사고 추이")

trend_df = df.copy()
if selected_region != "전체":
    trend_df = trend_df[trend_df["시도"] == selected_region]

trend = trend_df.groupby("사고년도").agg(
    사고건수=("사고건수", "sum"),
    사망자수=("사망자수", "sum"),
    부상자수=("부상자수", "sum"),
).reset_index()

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=trend["사고년도"], y=trend["사고건수"],
    name="사고건수", line=dict(color="#74c0fc", width=3),
    mode="lines+markers", marker=dict(size=8),
))
fig2.add_trace(go.Scatter(
    x=trend["사고년도"], y=trend["사망자수"],
    name="사망자수", line=dict(color="#ff6b6b", width=3),
    mode="lines+markers", marker=dict(size=8),
    yaxis="y2",
))
fig2.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#ffffff",
    height=320,
    xaxis=dict(gridcolor="#333", dtick=1),
    yaxis=dict(title="사고건수", gridcolor="#333"),
    yaxis2=dict(title="사망자수", overlaying="y", side="right", gridcolor="#333"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig2, use_container_width=True)

# ── 상세 데이터 테이블 ────────────────────────────────────────
with st.expander("📋 상세 데이터 보기"):
    display_df = df_year[["시도", "시군구", "사고건수", "사망자수", "부상자수", "중상자수", "경상자수"]].sort_values("사고건수", ascending=False)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
