import streamlit as st
from datetime import datetime, timedelta, date
import random
import json
import streamlit.components.v1 as components


# =========================
# 다국어 번역/데이터
# =========================
translations = {
    "ko": {
        "lang_label": "언어 / Language",
        "title": "⭐ 2026년 운세 ⭐",
        "subtitle": "띠 + MBTI + 사주 + 오늘/내일 운세",
        "name_label": "이름 입력 (결과에 표시돼요)",
        "birth_label": "생년월일 입력",
        "mbti_mode": "MBTI는 어떻게 할까요?",
        "mbti_direct": "직접 선택(이미 알아요)",
        "mbti_test": "간단 테스트(12문항)",
        "btn_view": "2026년 운세 보기!",
        "btn_view_test": "테스트 결과로 운세 보기!",
        "combo": "최고 조합!",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "overall_title": "2026 전체 운세",
        "combo_title": "조합 한 마디",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "tip_title": "팁",
        "tarot_btn": "오늘의 타로 카드 보기",
        "tarot_title": "오늘의 타로 카드",
        "share_btn": "친구에게 공유하기",
        "reset_btn": "처음부터 다시하기",
        "error_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "ad_badge": "광고",
        "ad_title": "🔥 정수기 렌탈 대박!",
        "ad_line1": "제휴카드면 월 0원부터!",
        "ad_line2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍 ✨",
        "ad_link": "🔗 다나눔렌탈.com 바로가기",
        "test_caption": "총 12문항(약 30초) — 솔직하게 고르면 더 잘 맞아요 🙂",
        "sec_ei": "1) 에너지(E/I)",
        "sec_sn": "2) 인식(S/N)",
        "sec_tf": "3) 판단(T/F)",
        "sec_jp": "4) 생활(J/P)",
        "share_title": "2026년 운세",
        "share_fail_copy": "공유 기능이 지원되지 않아 텍스트를 복사했어요!\n카톡에 붙여넣기 해주세요.",
        "share_manual_prompt": "아래 내용을 복사해서 카톡에 붙여넣기 해주세요:",
        "share_cancel": "공유가 취소되었거나 지원되지 않아요.\n복사 후 붙여넣기 해주세요."
    },
    "en": {
        "lang_label": "Language / 언어",
        "title": "⭐ 2026 Fortune ⭐",
        "subtitle": "Zodiac + MBTI + Fortune + Today/Tomorrow Luck",
        "name_label": "Name (shown in result)",
        "birth_label": "Birth date",
        "mbti_mode": "How to do MBTI?",
        "mbti_direct": "Select directly (I know it)",
        "mbti_test": "Quick test (12 questions)",
        "btn_view": "See my 2026 fortune!",
        "btn_view_test": "See fortune from test result!",
        "combo": "Best Combo!",
        "zodiac_title": "Zodiac fortune",
        "mbti_title": "MBTI traits",
        "saju_title": "Fortune comment",
        "today_title": "Today's luck",
        "tomorrow_title": "Tomorrow's luck",
        "overall_title": "2026 annual luck",
        "combo_title": "Combination meaning",
        "lucky_color_title": "Lucky color",
        "lucky_item_title": "Lucky item",
        "tip_title": "Tip",
        "tarot_btn": "Draw today's tarot card",
        "tarot_title": "Today's tarot card",
        "share_btn": "Share with friends",
        "reset_btn": "Start over",
        "error_year": "Please enter a birth year between 1900 and 2030!",
        "ad_badge": "Ad",
        "ad_title": "🔥 Water purifier rental deal!",
        "ad_line1": "From 0 won/month with partner card!",
        "ad_line2": "Up to 500,000 won support + gifts ✨",
        "ad_link": "🔗 Go to DananumRental.com",
        "test_caption": "12 questions (~30 sec) — answer honestly 🙂",
        "sec_ei": "1) Energy (E/I)",
        "sec_sn": "2) Perception (S/N)",
        "sec_tf": "3) Decision (T/F)",
        "sec_jp": "4) Lifestyle (J/P)",
        "share_title": "2026 Fortune",
        "share_fail_copy": "Sharing isn't supported here, so the text was copied.\nPaste it in KakaoTalk or message.",
        "share_manual_prompt": "Copy and paste this text to share:",
        "share_cancel": "Sharing was canceled or not supported.\nPlease copy & paste."
    }
}

