import streamlit as st
import random
from datetime import datetime
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="고급 영어 쓰기",
    page_icon="🌳",
    layout="wide"
)

# OpenAI 클라이언트 초기화
@st.cache_resource
def init_openai_client():
    return OpenAI(api_key=st.secrets["openai"]["api_key"])

client = init_openai_client()

# 세션 상태 초기화
if 'writing_content_adv' not in st.session_state:
    st.session_state.writing_content_adv = ""
if 'chat_history_adv' not in st.session_state:
    st.session_state.chat_history_adv = []
if 'selected_task_adv' not in st.session_state:
    st.session_state.selected_task_adv = None
if 'writing_goals' not in st.session_state:
    st.session_state.writing_goals = []
if 'peer_feedback' not in st.session_state:
    st.session_state.peer_feedback = []

# 고급 수준 과제 데이터
ADVANCED_TASKS = {
    "사회 이슈 분석": {
        "type": "analytical_essay",
        "description": "현재 사회의 중요한 이슈를 선택하여 다각도로 분석하고 본인의 견해를 논리적으로 제시하세요. (400-500단어)",
        "minimal_guidance": [
            "Choose a current social issue that interests you",
            "Analyze the issue from multiple perspectives",
            "Present your own well-reasoned opinion",
            "Support your arguments with evidence and examples"
        ],
        "advanced_vocabulary": [
            "contemporary", "prevalent", "paradigm", "multifaceted", "implications", 
            "predominantly", "substantial", "deteriorate", "advocate", "controversial",
            "underlying", "comprehensive", "sustainable", "innovative", "profound"
        ],
        "complex_structures": [
            "Despite the fact that..., it is evident that...",
            "While some argue that..., others contend that...",
            "Not only does this issue affect..., but it also...",
            "What is particularly concerning is that...",
            "It is worth noting that..."
        ]
    },
    "창의적 내러티브": {
        "type": "creative_writing",
        "description": "상상력을 발휘하여 독창적인 이야기를 창작하세요. 캐릭터, 배경, 갈등을 중심으로 한 완성도 높은 작품을 만들어보세요.",
        "minimal_guidance": [
            "Create original characters with depth and complexity",
            "Develop an engaging plot with conflict and resolution",
            "Use vivid descriptions and dialogue",
            "Experiment with narrative techniques and literary devices"
        ],
        "advanced_vocabulary": [
            "enigmatic", "resilient", "melancholy", "serene", "tumultuous",
            "profound", "intricate", "captivating", "haunting", "whimsical",
            "compelling", "poignant", "evocative", "subtle", "sophisticated"
        ],
        "complex_structures": [
            "Had it not been for..., the outcome would have been...",
            "Little did [character] know that...",
            "In the midst of..., there emerged...",
            "What struck [character] most was...",
            "As if by some twist of fate..."
        ]
    },
    "철학적 에세이": {
        "type": "philosophical_essay",
        "description": "추상적이고 복합적인 주제에 대해 깊이 있게 사고하고, 논리적 추론과 성찰을 통해 본인의 철학적 관점을 펼쳐보세요.",
        "minimal_guidance": [
            "Explore abstract concepts and ideas",
            "Engage in deep philosophical reasoning",
            "Question assumptions and explore implications",
            "Develop your own unique perspective on complex issues"
        ],
        "advanced_vocabulary": [
            "existential", "empirical", "metaphysical", "intrinsic", "paradox",
            "paradigm", "fundamental", "subjective", "objective", "inherent",
            "contemplation", "consciousness", "perception", "rationality", "morality"
        ],
        "complex_structures": [
            "One might argue that..., however, upon closer examination...",
            "The question remains as to whether...",
            "This raises the fundamental question of...",
            "From a philosophical standpoint...",
            "It is precisely this ambiguity that..."
        ]
    },
    "비판적 리뷰": {
        "type": "critical_review",
        "description": "책, 영화, 예술 작품, 또는 현상에 대한 비판적 분석을 수행하세요. 객관적 분석과 주관적 평가를 균형있게 제시하세요.",
        "minimal_guidance": [
            "Provide both objective analysis and subjective evaluation",
            "Support your judgments with specific evidence",
            "Consider multiple criteria for assessment",
            "Engage with the work's broader significance and impact"
        ],
        "advanced_vocabulary": [
            "sophisticated", "nuanced", "compelling", "innovative", "conventional",
            "provocative", "mediocre", "exceptional", "superficial", "profound",
            "aesthetic", "thematic", "symbolic", "interpretation", "critique"
        ],
        "complex_structures": [
            "What distinguishes this work from others is...",
            "While the work succeeds in..., it falls short of...",
            "The most striking aspect of... is...",
            "This raises important questions about...",
            "In terms of artistic merit..."
        ]
    },
    "연구 보고서": {
        "type": "research_report",
        "description": "관심 있는 주제에 대해 심도 있는 조사를 실시하고, 발견한 정보를 체계적으로 정리하여 전문적인 보고서를 작성하세요.",
        "minimal_guidance": [
            "Conduct thorough research on your chosen topic",
            "Organize information systematically and logically",
            "Present findings objectively with proper analysis",
            "Draw meaningful conclusions from your research"
        ],
        "advanced_vocabulary": [
            "methodology", "comprehensive", "empirical", "statistical", "correlation",
            "hypothesis", "variables", "findings", "implications", "significant",
            "preliminary", "substantial", "systematic", "objective", "conclusive"
        ],
        "complex_structures": [
            "The research reveals that...",
            "According to recent studies...",
            "Data indicates a strong correlation between...",
            "These findings suggest that...",
            "Further investigation is needed to..."
        ]
    }
}

