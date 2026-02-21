import streamlit as st
import requests
import urllib.parse

st.set_page_config(page_title="뉴스 모니터링 Pro", layout="wide")
st.title("📡 최신 뉴스 레이더 (정식 API 버전)")

# 1. 사이드바 설정
st.sidebar.header("🔍 검색 설정")
api_key = st.sidebar.text_input("GNews API 키 입력 (필수)", type="password")

default_keywords = ["Tesla", "팔레타이징", "PLC", "산업용 로봇", "해양경찰"]
search_term = st.sidebar.selectbox("키워드 선택", default_keywords)
custom_keyword = st.sidebar.text_input("직접 검색어 입력")
if custom_keyword:
    search_term = custom_keyword

st.sidebar.markdown("---")
sort_order = st.sidebar.radio("정렬 순서", ("최신순", "관련도순"))
sort_by = "publishedAt" if sort_order == "최신순" else "relevance"

# 2. 뉴스 검색 함수
def get_news(query, key, sort):
    encoded_query = urllib.parse.quote(query)
    url = f"https://gnews.io/api/v4/search?q={encoded_query}&apikey={key}&lang=ko&sortby={sort}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        # 에러의 진짜 원인을 화면에 빨간색으로 띄움
        st.error(f"🚨 API 에러 상세: {response.text}")
        return []

# 3. 실행 버튼
if st.button("뉴스 검색 시작 🚀"):
    if not api_key:
        st.warning("왼쪽 사이드바에 API 키를 먼저 입력해줘!")
    else:
        st.write(f"**'{search_term}'** 키워드로 검색 중...")
        articles = get_news(search_term, api_key, sort_by)
        
        if not articles:
            st.warning("조건에 맞는 뉴스가 없거나 접속에 실패했어.")
        elif len(articles) > 0:
            st.success(f"성공! {len(articles)}개의 기사를 찾았어.")
            st.markdown("---")
            
            for article in articles:
                with st.container():
                    st.subheader(f"📰 {article['title']}")
                    st.text(f"출처: {article['source']['name']} | {article['publishedAt'][:10]}")
                    st.link_button("👉 기사 원문 보러가기", article['url'])
                    st.markdown("---")
