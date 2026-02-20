import streamlit as st
import feedparser
import urllib.parse
import requests
import time
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="뉴스 모니터링 Pro", layout="wide")
st.title("📡 최신 뉴스 레이더 (기간/정렬/출처 설정)")
st.caption("구글/Bing 엔진을 사용하여 뉴스를 맞춤 검색합니다.")

# 2. 사이드바 설정
st.sidebar.header("🔍 검색 설정")
default_keywords = ["Tesla", "팔레타이징", "PLC", "산업용 로봇", "해양경찰"]
selected_keyword = st.sidebar.selectbox("키워드 선택", default_keywords)
custom_keyword = st.sidebar.text_input("직접 검색어 입력 (해외 뉴스는 영어로 입력 권장)")

search_term = custom_keyword if custom_keyword else selected_keyword

st.sidebar.markdown("---")

sort_order = st.sidebar.radio("정렬 순서", ("최신순", "과거순"))

st.sidebar.markdown("---")

news_type = st.sidebar.radio("뉴스 종류", ("국내 뉴스", "해외 뉴스"))

st.sidebar.markdown("---")

time_option = st.sidebar.selectbox(
    "기간 선택",
    ("지난 24시간 (1d)", "지난 1주일 (7d)", "지난 1달 (1m)", "특정 기간 지정"),
    index=0
)

period_cmd = ""
if "24시간" in time_option:
    period_cmd = " when:1d"
elif "1주일" in time_option:
    period_cmd = " when:7d"
elif "1달" in time_option:
    period_cmd = " when:30d"
else:
    start_date = st.sidebar.date_input("시작일", datetime.today() - timedelta(days=7))
    end_date = st.sidebar.date_input("종료일", datetime.today())
    period_cmd = f" after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"

st.sidebar.markdown("---")

# 3. 뉴스 수집 함수 (구글 RSS)
def get_google_rss(query, period, is_global=False):
    full_query = query + period
    encoded_query = urllib.parse.quote(full_query)
    
    if is_global:
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"
    else:
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return feed.entries
    except:
        return []
    return []

# 4. 뉴스 수집 함수 (Bing)
def get_bing_rss(query, is_global=False):
    encoded_query = urllib.parse.quote(query)
    
    if is_global:
        url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss&sortBy=Date&mkt=en-US"
    else:
        url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss&sortBy=Date&mkt=ko-KR"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return feed.entries
    except:
        return []
    return []

# 5. 실행 버튼
if st.button("뉴스 검색 시작 🚀"):
    is_global = (news_type == "해외 뉴스")
    
    final_search_term = search_term

    st.write(f"**'{search_term}'** 키워드로 **{news_type}**를 검색합니다...")
    
    news_items = get_google_rss(final_search_term, period_cmd, is_global)
    source_used = "Google News"
    
    if not news_items:
        st.write("😅 구글 접속 지연, Bing에서 찾습니다...")
        news_items = get_bing_rss(final_search_term, is_global)
        source_used = "Bing News"
    
    if not news_items:
        st.warning("조건에 맞는 뉴스가 없거나 접속이 차단됐어.")
    else:
        is_reverse = True if sort_order == "최신순" else False
        news_items.sort(key=lambda x: x.get('published_parsed') or time.localtime(0), reverse=is_reverse)

        st.success(f"성공! {source_used}에서 {len(news_items)}개의 기사를 가져왔어.")
        st.markdown("---")
        
        for item in news_items:
            with st.container():
                st.subheader(f"📰 {item.title}")
                
                published = item.get('published', '날짜 정보 없음')
                source = item.get('source', {}).get('title', source_used)
                
                st.text(f"출처: {source} | {published}")
                
                link = item.get('link')
                if link:
                    st.link_button("👉 기사 원문 보러가기", link)
                
                st.markdown("---")