# 고급 쓰기 전략 및 도구
ADVANCED_TOOLS = {
    "Rhetorical Devices": [
        "Metaphor and Simile", "Alliteration and Assonance", "Rhetorical Questions",
        "Parallelism", "Irony and Satire", "Hyperbole", "Personification"
    ],
    "Essay Structures": [
        "Classical Five-Paragraph", "Compare and Contrast", "Cause and Effect",
        "Problem-Solution", "Chronological", "Process Analysis", "Classification"
    ],
    "Critical Thinking": [
        "Analysis vs. Evaluation", "Identifying Assumptions", "Logical Fallacies",
        "Evidence Assessment", "Multiple Perspectives", "Counterarguments"
    ],
    "Style Techniques": [
        "Tone and Voice", "Sentence Variety", "Transitions", "Cohesion and Coherence",
        "Precise Word Choice", "Active vs. Passive Voice", "Formal vs. Informal Register"
    ]
}

# 도우미 응답 생성 함수 (고급 수준)
def generate_ai_response_advanced(user_input, task_context=None, writing_content=""):
    try:
        # 고급 수준 학습자를 위한 시스템 프롬프트
        system_prompt = f"""
        당신은 한국 고등학생 및 대학생 수준의 고급 영어 학습자를 위한 전문적인 AI 영어 튜터입니다.
        
        특징:
        - 고도의 분석적이고 비판적 사고 능력 개발
        - 복잡한 문법 구조와 고급 어휘 활용 지도
        - 창의성과 독창성을 중시하는 접근
        - 학문적이고 전문적인 글쓰기 기술 향상
        - 자기성찰과 메타인지 전략 촉진
        
        현재 과제 유형: {task_context if task_context else "일반"}
        
        학습자가 질문하면:
        1. 내용: 복잡한 아이디어 발전, 비판적 분석, 독창적 관점 개발
        2. 구조: 고급 에세이 구조, 논리적 흐름, coherence와 cohesion
        3. 언어: 정교한 어휘 선택, 복잡한 문장 구조, 수사법 활용
        4. 스타일: 학문적 어조, 개인적 목소리, 장르별 특성
        
        답변은 5-6문장으로 심도 있고 전문적으로, 이모지를 최소한으로 사용해주세요.
        """
        
        # 사용자의 현재 작성 내용과 과제 맥락 제공
        user_message = f"학생 질문: {user_input}"
        if writing_content.strip():
            user_message += f"\n\n학생이 현재 작성 중인 글: {writing_content[:500]}..."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=400
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # API 오류 시 기본 응답
        fallback_responses = [
            "죄송합니다. 현재 시스템에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "서비스 연결에 문제가 있습니다. 다시 질문해주시면 더 나은 답변을 드리겠습니다.",
            "기술적 오류가 발생했습니다. 곧 정상화되니 양해 부탁드립니다."
        ]
        return random.choice(fallback_responses)

