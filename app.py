import streamlit as st
from datetime import datetime, timedelta
import random
import time

# =========================
# Google Sheet (optional)
# =========================
SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_TAB = "시트1"  # ✅ 사용자 제공 탭 이름

def get_gsheet_client():
    """Streamlit Secrets에 [gcp_service_account]가 있으면 gspread 클라이언트 생성"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception:
        return None, "requirements.txt에 gspread/google-auth가 없어요."

    try:
        if "gcp_service_account" not in st.secrets:
            return None, "Secrets에 [gcp_service_account]가 없어요."

        info = dict(st.secrets["gcp_service_account"])
        # Streamlit TOML에서 private_key 줄바꿈이 깨지는 케이스 방어
        # (정상은 이미 \n 포함 문자열이어야 함)
        if "private_key" in info and "\\n" in info["private_key"]:
            # "\\n" 문자열을 실제 "\n"로 변환 (안전 장치)
            info["private_key"] = info["private_key"].replace("\\n", "\n")

        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        gc = gspread.authorize(creds)
        return gc, None
    except Exception as e:
        return None, f"서비스계정/Secrets 형식 문제일 수 있어요: {e}"

def gsheet_healthcheck():
    """연결 점검 + 탭 존재 확인"""
    gc, err = get_gsheet_client()
    if gc is None:
        return False, err

    try:
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(SHEET_TAB)  # ✅ '시트1'로 고정
        # 간단 읽기
        _ = ws.get_all_values()
        return True, None
    except Exception as e:
        return False, f"시트 열기/탭 찾기 오류: {e}"

# =========================
# i18n (간단 버전: 기본 한국어/영어 유지)
# =========================
translations = {
    "ko": {
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "caption": "완전 무료",
        "lang_label": "언어 / Language",
        "name_placeholder": "이름 입력 (결과에 표시돼요)",
        "birth": "### 생년월일 입력",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test12": "간단 테스트 (12문항)",
        "test16": "상세 테스트 (16문항)",
        "fortune_btn": "2026년 운세 보기!",
        "result_btn": "결과 보기!",
        "reset": "처음부터 다시하기",
        "share_btn": "친구에게 결과 공유하기",
        "tarot_btn": "오늘의 타로 카드 뽑기",
        "tarot_title": "오늘의 타로 카드",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "overall_title": "2026 전체 운세",
        "combo_title": "조합 조언",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "tip_title": "팁",
        "warning_sheet": "구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유/탭 이름 확인 필요)",
        "share_hint_mobile": "모바일에서는 공유창이 뜨고, PC에서는 자동으로 복사돼요.",
        "copy_done": "공유용 텍스트를 복사했어요! 카톡/메시지에 붙여넣기 해주세요.",
        "need_year": "생년은 1900~2030년 사이로 입력해주세요!",
        "ad_title": "정수기 렌탈 대박!",
        "ad_desc1": "제휴카드면 월 0원부터!",
        "ad_desc2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍",
        "ad_link": "다나눔렌탈.com 바로가기",
        "ad_url": "https://www.다나눔렌탈.com",
        "test16_desc": "각 축 4문항씩. 제출하면 결과로 넘어갑니다.",
        "test12_desc": "제출하면 바로 결과로 넘어갑니다.",
    },
    "en": {
        "title": "2026 Zodiac + MBTI + Fortune + Today/Tomorrow Luck",
        "caption": "Completely Free",
        "lang_label": "Language / 언어",
        "name_placeholder": "Enter name (shown in result)",
        "birth": "### Enter Birth Date",
        "mbti_mode": "How to do MBTI?",
        "direct": "Direct input",
        "test12": "Quick test (12)",
        "test16": "Detailed test (16)",
        "fortune_btn": "View 2026 Fortune!",
        "result_btn": "View Result!",
        "reset": "Start Over",
        "share_btn": "Share with Friends",
        "tarot_btn": "Draw Today's Tarot Card",
        "tarot_title": "Today's Tarot Card",
        "zodiac_title": "Zodiac Fortune",
        "mbti_title": "MBTI Traits",
        "saju_title": "Fortune Comment",
        "today_title": "Today's Luck",
        "tomorrow_title": "Tomorrow's Luck",
        "overall_title": "2026 Annual Luck",
        "combo_title": "Combo Advice",
        "lucky_color_title": "Lucky Color",
        "lucky_item_title": "Lucky Item",
        "tip_title": "Tip",
        "warning_sheet": "Google Sheet is not connected yet. (Check Secrets/requirements/share/tab name)",
        "share_hint_mobile": "On mobile, share sheet opens. On PC, it auto-copies.",
        "copy_done": "Copied! Paste it to KakaoTalk / Messages.",
        "need_year": "Please enter a birth year between 1900 and 2030!",
        "ad_title": "Water Purifier Rental Deal!",
        "ad_desc1": "From 0 won/month with partner card!",
        "ad_desc2": "Up to 500,000 won support + many gifts",
        "ad_link": "Go to DananumRental.com",
        "ad_url": "https://www.다나눔렌탈.com",
        "test16_desc": "4 questions per axis. Submit to see result.",
        "test12_desc": "Submit to see result instantly.",
    }
}

# =========================
# Content DB (간단 확장)
# =========================
ZODIAC_KO = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
ZODIAC_EN = ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"]

ZODIAC_TEXT = {
    "ko": {
        "쥐띠": "안정 속 새로운 기회! 민첩한 판단으로 성공 잡아요",
        "소띠": "꾸준함의 결실! 안정된 성장과 행복한 가족운",
        "호랑이띠": "대박 띠! 도전과 성공, 리더십 발휘로 큰 성과",
        "토끼띠": "변화에 신중! 급한 결정보다 흐름을 읽는 게 이득",
        "용띠": "운기 상승! 리더십과 승진 기회 많음",
        "뱀띠": "직감과 실속! 예상치 못한 재물운",
        "말띠": "추진력 강하지만 균형이 핵심",
        "양띠": "편안함과 돈운이 좋은 해, 가정운도 상승",
        "원숭이띠": "변화와 재능 발휘! 창의력으로 기회 잡기",
        "닭띠": "노력 결실! 인정과 승진 가능성 높음",
        "개띠": "귀인 도움과 네트워킹으로 상승",
        "돼지띠": "여유와 재물운! 즐기면서도 관리가 관건"
    },
    "en": {
        "Rat": "New opportunities in stability! Success with quick judgment",
        "Ox": "Fruits of perseverance! Stable growth and happy family",
        "Tiger": "Big luck! Challenge and success with leadership",
        "Rabbit": "Be cautious with changes; read the flow before acting",
        "Dragon": "Rising fortune! Leadership and promotion opportunities",
        "Snake": "Intuition pays off; unexpected gains",
        "Horse": "Strong drive, but balance is key",
        "Goat": "Comfort and money luck rise; home life improves",
        "Monkey": "Change and talent shine; grab creative chances",
        "Rooster": "Effort rewarded; recognition and promotion",
        "Dog": "Helpful people and networking lift you up",
        "Pig": "Relaxation and wealth; enjoy but manage well"
    }
}

MBTI_TRAITS = {
    "ko": {
        "ISTJ":"규칙 지킴이 · 성실/책임",
        "ISFJ":"세상 따뜻함 · 배려/헌신",
        "INFJ":"마음 마스터 · 통찰/이상",
        "INTJ":"냉철 전략가 · 계획/전략",
        "ISTP":"고치는 장인 · 실용/즉흥",
        "ISFP":"감성 힐러 · 유연/감각",
        "INFP":"감성 예술가 · 가치/상상",
        "INTP":"아이디어 천재 · 분석/호기심",
        "ESTP":"모험왕 · 실행/도전",
        "ESFP":"파티 주인공 · 에너지/관계",
        "ENFP":"인간 비타민 · 영감/확장",
        "ENTP":"토론왕 · 아이디어/변주",
        "ESTJ":"리더 · 현실/성과",
        "ESFJ":"분위기 메이커 · 조화/관리",
        "ENFJ":"모두 선생님 · 리드/공감",
        "ENTJ":"보스 · 결단/리더십",
    },
    "en": {
        "ISTJ":"Logistician · Duty/Order",
        "ISFJ":"Defender · Caring/Loyal",
        "INFJ":"Advocate · Insight/Vision",
        "INTJ":"Strategist · Planning",
        "ISTP":"Virtuoso · Practical",
        "ISFP":"Adventurer · Flexible",
        "INFP":"Mediator · Values",
        "INTP":"Thinker · Analysis",
        "ESTP":"Entrepreneur · Action",
        "ESFP":"Entertainer · Social",
        "ENFP":"Campaigner · Inspiration",
        "ENTP":"Debater · Ideas",
        "ESTJ":"Executive · Results",
        "ESFJ":"Consul · Harmony",
        "ENFJ":"Protagonist · Empathy",
        "ENTJ":"Commander · Leadership",
    }
}

SAJU_MSGS = {
    "ko": [
        "목(木) 기운 → 성장과 발전의 해!",
        "화(火) 기운 → 열정이 성과로 연결!",
        "토(土) 기운 → 안정과 재물운 강화",
        "금(金) 기운 → 결단력과 선택이 빛남",
        "수(水) 기운 → 지혜롭게 흐름을 타기",
        "오행 균형 → 무리하지 않으면 전반적으로 대길!",
        "양기 강함 → 도전이 기회가 됨",
        "음기 강함 → 내면 정리 후 도약"
    ],
    "en": [
        "Wood energy → A year of growth and progress!",
        "Fire energy → Passion turns into results!",
        "Earth energy → Stability and wealth strengthen",
        "Metal energy → Decisions and choices shine",
        "Water energy → Ride the flow wisely",
        "Balanced elements → Great year if you don't overdo it!",
        "Strong Yang → Challenges become opportunities",
        "Strong Yin → Reflect, then leap forward"
    ]
}

DAILY_MSGS = {
    "ko": [
        "정리하면 운이 열립니다.",
        "사람 운이 강해요. 오늘은 대화가 열쇠!",
        "작은 투자/절약이 이득으로 연결될 수 있어요.",
        "컨디션 관리가 핵심. 무리한 일정은 피하세요.",
        "귀인 운! 도움을 요청하면 길이 열려요.",
        "집중력 최고. 미뤄둔 일을 끝내기 좋아요.",
        "갑작스런 약속도 행운. 가벼운 외출 추천!",
        "웃음이 복이 됩니다. 가벼운 유머가 분위기 살려요."
    ],
    "en": [
        "Organize things and luck opens up.",
        "People-luck is strong. Conversations are the key!",
        "Small saving/investment may bring gains.",
        "Energy management matters. Avoid over-scheduling.",
        "Helpful people appear. Ask for support.",
        "High focus—finish what you postponed.",
        "Spontaneous plans can be lucky. Go out lightly!",
        "Smiles bring luck. A little humor helps."
    ]
}

OVERALL_MSGS = {
    "ko": [
        "꾸준함이 대박을 부릅니다!",
        "변화를 잘 타면 기회가 커져요.",
        "관계운이 크게 열립니다.",
        "돈의 흐름이 좋아요. 관리하면 더 커져요.",
        "마음의 여유가 성과를 끌어옵니다."
    ],
    "en": [
        "Consistency brings big wins!",
        "Ride changes well and opportunities grow.",
        "Relationship luck opens wide.",
        "Money flow improves—manage it to grow more.",
        "Calm mind attracts results."
    ]
}

LUCKY_COLORS = {"ko":["골드","레드","블루","그린","퍼플"], "en":["Gold","Red","Blue","Green","Purple"]}
LUCKY_ITEMS = {"ko":["황금 액세서리","빨간 지갑","파란 목걸이","초록 식물","보라색 펜"], "en":["Golden accessory","Red wallet","Blue necklace","Green plant","Purple pen"]}

TAROT_CARDS = {
    "ko": {
        "The Fool":"바보 - 새로운 시작, 모험",
        "The Magician":"마법사 - 창조력, 집중",
        "The High Priestess":"여사제 - 직감, 내면",
        "The Empress":"여제 - 풍요, 창작",
        "The Emperor":"황제 - 안정, 구조",
        "The Lovers":"연인 - 사랑, 선택",
        "The Chariot":"전차 - 승리, 의지",
        "The Star":"별 - 희망, 치유",
        "The Sun":"태양 - 행복, 성공, 긍정",
        "The World":"세계 - 완성, 성취"
    },
    "en": {
        "The Fool":"New beginnings, adventure",
        "The Magician":"Manifestation, skill",
        "The High Priestess":"Intuition, inner voice",
        "The Empress":"Abundance, creativity",
        "The Emperor":"Stability, structure",
        "The Lovers":"Love, choices",
        "The Chariot":"Victory, willpower",
        "The Star":"Hope, healing",
        "The Sun":"Joy, success, positivity",
        "The World":"Completion, fulfillment"
    }
}

# =========================
# Helpers
# =========================
st.set_page_config(page_title="2026 Fortune", layout="centered")

def get_zodiac(year, lang):
    if lang == "en":
        return ZODIAC_EN[(year - 4) % 12] if 1900 <= year <= 2030 else None
    return ZODIAC_KO[(year - 4) % 12] if 1900 <= year <= 2030 else None

def get_saju(year, month, day, lang):
    total = year + month + day
    return SAJU_MSGS[lang][total % len(SAJU_MSGS[lang])]

def get_daily(zodiac, lang, offset=0):
    today = datetime.now() + timedelta(days=offset)
    # zodiac index 기반 seed
    z_list = list(ZODIAC_TEXT[lang].keys())
    idx = z_list.index(zodiac) if zodiac in z_list else 0
    seed = int(today.strftime("%Y%m%d")) + idx
    random.seed(seed)
    return random.choice(DAILY_MSGS[lang])

def combo_advice(mbti, zodiac, lang):
    # MBTI가 운세(행동/선택)에 미치는 영향 형태로 조언
    if lang == "ko":
        return (
            f"{mbti} 성향은 올해 '{zodiac}'의 흐름에서 **선택의 속도**가 강점이 될 수 있어요. "
            f"다만 급해지면 실수가 늘 수 있으니, 중요한 결정은 **24시간만 숙성**시키면 운이 더 좋아집니다."
        )
    return (
        f"As {mbti}, your strength is decision speed—this pairs well with the '{zodiac}' flow. "
        f"But if you rush, mistakes increase. Let big decisions sit for 24 hours to improve outcomes."
    )

APP_URL = "https://my-fortune.streamlit.app"

# =========================
# Session init
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "result_shown" not in st.session_state:
    st.session_state.result_shown = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "year" not in st.session_state:
    st.session_state.year = 2005
if "month" not in st.session_state:
    st.session_state.month = 1
if "day" not in st.session_state:
    st.session_state.day = 1
if "mbti" not in st.session_state:
    st.session_state.mbti = None

# =========================
# Global CSS (가독성 강화)
# =========================
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; }
@media (max-width: 768px){
  .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}
.card {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
}
.gradient {
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 55%, #8ec5fc 100%);
  border-radius: 18px;
  padding: 16px;
  color: white;
  text-align: center;
  box-shadow: 0 10px 24px rgba(0,0,0,0.12);
}
.subtle {
  color: rgba(255,255,255,0.92);
  font-size: 0.95rem;
}
.adbox{
  background:#fff;
  border-radius: 16px;
  padding: 16px;
  border: 2px solid rgba(230,126,34,0.35);
  box-shadow: 0 10px 22px rgba(0,0,0,0.08);
}
.adbadge{
  display:inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(231,76,60,0.12);
  color: #e74c3c;
  border: 1px solid rgba(231,76,60,0.20);
  margin-bottom: 8px;
}
.bigbtn button{
  width: 100% !important;
  border-radius: 999px !important;
  padding: 14px 16px !important;
  font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Language
# =========================
st.session_state.lang = st.radio(
    translations[st.session_state.lang]["lang_label"],
    ["ko", "en"],
    index=0 if st.session_state.lang == "ko" else 1,
    horizontal=True
)
t = translations[st.session_state.lang]
lang = st.session_state.lang

# =========================
# Google Sheet status (silent check, show small warning only)
# =========================
sheet_ok, sheet_err = gsheet_healthcheck()
if not sheet_ok:
    st.warning(t["warning_sheet"])

# =========================
# Input screen
# =========================
if not st.session_state.result_shown:
    st.markdown(f"""
    <div class="gradient">
      <div style="font-size:1.6rem; font-weight:900;">{t['title']}</div>
      <div class="subtle">{t['caption']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.session_state.name = st.text_input(t["name_placeholder"], value=st.session_state.name)

    st.markdown(t["birth"])
    c1, c2, c3 = st.columns(3)
    st.session_state.year = c1.number_input("Year" if lang == "en" else "년", 1900, 2030, st.session_state.year, 1)
    st.session_state.month = c2.number_input("Month" if lang == "en" else "월", 1, 12, st.session_state.month, 1)
    st.session_state.day = c3.number_input("Day" if lang == "en" else "일", 1, 31, st.session_state.day, 1)

    mode = st.radio(t["mbti_mode"], [t["direct"], t["test12"], t["test16"]], horizontal=False)

    if mode == t["direct"]:
        mbti_input = st.selectbox("MBTI", sorted(MBTI_TRAITS[lang].keys()))
        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button(t["fortune_btn"]):
            st.session_state.mbti = mbti_input
            st.session_state.result_shown = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif mode == t["test12"]:
        st.markdown(f"<div class='card'><b>MBTI – 12</b><br>{t['test12_desc']}</div>", unsafe_allow_html=True)
        # 12문항(간단): 각 축 3문항
        questions = [
            ("E", "I",
             {"ko":"사람 많은 자리에서 에너지가 충전된다", "en":"Crowds recharge my energy"},
             {"ko":"혼자 있을 때 에너지가 충전된다", "en":"Alone time recharges me"}),
            ("E", "I",
             {"ko":"생각이 나면 바로 말로 정리하는 편", "en":"I think by speaking out loud"},
             {"ko":"머릿속에서 먼저 정리하고 말한다", "en":"I organize in my head first"}),
            ("E", "I",
             {"ko":"새로운 사람을 만나면 금방 친해진다", "en":"I quickly befriend new people"},
             {"ko":"시간이 좀 걸린다", "en":"It takes time"}),

            ("S", "N",
             {"ko":"사실/디테일을 먼저 본다", "en":"I notice facts/details first"},
             {"ko":"전체/의미/가능성을 먼저 본다", "en":"I see meaning/possibilities first"}),
            ("S", "N",
             {"ko":"실용적인 게 최고다", "en":"Practical matters most"},
             {"ko":"새로운 아이디어가 중요하다", "en":"New ideas matter most"}),
            ("S", "N",
             {"ko":"현재에 집중한다", "en":"I focus on the present"},
             {"ko":"미래를 상상한다", "en":"I imagine the future"}),

            ("T", "F",
             {"ko":"결정은 논리가 우선", "en":"Logic comes first in decisions"},
             {"ko":"결정은 사람 마음이 우선", "en":"People's feelings come first"}),
            ("T", "F",
             {"ko":"문제 해결 조언이 먼저 나온다", "en":"I give solutions first"},
             {"ko":"공감하며 들어주는 게 먼저", "en":"I empathize first"}),
            ("T", "F",
             {"ko":"정확한 말이 중요하다", "en":"Accuracy matters"},
             {"ko":"부드러운 말이 중요하다", "en":"Gentleness matters"}),

            ("J", "P",
             {"ko":"계획대로 해야 마음이 편하다", "en":"Plans make me comfortable"},
             {"ko":"즉흥이어도 괜찮다", "en":"Spontaneous is fine"}),
            ("J", "P",
             {"ko":"마감 전 미리 끝낸다", "en":"I finish early"},
             {"ko":"마감 직전에 집중한다", "en":"I focus near the deadline"}),
            ("J", "P",
             {"ko":"정리정돈이 중요하다", "en":"Organization is important"},
             {"ko":"어느 정도 어수선해도 된다", "en":"Some mess is okay"}),
        ]

        scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
        for idx, (a, b, qa, qb) in enumerate(questions):
            ans = st.radio(
                f"{idx+1}. {qa[lang]} / {qb[lang]}",
                [qa[lang], qb[lang]],
                key=f"q12_{idx}"
            )
            if ans == qa[lang]:
                scores[a] += 1
            else:
                scores[b] += 1

        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button(t["result_btn"]):
            mbti = ("E" if scores["E"] >= scores["I"] else "I") + \
                   ("S" if scores["S"] >= scores["N"] else "N") + \
                   ("T" if scores["T"] >= scores["F"] else "F") + \
                   ("J" if scores["J"] >= scores["P"] else "P")
            st.session_state.mbti = mbti
            st.session_state.result_shown = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:  # test16
        st.markdown(f"<div class='card'><b>MBTI – 16</b><br>{t['test16_desc']}</div>", unsafe_allow_html=True)

        # 16문항 (각 축 4문항)
        axes = [
            ("E", "I", [
                {"ko":"주말에 갑자기 '놀자!' 하면 바로 나간다", "en":"If friends suddenly ask to hang out, I go"},
                {"ko":"모임에서 처음 본 사람과 대화가 편하다", "en":"Talking to strangers at a gathering is easy"},
                {"ko":"사람을 많이 만나면 오히려 에너지가 생긴다", "en":"Meeting many people energizes me"},
                {"ko":"생각이 떠오르면 말로 풀어낸다", "en":"I process thoughts by speaking"},
            ], [
                {"ko":"집에서 쉬고 싶다", "en":"I prefer staying home"},
                {"ko":"처음 본 사람과 대화가 부담스럽다", "en":"Talking to strangers is tiring"},
                {"ko":"사람을 많이 만나면 지친다", "en":"Meeting many people drains me"},
                {"ko":"머릿속에서 정리한 뒤 말한다", "en":"I speak after organizing my thoughts"},
            ]),
            ("S", "N", [
                {"ko":"메뉴판 가격/구성을 먼저 본다", "en":"I notice prices/items first"},
                {"ko":"사실과 디테일이 중요하다", "en":"Facts and details matter"},
                {"ko":"검증된 방법이 좋다", "en":"Proven methods are better"},
                {"ko":"지금 할 수 있는 걸 바로 한다", "en":"I act on what I can do now"},
            ], [
                {"ko":"분위기/컨셉을 먼저 본다", "en":"I notice vibe/concept first"},
                {"ko":"가능성과 의미가 중요하다", "en":"Possibilities and meaning matter"},
                {"ko":"새로운 시도가 좋다", "en":"New attempts are better"},
                {"ko":"미래 그림을 상상한다", "en":"I imagine the future picture"},
            ]),
            ("T", "F", [
                {"ko":"논리적으로 누가 맞는지 따진다", "en":"I analyze who is right logically"},
                {"ko":"문제 해결 방법을 제시한다", "en":"I propose solutions"},
                {"ko":"팩트가 우선이다", "en":"Facts first"},
                {"ko":"결정은 효율을 본다", "en":"I value efficiency in decisions"},
            ], [
                {"ko":"서로 기분 상하지 않게 조율한다", "en":"I mediate to avoid hurt feelings"},
                {"ko":"공감하며 들어준다", "en":"I empathize first"},
                {"ko":"배려가 우선이다", "en":"Consideration first"},
                {"ko":"결정은 관계를 본다", "en":"I value relationships in decisions"},
            ]),
            ("J", "P", [
                {"ko":"일정은 미리 계획한다", "en":"I plan ahead"},
                {"ko":"미리미리 끝낸다", "en":"I finish early"},
                {"ko":"정리정돈이 편하다", "en":"I like things organized"},
                {"ko":"결정은 빠르게 내린다", "en":"I decide quickly"},
            ], [
                {"ko":"즉흥이 편하다", "en":"I prefer spontaneity"},
                {"ko":"마감 직전에 몰아서 한다", "en":"I rush near deadlines"},
                {"ko":"약간 어수선해도 괜찮다", "en":"Some chaos is fine"},
                {"ko":"더 알아보고 결정한다", "en":"I explore more before deciding"},
            ])
        ]

        scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
        for ax_i, (A, B, Aqs, Bqs) in enumerate(axes):
            st.subheader(f"{A}/{B}")
            for i in range(4):
                a_text = Aqs[i][lang]
                b_text = Bqs[i][lang]
                ans = st.radio(
                    f"{i+1}/4",
                    [a_text, b_text],
                    key=f"q16_{ax_i}_{i}"
                )
                if ans == a_text:
                    scores[A] += 1
                else:
                    scores[B] += 1

        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button(t["result_btn"]):
            mbti = ("E" if scores["E"] >= scores["I"] else "I") + \
                   ("S" if scores["S"] >= scores["N"] else "N") + \
                   ("T" if scores["T"] >= scores["F"] else "F") + \
                   ("J" if scores["J"] >= scores["P"] else "P")
            st.session_state.mbti = mbti
            st.session_state.result_shown = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Result screen
# =========================
if st.session_state.result_shown:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(st.session_state.year, lang)

    if zodiac is None:
        st.error(t["need_year"])
        if st.button(t["reset"]):
            st.session_state.clear()
            st.rerun()
        st.stop()

    name = st.session_state.name.strip()
    name_display = f"{name}님" if (lang == "ko" and name) else (name if name else "")

    saju = get_saju(st.session_state.year, st.session_state.month, st.session_state.day, lang)
    today = get_daily(zodiac, lang, 0)
    tomorrow = get_daily(zodiac, lang, 1)
    overall = random.choice(OVERALL_MSGS[lang])
    lucky_color = random.choice(LUCKY_COLORS[lang])
    lucky_item = random.choice(LUCKY_ITEMS[lang])
    advice = combo_advice(mbti, zodiac, lang)

    # header
    st.markdown(f"""
    <div class="gradient">
      <div style="font-size:1.2rem; font-weight:900;">{name_display} {mbti}</div>
      <div style="font-size:1.0rem; margin-top:6px; font-weight:800;">{zodiac} · {t['overall_title']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # main card
    zodiac_desc = ZODIAC_TEXT[lang][zodiac]
    mbti_desc = MBTI_TRAITS[lang].get(mbti, mbti)

    st.markdown(f"""
    <div class="card">
      <div style="font-size:1.05rem; line-height:1.85;">
        <b>{t['zodiac_title']}</b>: {zodiac_desc}<br>
        <b>{t['mbti_title']}</b>: {mbti_desc}<br>
        <b>{t['saju_title']}</b>: {saju}<br><br>
        <b>{t['today_title']}</b>: {today}<br>
        <b>{t['tomorrow_title']}</b>: {tomorrow}<br><br>
        <b>{t['overall_title']}</b>: {overall}<br><br>
        <b>{t['combo_title']}</b>: {advice}<br><br>
        <b>{t['lucky_color_title']}</b>: {lucky_color} &nbsp;|&nbsp;
        <b>{t['lucky_item_title']}</b>: {lucky_item}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # ✅ 광고(한국어만) + 미니게임 위로 복구
    if lang == "ko":
        st.markdown(f"""
        <div class="adbox">
          <div class="adbadge">광고</div>
          <div style="font-weight:900; font-size:1.05rem;">{t['ad_title']}</div>
          <div style="margin-top:6px; line-height:1.65;">
            {t['ad_desc1']}<br>
            {t['ad_desc2']}
          </div>
          <div style="margin-top:10px;">
            <a href="{t['ad_url']}" target="_blank" style="font-weight:900; color:#e67e22; text-decoration:none;">
              {t['ad_link']}
            </a>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

    # tarot (button)
    if st.button(t["tarot_btn"], use_container_width=True):
        tarot_card = random.choice(list(TAROT_CARDS[lang].keys()))
        tarot_meaning = TAROT_CARDS[lang][tarot_card]
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900; color:#8e44ad;">{t['tarot_title']}</div>
          <div style="font-size:1.6rem; font-weight:900; margin-top:6px;">{tarot_card}</div>
          <div style="margin-top:6px; line-height:1.7;">{tarot_meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # share (Web Share API on mobile; fallback copy on PC)
    share_text = (
        f"{name_display} {('2026년 운세' if lang=='ko' else '2026 Fortune')}\n"
        f"{zodiac} + {mbti}\n\n"
        f"{t['today_title']}: {today}\n"
        f"{t['tomorrow_title']}: {tomorrow}\n\n"
        f"{t['overall_title']}: {overall}\n"
        f"{t['combo_title']}: {advice}\n"
        f"{t['lucky_color_title']}: {lucky_color} | {t['lucky_item_title']}: {lucky_item}\n\n"
        f"{APP_URL}"
    )

    st.markdown(f"""
    <div class="bigbtn">
      <button id="shareBtn" style="background:#6c3bd1; color:white; border:none; cursor:pointer;">
        {t["share_btn"]}
      </button>
    </div>
    <div style="text-align:center; margin-top:10px; font-size:0.9rem; color:#666;">
      {t["share_hint_mobile"]}
    </div>
    <textarea id="shareText" style="position:absolute; left:-9999px;">{share_text}</textarea>
    <script>
      const btn = window.parent.document.getElementById("shareBtn");
      const txt = window.parent.document.getElementById("shareText");
      if (btn) {{
        btn.onclick = async () => {{
          const text = txt.value;
          try {{
            if (navigator.share) {{
              await navigator.share({{ text: text, url: "{APP_URL}" }});
            }} else {{
              await navigator.clipboard.writeText(text);
              alert("{t['copy_done']}");
            }}
          }} catch (e) {{
            try {{
              await navigator.clipboard.writeText(text);
              alert("{t['copy_done']}");
            }} catch (e2) {{
              alert("Share failed. Please copy manually.");
            }}
          }}
        }};
      }}
    </script>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown(f"<div style='text-align:center; color:#888; font-size:0.9rem;'>{APP_URL}</div>", unsafe_allow_html=True)
    st.write("")

    # ✅ 하단의 "입력화면 버튼"은 삭제 요청 반영 (reset만 남김)
    if st.button(t["reset"], use_container_width=True):
        st.session_state.clear()
        st.rerun()
