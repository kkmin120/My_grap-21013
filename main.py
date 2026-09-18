import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# =========================================================
# 제목
# =========================================================

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 216편의 데이터를 여러 그래프로 살펴봅니다."
)


# =========================================================
# 데이터 불러오기
# =========================================================

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL)


df = load_data()


# =========================================================
# 데이터 전처리
# =========================================================

# 장르가 여러 개 적혀 있으면 첫 번째 장르만 사용
df["genre_first"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

df["genre_first"] = df["genre_first"].replace("", "미상")


# 제작 국가 빈 값 처리
df["nation"] = (
    df["nation"]
    .fillna("미상")
    .astype(str)
    .str.strip()
)

df["nation"] = df["nation"].replace("", "미상")


# 숫자 데이터 변환
df["first_scrn"] = pd.to_numeric(
    df["first_scrn"],
    errors="coerce"
)

df["first_show"] = pd.to_numeric(
    df["first_show"],
    errors="coerce"
)

df["first_week_audi"] = pd.to_numeric(
    df["first_week_audi"],
    errors="coerce"
)

df["total_audi"] = pd.to_numeric(
    df["total_audi"],
    errors="coerce"
)

df["days_in_top10"] = pd.to_numeric(
    df["days_in_top10"],
    errors="coerce"
)


# =========================================================
# 그래프 1
# 장르별 영화 편수 - 도넛 그래프
# =========================================================

st.divider()

st.header("📊 그래프 1. 장르별 영화 편수")

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]


fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    height=550,
    font=dict(size=16),
    legend_title_text="장르"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "이 기간에 박스오피스 10위권에 든 영화는 어떤 장르가 많고, "
    "각 장르가 전체 영화에서 어느 정도의 비율을 차지하는지 알 수 있다."
)


# =========================================================
# 그래프 2
# 장르 안에 영화가 들어 있는 트리맵
# 크기 = 총 관객
# =========================================================

st.divider()

st.header("🌳 그래프 2. 장르별 영화와 총 관객")

treemap_df = df.dropna(
    subset=["total_audi", "movieNm"]
).copy()


fig2 = px.treemap(
    treemap_df,
    path=["genre_first", "movieNm"],
    values="total_audi",
    title="장르 안에 들어 있는 영화와 총 관객"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=700,
    font=dict(size=16)
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "각 장르 안에서 어떤 영화가 많은 관객을 모았는지, "
    "영화별 총 관객 규모의 차이를 한눈에 비교할 수 있다."
)


# =========================================================
# 그래프 3
# 총 관객 수 히스토그램
# =========================================================

st.divider()

st.header("📈 그래프 3. 총 관객 수의 분포")

hist_df = df.dropna(
    subset=["total_audi"]
).copy()


fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_layout(
    height=550,
    font=dict(size=16),
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 수 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# 가장 많이 몰린 구간 계산
counts, bins = pd.cut(
    hist_df["total_audi"],
    bins=20,
    include_lowest=True,
    retbins=True
)

bin_counts = counts.value_counts().sort_index()

most_common_bin = bin_counts.idxmax()

low = int(most_common_bin.left)
high = int(most_common_bin.right)


# 가장 관객이 많은 영화
max_movie = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

max_movie_name = max_movie["movieNm"]
max_movie_audience = int(max_movie["total_audi"])


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    f"대부분의 영화는 총 관객 **{low:,}명 ~ {high:,}명** 구간에 "
    f"가장 많이 몰려 있으며, 총 관객이 가장 많은 영화는 "
    f"**{max_movie_name}**으로 약 **{max_movie_audience:,}명**의 "
    f"관객을 기록했다."
)


# =========================================================
# 그래프 4
# 개봉일 스크린수와 총 관객의 산점도
# =========================================================

st.divider()

st.header("🔵 그래프 4. 개봉일 스크린수와 총 관객의 관계")

scatter_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "movieNm"
    ]
).copy()


fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "genre_first": "장르"
    }
)

fig4.update_traces(
    marker=dict(size=10),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=650,
    font=dict(size=16),
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "개봉일에 스크린을 많이 확보한 영화가 총 관객도 많은지, "
    "그리고 장르에 따라 이러한 관계가 어떻게 나타나는지 비교할 수 있다."
)


# =========================================================
# 그래프 5
# 장르별 총 관객 수 상자 그림
# 영화가 10편 이상인 장르만 사용
# =========================================================

st.divider()

st.header("📦 그래프 5. 장르별 총 관객 분포")


genre_movie_counts = (
    df["genre_first"]
    .value_counts()
)

selected_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index


box_df = df[
    df["genre_first"].isin(selected_genres)
].dropna(
    subset=["total_audi", "movieNm"]
).copy()


fig5 = px.box(
    box_df,
    x="genre_first",
    y="total_audi",
    color="genre_first",
    points="outliers",
    hover_name="movieNm",
    title="영화가 10편 이상인 장르의 총 관객 분포",
    labels={
        "genre_first": "장르",
        "total_audi": "총 관객 수"
    }
)

