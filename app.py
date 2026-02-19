# 5. 실행 버튼
if st.button("뉴스 검색 시작 🚀"):
    is_global = (news_type == "해외 뉴스")
    
    # 복잡한 site: 필터가 키워드 검색을 방해하므로 제거. 
    # 대신 엔진 자체의 언어/지역(미국, 영어) 설정이 해외 언론사만 정확히 타겟팅함.
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