# KO/EN 각각 띠/설명
ZODIAC_LIST_KO = ["쥐띠", "소띠", "호랑이띠", "토끼띠", "용띠", "뱀띠", "말띠", "양띠", "원숭이띠", "닭띠", "개띠", "돼지띠"]
ZODIAC_LIST_EN = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]

ZODIACS = {
    "ko": {
        "쥐띠": "안정 속 새로운 기회! 민첩한 판단으로 성공 잡아요",
        "소띠": "꾸준함의 결실! 안정된 성장과 행복한 가족운",
        "호랑이띠": "대박 띠! 도전과 성공, 리더십 발휘로 큰 성과",
        "토끼띠": "삼재 주의! 신중함으로 변화 대처, 안정 추구",
        "용띠": "운기 상승! 리더십과 승진 기회 많음",
        "뱀띠": "직감과 실속! 예상치 못한 재물운",
        "말띠": "본띠 해! 추진력 강하지만 균형이 핵심",
        "양띠": "대박 띠! 편안함과 최고 돈운, 가정 행복",
        "원숭이띠": "변화와 재능 발휘! 창의력으로 성공",
        "닭띠": "노력 결실! 인정과 승진 가능성 높음",
        "개띠": "대박 띠! 귀인 도움과 네트워킹으로 상승",
        "돼지띠": "여유와 재물 대박! 즐기는 최고의 해"
    },
    "en": {
        "Rat": "New opportunities within stability! Quick judgment brings success",
        "Ox": "Rewards of persistence! Stable growth and family happiness",
        "Tiger": "Big luck! Challenge, success, and strong leadership",
        "Rabbit": "Be cautious with changes! Stay steady and careful",
        "Dragon": "Rising fortune! Leadership and promotion chances",
        "Snake": "Intuition pays off! Unexpected wealth",
        "Horse": "Your zodiac year! Strong drive, but balance is key",
        "Goat": "Big luck! Comfort, money luck, happy home",
        "Monkey": "Change and talent shine! Creativity leads to success",
        "Rooster": "Effort rewarded! Recognition and promotion possible",
        "Dog": "Big luck! Helpful people and networking boost",
        "Pig": "Relaxation and wealth! Enjoy a great year"
    }
}

MBTIS = {
    "ko": {
        "INTJ": "냉철 전략가", "INTP": "아이디어 천재", "ENTJ": "보스", "ENTP": "토론왕",
        "INFJ": "마음 마스터", "INFP": "감성 예술가", "ENFJ": "모두 선생님", "ENFP": "인간 비타민",
        "ISTJ": "규칙 지킴이", "ISFJ": "세상 따뜻함", "ESTJ": "리더", "ESFJ": "분위기 메이커",
        "ISTP": "고치는 장인", "ISFP": "감성 힐러", "ESTP": "모험왕", "ESFP": "파티 주인공"
    },
    "en": {
        "INTJ": "Strategist", "INTP": "Thinker", "ENTJ": "Commander", "ENTP": "Debater",
        "INFJ": "Advocate", "INFP": "Mediator", "ENFJ": "Protagonist", "ENFP": "Campaigner",
        "ISTJ": "Logistician", "ISFJ": "Defender", "ESTJ": "Executive", "ESFJ": "Consul",
        "ISTP": "Virtuoso", "ISFP": "Adventurer", "ESTP": "Entrepreneur", "ESFP": "Entertainer"
    }
}

