import streamlit as st
from datetime import datetime, timedelta
import random

# 다국어 사전
translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 + 오늘/내일 운세 🌟",
        "caption": "완전 무료 😄",
        "qr": "### 📱 QR 코드 스캔!",
        "share": "### 🔗 공유 링크",
        "share_desc": "위 링크 복사해서 친구들한테 보내주세요!",
        "ad_title": "💳 렌탈 궁금할 때?",
        "ad_text": "<b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 페이백</b>!",
        "ad_btn": "🔗 보러가기",
        "birth": "### 생년월일 입력",
        "name_placeholder": "이름 입력 (결과에 표시돼요)",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test": "상세 테스트 (16문제)",
        "test_start": "상세 테스트 시작! 하나씩 답해주세요 😊",
        "energy": "에너지 방향",
        "info": "정보 수집",
        "decision": "결정 방식",
        "life": "생활 방식",
        "result_btn": "결과 보기!",
        "fortune_btn": "🔮 2026년 운세 보기!",
        "reset": "처음부터 다시 하기",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "combo": "최고 조합!",
        "your_fortune": "님의 2026년 운세",
        "footer": "재미로만 봐주세요 😊",
        "zodiacs": {
            "쥐띠": "🐭 활발·성장, 돈↑",
            "소띠": "🐮 노력 결실",
            "호랑이띠": "🐯 도전 성공, 돈 대박",
            "토끼띠": "🐰 안정·사랑 운",
            "용띠": "🐲 운↑ 리더십",
            "뱀띠": "🐍 실속·직감",
            "말띠": "🐴 새 도전·돈 기회",
            "양띠": "🐑 편안+결혼 운",
            "원숭이띠": "🐵 변화·재능",
            "닭띠": "🐔 노력 결과",
            "개띠": "🐶 친구·돈↑",
            "돼지띠": "🐷 여유·돈 최고"
        },
        "mbtis": {
            "INTJ": "🧠 냉철 전략가",
            "INTP": "💡 아이디어 천재",
            "ENTJ": "👑 보스",
            "ENTP": "⚡ 토론왕",
            "INFJ": "🔮 마음 마스터",
            "INFP": "🎨 감성 예술가",
            "ENFJ": "🤗 모두 선생님",
            "ENFP": "🎉 인간 비타민",
            "ISTJ": "📋 규칙 지킴이",
            "ISFJ": "🛡️ 세상 따뜻함",
            "ESTJ": "📢 리더",
            "ESFJ": "💕 분위기 메이커",
            "ISTP": "🔧 고치는 장인",
            "ISFP": "🌸 감성 힐러",
            "ESTP": "🏄 모험왕",
            "ESFP": "🎭 파티 주인공"
        },
        "saju_msgs": [
            "목(木) 기운 강함 → 성장과 발전의 해! 🌱",
            "화(火) 기운 강함 → 열정 폭발! ❤️",
            "토(土) 기운 강함 → 안정과 재물운 💰",
            "금(金) 기운 강함 → 결단력 좋음! 👔",
            "수(水) 기운 강함 → 지혜와 흐름 🌊",
            "오행 균형 → 행복한 한 해 ✨",
            "양기 강함 → 도전 성공 🚀",
            "음기 강함 → 내면 성찰 😌"
        ],
        "daily_msgs": [
            "재물운 좋음! 작은 투자도 이득 봐요 💰",
            "연애운 최고! 고백하거나 데이트 좋음 ❤️",
            "건강 주의! 과로 피하고 쉬세요 😴",
            "전체운 대박! 좋은 일만 생길 거예요 🌟",
            "인간관계 운 좋음! 귀인 만남 가능 🤝",
            "학업/일 운 최고! 집중력 최고 📚",
            "여행운 좋음! 갑자기 떠나도 괜찮아요 ✈️",
            "기분 좋은 하루! 웃음이 가득할 거예요 😄"
        ]
    },
    "en": {
        "title": "🌟 2026 Zodiac + MBTI + Saju + Today/Tomorrow Fortune 🌟",
        "caption": "Completely Free 😄",
        "qr": "### 📱 Scan QR Code!",
        "share": "### 🔗 Share Link",
        "share_desc": "Copy the link and share with friends!",
        "ad_title": "💳 Curious about rental?",
        "ad_text": "<b>Dananum Rental</b> partner card: <b>0 won/month</b> + <b>Cashback</b>!",
        "ad_btn": "🔗 Check it out",
        "birth": "### Enter Birth Date",
        "name_placeholder": "Enter your name (shown in result)",
        "mbti_mode": "How to get MBTI?",
        "direct": "Enter directly",
        "test": "Detailed Test (16 questions)",
        "test_start": "Start detailed test! Answer one by one 😊",
        "energy": "Energy Direction",
        "info": "Information Gathering",
        "decision": "Decision Making",
        "life": "Lifestyle",
        "result_btn": "View Results!",
        "fortune_btn": "🔮 View 2026 Fortune!",
        "reset": "Start Over",
        "zodiac_title": "Zodiac Fortune",
        "mbti_title": "MBTI Traits",
        "saju_title": "Saju Message",
        "today_title": "Today's Fortune",
        "tomorrow_title": "Tomorrow's Fortune",
        "combo": "Best combo!",
        "your_fortune": "'s 2026 Fortune",
        "footer": "For fun only 😊",
        "zodiacs": {
            "Rat": "🐭 Active growth, money ↑",
            "Ox": "🐮 Effort pays off",
            "Tiger": "🐯 Challenge success, big money",
            "Rabbit": "🐰 Stability, love luck",
            "Dragon": "🐲 Luck ↑ leadership",
            "Snake": "🐍 Practical, intuition",
            "Horse": "🐴 New challenge, money chance",
            "Goat": "🐑 Comfort + marriage luck",
            "Monkey": "🐵 Change, talent",
            "Rooster": "🐔 Effort result",
            "Dog": "🐶 Friends, money ↑",
            "Pig": "🐷 Leisure, best money"
        },
        "mbtis": {
            "INTJ": "🧠 Cool strategist",
            "INTP": "💡 Idea genius",
            "ENTJ": "👑 Boss",
            "ENTP": "⚡ Debate king",
            "INFJ": "🔮 Mind master",
            "INFP": "🎨 Emotional artist",
            "ENFJ": "🤗 Teacher to all",
            "ENFP": "🎉 Human vitamin",
            "ISTJ": "📋 Rule keeper",
            "ISFJ": "🛡️ World warmer",
            "ESTJ": "📢 Leader",
            "ESFJ": "💕 Mood maker",
            "ISTP": "🔧 Fixer artisan",
            "ISFP": "🌸 Emotional healer",
            "ESTP": "🏄 Adventure king",
            "ESFP": "🎭 Party protagonist"
        },
        "saju_msgs": [
            "Wood strong → Growth year! 🌱",
            "Fire strong → Passion explosion! ❤️",
            "Earth strong → Stability & wealth 💰",
            "Metal strong → Good decisiveness! 👔",
            "Water strong → Wisdom & flow 🌊",
            "Balanced elements → Happy year ✨",
            "Yang strong → Challenge success 🚀",
            "Yin strong → Inner reflection 😌"
        ],
        "daily_msgs": [
            "Good money luck! Small investments pay off 💰",
            "Great love luck! Perfect for confession or date ❤️",
            "Health caution! Avoid overwork and rest 😴",
            "Overall great luck! Only good things happen 🌟",
            "Good relationships! Chance to meet helpful person 🤝",
            "Best for study/work! Maximum focus 📚",
            "Good travel luck! Spontaneous trip OK ✈️",
            "Happy day! Full of smiles 😄"
        ]
    }
}