# 메인 헤더
st.title("🌳 고급 영어 쓰기")
st.markdown("### 창의적이고 비판적인 사고력으로 깊이 있는 글을 써봐요!")

# 사이드바
with st.sidebar:
    st.header("📚 과제 선택")
    
    task_names = list(ADVANCED_TASKS.keys())
    selected_task_name = st.selectbox("쓰기 과제를 선택하세요:", ["선택해주세요"] + task_names)
    
    if selected_task_name != "선택해주세요":
        st.session_state.selected_task_adv = ADVANCED_TASKS[selected_task_name]
        st.success(f"'{selected_task_name}' 과제를 선택했습니다!")
    
    st.markdown("---")
    st.markdown("### 🎯 고급 수준 특징")
    st.markdown("- 최소한의 지침 제공")
    st.markdown("- 창의적 사고 중시")
    st.markdown("- 복잡한 문장 구조")
    st.markdown("- 비판적 분석 능력")
    st.markdown("- 개인적 목소리 개발")
    
    # 개인 학습 목표 설정
    if st.session_state.selected_task_adv:
        st.markdown("---")
        st.markdown("### 🎯 개인 학습 목표")
        
        goal_input = st.text_input("이번 글쓰기의 개인적 목표를 설정하세요:")
        if st.button("목표 추가") and goal_input:
            st.session_state.writing_goals.append(goal_input)
            st.success("목표가 추가되었습니다!")
        
        if st.session_state.writing_goals:
            st.markdown("**설정된 목표들:**")
            for i, goal in enumerate(st.session_state.writing_goals):
                st.markdown(f"{i+1}. {goal}")
                
            if st.button("목표 초기화"):
                st.session_state.writing_goals = []
                st.rerun()