SAJU_MSGS = {
    "ko": [
        "목(木) 기운 강함 → 성장과 발전의 해!",
        "화(火) 기운 강함 → 열정 폭발!",
        "토(土) 기운 강함 → 안정과 재물운",
        "금(金) 기운 강함 → 결단력 좋음!",
        "수(水) 기운 강함 → 지혜와 흐름",
        "오행 균형 → 행복한 한 해",
        "양기 강함 → 도전 성공",
        "음기 강함 → 내면 성찰"
    ],
    "en": [
        "Strong Wood → A year of growth!",
        "Strong Fire → Passion explodes!",
        "Strong Earth → Stability & wealth",
        "Strong Metal → Decisive energy!",
        "Strong Water → Wisdom & flow",
        "Balanced elements → Happy year",
        "Strong Yang → Challenge & success",
        "Strong Yin → Inner reflection"
    ]
}

DAILY_MSGS = {
    "ko": [
        "재물운 좋음! 작은 투자도 이득 봐요",
        "연애운 최고! 고백하거나 데이트 좋음",
        "건강 주의! 과로 피하고 쉬세요",
        "전체운 대박! 좋은 일만 생길 거예요",
        "인간관계 운 좋음! 귀인 만남 가능",
        "학업/일 운 최고! 집중력 최고",
        "여행운 좋음! 갑자기 떠나도 괜찮아요",
        "기분 좋은 하루! 웃음이 가득할 거예요"
    ],
    "en": [
        "Money luck is great! Even small investments pay off",
        "Love luck is high! Great day for dates/confessions",
        "Health caution! Avoid overwork and rest well",
        "Overall big luck! Good things are coming",
        "Relationships are good! Helpful people may appear",
        "Best for study/work! Your focus is strong",
        "Travel luck is good! Spontaneous trips are okay",
        "A happy day full of laughter"
    ]
}

OVERALL_FORTUNES = {
    "ko": [
        "성장과 재물이 함께하는 최고의 해! 대박 기운 가득",
        "안정과 행복이 넘치는 한 해! 가족과 함께하는 기쁨",
        "도전과 성공의 해! 큰 성과를 이룰 거예요",
        "사랑과 인연이 피어나는 로맨틱한 해",
        "변화와 새로운 시작! 창의력이 빛나는 한 해"
    ],
    "en": [
        "Growth and wealth together — your best year!",
        "A stable and happy year with family joy",
        "A year of challenge & success with big achievements",
        "A romantic year where love blooms",
        "A year of change and new beginnings — creativity shines"
    ]
}

COMBO_COMMENTS = {
    "ko": [
        "{}의 노력과 {}의 따뜻함으로 모두를 이끄는 리더가 될 거예요!",
        "{}의 리더십과 {}의 창의력이 완벽한 시너지!",
        "{}의 직감과 {}의 논리로 무적 조합!",
        "{}의 안정감과 {}의 열정으로 대박 성공!",
        "{}의 유연함과 {}의 결단력으로 모든 일 해결!"
    ],
    "en": [
        "With {}'s drive and {}'s warmth, you can lead people!",
        "{}'s leadership + {}'s creativity = perfect synergy!",
        "{}'s intuition + {}'s logic = an unbeatable combo!",
        "{}'s stability + {}'s passion = big success!",
        "{}'s flexibility + {}'s decisiveness = problem solver!"
    ]
}

LUCKY_COLORS = {"ko": ["골드", "레드", "블루", "그린", "퍼플"], "en": ["Gold", "Red", "Blue", "Green", "Purple"]}
LUCKY_ITEMS = {
    "ko": ["황금 액세서리", "빨간 지갑", "파란 목걸이", "초록 식물", "보라색 펜"],
    "en": ["Golden accessory", "Red wallet", "Blue necklace", "Green plant", "Purple pen"]
}
TIPS = {
    "ko": [
        "새로운 사람 만나는 기회 많아요. 적극적으로!",
        "작은 투자에 집중하세요. 이득 볼 가능성 높음",
        "건강 관리에 신경 쓰세요. 규칙적인 운동 추천",
        "가족/친구와 시간 보내세요. 행복 충전!",
        "창의적인 취미를 시작해보세요. 재능 발휘될 거예요"
    ],
    "en": [
        "Many chances to meet new people. Be proactive!",
        "Focus on small investments. Profit chance is high",
        "Take care of health. Regular exercise helps",
        "Spend time with family/friends. Recharge happiness",
        "Start a creative hobby. Your talent will shine"
    ]
}