# 언어 선택
if "lang" not in st.session_state:
    st.session_state.lang = "ko"

lang = st.selectbox("🌐 Language", ["한국어", "English"], index=0 if st.session_state.lang == "ko" else 1)
st.session_state.lang = "ko" if lang == "한국어" else "en"

t = translations[st.session_state.lang]
Z = t["zodiacs"]
M = t["mbtis"]
saju_msg = t["saju_msgs"]
daily_msgs = t["daily_msgs"]

def get_zodiac(y):
    z_list = list(Z.keys())
    return z_list[(y-4)%12] if 1900<=y<=2030 else None

def get_saju(year, month, day):
    total = year + month + day
    index = total % 8
    return saju_msg[index]

def get_daily_fortune(zodiac, offset=0):
    today = datetime.now() + timedelta(days=offset)
    seed = int(today.strftime("%Y%m%d")) + list(Z.keys()).index(zodiac)
    random.seed(seed)
    return random.choice(daily_msgs)

st.set_page_config(page_title="운세", layout="centered")

# 초기 화면
st.markdown(f"<h1 style='text-align:center; color:#ff6b6b;'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#666;'>{t['caption']}</p>", unsafe_allow_html=True)

app_url = "https://my-fortune.streamlit.app"

st.markdown(f"<h3 style='text-align:center;'>{t['qr']}</h3>", unsafe_allow_html=True)
st.image("frame.png", use_column_width=True)