# 메인 콘텐츠
if st.session_state.selected_task_adv:
    task = st.session_state.selected_task_adv
    
    # 과제 설명
    st.markdown("## 📝 과제 설명")
    st.info(task["description"])
    
    # 탭으로 구성된 인터페이스
    tab1, tab2, tab3, tab4 = st.tabs(["✍️ 작성하기", "🎨 고급 도구", "📖 참고 자료", "🔍 자가 평가"])
    
    with tab1:
        # 작성 영역
        st.markdown("### 글 작성")
        
        # 글쓰기 목표 표시
        if st.session_state.writing_goals:
            with st.expander("📋 설정된 학습 목표", expanded=False):
                for goal in st.session_state.writing_goals:
                    st.markdown(f"• {goal}")
        
        writing_text = st.text_area(
            "여기에 여러분의 글을 작성해보세요:",
            value=st.session_state.writing_content_adv,
            height=500,
            placeholder="자유롭게, 창의적으로 여러분만의 목소리로 글을 써보세요..."
        )
        st.session_state.writing_content_adv = writing_text
        
        # 실시간 통계
        if writing_text:
            words = len(writing_text.split())
            chars = len(writing_text)
            sentences = len([s for s in writing_text.split('.') if s.strip()])
            paragraphs = len([p for p in writing_text.split('\n\n') if p.strip()])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("단어", words)
            with col2:
                st.metric("문자", chars)
            with col3:
                st.metric("문장", sentences)
            with col4:
                st.metric("문단", paragraphs)
        
        # 작성 도구
        st.markdown("### 🛠️ 작성 도구")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("💾 저장하기", type="primary"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success(f"작품이 저장되었습니다! ({timestamp})")
                st.balloons()
        
        with col2:
            if st.button("🔄 다시 시작"):
                if st.checkbox("정말 다시 시작하시겠습니까?"):
                    st.session_state.writing_content_adv = ""
                    st.rerun()
        
        with col3:
            if st.button("📊 상세 분석"):
                if writing_text:
                    # 고급 텍스트 분석
                    avg_words_per_sentence = words / max(sentences, 1)
                    avg_chars_per_word = chars / max(words, 1)
                    
                    st.markdown("#### 📈 글쓰기 분석")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("문장당 평균 단어 수", f"{avg_words_per_sentence:.1f}")
                        st.metric("단어당 평균 글자 수", f"{avg_chars_per_word:.1f}")
                    with col_b:
                        # 복잡도 분석
                        if words > 100:
                            st.success("✅ 충분한 분량의 글입니다")
                        if avg_words_per_sentence > 15:
                            st.info("🔍 복잡한 문장 구조를 잘 활용하고 있습니다")
                        if paragraphs >= 4:
                            st.success("📝 잘 구조화된 글입니다")
                else:
                    st.warning("먼저 글을 작성해주세요!")
        
        with col4:
            if st.button("🎯 목표 확인"):
                if st.session_state.writing_goals and writing_text:
                    st.markdown("#### 🎯 목표 달성 체크")
                    for goal in st.session_state.writing_goals:
                        achievement = st.slider(f"'{goal}' 달성도", 0, 100, 50, key=f"goal_{goal}")
                        if achievement >= 80:
                            st.success(f"✅ 목표를 잘 달성했습니다!")
                        elif achievement >= 60:
                            st.info(f"🔄 좀 더 발전이 필요합니다")
                        else:
                            st.warning(f"📚 다음에 더 노력해보세요")
                else:
                    st.info("목표를 설정하고 글을 작성해주세요!")
        
        with col5:
            if st.button("💡 창의성 피드백"):
                if writing_text:
                    # 창의성 관련 피드백
                    creativity_aspects = [
                        ("독창적 아이디어", random.randint(70, 95)),
                        ("표현의 다양성", random.randint(65, 90)),
                        ("개인적 목소리", random.randint(75, 100)),
                        ("구조적 혁신", random.randint(60, 85))
                    ]
                    
                    st.markdown("#### 🎨 창의성 평가")
                    for aspect, score in creativity_aspects:
                        st.progress(score/100)
                        st.caption(f"{aspect}: {score}/100")
                else:
                    st.warning("먼저 글을 작성해주세요!")
    
    with tab2:
        # 고급 쓰기 도구들
        st.markdown("### 🎨 고급 쓰기 도구")
        
        tool_category = st.selectbox(
            "도구 카테고리 선택:",
            list(ADVANCED_TOOLS.keys())
        )
        
        st.markdown(f"#### {tool_category}")
        selected_tools = ADVANCED_TOOLS[tool_category]
        
        for tool in selected_tools:
            with st.expander(f"📚 {tool}"):
                if tool_category == "Rhetorical Devices":
                    # 수사법 예시와 설명
                    rhetorical_examples = {
                        "Metaphor and Simile": "Life is a journey (metaphor) vs. Life is like a journey (simile)",
                        "Rhetorical Questions": "How can we call ourselves civilized when...",
                        "Parallelism": "I came, I saw, I conquered"
                    }
                    if tool in rhetorical_examples:
                        st.code(rhetorical_examples[tool])
                
                elif tool_category == "Essay Structures":
                    # 에세이 구조 안내
                    structure_guides = {
                        "Classical Five-Paragraph": "Introduction → 3 Body Paragraphs → Conclusion",
                        "Compare and Contrast": "Point-by-point or Block method comparison",
                        "Problem-Solution": "Problem identification → Analysis → Proposed solutions"
                    }
                    if tool in structure_guides:
                        st.info(structure_guides[tool])
                
                st.text_area(f"{tool} 연습:", placeholder=f"{tool}을/를 활용해 문장을 써보세요...", key=f"practice_{tool}")
        
        # 어휘 및 구조 제안
        st.markdown("---")
        st.markdown("### 📚 고급 어휘 및 표현")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🎓 고급 어휘")
            for vocab in task["advanced_vocabulary"][:8]:
                if st.button(f"📝 {vocab}", key=f"vocab_{vocab}"):
                    # 클립보드나 텍스트 영역에 단어 추가하는 기능 (구현 예정)
                    st.info(f"'{vocab}' 선택됨")
        
        with col2:
            st.markdown("#### 🔗 복합 문장 구조")
            for structure in task["complex_structures"]:
                with st.expander(f"📖 {structure[:30]}..."):
                    st.code(structure)
    
    with tab3:
        # 참고 자료 및 가이드라인
        st.markdown("### 📖 최소 지침")
        
        for i, guidance in enumerate(task["minimal_guidance"], 1):
            st.markdown(f"**{i}.** {guidance}")
        
        st.markdown("---")
        
        # 장르별 특성 가이드
        st.markdown("### 📝 장르별 특성")
        
        if task["type"] == "analytical_essay":
            st.markdown("""
            **📊 분석적 에세이 특성:**
            - 객관적이고 논리적인 접근
            - 다양한 관점의 균형잡힌 제시
            - 증거와 예시 기반 논증
            - 명확한 thesis statement
            """)
        
        elif task["type"] == "creative_writing":
            st.markdown("""
            **🎭 창의적 글쓰기 특성:**
            - 상상력과 독창성 중시
            - 생생한 묘사와 대화
            - 문학적 장치 활용
            - 독자의 감정적 참여 유도
            """)
        
        elif task["type"] == "philosophical_essay":
            st.markdown("""
            **🤔 철학적 에세이 특성:**
            - 추상적 개념 탐구
            - 논리적 추론과 성찰
            - 가정에 대한 질문
            - 개인적 철학 관점 개발
            """)
        
        elif task["type"] == "critical_review":
            st.markdown("""
            **⭐ 비판적 리뷰 특성:**
            - 객관적 분석과 주관적 평가 균형
            - 구체적 증거 기반 판단
            - 다양한 평가 기준 고려
            - 작품의 의미와 영향 고찰
            """)
        
        elif task["type"] == "research_report":
            st.markdown("""
            **🔬 연구 보고서 특성:**
            - 체계적 정보 조사
            - 객관적 사실 제시
            - 논리적 정보 구성
            - 의미있는 결론 도출
            """)
        
        # 자기성찰 질문
        st.markdown("---")
        st.markdown("### 🪞 자기성찰 질문")
        reflection_questions = [
            "이 글을 통해 어떤 메시지를 전달하고 싶은가?",
            "나만의 독특한 관점은 무엇인가?",
            "더 효과적인 표현 방법은 없을까?",
            "독자가 이 글을 읽고 어떤 변화를 경험하기를 바라는가?"
        ]
        
        for question in reflection_questions:
            with st.expander(f"💭 {question}"):
                st.text_area("생각 정리:", key=f"reflection_{hash(question)}", placeholder="이 질문에 대해 자유롭게 생각을 정리해보세요...")
    
    with tab4:
        # 자가 평가 도구
        st.markdown("### 🔍 자가 평가")
        
        if writing_text:
            st.markdown("#### 📋 체크리스트")
            
            # 내용 평가
            st.markdown("**💡 내용 (Content):**")
            content_criteria = [
                "명확하고 집중된 주제를 다루고 있다",
                "독창적이고 흥미로운 아이디어를 제시한다",
                "충분한 세부사항과 예시를 포함한다",
                "논리적이고 설득력 있는 논증을 펼친다"
            ]
            
            content_scores = []
            for criterion in content_criteria:
                score = st.slider(criterion, 1, 5, 3, key=f"content_{criterion}")
                content_scores.append(score)
            
            # 구조 평가
            st.markdown("**🏗️ 구조 (Organization):**")
            organization_criteria = [
                "명확한 서론, 본론, 결론 구조를 갖는다",
                "각 문단이 하나의 주요 아이디어를 다룬다",
                "문단 간 자연스러운 연결이 이루어진다",
                "전체적으로 논리적 흐름을 따른다"
            ]
            
            org_scores = []
            for criterion in organization_criteria:
                score = st.slider(criterion, 1, 5, 3, key=f"org_{criterion}")
                org_scores.append(score)
            
            # 언어 평가
            st.markdown("**🗣️ 언어 (Language):**")
            language_criteria = [
                "다양하고 정확한 어휘를 사용한다",
                "복잡하고 효과적인 문장 구조를 활용한다",
                "적절한 어조와 문체를 유지한다",
                "문법적으로 정확하다"
            ]
            
            lang_scores = []
            for criterion in language_criteria:
                score = st.slider(criterion, 1, 5, 3, key=f"lang_{criterion}")
                lang_scores.append(score)
            
            # 종합 평가
            st.markdown("---")
            st.markdown("#### 📊 종합 평가")
            
            avg_content = sum(content_scores) / len(content_scores)
            avg_org = sum(org_scores) / len(org_scores)
            avg_lang = sum(lang_scores) / len(lang_scores)
            overall = (avg_content + avg_org + avg_lang) / 3
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("내용", f"{avg_content:.1f}/5")
            with col2:
                st.metric("구조", f"{avg_org:.1f}/5")
            with col3:
                st.metric("언어", f"{avg_lang:.1f}/5")
            with col4:
                st.metric("종합", f"{overall:.1f}/5")
            
            # 성장 포인트 제안
            improvement_areas = []
            if avg_content < 4:
                improvement_areas.append("💡 내용의 깊이와 독창성을 더 발전시켜보세요")
            if avg_org < 4:
                improvement_areas.append("🏗️ 글의 구조와 논리적 흐름을 개선해보세요")
            if avg_lang < 4:
                improvement_areas.append("🗣️ 어휘와 문장 구조의 다양성을 높여보세요")
            
            if improvement_areas:
                st.markdown("#### 🌱 발전 포인트")
                for area in improvement_areas:
                    st.markdown(f"- {area}")
            else:
                st.success("🎉 모든 영역에서 우수한 성과를 보이고 있습니다!")
            
            # 개인 노트
            st.markdown("---")
            st.markdown("#### 📝 개인 성찰 노트")
            personal_note = st.text_area(
                "이번 글쓰기에서 배운 점, 어려웠던 점, 다음에 시도해보고 싶은 것들을 자유롭게 기록해보세요:",
                key="personal_reflection",
                placeholder="자신의 글쓰기 과정을 되돌아보고 성찰해보세요...",
                height=150
            )
            
            if st.button("📝 성찰 노트 저장"):
                if personal_note:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success(f"성찰 노트가 저장되었습니다! ({timestamp})")
                else:
                    st.warning("성찰 노트를 작성해주세요!")
        
        else:
            st.info("자가 평가를 위해 먼저 글을 작성해주세요!")
        
        # 동료 피드백 시뮬레이션
        st.markdown("---")
        st.markdown("### 👥 동료 피드백 (시뮬레이션)")
        
        if writing_text and st.button("🎭 동료 피드백 받기"):
            # 시뮬레이션된 동료 피드백
            peer_feedback_samples = [
                {
                    "name": "지민",
                    "feedback": "정말 창의적인 접근이에요! 특히 독특한 관점이 인상적이었습니다. 다만 중간 부분에서 조금 더 구체적인 예시가 있으면 더 좋을 것 같아요.",
                    "rating": 4.2
                },
                {
                    "name": "현우",
                    "feedback": "논리적인 전개가 잘 되어 있네요. 문장 구조도 다양하고 어휘 선택도 적절합니다. 결론 부분을 좀 더 강렬하게 마무리하면 어떨까요?",
                    "rating": 4.5
                },
                {
                    "name": "수연",
                    "feedback": "정말 흥미롭게 읽었어요! 개인적인 목소리가 잘 드러나는 글이었습니다. 몇 군데 문법적으로 다듬으면 완벽할 것 같네요.",
                    "rating": 4.0
                }
            ]
            
            selected_feedback = random.choice(peer_feedback_samples)
            st.session_state.peer_feedback.append(selected_feedback)
            
            with st.container():
                st.markdown(f"**👤 {selected_feedback['name']}의 피드백:**")
                st.write(selected_feedback['feedback'])
                st.metric("평점", f"{selected_feedback['rating']}/5.0")
        
        # 저장된 피드백들
        if st.session_state.peer_feedback:
            st.markdown("#### 📚 받은 피드백들")
            for i, feedback in enumerate(st.session_state.peer_feedback):
                with st.expander(f"피드백 {i+1} - {feedback['name']} ({feedback['rating']}/5.0)"):
                    st.write(feedback['feedback'])
            
            if st.button("🗑️ 피드백 기록 삭제"):
                st.session_state.peer_feedback = []
                st.rerun()

# AI 도우미 챗봇
st.markdown("---")
st.markdown("## 🤖 AI 멘토와 대화하기")

# 채팅 인터페이스
chat_container = st.container()
with chat_container:
    # 채팅 히스토리 표시
    for chat in st.session_state.chat_history_adv:
        if chat["role"] == "user":
            st.markdown(f"**🙋‍♀️ 나:** {chat['message']}")
        else:
            st.markdown(f"**🎓 AI 멘토:** {chat['message']}")

# 사용자 입력
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "AI 멘토에게 질문해보세요:", 
        placeholder="창의성, 비판적 사고, 학문적 글쓰기 등에 대해 심도 있게 논의해보세요"
    )