TAROT_CARDS = {
    "The Fool": {"ko": "바보 - 새로운 시작, 모험, 순수한 믿음", "en": "New beginnings, adventure, innocence"},
    "The Magician": {"ko": "마법사 - 창조력, 능력 발휘, 집중", "en": "Skill, manifestation, focus"},
    "The High Priestess": {"ko": "여사제 - 직감, 신비, 내면의 목소리", "en": "Intuition, mystery, inner voice"},
    "The Empress": {"ko": "여제 - 풍요, 어머니의 사랑, 창작", "en": "Abundance, nurturing, creativity"},
    "The Emperor": {"ko": "황제 - 안정, 권위, 구조", "en": "Stability, authority, structure"},
    "The Lovers": {"ko": "연인 - 사랑, 조화, 선택", "en": "Love, harmony, choices"},
    "The Chariot": {"ko": "전차 - 승리, 의지력, 방향", "en": "Victory, willpower, direction"},
    "The Star": {"ko": "별 - 희망, 영감, 치유", "en": "Hope, inspiration, healing"},
    "The Sun": {"ko": "태양 - 행복, 성공, 긍정 에너지", "en": "Happiness, success, positivity"},
    "The World": {"ko": "세계 - 완성, 성취, 전체성", "en": "Completion, achievement, wholeness"}
}


# =========================
# 유틸
# =========================
def get_zodiac(year: int, lang: str):
    if not (1900 <= year <= 2030):
        return None
    idx = (year - 4) % 12
    return (ZODIAC_LIST_EN[idx] if lang == "en" else ZODIAC_LIST_KO[idx])

def get_saju(year: int, month: int, day: int, lang: str):
    return SAJU_MSGS[lang][(year + month + day) % 8]

def daily_fortune(zodiac: str, lang: str, offset=0):
    # 오늘/내일: 날짜+띠로 고정
    today = datetime.now() + timedelta(days=offset)
    z_list = ZODIAC_LIST_EN if lang == "en" else ZODIAC_LIST_KO
    seed = int(today.strftime("%Y%m%d")) + z_list.index(zodiac)
    rng = random.Random(seed)
    return rng.choice(DAILY_MSGS[lang])

def stable_rng(name: str, y: int, m: int, d: int, mbti: str, lang: str):
    key = f"{lang}|{name}|{y:04d}-{m:02d}-{d:02d}|{mbti}"
    seed = abs(hash(key)) % (10**9)
    return random.Random(seed)


# =========================
# Streamlit 기본
# =========================
st.set_page_config(page_title="2026 Fortune", layout="centered")

# 세션
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "result" not in st.session_state:
    st.session_state.result = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "birthdate" not in st.session_state:
    st.session_state.birthdate = date(2005, 1, 1)
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFJ"

# 언어 선택
st.session_state.lang = st.radio(
    translations[st.session_state.lang]["lang_label"],
    ["ko", "en"],
    index=0 if st.session_state.lang == "ko" else 1,
    horizontal=True
)
lang = st.session_state.lang
t = translations[lang]

