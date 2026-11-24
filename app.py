# ===== 라이브러리 임포트 =====
import streamlit as st
import pandas as pd
import plotly.express as px

# ===== [추가] 페이지 기본 설정 (가장 먼저 실행되는 st 명령이어야 합니다) =====
st.set_page_config(page_title="Titanic 대시보드", layout="wide") # [추가]

# ===== 데이터 로드 및 캐싱 =====
@st.cache_data
def load_data():
    # titanic.csv 파일을 캐싱하여 로드
    return pd.read_csv('titanic.csv')

df = load_data()

# ===== 함수 정의: 데이터 필터링 =====
def filter_data(df, sexes, classes, age_range):
    cond_sex = df['sex'].isin(sexes)
    cond_class = df['pclass'].isin(classes)
    cond_age = (df['age'] >= age_range[0]) & (df['age'] <= age_range[1])
    return df[cond_sex & cond_class & cond_age]

# ===== 함수 정의: KPI 계산 =====
def kpi(df):
    if df.empty:
        return 0, 0, 0
    total_passengers = len(df)
    survival_rate = round((df['survived'].sum() / total_passengers) * 100, 1)
    if df['age'].isnull().all():
        avg_age = 0.0
    else:
        avg_age = round(df['age'].mean(), 1)
    return total_passengers, survival_rate, avg_age

# ===== 함수 정의: 시각화(막대 그래프) =====
def class_rate_bar(df):
    if df.empty:
        return px.bar(title="데이터가 비어 있습니다")
    class_summary = df.groupby('pclass', as_index=False).agg(
        survival_rate=('survived', lambda x: round(x.mean() * 100, 1))
    )
    fig = px.bar(
        class_summary, 
        x='pclass', 
        y='survival_rate', 
        text='survival_rate',
        title='객실 등급별 생존율(%)',
        labels={'pclass': '객실 등급', 'survival_rate': '생존율 (%)'}
    )
    fig.update_traces(textposition='outside')
    return fig

# ===== 함수 정의: 시각화(히스토그램) =====
def age_hist(df):
    if df.empty:
        return px.histogram(title="데이터가 비어 있습니다")
    plot_df = df.copy()
    plot_df['survived'] = plot_df['survived'].map({0: '사망', 1: '생존'})
    fig = px.histogram(
        plot_df, 
        x='age', 
        color='survived', 
        barmode='overlay', 
        opacity=0.6,
        title='생존 여부별 나이 분포',
        labels={'age': '나이', 'survived': '생존 여부', 'count': '승객 수'}
    )
    return fig

# ===== 대시보드 UI 영역 =====
# 대시보드 타이틀
st.title("타이타닉, 누가 살아남았나?")

# 사이드바 필터 구성
st.sidebar.header("필터 설정")

# 1. 성별 선택 (기본값으로 모든 성별 선택)
unique_sexes = df['sex'].unique().tolist()
selected_sexes = st.sidebar.multiselect("성별 선택", options=unique_sexes, default=unique_sexes)

# 2. 객실 등급 선택 (기본값으로 모든 등급 선택)
unique_classes = sorted(df['pclass'].unique().tolist())
selected_classes = st.sidebar.multiselect("객실 등급 선택", options=unique_classes, default=unique_classes)

# 3. 나이 범위 슬라이더
min_age = int(df['age'].min())
max_age = int(df['age'].max())
selected_age_range = st.sidebar.slider("나이 범위", min_value=min_age, max_value=max_age, value=(min_age, max_age))

# ===== 데이터 필터링 적용 =====
filtered_df = filter_data(df, selected_sexes, selected_classes, selected_age_range)

# ===== 본문 출력 =====
# KPI 수치 계산
total_passengers, survival_rate, avg_age = kpi(filtered_df)

# st.columns를 사용하여 상단 KPI 3개를 가로로 나열
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("승객 수", f"{total_passengers} 명")

with col2:
    st.metric("생존율", f"{survival_rate} %")

with col3:
    st.metric("평균 나이", f"{avg_age} 세")

# ===== [추가] 2단 레이아웃으로 차트 배치 =====
chart_col1, chart_col2 = st.columns(2) # [추가]

with chart_col1: # [추가]
    fig_bar = class_rate_bar(filtered_df) # [추가]
    st.plotly_chart(fig_bar, use_container_width=True) # [추가]

with chart_col2: # [추가]
    fig_hist = age_hist(filtered_df) # [추가]
    st.plotly_chart(fig_hist, use_container_width=True) # [추가]

# ===== [추가] 토글 방식으로 데이터 테이블 제공 =====
with st.expander("데이터 보기"): # [추가]
    st.dataframe(filtered_df, use_container_width=True) # [추가]