fig5.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    height=650,
    font=dict(size=16),
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    showlegend=False
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "영화가 10편 이상인 장르끼리 총 관객의 분포와 중앙값을 비교하고, "
    "상자 밖으로 튀어나온 점을 통해 다른 영화보다 총 관객이 특히 많은 "
    "영화를 확인할 수 있다."
)


# =========================================================
# 그래프 6
# 개봉일 스크린수 × 총 관객
# 점 크기 = 첫 주 관객
# =========================================================

st.divider()

st.header("🫧 그래프 6. 첫 주 관객을 크기로 표현한 버블 그래프")


bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi",
        "movieNm"
    ]
).copy()


fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_first",
    hover_name="movieNm",
    size_max=50,
    title="개봉일 스크린수와 총 관객 - 첫 주 관객 버블",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "first_week_audi": "첫 주 관객",
        "genre_first": "장르"
    }
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{marker.size:,}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    height=700,
    font=dict(size=16),
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "개봉일 스크린수와 총 관객의 관계를 보면서, "
    "점의 크기를 통해 개봉 첫 주에 얼마나 많은 관객이 몰렸는지도 "
    "함께 비교할 수 있다."
)


# =========================================================
# 그래프 7
# 제작 국가 → 장르 선버스트
# 크기 = 영화 편수
# =========================================================

st.divider()

st.header("☀️ 그래프 7. 제작 국가별 장르 분포")


sunburst_df = df.dropna(
    subset=["nation", "genre_first", "movieNm"]
).copy()


fig7 = px.sunburst(
    sunburst_df,
    path=["nation", "genre_first"],
    title="제작 국가에서 장르로 내려가는 영화 분포",
    labels={
        "nation": "제작 국가",
        "genre_first": "장르"
    }
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    height=700,
    font=dict(size=16)
)

st.plotly_chart(
    fig7,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "제작 국가별로 어떤 장르의 영화가 많이 포함되어 있는지와 "
    "각 국가와 장르의 영화 편수를 한눈에 비교할 수 있다."
)


# =========================================================
# 그래프 8
# 나만의 질문
# =========================================================

st.divider()

st.header(
    "🔎 그래프 8. 첫 주에 많이 본 영화가 끝까지 오래 살아남았을까?"
)


# 그래프에 사용할 데이터
question_df = df.dropna(
    subset=[
        "first_week_audi",
        "days_in_top10",
        "movieNm"
    ]
).copy()


# 숫자로 변환
question_df["first_week_audi"] = pd.to_numeric(
    question_df["first_week_audi"],
    errors="coerce"
)

question_df["days_in_top10"] = pd.to_numeric(
    question_df["days_in_top10"],
    errors="coerce"
)


# 빈 값 제거
question_df = question_df.dropna(
    subset=[
        "first_week_audi",
        "days_in_top10"
    ]
)


# 산점도
fig8 = px.scatter(
    question_df,
    x="first_week_audi",
    y="days_in_top10",
    color="genre_first",
    hover_name="movieNm",
    title="첫 주에 많이 본 영화가 끝까지 오래 살아남았을까?",
    labels={
        "first_week_audi": "개봉 첫 주 관객",
        "days_in_top10": "10위권에 머문 날수",
        "genre_first": "장르"
    }
)


# 마우스를 올렸을 때 영화명 표시
fig8.update_traces(
    marker=dict(size=10),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉 첫 주 관객: %{x:,}명<br>"
        "10위권에 머문 날수: %{y}일"
        "<extra></extra>"
    )
)


fig8.update_layout(
    height=650,
    font=dict(size=16),
    xaxis_title="개봉 첫 주 관객",
    yaxis_title="10위권에 머문 날수",
    legend_title_text="장르"
)


st.plotly_chart(
    fig8,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "개봉 첫 주에 많은 관객을 모은 영화가 10위권에서도 "
    "오랫동안 머무르는 경향이 있는지 확인할 수 있다."
)


# =========================================================
# 데이터 확인
# =========================================================

st.divider()

st.header("📋 사용한 데이터")

st.write(
    f"전체 영화 수: **{len(df)}편**"
)


st.dataframe(
    df[
        [
            "movieNm",
            "openDt",
            "genre_first",
            "nation",
            "first_scrn",
            "first_show",
            "first_week_audi",
            "total_audi",
            "days_in_top10"
        ]
    ].rename(
        columns={
            "movieNm": "영화명",
            "openDt": "개봉일",
            "genre_first": "장르",
            "nation": "제작 국가",
            "first_scrn": "개봉일 스크린수",
            "first_show": "개봉일 상영횟수",
            "first_week_audi": "개봉 첫 주 관객",
            "total_audi": "총 관객",
            "days_in_top10": "10위권 머문 날수"
        }
    ),
    use_container_width=True,
    hide_index=True
)
