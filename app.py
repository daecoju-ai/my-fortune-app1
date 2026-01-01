import streamlit as st
from datetime import datetime, timedelta
import random
import json

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="2026 Fortune × MBTI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# 세션 상태
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "step" not in st.session_state:
    st.session_state.step = "input"
if "name" not in st.session_state:
    st.session_state.name = ""
if "mbti" not in st.session_state:
    st.session_state.mbti = ""
if "birth" not in st.session_state:
    st.session_state.birth = {"y": 2000, "m": 1, "d": 1}

# =========================
# 다국어 텍스트
# =========================
TEXT = {
    "ko": {
        "title": "2026 운세 × MBTI",
        "sub": "무료 · 오늘 / 내일 / 연간",
        "name": "이름 (선택)",
        "birth": "생년월일",
        "lang": "언어",
        "mbti_mode": "MBTI 선택 방식",
        "direct": "직접 입력",
        "simple": "간단 테스트 (12문항)",
        "detail": "상세 테스트 (16문항)",
        "result": "운세 보기",
        "share": "친구에게 결과 공유",
        "reset": "처음부터 다시",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year": "2026 전체 운세",
        "love": "연애",
        "money": "재물",
        "work": "일 / 학업",
        "health": "건강",
        "tip": "행운 포인트",
        "ad": "광고",
        "ad_msg": "정수기 렌탈 고민되면 다나눔렌탈",
    },
    "en": {
        "title": "2026 Fortune × MBTI",
        "sub": "Free · Today / Tomorrow / Year",
        "name": "Name (optional)",
        "birth": "Birth date",
        "lang": "Language",
        "mbti_mode": "MBTI method",
        "direct": "Direct input",
        "simple": "Simple test (12)",
        "detail": "Detailed test (16)",
        "result": "View result",
        "share": "Share result",
        "reset": "Restart",
        "today": "Today",
        "tomorrow": "Tomorrow",
        "year": "Year 2026",
        "love": "Love",
        "money": "Money",
        "work": "Work",
        "health": "Health",
        "tip": "Lucky tip",
        "ad": "Ad",
        "ad_msg": "Looking for water purifier rental?",
    },
}

# =========================
# 공통 데이터
# =========================
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

FORTUNE_POOL = {
    "today": [
        "집중력이 높아지는 날입니다. 중요한 결정에 좋아요.",
        "사람과의 대화에서 기회가 생길 수 있어요.",
        "무리하지 말고 페이스 조절이 필요합니다.",
        "기분 좋은 소식이 들어올 가능성이 큽니다."
    ],
    "tomorrow": [
        "작은 선택이 큰 결과로 이어질 수 있어요.",
        "계획을 정리하면 마음이 편해집니다.",
        "주변 도움을 받는 것이 유리합니다.",
        "휴식이 필요한 하루가 될 수 있어요."
    ],
    "year": [
        "2026년은 방향을 잡는 해가 됩니다.",
        "꾸준함이 가장 큰 무기가 되는 해입니다.",
        "사람 관계가 운을 좌우합니다.",
        "새로운 도전을 해볼 만한 해입니다."
    ],
    "love": [
        "솔직한 표현이 관계를 깊게 만듭니다.",
        "서두르지 않는 것이 중요합니다.",
        "기존 인연이 더 단단해질 수 있어요."
    ],
    "money": [
        "지출 관리에 신경 쓰면 안정됩니다.",
        "작은 수익이 쌓이는 흐름입니다.",
        "충동 소비만 피하면 좋습니다."
    ],
    "work": [
        "정리 능력이 빛을 발합니다.",
        "협업에서 성과가 납니다.",
        "혼자보다 함께할 때 유리합니다."
    ],
    "health": [
        "생활 리듬 관리가 중요합니다.",
        "과로만 주의하세요.",
        "가벼운 운동이 도움이 됩니다."
    ],
    "tip": [
        "파란색 계열",
        "아침 시간 활용",
        "메모 습관",
        "정리 정돈"
    ]
}

# =========================
# 유틸
# =========================
def seeded_choice(arr, seed):
    random.seed(seed)
    return random.choice(arr)

def today_seed():
    return int(datetime.now().strftime("%Y%m%d"))

# =========================
# UI 상단
# =========================
lang = st.radio(
    TEXT[st.session_state.lang]["lang"],
    ["ko","en"],
    index=0 if st.session_state.lang=="ko" else 1,
    horizontal=True
)
st.session_state.lang = lang
t = TEXT[lang]

st.markdown(f"<h1 style='text-align:center'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:gray'>{t['sub']}</p>", unsafe_allow_html=True)

# =========================
# 입력 화면
# =========================
if st.session_state.step == "input":
    st.session_state.name = st.text_input(t["name"], st.session_state.name)

    c1,c2,c3 = st.columns(3)
    st.session_state.birth["y"] = c1.number_input("Y",1900,2030,st.session_state.birth["y"])
    st.session_state.birth["m"] = c2.number_input("M",1,12,st.session_state.birth["m"])
    st.session_state.birth["d"] = c3.number_input("D",1,31,st.session_state.birth["d"])

    mode = st.radio(
        t["mbti_mode"],
        [t["direct"], t["simple"], t["detail"]]
    )

    if mode == t["direct"]:
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST)

    if st.button(t["result"], use_container_width=True):
        if not st.session_state.mbti:
            st.session_state.mbti = random.choice(MBTI_LIST)
        st.session_state.step = "result"
        st.experimental_rerun()

# =========================
# 결과 화면
# =========================
if st.session_state.step == "result":
    seed = today_seed()
    name = st.session_state.name
    mbti = st.session_state.mbti

    st.markdown(
        f"<h2 style='text-align:center'>{name} {mbti}</h2>",
        unsafe_allow_html=True
    )

    for key in ["today","tomorrow","year","love","money","work","health"]:
        st.markdown(
            f"**{t[key]}**  \n"
            f"{seeded_choice(FORTUNE_POOL[key], seed+hash(key))}"
        )

    st.markdown(
        f"**{t['tip']}** : {seeded_choice(FORTUNE_POOL['tip'], seed)}"
    )

    # 광고 (한국어만)
    if lang == "ko":
        st.markdown("---")
        st.markdown(f"**{t['ad']}**")
        st.info(t["ad_msg"])

    # 공유 (모바일 = 시스템 공유 / PC = 복사)
    share_text = (
        f"{t['title']}\n"
        f"{name} {mbti}\n\n"
        f"{t['today']}: {seeded_choice(FORTUNE_POOL['today'], seed)}\n"
        f"{t['tomorrow']}: {seeded_choice(FORTUNE_POOL['tomorrow'], seed)}\n"
    )

    st.components.v1.html(f"""
    <script>
    function shareResult() {{
        if (navigator.share) {{
            navigator.share({{
                text: `{share_text}`
            }});
        }} else {{
            navigator.clipboard.writeText(`{share_text}`);
            alert("복사되었습니다");
        }}
    }}
    </script>
    <button onclick="shareResult()" style="
        width:100%;
        padding:14px;
        font-size:16px;
        border-radius:12px;
        border:none;
        background:#6f42c1;
        color:white;
        font-weight:bold;
    ">{t['share']}</button>
    """, height=80)

    if st.button(t["reset"], use_container_width=True):
        st.session_state.clear()
        st.experimental_rerun()