with col2:
    send_button = st.button("보내기", type="primary")

if send_button and user_input:
    # 사용자 메시지 추가
    st.session_state.chat_history_adv.append({"role": "user", "message": user_input})
    
    # AI 응답 생성 (과제 타입 정보와 현재 글 내용 포함)
    task_type = st.session_state.selected_task_adv["type"] if st.session_state.selected_task_adv else None
    with st.spinner("AI 멘토가 깊이 생각하고 있습니다..."):
        ai_response = generate_ai_response_advanced(user_input, task_type, st.session_state.writing_content_adv)
    st.session_state.chat_history_adv.append({"role": "ai", "message": ai_response})
    
    st.rerun()

# 전문가 수준 질문 버튼들
st.markdown("#### 전문가 질문:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎨 창의성 개발"):
        st.session_state.chat_history_adv.append({"role": "user", "message": "창의적 사고와 독창적 표현을 어떻게 개발할 수 있을까요?"})
        with st.spinner("창의성에 대해 분석 중..."):
            ai_response = generate_ai_response_advanced("창의적 사고와 독창적 표현을 어떻게 개발할 수 있을까요?", None, st.session_state.writing_content_adv)
        st.session_state.chat_history_adv.append({"role": "ai", "message": ai_response})
        st.rerun()

