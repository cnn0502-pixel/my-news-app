import streamlit as st
from duckduckgo_search import DDGS

# 1. 페이지 설정
st.set_page_config(page_title="최신 뉴스 모니터링", layout="wide")
st.title("🦆 최신 뉴스 레이더 (DuckDuckGo)")
st.caption("기간 설정을 통해 최신 뉴스만 골라옵니다.")

# 2. 사이드바 설정
st.sidebar.header("🔍 검색 설정")
default_keywords = ["Beckhoff", "팔레타이징", "PLC 제어", "산업용 로봇", "테슬라", "해양경찰"]
selected_keyword = st.sidebar.selectbox("키워드 선택", default_keywords)
custom_keyword = st.sidebar.text_input("직접 검색어 입력")

search_term = custom_keyword if custom_keyword else selected_keyword

st.sidebar.markdown("---")

# ★ 핵심 기능 추가: 기간 설정
time_option = st.sidebar.selectbox(
    "기간 선택 (최신순)",
    ("지난 1달 (m)", "지난 1주일 (w)", "지난 24시간 (d)"),
    index=0
)

# 선택한 옵션을 라이브러리용 코드(d, w, m)로 변환
if "24시간" in time_option:
    time_code = "d"
elif "1주일" in time_option:
    time_code = "w"
else:
    time_code = "m"

st.sidebar.markdown("---")

# 3. 뉴스 가져오기 함수
def get_safe_news(query, period):
    try:
        # timelimit 옵션 추가: d(하루), w(주), m(월)
        results = DDGS().news(
            keywords=query, 
            region="kr-kr", 
            safesearch="off", 
            timelimit=period,  # ★ 여기가 핵심!
            max_results=10
        )
        return results
    except Exception as e:
        st.error(f"검색 중 오류가 발생했습니다: {e}")
        return []

# 4. 실행 버튼
if st.button("뉴스 검색 시작 🚀"):
    st.write(f"**'{search_term}'** 키워드로 **{time_option}** 동안의 뉴스를 검색합니다...")
    
    news_items = get_safe_news(search_term, time_code)
    
    if not news_items:
        st.warning(f"최근 {time_option} 동안 올라온 뉴스가 없습니다.")
    else:
        st.success(f"성공! 최신 기사 {len(news_items)}개를 가져왔습니다.")
        st.markdown("---")
        
        for item in news_items:
            with st.container():
                st.subheader(f"📰 {item.get('title', '제목 없음')}")
                
                source = item.get('source', '뉴스')
                date = item.get('date', '날짜 정보 없음')
                
                # 날짜가 이상하게 나올 수 있어서(예: 2 hours ago), 그대로 출력
                st.text(f"출처: {source} | 게시일: {date}")
                
                st.info(item.get('body', '내용 미리보기가 없습니다.'))
                
                link = item.get('url')
                if link:
                    st.link_button("👉 기사 원문 보러가기", link)
                
                st.markdown("---")