# =========================
# 모바일 최적화 CSS (상단 잘림 방지)
# =========================
st.markdown(
    """
    <style>
      header {visibility: hidden;}
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      .stApp { background: #efe9ff; }

      .block-container {
        padding-top: 10px !important;
        padding-bottom: 30px !important;
        max-width: 760px;
      }

      .title {
        font-size: 28px; font-weight: 900; color:#2b2b2b; text-align:center;
        margin: 14px 0 4px;
      }
      .subtitle {
        font-size: 14px; font-weight: 700; color:#555; text-align:center;
        margin: 0 0 14px;
      }

      .card {
        background: rgba(255,255,255,0.75);
        border: 1px solid rgba(140,120,200,0.25);
        border-radius: 18px;
        padding: 16px 16px;
        box-shadow: 0 10px 22px rgba(0,0,0,0.08);
        margin: 10px 0 16px;
      }
      .card p { margin: 6px 0; line-height: 1.65; font-size: 14.5px; color:#2b2b2b; }
      .kv { font-weight: 900; }

      .ad {
        background: rgba(255,255,255,0.65);
        border: 1px solid rgba(140,120,200,0.22);
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 10px 22px rgba(0,0,0,0.06);
        margin: 10px 0 18px;
      }
      .ad-badge { font-size:12px; font-weight:900; color:#e11d48; }
      .ad-title { font-weight: 900; font-size: 15px; margin-top:4px; }
      .ad-link {
        display: inline-block;
        margin-top: 10px;
        padding: 7px 12px;
        border-radius: 10px;
        border: 1px solid rgba(80,80,180,0.25);
        background: rgba(255,255,255,0.7);
        font-weight: 900;
        color: #2b5bd7;
        text-decoration: none;
      }

      .bigline {
        font-size: 20px;
        font-weight: 900;
        text-align: center;
        color: #2b2b2b;
        margin: 8px 0 4px;
      }

      @media (max-width: 480px) {
        .title { font-size: 24px; }
        .bigline { font-size: 18px; }
      }
    </style>
    """,
    unsafe_allow_html=True
)

APP_URL = "https://my-fortune.streamlit.app"   # 네 배포 URL
AD_URL = "https://www.다나눔렌탈.com"


