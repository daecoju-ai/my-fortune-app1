import streamlit as st

# 다국어 사전 확장 (띠, MBTI, 사주까지!)
translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 운세 🌟",
        "caption": "완전 무료 😄",
        "qr": "### 📱 QR 코드 스캔!",
        "share": "### 🔗 공유 링크",
        "share_desc": "위 링크 복사해서 친구들한테 보내주세요!",
        "ad_title": "💳 렌탈 궁금할 때?",
        "ad_text": "<b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 페이백</b>!",
        "ad_btn": "🔗 보러가기",
        "birth": "### 생년월일 입력 (사주 계산을 위해!)",
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
        "zodiac_title": "**띠 운세**",
        "mbti_title": "**MBTI 특징**",
        "saju_title": "**사주 한 마디**",
        "footer": "재미로만 봐주세요! 친구들이랑 같이 해보세요 😊",
        "zodiacs": {"쥐띠":"🐭 활발·성장, 돈↑","소띠":"🐮 노력 결실","호랑이띠":"🐯 도전 성공, 돈 대박","토끼띠":"🐰 안정·사랑 운","용띠":"🐲 운↑ 리더십","뱀띠":"🐍 실속·직감","말띠":"🐴 새 도전·돈 기회","양띠":"🐑 편안+결혼 운","원숭이띠":"🐵 변화·재능","닭띠":"🐔 노력 결과","개띠":"🐶 친구·돈↑","돼지띠":"🐷 여유·돈 최고"},
        "mbtis": {"INTJ":"🧠 냉철 전략가","INTP":"💡 아이디어 천재","ENTJ":"👑 보스","ENTP":"⚡ 토론왕","INFJ":"🔮 마음 마스터","INFP":"🎨 감성 예술가","ENFJ":"🤗 모두 선생님","ENFP":"🎉 인간 비타민","ISTJ":"📋 규칙 지킴이","ISFJ":"🛡️ 세상 따뜻함","ESTJ":"📢 리더","ESFJ":"💕 분위기 메이커","ISTP":"🔧 고치는 장인","ISFP":"🌸 감성 힐러","ESTP":"🏄 모험왕","ESFP":"🎭 파티 주인공"},
        "saju_msgs": [
            "목(木) 기운 강함 → 성장과 발전의 해! 🌱",
            "화(火) 기운 강함 → 열정 폭발! ❤️",
            "토(土) 기운 강함 → 안정과 재물운 💰",
            "금(金) 기운 강함 → 결단력 좋음! 👔",
            "수(水) 기운 강함 → 지혜와 흐름 🌊",
            "오행 균형 → 행복한 한 해 ✨",
            "양기 강함 → 도전 성공 🚀",
            "음기 강함 → 내면 성찰 😌"
        ]
    },
    "en": {
        "title": "🌟 2026 Zodiac + MBTI + Saju Fortune 🌟",
        "caption": "Completely Free 😄",
        "qr": "### 📱 Scan QR Code!",
        "share": "### 🔗 Share Link",
        "share_desc": "Copy the link and share with friends!",
        "ad_title": "💳 Curious about rental?",
        "ad_text": "<b>Dananum Rental</b> partner card: <b>0 won/month</b> + <b>Cashback</b>!",
        "ad_btn": "🔗 Check it out",
        "birth": "### Enter Birth Date",
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
        "zodiac_title": "**Zodiac Fortune**",
        "mbti_title": "**MBTI Traits**",
        "saju_title": "**Saju Message**",
        "footer": "For fun only! Try with friends 😊",
        "zodiacs": {"Rat":"🐭 Active growth, money ↑","Ox":"🐮 Effort pays off","Tiger":"🐯 Challenge success, big money","Rabbit":"🐰 Stability, love luck","Dragon":"🐲 Luck ↑ leadership","Snake":"🐍 Practical, intuition","Horse":"🐴 New challenge, money chance","Sheep":"🐑 Comfort + marriage luck","Monkey":"🐵 Change, talent","Rooster":"🐔 Effort result","Dog":"🐶 Friends, money ↑","Pig":"🐷 Leisure, best money"},
        "mbtis": {"INTJ":"🧠 Cool strategist","INTP":"💡 Idea genius","ENTJ":"👑 Boss","ENTP":"⚡ Debate king","INFJ":"🔮 Mind master","INFP":"🎨 Emotional artist","ENFJ":"🤗 Teacher to all","ENFP":"🎉 Human vitamin","ISTJ":"📋 Rule keeper","ISFJ":"🛡️ World warmer","ESTJ":"📢 Leader","ESFJ":"💕 Mood maker","ISTP":"🔧 Fixer artisan","ISFP":"🌸 Emotional healer","ESTP":"🏄 Adventure king","ESFP":"🎭 Party protagonist"},
        "saju_msgs": [
            "Wood strong → Growth year! 🌱",
            "Fire strong → Passion explosion! ❤️",
            "Earth strong → Stability & wealth 💰",
            "Metal strong → Good decisiveness! 👔",
            "Water strong → Wisdom & flow 🌊",
            "Balanced five elements → Happy year ✨",
            "Yang strong → Challenge success 🚀",
            "Yin strong → Inner reflection 😌"
        ]
    },
    # 일본어·중국어는 필요시 추가 (영어 먼저 완벽하게!)
}

if "lang" not in st.session_state:
    st.session_state.lang = "ko"

lang = st.selectbox("🌐 Language", ["한국어", "English"], 
                    index=["ko", "en"].index(st.session_state.lang), key="lang_select")
st.session_state.lang = {"한국어": "ko", "English": "en"}[lang]

t = translations[st.session_state.lang]
Z = t["zodiacs"]
M = t["mbtis"]
saju_msg = t["saju_msgs"]

def get_zodiac(y): 
    z_list = list(Z.keys())
    return z_list[(y-4)%12] if 1900<=y<=2030 else None

def get_saju(year, month, day):
    total = year + month + day
    index = total % 8
    return saju_msg[index]

# 나머지 코드 동일 (생략하지 않고 전체 붙여넣기 추천!)
# (이전 코드에서 Z, M, saju_msg 부분만 t["zodiacs"] 등으로 바꿈)

# ... (이전 코드의 나머지 부분 그대로)

# 결과 부분 예시
st.success(f"{Z[zodiac].split(',',1)[0]} **{zodiac}** + {M[mbti].split(',',1)[0]} **{mbti}** Best combo!")
st.info(f"{t['zodiac_title']}: {Z[zodiac].split(',',1)[1] if ',' in Z[zodiac] else ''}")
st.info(f"{t['mbti_title']}: {M[mbti].split(',',1)[1] if ',' in M[mbti] else ''}")
st.warning(f"{t['saju_title']}: {saju}")

# 공유 텍스트도 언어 맞춰 (필요시 추가)
