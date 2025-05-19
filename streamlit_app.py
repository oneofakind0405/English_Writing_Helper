import streamlit as st
import subprocess
import sys

# 페이지 설정
st.set_page_config(
    page_title="AI 영어 쓰기 도우미",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 메뉴
st.sidebar.title("🎯 수준 선택")
page = st.sidebar.selectbox(
    "학습 수준을 선택하세요:",
    ["메인 페이지", "초급 (Beginners)", "중급 (Intermediate)", "고급 (Advanced)"]
)

# 메인 페이지 내용
def main_page():
    # 헤더
    st.title("🌟 AI 영어 쓰기 도우미")
    st.markdown("### 한국 중학생을 위한 수준별 영어 쓰기 학습 플랫폼")
    
    # 소개 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 👋 안녕하세요!
        
        **AI 영어 쓰기 도우미**에 오신 것을 환영합니다! 
        
        이 웹앱은 한국 중학생 영어 학습자들이 자신의 수준에 맞는 영어 쓰기 과제를 수행하고, 
        AI의 도움을 받아 효과적으로 영어 쓰기 실력을 향상시킬 수 있도록 설계되었습니다.
        
        ### ✨ 주요 기능
        
        - **🎯 수준별 맞춤 과제**: 초급, 중급, 고급으로 나누어진 체계적인 쓰기 과제
        - **🤖 AI 챗봇 도우미**: 실시간 질문 답변, 아이디어 제안, 기본 피드백 제공
        - **📝 다양한 쓰기 유형**: 그림 묘사, 의견 제시, 설명문, 이야기 쓰기, 비교/대조 등
        - **💡 스캐폴딩 지원**: 각 수준에 맞는 적절한 학습 지원 제공
        - **📊 진행 상황 추적**: 작성한 글의 저장 및 분석 기능
        """)
    
    with col2:
        st.image("https://via.placeholder.com/300x400/4CAF50/FFFFFF?text=AI+Writing+Assistant", 
                caption="AI와 함께하는 영어 쓰기 학습")
    
    # 수준별 안내
    st.markdown("---")
    st.markdown("## 📚 수준별 학습 안내")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🌱 초급 (Beginners)
        - 빈칸 채우기 문단 작성
        - 그림과 단어 매칭
        - 기본 어휘 및 표현 제공
        - 단순한 문장 구조 연습
        """)
        if st.button("초급 수준으로 가기", key="beginner"):
            st.session_state.page = "초급 (Beginners)"
            st.rerun()
    
    with col2:
        st.markdown("""
        ### 🌿 중급 (Intermediate)
        - 가이드 질문을 통한 쓰기
        - 연결어구 및 표현 목록 제공
        - 아이디어 구상 팁 제공
        - 문단 구조 학습
        """)
        if st.button("중급 수준으로 가기", key="intermediate"):
            st.session_state.page = "중급 (Intermediate)"
            st.rerun()
    
    with col3:
        st.markdown("""
        ### 🌳 고급 (Advanced)
        - 자유로운 주제 선택
        - 최소한의 지침 제공
        - 다양한 어휘 및 문장 구조
        - 창의적 표현 권장
        """)
        if st.button("고급 수준으로 가기", key="advanced"):
            st.session_state.page = "고급 (Advanced)"
            st.rerun()
    
    # 시작하기 섹션
    st.markdown("---")
    st.markdown("## 🚀 시작하기")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 💭 수준을 모르겠나요?
        
        간단한 진단 평가를 통해 자신의 영어 쓰기 수준을 확인해보세요!
        """)
        if st.button("🔍 수준 진단 받기", type="primary"):
            st.balloons()
            st.success("수준 진단 기능은 곧 추가될 예정입니다!")
    
    with col2:
        st.markdown("""
        ### 📖 사용법 안내
        
        1. 왼쪽 사이드바에서 수준 선택
        2. 원하는 쓰기 과제 선택
        3. AI 도우미와 함께 쓰기 시작
        4. 완성된 글 저장 및 피드백 받기
        """)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>📧 문의사항이 있으시면 언제든지 연락주세요!</p>
        <p><em>AI 영어 쓰기 도우미와 함께 즐거운 영어 학습 되세요! 🎉</em></p>
    </div>
    """, unsafe_allow_html=True)

# 페이지 라우팅
def run_page(page_name):
    if page_name == "초급 (Beginners)":
        subprocess.run([sys.executable, "-m", "streamlit", "run", "beginner.py"])
    elif page_name == "중급 (Intermediate)":
        subprocess.run([sys.executable, "-m", "streamlit", "run", "intermediate.py"])
    elif page_name == "고급 (Advanced)":
        subprocess.run([sys.executable, "-m", "streamlit", "run", "advanced.py"])

# 메인 실행
if __name__ == "__main__":
    if page == "메인 페이지":
        main_page()
    else:
        st.info(f"{page} 페이지로 이동하려면 해당 Python 파일을 직접 실행해주세요.")
        st.code(f"streamlit run {page.split()[0].lower()}.py")
        main_page()