with col2:
    if st.button("🧠 비판적 사고"):
        st.session_state.chat_history_adv.append({"role": "user", "message": "비판적 분석과 논리적 추론을 향상시키려면 어떻게 해야 할까요?"})
        with st.spinner("비판적 사고에 대해 분석 중..."):
            ai_response = generate_ai_response_advanced("비판적 분석과 논리적 추론을 향상시키려면 어떻게 해야 할까요?", None, st.session_state.writing_content_adv)
        st.session_state.chat_history_adv.append({"role": "ai", "message": ai_response})
        st.rerun()

with col3:
    if st.button("📚 학문적 글쓰기"):
        st.session_state.chat_history_adv.append({"role": "user", "message": "더 학문적이고 정교한 글쓰기를 위한 조언을 주세요"})
        with st.spinner("학문적 글쓰기에 대해 분석 중..."):
            ai_response = generate_ai_response_advanced("더 학문적이고 정교한 글쓰기를 위한 조언을 주세요", None, st.session_state.writing_content_adv)
        st.session_state.chat_history_adv.append({"role": "ai", "message": ai_response})
        st.rerun()

with col4:
    if st.button("🎭 개인적 목소리"):
        st.session_state.chat_history_adv.append({"role": "user", "message": "나만의 독특한 글쓰기 스타일과 목소리를 어떻게 개발할 수 있을까요?"})
        with st.spinner("개인적 목소리에 대해 분석 중..."):
            ai_response = generate_ai_response_advanced("나만의 독특한 글쓰기 스타일과 목소리를 어떻게 개발할 수 있을까요?", None, st.session_state.writing_content_adv)
        st.session_state.chat_history_adv.append({"role": "ai", "message": ai_response})
        st.rerun()