st.markdown(f"<h3 style='text-align:center;'>{t['share']}</h3>", unsafe_allow_html=True)
st.code(app_url, language=None)
st.markdown(f"<p style='text-align:center;'>{t['share_desc']}</p>", unsafe_allow_html=True)

# 이름 입력
name = st.text_input(t["name_placeholder"], placeholder="예: 홍길동")

st.markdown(f"<h3 style='text-align:center;'>{t['birth']}</h3>", unsafe_allow_html=True)
year = st.number_input("Year", 1900, 2030, 2005, step=1)
month = st.number_input("Month", 1, 12, 1, step=1)
day = st.number_input("Day", 1, 31, 1, step=1)

if "mbti" not in st.session_state:
    st.session_state.mbti = None
if "result_shown" not in st.session_state:
    st.session_state.result_shown = False

if st.session_state.mbti is None:
    choice = st.radio(t["mbti_mode"], [t["direct"], t["test"]])
    if choice == t["direct"]:
        mbti_input = st.selectbox("MBTI", sorted(M.keys()))
        if st.button(t["fortune_btn"], use_container_width=True):
            st.session_state.mbti = mbti_input
            st.session_state.result_shown = False
            st.rerun()
    else:
        st.markdown(f"<h3 style='text-align:center; color:#3498db;'>{t['test_start']}</h3>", unsafe_allow_html=True)
        e_i = s_n = t_f = j_p = 0
        # (16문제 테스트 코드 생략 - 이전과 동일하게 유지)
        # ... (테스트 질문들 그대로)
        if st.button(t["result_btn"], use_container_width=True):
            ei = "E" if e_i >= 3 else "I"
            sn = "S" if s_n >= 3 else "N"
            tf = "T" if t_f >= 3 else "F"
            jp = "J" if j_p >= 3 else "P"
            st.session_state.mbti = ei + sn + tf + jp
            st.session_state.result_shown = False
            st.rerun()

# 최종 결과 카드 (전체 화면 꽉 채움)
if st.session_state.mbti and not st.session_state.result_shown:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(year)
    if zodiac:
        score = 90
        saju = get_saju(year, month, day)
        today = get_daily_fortune(zodiac, 0)
        tomorrow = get_daily_fortune(zodiac, 1)
        zodiac_emoji = Z[zodiac].split(' ',1)[0]
        zodiac_desc = Z[zodiac].split(' ',1)[1] if ' ' in Z[zodiac] else ""
        mbti_emoji = M[mbti].split(' ',1)[0]
        mbti_desc = M[mbti].split(' ',1)[1] if ' ' in M[mbti] else ""
        name_text = f"{name}{t['your_fortune']}" if name else "2026년 운세"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                     width:100vw;
                     height:100vh;
                     margin:-80px 0 0 -20px;
                     padding:40px 20px;
                     box-sizing:border-box;
                     display:flex;
                     flex-direction:column;
                     justify-content:space-between;
                     align-items:center;
                     color:white;
                     position:relative;
                     overflow:hidden;">
          <div style="text-align:center;">
            <h1 style="font-size:2.8em; margin:0;">{name_text}</h1>
          </div>
          <div style="text-align:center;">
            <h2 style="font-size:2.5em; margin:30px 0;">
              {zodiac_emoji} <b>{zodiac}</b> + {mbti_emoji} <b>{mbti}</b>
            </h2>
            <h3 style="font-size:2.2em; margin:30px 0;">{t['combo']}</h3>
            <h2 style="font-size:5em; margin:40px 0; color:#ffd700;">{score}점</h2>
          </div>
          <div style="width:90%; background:rgba(255,255,255,0.15); border-radius:20px; padding:20px;">
            <p style="font-size:1.4em; margin:15px 0;"><b>{t['zodiac_title']}</b>: {zodiac_desc}</p>
            <p style="font-size:1.4em; margin:15px 0;"><b>{t['mbti_title']}</b>: {mbti_desc}</p>
            <p style="font-size:1.4em; margin:15px 0;"><b>{t['saju_title']}</b>: {saju}</p>
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.3); margin:25px 0;">
            <p style="font-size:1.5em; margin:15px 0;"><b>{t['today_title']}</b>: {today}</p>
            <p style="font-size:1.5em; margin:15px 0;"><b>{t['tomorrow_title']}</b>: {tomorrow}</p>
          </div>
          <p style="font-size:0.9em; opacity:0.7; margin-top:20px;">{app_url}</p>
        </div>
        """, unsafe_allow_html=True)

        st.balloons()
        st.snow()

        st.session_state.result_shown = True

    if st.button(t["reset"], use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