# =========================
# 입력 화면
# =========================
if not st.session_state.result:
    st.markdown(f"<div class='title'>{t['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)

    st.session_state.name = st.text_input(t["name_label"], value=st.session_state.name)

    st.session_state.birthdate = st.date_input(
        t["birth_label"],
        value=st.session_state.birthdate,
        min_value=date(1900, 1, 1),
        max_value=date(2030, 12, 31),
    )

    mbti_mode = st.radio(t["mbti_mode"], [t["mbti_direct"], t["mbti_test"]], horizontal=True)

    if mbti_mode == t["mbti_direct"]:
        st.session_state.mbti = st.selectbox("MBTI", sorted(MBTIS[lang].keys()))
        if st.button(t["btn_view"], use_container_width=True):
            st.session_state.result = True
            st.rerun()

    else:
        st.caption(t["test_caption"])

        # 12문항(각 축 3문항)
        if lang == "ko":
            q_ei = [
                ("약속이 갑자기 잡히면?", "좋아! 나가자(E)", "음… 집이 좋아(I)"),
                ("에너지 충전은?", "사람 만나면 충전(E)", "혼자 있어야 충전(I)"),
                ("대화할 때 나는?", "말하면서 정리(E)", "생각 정리 후 말(I)"),
            ]
            q_sn = [
                ("새 정보를 볼 때?", "현실/사실 위주(S)", "가능성/의미 위주(N)"),
                ("설명 들을 때?", "예시·디테일(S)", "전체 그림·핵심(N)"),
                ("아이디어는 보통?", "검증된 방식(S)", "새로운 방식(N)"),
            ]
            q_tf = [
                ("의견 충돌 시?", "논리/원칙(T)", "배려/관계(F)"),
                ("결정 기준은?", "효율/정확(T)", "마음/가치(F)"),
                ("피드백할 때?", "직설적으로(T)", "부드럽게(F)"),
            ]
            q_jp = [
                ("일정 스타일?", "계획대로(J)", "즉흥적으로(P)"),
                ("마감 앞두면?", "미리 끝냄(J)", "막판 몰아함(P)"),
                ("정리정돈은?", "깔끔하게 유지(J)", "필요할 때만(P)"),
            ]
        else:
            q_ei = [
                ("If plans come up suddenly?", "Awesome! Let's go (E)", "I'd rather stay home (I)"),
                ("You recharge by…", "Meeting people (E)", "Being alone (I)"),
                ("When talking, you…", "Think while speaking (E)", "Think first, then speak (I)"),
            ]
            q_sn = [
                ("When seeing new info?", "Facts & details (S)", "Possibilities & meaning (N)"),
                ("You prefer explanations with…", "Examples & specifics (S)", "Big picture (N)"),
                ("Your ideas are usually…", "Proven methods (S)", "New approaches (N)"),
            ]
            q_tf = [
                ("In conflict, you choose…", "Logic & principles (T)", "Care & harmony (F)"),
                ("Your decision 기준 is…", "Efficiency & accuracy (T)", "Values & feelings (F)"),
                ("When giving feedback…", "Direct & clear (T)", "Gentle & considerate (F)"),
            ]
            q_jp = [
                ("Your schedule style?", "Planned (J)", "Spontaneous (P)"),
                ("Before a deadline…", "Finish early (J)", "Rush at the end (P)"),
                ("Tidying up is…", "Keep it neat (J)", "Only when needed (P)"),
            ]

        ei = sn = tf = jp = 0

        st.subheader(t["sec_ei"])
        for i, (q, a, b) in enumerate(q_ei):
            if st.radio(q, [a, b], key=f"ei_{lang}_{i}") == a:
                ei += 1

        st.subheader(t["sec_sn"])
        for i, (q, a, b) in enumerate(q_sn):
            if st.radio(q, [a, b], key=f"sn_{lang}_{i}") == a:
                sn += 1

        st.subheader(t["sec_tf"])
        for i, (q, a, b) in enumerate(q_tf):
            if st.radio(q, [a, b], key=f"tf_{lang}_{i}") == a:
                tf += 1

        st.subheader(t["sec_jp"])
        for i, (q, a, b) in enumerate(q_jp):
            if st.radio(q, [a, b], key=f"jp_{lang}_{i}") == a:
                jp += 1

        if st.button(t["btn_view_test"], use_container_width=True):
            mbti = ""
            mbti += "E" if ei >= 2 else "I"
            mbti += "S" if sn >= 2 else "N"
            mbti += "T" if tf >= 2 else "F"
            mbti += "J" if jp >= 2 else "P"
            st.session_state.mbti = mbti
            st.session_state.result = True
            st.rerun()


# =========================
# 결과 화면
# =========================
if st.session_state.result:
    y = st.session_state.birthdate.year
    m = st.session_state.birthdate.month
    d = st.session_state.birthdate.day
    name = st.session_state.name.strip()
    mbti = st.session_state.mbti

    zodiac = get_zodiac(y, lang)
    if zodiac is None:
        st.error(t["error_year"])
        if st.button(t["reset_btn"], use_container_width=True):
            st.session_state.result = False
            st.rerun()
        st.stop()

    zodiac_desc = ZODIACS[lang][zodiac]
    mbti_desc = MBTIS[lang].get(mbti, "MBTI")
    saju = get_saju(y, m, d, lang)
    today_msg = daily_fortune(zodiac, lang, 0)
    tomorrow_msg = daily_fortune(zodiac, lang, 1)

    rng = stable_rng(name, y, m, d, mbti, lang)
    overall = rng.choice(OVERALL_FORTUNES[lang])
    combo_comment = rng.choice(COMBO_COMMENTS[lang]).format(zodiac, mbti_desc)
    lucky_color = rng.choice(LUCKY_COLORS[lang])
    lucky_item = rng.choice(LUCKY_ITEMS[lang])
    tip = rng.choice(TIPS[lang])

    name_display = (f"{name}" + ("님의" if lang == "ko" else "") ) if name else ""
    line_head = f"{name_display} {zodiac} · {mbti}" if name_display else f"{zodiac} · {mbti}"

    st.markdown(f"<div class='title'>{t['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='bigline'>🔮 {line_head}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>{t['combo']}</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="card">
          <p><span class="kv">✨ {t['zodiac_title']}</span>: {zodiac_desc}</p>
          <p><span class="kv">🧠 {t['mbti_title']}</span>: {mbti_desc}</p>
          <p><span class="kv">🍀 {t['saju_title']}</span>: {saju}</p>
          <hr style="border:none;height:1px;background:rgba(120,100,180,0.18);margin:12px 0;">
          <p><span class="kv">💗 {t['today_title']}</span>: {today_msg}</p>
          <p><span class="kv">🌙 {t['tomorrow_title']}</span>: {tomorrow_msg}</p>
          <hr style="border:none;height:1px;background:rgba(120,100,180,0.18);margin:12px 0;">
          <p><span class="kv">💝 {t['overall_title']}</span>: {overall}</p>
          <p><span class="kv">💬 {t['combo_title']}</span>: {combo_comment}</p>
          <p><span class="kv">🎨 {t['lucky_color_title']}</span>: {lucky_color} &nbsp; | &nbsp;
             <span class="kv">🧿 {t['lucky_item_title']}</span>: {lucky_item}</p>
          <p><span class="kv">✅ {t['tip_title']}</span>: {tip}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 광고 카드
    st.markdown(
        f"""
        <div class="ad">
          <div class="ad-badge">{t['ad_badge']}</div>
          <div class="ad-title">{t['ad_title']}</div>
          <div style="margin-top:6px; color:#2b2b2b; font-size:14px; line-height:1.6;">
            {t['ad_line1']}<br/>
            {t['ad_line2']}
          </div>
          <a class="ad-link" href="{AD_URL}" target="_blank">{t['ad_link']}</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 타로(Expander)
    with st.expander(t["tarot_btn"], expanded=False):
        tarot_rng = random.Random(abs(hash(f"tarot|{datetime.now().strftime('%Y%m%d')}|{name}|{mbti}|{lang}")) % (10**9))
        tarot_card = tarot_rng.choice(list(TAROT_CARDS.keys()))
        tarot_meaning = TAROT_CARDS[tarot_card][lang]
        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
              <p style="font-weight:900; color:#7c3aed;">{t['tarot_title']}</p>
              <p style="font-size:22px; font-weight:900; margin-top:6px;">{tarot_card}</p>
              <p style="margin-top:8px;">{tarot_meaning}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =========================
    # 공유(텍스트만): Web Share API → 실패 시 자동 복사
    # =========================
    share_text = (
        f"{line_head}\n"
        f"{t['combo']}\n\n"
        f"{t['today_title']}: {today_msg}\n"
        f"{t['tomorrow_title']}: {tomorrow_msg}\n\n"
        f"{t['overall_title']}: {overall}\n"
        f"{t['combo_title']}: {combo_comment}\n"
        f"{t['lucky_color_title']}: {lucky_color} | {t['lucky_item_title']}: {lucky_item}\n"
        f"{t['tip_title']}: {tip}\n\n"
        f"{APP_URL}"
    )

    share_payload = json.dumps(share_text)
    share_title_payload = json.dumps(t["share_title"])
    fail_copy_payload = json.dumps(t["share_fail_copy"])
    manual_prompt_payload = json.dumps(t["share_manual_prompt"])
    cancel_payload = json.dumps(t["share_cancel"])

    components.html(
        f"""
        <div style="text-align:center; margin:22px 0 10px;">
          <button onclick="doShare()"
            style="background:#7c3aed; color:#ffffff; padding:16px 64px; border:none; border-radius:999px;
                   font-size:1.1em; font-weight:900; box-shadow: 0 8px 25px rgba(124,58,237,0.35);
                   cursor:pointer;">
            {t["share_btn"]}
          </button>
        </div>

        <script>
        async function doShare() {{
          const text = {share_payload};
          const title = {share_title_payload};

          try {{
            if (navigator.share) {{
              await navigator.share({{
                title: title,
                text: text
              }});
              return;
            }}

            if (navigator.clipboard && navigator.clipboard.writeText) {{
              await navigator.clipboard.writeText(text);
              alert({fail_copy_payload});
              return;
            }}

            prompt({manual_prompt_payload}, text);

          }} catch (e) {{
            alert({cancel_payload});
            try {{
              if (navigator.clipboard && navigator.clipboard.writeText) {{
                await navigator.clipboard.writeText(text);
              }}
            }} catch (_) {{}}
          }}
        }}
        </script>
        """,
        height=110
    )

    st.markdown(f"<div style='text-align:center; color:#6b6b6b; font-size:12px; margin-top:6px;'>{APP_URL}</div>", unsafe_allow_html=True)

    if st.button(t["reset_btn"], use_container_width=True):
        st.session_state.result = False
        st.rerun()
