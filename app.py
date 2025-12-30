import streamlit as st
from datetime import datetime, timedelta

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
        "birth": "### 생년월일 입력 (사주 계산을 위해!)",
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
        "share_text_label": "공유 텍스트 (길게 눌러 복사)",
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
        "today_title": "Today's Fortune",
        "tomorrow_title": "Tomorrow's Fortune",
        "daily_msgs": [
            "Good money luck! Small investments pay off 💰",
            "Great love luck! Perfect for confession or date ❤️",
            "Health caution! Avoid overwork and rest 😴",
            "Overall great luck! Only good things happen 🌟",
            "Good relationships! Chance to meet helpful person 🤝",
            "Best for study/work! Maximum focus 📚",
            "Good travel luck! Spontaneous trip OK ✈️",
            "Happy day! Full of smiles 😄"
        ],
        # 다른 번역은 이전과 동일 (생략)
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "ko"

lang = st.selectbox("🌐 Language", ["한국어", "English"], 
                    index=0 if st.session_state.lang == "ko" else 1)
st.session_state.lang = "ko" if lang == "한국어" else "en"

t = translations[st.session_state.lang]
Z = t["zodiacs"]
M = t["mbtis"]
saju_msg = t["saju_msgs"]
daily_msgs = t.get("daily_msgs", translations["ko"]["daily_msgs"])

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

# 디자인 및 나머지 코드 (이전과 동일, 이름 입력 포함)

# ... (이전 코드의 디자인, 이름 입력, 생년월일, MBTI 테스트 부분 그대로)

# 결과 카드 부분 (오늘·내일 운세 추가!)
if st.session_state.mbti and not st.session_state.result_shown:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(year)
    if zodiac:
        score = 90
        saju = get_saju(year, month, day)
        today_fortune = get_daily_fortune(zodiac, 0)
        tomorrow_fortune = get_daily_fortune(zodiac, 1)
        zodiac_emoji = Z[zodiac].split(' ',1)[0]
        zodiac_desc = Z[zodiac].split(' ',1)[1] if ' ' in Z[zodiac] else ""
        mbti_emoji = M[mbti].split(' ',1)[0]
        mbti_desc = M[mbti].split(' ',1)[1] if ' ' in M[mbti] else ""
        
        name_text = f"{name}{t['your_fortune']}" if name else "2026년 운세"
        
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:30px;border-radius:30px;text-align:center;margin:30px 0;box-shadow: 0 10px 30px rgba(0,0,0,0.3);color:white;">
          <h1 style="font-size:2.5em;margin-bottom:10px;">{name_text}</h1>
          <h2 style="font-size:2em;margin:20px 0;">{zodiac_emoji} <b>{zodiac}</b> + {mbti_emoji} <b>{mbti}</b></h2>
          <h3 style="font-size:1.8em;margin:20px 0;">{t['combo']}</h3>
          <h2 style="font-size:3em;margin:30px 0;color:#ffd700;">{score}점</h2>
          <p style="font-size:1.3em;background:rgba(255,255,255,0.2);padding:15px;border-radius:15px;margin:20px 0;">{t['zodiac_title']}: {zodiac_desc}</p>
          <p style="font-size:1.3em;background:rgba(255,255,255,0.2);padding:15px;border-radius:15px;margin:20px 0;">{t['mbti_title']}: {mbti_desc}</p>
          <p style="font-size:1.3em;background:rgba(255,255,255,0.2);padding:15px;border-radius:15px;margin:20px 0;">{t['saju_title']}: {saju}</p>
          <hr style="border-color:rgba(255,255,255,0.3);margin:30px 0;">
          <h3 style="font-size:1.8em;margin-bottom:20px;">{t.get('today_title', '오늘 운세')}</h3>
          <p style="font-size:1.4em;background:rgba(255,255,255,0.2);padding:15px;border-radius:15px;">{today_fortune}</p>
          <h3 style="font-size:1.8em;margin:30px 0 20px 0;">{t.get('tomorrow_title', '내일 운세')}</h3>
          <p style="font-size:1.4em;background:rgba(255,255,255,0.2);padding:15px;border-radius:15px;">{tomorrow_fortune}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.balloons()
        st.snow()

        share_text = f"{name_text}!\n띠: {zodiac}\nMBTI: {mbti}\n사주: {saju}\n오늘: {today_fortune}\n내일: {tomorrow_fortune}\n점수 {score}점!\n{app_url}" if st.session_state.lang == "ko" else f"{name}'s Fortune!\nZodiac: {zodiac}\nMBTI: {mbti}\nSaju: {saju}\nToday: {today_fortune}\nTomorrow: {tomorrow_fortune}\nScore {score}점!\n{app_url}"
        st.text_area(t["share_text_label"], share_text, height=150, key="share_unique")

        st.session_state.result_shown = True

    if st.button(t["reset"], use_container_width=True, key="reset"):
        st.session_state.clear()
        st.rerun()

st.markdown(f"<p style='text-align: center; color: #95a5a6;'>{t['footer']}</p>", unsafe_allow_html=True)
