import streamlit as st
import random
from datetime import datetime
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="초급 영어 쓰기",
    page_icon="🌱",
    layout="wide"
)

# OpenAI 클라이언트 초기화
@st.cache_resource
def init_openai_client():
    return OpenAI(api_key=st.secrets["openai"]["api_key"])

client = init_openai_client()

# 세션 상태 초기화
if 'writing_content' not in st.session_state:
    st.session_state.writing_content = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None

# 초급 수준 과제 데이터
BEGINNER_TASKS = {
    "자기소개": {
        "type": "fill_blanks",
        "description": "빈칸을 채워서 자기소개 문단을 완성하세요.",
        "template": """Hello! My name is _______. I am _______ years old. I live in _______ with my _______. 
I have _______ (pet/hobby). My favorite subject is _______. I like to _______ in my free time. 
My favorite food is _______. Nice to meet you!""",
        "vocabulary": ["name", "age", "family", "hobby", "subject", "food", "pet"],
        "hints": ["이름을 써보세요", "나이를 숫자로 써보세요", "사는 곳을 써보세요"]
    },
    "내 방 묘사": {
        "type": "picture_description",
        "description": "그림을 보고 방을 묘사하는 글을 써보세요.",
        "template": """This is my room. In my room, there is _______. 
The _______ is next to the _______. I have _______ on the desk. 
The walls are _______ color. I like my room because _______.""",
        "vocabulary": ["bed", "desk", "chair", "window", "door", "lamp", "book", "computer"],
        "hints": ["방에 있는 물건들을 써보세요", "색깔을 설명해보세요", "위치를 나타내는 말을 써보세요"]
    },
    "좋아하는 음식": {
        "type": "opinion",
        "description": "좋아하는 음식에 대해 간단히 써보세요.",
        "template": """My favorite food is _______. It tastes _______. 
I usually eat it _______. My mom/dad makes it for me. 
I like it because _______. When I eat it, I feel _______.""",
        "vocabulary": ["delicious", "sweet", "spicy", "healthy", "happy", "hungry", "breakfast", "lunch", "dinner"],
        "hints": ["음식 이름을 써보세요", "맛을 설명해보세요", "언제 먹는지 써보세요"]
    }
}

# 도우미 응답 생성 함수 (OpenAI API 사용)
def generate_ai_response(user_input, writing_content=""):
    try:
        # 초급 수준 학습자를 위한 시스템 프롬프트
        system_prompt = """
        당신은 한국 중학생 영어 초급 학습자를 위한 친근하고 도움이 되는 AI 영어 선생님입니다.
        
        특징:
        - 간단하고 이해하기 쉬운 한국어로 설명
        - 기초적인 문법과 어휘 중심
        - 격려와 동기부여 제공
        - 실수를 두려워하지 않도록 따뜻한 톤
        - 구체적이고 실용적인 조언
        
        학습자가 질문하면:
        1. 문법: 기본 문법을 예시와 함께 설명
        2. 어휘: 초급 수준 단어와 표현 제안
        3. 작문: 간단한 문장 구조와 아이디어 제공
        4. 일반: 영어 학습 동기부여와 격려
        
        답변은 3-4문장으로 간결하게, 이모지를 적절히 사용해서 친근하게 해주세요.
        """
        
        # 사용자의 현재 작성 내용도 컨텍스트로 제공
        user_message = f"학생 질문: {user_input}"
        if writing_content.strip():
            user_message += f"\n\n학생이 현재 작성 중인 글: {writing_content[:200]}..."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # API 오류 시 기본 응답
        fallback_responses = [
            "죄송해요! 일시적으로 문제가 있네요. 다시 시도해주세요. 🤖",
            "잠깐만요! 다시 한 번 물어봐주시겠어요? 😊",
            "아, 지금 조금 바빠요! 곧 도와드릴게요! ⏰"
        ]
        return random.choice(fallback_responses)

# 메인 헤더
st.title("🌱 초급 영어 쓰기")
st.markdown("### 기초부터 천천히 시작해봐요!")

# 사이드바
with st.sidebar:
    st.header("📚 과제 선택")
    
    task_names = list(BEGINNER_TASKS.keys())
    selected_task_name = st.selectbox("쓰기 과제를 선택하세요:", ["선택해주세요"] + task_names)
    
    if selected_task_name != "선택해주세요":
        st.session_state.selected_task = BEGINNER_TASKS[selected_task_name]
        st.success(f"'{selected_task_name}' 과제를 선택했습니다!")
    
    st.markdown("---")
    st.markdown("### 🎯 초급 수준 특징")
    st.markdown("- 빈칸 채우기 문단")
    st.markdown("- 기본 어휘 제공")
    st.markdown("- 단순한 문장 구조")
    st.markdown("- 단계별 가이드")

