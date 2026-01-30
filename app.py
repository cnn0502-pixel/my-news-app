import streamlit as st
import feedparser
import urllib.parse
import requests
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="뉴스 모니터링 Pro", layout="wide")
st.title("📡 최신 뉴스 레이더 (기간 설정 기능 포함)")
st.caption("구글/Bing 엔진을 사용하여 최신 뉴스를 기간별로 가져옵니다.")

# 2. 사이드바 설정
st.sidebar.header("🔍 검색 설정")
default_keywords = ["팔레타이징", "PLC 제어", "산업용 로봇", "테슬라", "해양경찰"]
selected_keyword = st.sidebar.selectbox("키워드 선택", default_keywords)
custom_keyword = st.sidebar.text_input("직접 검색어 입력")

search_term = custom_keyword if custom_keyword else selected_keyword

st.sidebar.markdown("---")

# ★ 부활한 기간 설정 기능
time_option = st.sidebar.selectbox(
    "기간 선택",
    ("지난 24시간 (1d)", "지난 1주일 (7d)", "지난 1달 (1m)"),
    index=0
)

# 선택한 옵션을 구글 검색 명령어(when:1d 등)로 변환
if "24시간" in time_option:
    period_cmd = " when:1d"
elif "1주일" in time_option:
    period_cmd = " when:7d"
else:
    period_cmd = " when:30d"

st.sidebar.markdown("---")

# 3. 뉴스 수집 함수 (구글 RSS + 기간 명령어 적용)
def get_google_rss(query, period):
    # 검색어 뒤에 ' when:1d' 같은 명령어를 붙여서 인코딩
    full_query = query + period
    encoded_query = urllib.parse.quote(full_query)
    
    # 구글 뉴스 RSS (한국어, 최신순 정렬 시도)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return feed.entries
    except:
        return []
    return []

# 4. 백업용 뉴스 수집 함수 (Bing)
def get_bing_rss(query):
    encoded_query = urllib.parse.quote(query)
    # Bing은 sortBy=Date로 최신순 유도
    url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss&sortBy=Date"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
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
    st.write(f"**'{search_term}'** 키워드로 **{time_option}** 동안의 뉴스를 검색합니다...")
    
    # 1차 시도: 구글 (기간 설정 적용됨)
    news_items = get_google_rss(search_term, period_cmd)
    source_used = "Google News"
    
    # 실패 시 2차 시도: Bing (기간 설정은 약하지만 최신순)
    if not news_items:
        st.write("😅 구글 접속이 원활하지 않아 Bing에서 찾아봅니다...")
        news_items = get_bing_rss(search_term)
        source_used = "Bing News"
    
    if not news_items:
        st.warning(f"최근 {time_option} 동안 관련 뉴스가 없거나, 접속이 차단되었습니다.")
    else:
        st.success(f"성공! {source_used}에서 {len(news_items)}개의 기사를 가져왔습니다.")
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