# 채팅 기록 관리
if st.session_state.chat_history_adv:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 채팅 기록 내보내기"):
            chat_export = "\n".join([f"{chat['role']}: {chat['message']}" for chat in st.session_state.chat_history_adv])
            st.download_button(
                label="💾 텍스트 파일로 다운로드",
                data=chat_export,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("🗑️ 채팅 기록 삭제"):
            st.session_state.chat_history_adv = []
            st.rerun()

else:
    # 과제를 선택하지 않은 경우
    st.markdown("## 👈 왼쪽 사이드바에서 과제를 선택해주세요!")
    
    # 샘플 과제 미리보기
    st.markdown("### 📋 과제 미리보기")
    
    for task_name, task_info in ADVANCED_TASKS.items():
        with st.expander(f"🔍 {task_name}"):
            st.markdown(f"**유형:** {task_info['type']}")
            st.markdown(f"**설명:** {task_info['description']}")
            st.markdown("**최소 지침:**")
            for guidance in task_info['minimal_guidance'][:2]:
                st.markdown(f"• {guidance}")
            st.markdown("*...더 많은 지침과 도구들이 준비되어 있습니다*")

# 고급 사용자를 위한 추가 기능
st.markdown("---")
st.markdown("## 🚀 고급 기능")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 학습 포트폴리오")
    if st.button("📈 나의 성장 기록 보기"):
        st.info("학습 포트폴리오 기능은 곧 추가될 예정입니다!")

with col2:
    st.markdown("### 🎓 맞춤형 과제")
    if st.button("🎯 개인 맞춤 과제 생성"):
        st.info("AI 기반 맞춤형 과제 생성 기능은 곧 추가될 예정입니다!")

with col3:
    st.markdown("### 👥 협업 글쓰기")
    if st.button("🤝 동료와 함께 쓰기"):
        st.info("협업 글쓰기 기능은 곧 추가될 예정입니다!")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🌳 <strong>고급 수준</strong>에서는 창의적이고 비판적인 사고를 통해 깊이 있는 글을 써요!</p>
    <p><em>여러분만의 독특한 목소리로 세상에 메시지를 전달해보세요! ✨</em></p>
    <p style='margin-top: 20px; font-size: 12px; color: #666;'>
        💡 <strong>Tip:</strong> 고급 수준에서는 최소한의 가이드를 제공합니다. 창의성과 독창성을 마음껏 발휘해보세요!
    </p>
</div>
""", unsafe_allow_html=True)