# 메인 콘텐츠
if st.session_state.selected_task:
    task = st.session_state.selected_task
    
    # 과제 설명
    st.markdown("## 📝 과제 설명")
    st.info(task["description"])
    
    # 템플릿과 어휘 도움말
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### ✍️ 작성하기")
        st.markdown("**템플릿:** (빈칸을 채워보세요)")
        st.code(task["template"])
        
        # 작성 영역
        writing_text = st.text_area(
            "여기에 여러분의 글을 작성해보세요:",
            value=st.session_state.writing_content,
            height=300,
            placeholder="위의 템플릿을 참고해서 빈칸을 채워보세요..."
        )
        st.session_state.writing_content = writing_text
        
        # 저장 버튼
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            if st.button("💾 저장하기", type="primary"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success(f"글이 저장되었습니다! ({timestamp})")
                st.balloons()
        
        with col1_2:
            if st.button("🔄 다시 시작"):
                st.session_state.writing_content = ""
                st.rerun()
        
        with col1_3:
            if st.button("📊 기본 분석"):
                if writing_text:
                    word_count = len(writing_text.split())
                    char_count = len(writing_text)
                    st.metric("단어 수", word_count)
                    st.metric("글자 수", char_count)
                else:
                    st.warning("먼저 글을 작성해주세요!")
    
    with col2:
        st.markdown("### 💡 도움말")
        
        # 어휘 도움말
        with st.expander("📚 유용한 단어들", expanded=True):
            for word in task["vocabulary"]:
                st.markdown(f"- **{word}**")
        
        # 힌트
        with st.expander("🔍 힌트", expanded=True):
            for hint in task["hints"]:
                st.markdown(f"💭 {hint}")
        
        # 격려 메시지
        with st.expander("🌟 격려 메시지"):
            encouragements = [
                "천천히 해도 괜찮아요! 🐌",
                "실수를 두려워하지 마세요! 💪",
                "한 문장씩 차근차근! 📝",
                "여러분이 최고예요! ⭐",
                "계속 도전하는 모습이 멋져요! 🎯"
            ]
            st.markdown(random.choice(encouragements))

# AI 도우미 챗봇
st.markdown("---")
st.markdown("## 🤖 AI 도우미와 대화하기")

# 채팅 인터페이스
chat_container = st.container()
with chat_container:
    # 채팅 히스토리 표시
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"**🙋‍♀️ 나:** {chat['message']}")
        else:
            st.markdown(f"**🤖 AI 도우미:** {chat['message']}")

# 사용자 입력
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input("AI 도우미에게 질문해보세요:", placeholder="문법이나 단어에 대해 궁금한 것이 있나요?")
with col2:
    send_button = st.button("보내기", type="primary")

if send_button and user_input:
    # 사용자 메시지 추가
    st.session_state.chat_history.append({"role": "user", "message": user_input})
    
    # AI 응답 생성 (현재 작성 중인 글도 함께 전달)
    with st.spinner("AI가 생각하고 있어요..."):
        ai_response = generate_ai_response(user_input, st.session_state.writing_content)
    st.session_state.chat_history.append({"role": "ai", "message": ai_response})
    
    st.rerun()

# 퀵 질문 버튼들
st.markdown("#### 빠른 질문:")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("❓ 문법이 궁금해요"):
        st.session_state.chat_history.append({"role": "user", "message": "문법에 대해 도움을 주세요"})
        with st.spinner("답변을 준비하고 있어요..."):
            ai_response = generate_ai_response("문법에 대해 도움을 주세요", st.session_state.writing_content)
        st.session_state.chat_history.append({"role": "ai", "message": ai_response})
        st.rerun()

with col2:
    if st.button("📖 단어를 모르겠어요"):
        st.session_state.chat_history.append({"role": "user", "message": "단어에 대해 도움을 주세요"})
        with st.spinner("답변을 준비하고 있어요..."):
            ai_response = generate_ai_response("단어에 대해 도움을 주세요", st.session_state.writing_content)
        st.session_state.chat_history.append({"role": "ai", "message": ai_response})
        st.rerun()

with col3:
    if st.button("💭 아이디어가 떠오르지 않아요"):
        st.session_state.chat_history.append({"role": "user", "message": "아이디어에 대해 도움을 주세요"})
        with st.spinner("답변을 준비하고 있어요..."):
            ai_response = generate_ai_response("아이디어에 대해 도움을 주세요", st.session_state.writing_content)
        st.session_state.chat_history.append({"role": "ai", "message": ai_response})
        st.rerun()

# 채팅 기록 초기화 버튼
if st.session_state.chat_history:
    if st.button("🗑️ 채팅 기록 지우기"):
        st.session_state.chat_history = []
        st.rerun()

else:
    # 과제를 선택하지 않은 경우
    st.markdown("## 👈 왼쪽 사이드바에서 과제를 선택해주세요!")
    
    # 샘플 과제 미리보기
    st.markdown("### 📋 과제 미리보기")
    
    for task_name, task_info in BEGINNER_TASKS.items():
        with st.expander(f"🔍 {task_name}"):
            st.markdown(f"**설명:** {task_info['description']}")
            st.markdown("**템플릿 예시:**")
            st.code(task_info['template'][:100] + "...")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🌱 <strong>초급 수준</strong>에서는 천천히, 기초부터 시작해요!</p>
    <p><em>궁금한 것이 있으면 언제든지 AI 도우미에게 물어보세요! 🤖</em></p>
</div>
""", unsafe_allow_html=True)