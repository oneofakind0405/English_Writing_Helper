import streamlit as st
import random
from datetime import datetime
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="중급 영어 쓰기",
    page_icon="🌿",
    layout="wide"
)

# OpenAI 클라이언트 초기화
@st.cache_resource
def init_openai_client():
    return OpenAI(api_key=st.secrets["openai"]["api_key"])

client = init_openai_client()

# 세션 상태 초기화
if 'writing_content_inter' not in st.session_state:
    st.session_state.writing_content_inter = ""
if 'chat_history_inter' not in st.session_state:
    st.session_state.chat_history_inter = []
if 'selected_task_inter' not in st.session_state:
    st.session_state.selected_task_inter = None
if 'brainstorming_ideas' not in st.session_state:
    st.session_state.brainstorming_ideas = []

# 중급 수준 과제 데이터
INTERMEDIATE_TASKS = {
    "나의 꿈": {
        "type": "opinion_essay",
        "description": "미래의 꿈과 목표에 대해 3-4개 문단으로 글을 써보세요.",
        "guide_questions": [
            "What is your dream job? Why do you want this job?",
            "What skills do you need to achieve your dream?",
            "How will you prepare for your future career?",
            "What challenges might you face and how will you overcome them?"
        ],
        "useful_expressions": {
            "서론": ["In the future, I want to...", "My dream is to...", "I have always wanted to..."],
            "본론": ["The reason why I want this job is...", "First of all,", "Moreover,", "In addition to that,"],
            "결론": ["In conclusion,", "To sum up,", "I believe that...", "I am confident that..."]
        },
        "vocabulary": ["ambitious", "goal", "achieve", "determine", "challenge", "overcome", "prepare", "career"]
    },
    "환경 보호": {
        "type": "argumentative",
        "description": "환경 보호의 중요성과 실천 방법에 대해 설득력 있는 글을 써보세요.",
        "guide_questions": [
            "Why is environmental protection important?",
            "What are the main environmental problems we face today?",
            "What can individuals do to protect the environment?",
            "How can we encourage others to be more environmentally friendly?"
        ],
        "useful_expressions": {
            "의견 제시": ["I strongly believe that...", "It is crucial that...", "We must realize that..."],
            "예시 제공": ["For example,", "For instance,", "Such as", "A good example is..."],
            "결과 표현": ["As a result,", "Therefore,", "Consequently,", "This leads to..."]
        },
        "vocabulary": ["pollution", "sustainable", "recycle", "renewable", "conservation", "ecosystem", "reduce", "global warming"]
    },
    "문화 비교": {
        "type": "compare_contrast",
        "description": "한국 문화와 다른 나라 문화를 비교하고 대조하는 글을 써보세요.",
        "guide_questions": [
            "What country would you like to compare with Korea?",
            "What are the similarities between the two cultures?",
            "What are the main differences?",
            "What can we learn from each other's cultures?"
        ],
        "useful_expressions": {
            "유사점": ["Both countries have...", "Similarly,", "In the same way,", "Like Korea,"],
            "차이점": ["However,", "On the other hand,", "In contrast,", "Unlike Korea,"],
            "비교": ["compared to", "while", "whereas", "although"]
        },
        "vocabulary": ["tradition", "custom", "festival", "cuisine", "language", "society", "values", "diversity"]
    },
    "학교생활 경험": {
        "type": "narrative",
        "description": "기억에 남는 학교생활 경험이나 사건에 대한 이야기를 써보세요.",
        "guide_questions": [
            "What memorable event happened at school?",
            "When and where did it happen?",
            "Who was involved in this experience?",
            "How did you feel and what did you learn from it?"
        ],
        "useful_expressions": {
            "시간 순서": ["First,", "Then,", "After that,", "Finally,", "Meanwhile,"],
            "감정 표현": ["I felt...", "I was excited/nervous/proud", "It made me realize..."],
            "묘사": ["It was...", "The atmosphere was...", "I remember that..."]
        },
        "vocabulary": ["memorable", "experience", "participate", "nervous", "proud", "realize", "atmosphere", "encourage"]
    }
}

