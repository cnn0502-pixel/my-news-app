import streamlit as st
import requests
import urllib.parse

st.set_page_config(page_title="뉴스 모니터링 Pro", layout="wide")
st.title("📡 최신 뉴스 레이더 (글로벌 API 버전)")

st.sidebar.header("🔍 검색 설정")
api_key = st.sidebar.text_input("GNews API 키 입력 (필수)", type="password")
search_term = st.sidebar.text_input("검색어 (예: Tesla, Apple)", "Tesla")
news_lang = st.sidebar.radio("뉴스 언어", ("영어 (해외뉴스 빵빵함)", "한국어 (기사 거의 없음)"))
lang_code = "en" if "영어" in news_lang else "ko"

def get_news(query, key, lang):
    encoded_query = urllib.parse.quote(query)
    url = f"https://gnews.io/api/v4/search?q={encoded_query}&apikey={key}&lang={lang}"
    res = requests.get(url)
    return res

if st.button("뉴스 검색 시작 🚀"):
    if not api_key:
        st.warning("왼쪽 사이드바에 API 키부터 입력해!")
    else:
        res = get_news(search_term, api_key, lang_code)
        if res.status_code == 200:
            data = res.json()
            articles = data.get("articles", [])
            
            if not articles:
                st.warning("해당 언어로 된 기사가 0개야. 영어 키워드로 바꿔서 검색해봐!")
                st.write("🤖 (참고용) 구글 서버가 보낸 원본 응답:", data)
            else:
                st.success(f"성공! {len(articles)}개 기사 찾았어.")
                for article in articles:
                    st.subheader(f"📰 {article['title']}")
                    st.text(f"출처: {article['source']['name']} | {article['publishedAt'][:10]}")
                    st.link_button("👉 원문 보기", article['url'])
                    st.markdown("---")
        else:
            st.error(f"🚨 API 에러 떴어!: {res.text}")
