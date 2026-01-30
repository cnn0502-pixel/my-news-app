import streamlit as st
import feedparser
import urllib.parse
import requests
import time

# 1. 페이지 설정
st.set_page_config(page_title="뉴스 모니터링", layout="wide")
st.title("📡 무적의 뉴스 레이더 (No-Key 버전)")
st.caption("구글과 빙(Bing) 뉴스를 동시에 타격하여 뉴스를 가져옵니다.")

# 2. 사이드바 설정
st.sidebar.header("🔍 검색 설정")
default_keywords = ["Beckhoff", "팔레타이징", "PLC 제어", "산업용 로봇", "엔비디아", "해양경찰"]
selected_keyword = st.sidebar.selectbox("키워드 선택", default_keywords)
custom_keyword = st.sidebar.text_input("직접 검색어 입력")

search_term = custom_keyword if custom_keyword else selected_keyword

st.sidebar.markdown("---")

# 3. 뉴스 수집 함수 (구글 RSS + 헤더 위장)
def get_google_rss(query):
    encoded_query = urllib.parse.quote(query)
    # 구글 뉴스 RSS 주소 (한국어 설정)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    # 봇 차단 방지용 가짜 신분증(Header)
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

# 4. 백업용 뉴스 수집 함수 (빙 RSS)
def get_bing_rss(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss"
    
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
    st.write(f"**'{search_term}'** 키워드로 뉴스를 찾아옵니다...")
    
    # 전략: 구글 먼저 시도 -> 실패하면 빙 시도
    news_items = get_google_rss(search_term)
    source_used = "Google News"
    
    if not news_items:
        st.write("😅 구글이 잠시 막혔네요. Bing 뉴스로 우회합니다...")
        news_items = get_bing_rss(search_term)
        source_used = "Bing News"
    
    # 결과 출력
    if not news_items:
        st.error("모든 뉴스 채널이 응답하지 않습니다. 잠시 후 다시 시도해주세요.")
    else:
        st.success(f"성공! {source_used}에서 {len(news_items)}개의 최신 기사를 가져왔습니다.")
        st.markdown("---")
        
        for item in news_items:
            with st.container():
                st.subheader(f"📰 {item.title}")
                
                # 날짜 및 출처 처리
                published = item.get('published', '날짜 정보 없음')
                source = item.get('source', {}).get('title', source_used)
                
                st.text(f"출처: {source} | {published}")
                
                # 링크 버튼
                link = item.get('link')
                if link:
                    st.link_button("👉 기사 원문 보러가기", link)
                
                st.markdown("---")