# 아이디어 구상 도구
BRAINSTORMING_PROMPTS = {
    "Mind Map": ["중심 주제에서 시작해서 관련된 아이디어들을 가지치기해보세요", "각 가지에서 더 구체적인 예시나 경험을 생각해보세요"],
    "5W1H": ["누가(Who), 언제(When), 어디서(Where), 무엇을(What), 왜(Why), 어떻게(How)를 생각해보세요"],
    "For/Against": ["찬성하는 이유와 반대하는 이유를 각각 나열해보세요", "각 이유에 대한 구체적 예시를 생각해보세요"],
    "Story Structure": ["배경 설정 → 문제/갈등 → 해결과정 → 결과/교훈 순서로 구성해보세요"]
}

# 도우미 응답 생성 함수 (중급 수준)
def generate_ai_response_intermediate(user_input, task_context=None, writing_content=""):
    try:
        # 중급 수준 학습자를 위한 시스템 프롬프트
        system_prompt = f"""
        당신은 한국 중학생 영어 중급 학습자를 위한 전문적이고 도움이 되는 AI 영어 선생님입니다.
        
        특징:
        - 체계적이고 구조적인 조언 제공
        - 중급 수준의 문법과 어휘 활용
        - 글의 구조와 논리적 전개 중시
        - 구체적인 예시와 함께 설명
        - 학습자의 창의성과 자기표현 격려
        
        현재 과제 유형: {task_context if task_context else "일반"}
        
        학습자가 질문하면:
        1. 구조: 서론-본론-결론, 문단 구성, 연결어구 활용
        2. 어휘: 다양한 표현, 동의어, 연결어구 제안
        3. 문법: 복합문, 다양한 시제, 문장 패턴
        4. 내용: 아이디어 발전, 근거 제시, 예시 활용
        
        답변은 4-5문장으로 구체적이고 실용적으로, 이모지를 적절히 사용해주세요.
        """
        
        # 사용자의 현재 작성 내용과 과제 맥락 제공
        user_message = f"학생 질문: {user_input}"
        if writing_content.strip():
            user_message += f"\n\n학생이 현재 작성 중인 글: {writing_content[:300]}..."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # API 오류 시 기본 응답
        fallback_responses = [
            "미안해요! 지금 일시적으로 문제가 있어요. 다시 한 번 시도해주세요. 🔄",
            "잠깐만요! 더 나은 답변을 위해 다시 질문해주세요. 💭",
            "앗, 무언가 잘못됐네요! 조금 후에 다시 시도해주세요. ⚡"
        ]
        return random.choice(fallback_responses)

# 메인 헤더
st.title("🌿 중급 영어 쓰기")
st.markdown("### 체계적인 글쓰기와 창의적 표현을 익혀봐요!")

# 사이드바
with st.sidebar:
    st.header("📚 과제 선택")
    
    task_names = list(INTERMEDIATE_TASKS.keys())
    selected_task_name = st.selectbox("쓰기 과제를 선택하세요:", ["선택해주세요"] + task_names)
    
    if selected_task_name != "선택해주세요":
        st.session_state.selected_task_inter = INTERMEDIATE_TASKS[selected_task_name]
        st.success(f"'{selected_task_name}' 과제를 선택했습니다!")
    
    st.markdown("---")
    st.markdown("### 🎯 중급 수준 특징")
    st.markdown("- 안내 질문 제공")
    st.markdown("- 유용한 연결어구")
    st.markdown("- 아이디어 구상 도구")
    st.markdown("- 문단 구조 학습")
    
    # 아이디어 구상 도구
    if st.session_state.selected_task_inter:
        st.markdown("---")
        st.markdown("### 💡 아이디어 구상")
        brainstorming_method = st.selectbox(
            "구상 방법 선택:",
            list(BRAINSTORMING_PROMPTS.keys())
        )
        
        if st.button("💭 아이디어 생성"):
            if brainstorming_method in BRAINSTORMING_PROMPTS:
                idea = random.choice(BRAINSTORMING_PROMPTS[brainstorming_method])
                st.session_state.brainstorming_ideas.append(f"**{brainstorming_method}**: {idea}")
                st.success("새로운 아이디어가 추가되었습니다!")

# 메인 콘텐츠
if st.session_state.selected_task_inter:
    task = st.session_state.selected_task_inter
    
    # 과제 설명
    st.markdown("## 📝 과제 설명")
    st.info(task["description"])
    
    # 탭으로 구성된 인터페이스
    tab1, tab2, tab3 = st.tabs(["✍️ 작성하기", "📋 가이드", "🔍 도구"])
    
    with tab1:
        # 작성 영역
        st.markdown("### 글 작성")
        writing_text = st.text_area(
            "여기에 여러분의 글을 작성해보세요:",
            value=st.session_state.writing_content_inter,
            height=400,
            placeholder="안내 질문들을 참고해서 체계적으로 글을 써보세요..."
        )
        st.session_state.writing_content_inter = writing_text
        
        # 작성 도구
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("💾 저장하기", type="primary"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success(f"글이 저장되었습니다! ({timestamp})")
                st.balloons()
        
        with col2:
            if st.button("🔄 다시 시작"):
                st.session_state.writing_content_inter = ""
                st.rerun()
        
        with col3:
            if st.button("📊 글 분석"):
                if writing_text:
                    words = writing_text.split()
                    sentences = writing_text.split('.')
                    paragraphs = writing_text.split('\n\n')
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("단어 수", len(words))
                    with col_b:
                        st.metric("문장 수", len([s for s in sentences if s.strip()]))
                    with col_c:
                        st.metric("문단 수", len([p for p in paragraphs if p.strip()]))
                else:
                    st.warning("먼저 글을 작성해주세요!")
        
        with col4:
            if st.button("🔍 기본 피드백"):
                if writing_text:
                    # 기본적인 피드백 제공
                    word_count = len(writing_text.split())
                    if word_count < 50:
                        st.warning("더 자세히 써보세요! (최소 50단어 권장)")
                    elif word_count > 200:
                        st.info("충분히 자세하게 잘 써주셨네요!")
                    else:
                        st.success("적절한 길이의 글이에요!")
                    
                    # 문단 체크
                    if '\n\n' in writing_text:
                        st.success("✅ 문단 구분이 잘 되어 있어요!")
                    else:
                        st.info("💡 문단을 나누어서 써보세요!")
                else:
                    st.warning("먼저 글을 작성해주세요!")
    
    with tab2:
        # 가이드 질문들
        st.markdown("### 🗣️ 안내 질문들")
        st.markdown("이 질문들을 하나씩 생각하며 글을 써보세요:")
        
        for i, question in enumerate(task["guide_questions"], 1):
            with st.expander(f"질문 {i}: {question}"):
                st.text_area(
                    f"답변 {i}:",
                    key=f"answer_{i}",
                    placeholder="이 질문에 대한 답을 간단히 적어보세요...",
                    height=100
                )
        
        # 유용한 표현들
        st.markdown("### 💬 유용한 표현들")
        for category, expressions in task["useful_expressions"].items():
            with st.expander(f"📝 {category}"):
                for expr in expressions:
                    st.markdown(f"• {expr}")
        
        # 어휘 목록
        st.markdown("### 📚 주요 어휘")
        vocab_cols = st.columns(3)
        for i, word in enumerate(task["vocabulary"]):
            with vocab_cols[i % 3]:
                st.markdown(f"**{word}**")
    
    with tab3:
        # 아이디어 구상 결과
        st.markdown("### 💡 저장된 아이디어들")
        if st.session_state.brainstorming_ideas:
            for idea in st.session_state.brainstorming_ideas:
                st.markdown(idea)
            
            if st.button("🗑️ 아이디어 초기화"):
                st.session_state.brainstorming_ideas = []
                st.rerun()
        else:
            st.info("사이드바에서 아이디어를 생성해보세요!")
        
        # 글쓰기 팁
        st.markdown("### 📝 글쓰기 팁")
        tips = [
            "**서론-본론-결론** 구조를 지켜주세요",
            "각 문단은 **하나의 주요 아이디어**를 담아주세요",
            "**구체적인 예시**를 들어 설명해보세요",
            "**연결어구**를 사용해 문장을 자연스럽게 연결해주세요",
            "**다양한 어휘**를 사용해 표현력을 높여주세요"
        ]
        
        for tip in tips:
            st.markdown(f"💡 {tip}")

# AI 도우미 챗봇
st.markdown("---")
st.markdown("## 🤖 AI 도우미와 대화하기")

# 채팅 인터페이스
chat_container = st.container()
with chat_container:
    # 채팅 히스토리 표시
    for chat in st.session_state.chat_history_inter:
        if chat["role"] == "user":
            st.markdown(f"**🙋‍♀️ 나:** {chat['message']}")
        else:
            st.markdown(f"**🤖 AI 도우미:** {chat['message']}")

# 사용자 입력
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input(
        "AI 도우미에게 질문해보세요:", 
        placeholder="글의 구조, 어휘 선택, 내용 전개 등에 대해 질문해보세요"
    )
with col2:
    send_button = st.button("보내기", type="primary")

if send_button and user_input:
    # 사용자 메시지 추가
    st.session_state.chat_history_inter.append({"role": "user", "message": user_input})
    
    # AI 응답 생성 (과제 타입 정보와 현재 글 내용 포함)
    task_type = st.session_state.selected_task_inter["type"] if st.session_state.selected_task_inter else None
    with st.spinner("AI가 분석하고 있어요..."):
        ai_response = generate_ai_response_intermediate(user_input, task_type, st.session_state.writing_content_inter)
    st.session_state.chat_history_inter.append({"role": "ai", "message": ai_response})
    
    st.rerun()

# 퀵 질문 버튼들
st.markdown("#### 빠른 질문:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📐 글 구조"):
        st.session_state.chat_history_inter.append({"role": "user", "message": "글의 구조에 대해 도움을 주세요"})
        with st.spinner("구조 분석 중..."):
            ai_response = generate_ai_response_intermediate("글의 구조에 대해 도움을 주세요", None, st.session_state.writing_content_inter)
        st.session_state.chat_history_inter.append({"role": "ai", "message": ai_response})
        st.rerun()

with col2:
    if st.button("📚 어휘 선택"):
        st.session_state.chat_history_inter.append({"role": "user", "message": "어휘 선택에 대해 도움을 주세요"})
        with st.spinner("어휘 분석 중..."):
            ai_response = generate_ai_response_intermediate("더 나은 어휘 선택에 대해 조언해주세요", None, st.session_state.writing_content_inter)
        st.session_state.chat_history_inter.append({"role": "ai", "message": ai_response})
        st.rerun()

with col3:
    if st.button("✏️ 문법 활용"):
        st.session_state.chat_history_inter.append({"role": "user", "message": "문법 활용에 대해 도움을 주세요"})
        with st.spinner("문법 분석 중..."):
            ai_response = generate_ai_response_intermediate("더 다양한 문법 구조 활용에 대해 조언해주세요", None, st.session_state.writing_content_inter)
        st.session_state.chat_history_inter.append({"role": "ai", "message": ai_response})
        st.rerun()

with col4:
    if st.button("💭 내용 전개"):
        st.session_state.chat_history_inter.append({"role": "user", "message": "내용 전개에 대해 도움을 주세요"})
        with st.spinner("내용 분석 중..."):
            ai_response = generate_ai_response_intermediate("내용을 더 효과적으로 전개하는 방법에 대해 조언해주세요", None, st.session_state.writing_content_inter)
        st.session_state.chat_history_inter.append({"role": "ai", "message": ai_response})
        st.rerun()

# 채팅 기록 초기화 버튼
if st.session_state.chat_history_inter:
    if st.button("🗑️ 채팅 기록 지우기"):
        st.session_state.chat_history_inter = []
        st.rerun()

else:
    # 과제를 선택하지 않은 경우
    st.markdown("## 👈 왼쪽 사이드바에서 과제를 선택해주세요!")
    
    # 샘플 과제 미리보기
    st.markdown("### 📋 과제 미리보기")
    
    for task_name, task_info in INTERMEDIATE_TASKS.items():
        with st.expander(f"🔍 {task_name}"):
            st.markdown(f"**설명:** {task_info['description']}")
            st.markdown("**안내 질문 예시:**")
            st.markdown(f"• {task_info['guide_questions'][0]}")
            st.markdown(f"• {task_info['guide_questions'][1]}")
            st.markdown("*...더 많은 질문들이 준비되어 있습니다*")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🌿 <strong>중급 수준</strong>에서는 체계적이고 창의적인 글쓰기를 연습해요!</p>
    <p><em>안내 질문과 유용한 표현들을 활용해서 더 풍부한 글을 써보세요! 📝</em></p>
</div>
""", unsafe_allow_html=True)
