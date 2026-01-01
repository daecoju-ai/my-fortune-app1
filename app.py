import streamlit as st
from datetime import datetime, timedelta
import random
from streamlit.components.v1 import html as st_html

# 다국어 사전
translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 + 오늘/내일 운세 🌟",
        "caption": "완전 무료 😄",
        "ad_title": "💳 정수기렌탈 궁금할 때?",
        "ad_text": "<b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 최대 50만원 페이백</b>!",
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
        "share_btn": "친구에게 결과 공유",
        "tarot_btn": "🔮 오늘의 타로 카드 뽑기",
        "tarot_title": "오늘의 타로 카드",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "combo": "최고 조합!",
        "your_fortune": "님의 2026년 운세",
        "overall_title": "2026 전체 운세",
        "combo_title": "조합 한 마디",
        "lucky_color_title": "럭키 컬러",
        "lucky_item_title": "럭키 아이템",
        "tip_title": "팁",
        "footer": "재미로만 봐주세요 😊",
        "overall_fortunes": [
            "성장과 재물이 함께하는 최고의 해! 대박 기운 가득 ✨",
            "안정과 행복이 넘치는 한 해! 가족과 함께하는 기쁨 🏡",
            "도전과 성공의 해! 큰 성과를 이룰 거예요 🚀",
            "사랑과 인연이 피어나는 로맨틱한 해 ❤️",
            "변화와 새로운 시작! 창의력이 빛나는 한 해 🎨"
        ],
        "combo_comments": [
            "{}의 노력과 {}의 따뜻함으로 모두를 이끄는 리더가 될 거예요!",
            "{}의 리더십과 {}의 창의력이 완벽한 시너지!",
            "{}의 직감과 {}의 논리로 무적 조합!",
            "{}의 안정감과 {}의 열정으로 대박 성공!",
            "{}의 유연함과 {}의 결단력으로 모든 일 해결!"
        ],
        "lucky_colors": ["골드 💛", "레드 ❤️", "블루 💙", "그린 🌿", "퍼플 💜"],
        "lucky_items": ["황금 액세서리", "빨간 지갑", "파란 목걸이", "초록 식물", "보라색 펜"],
        "tips": [
            "새로운 사람 만나는 기회 많아요. 적극적으로!",
            "작은 투자에 집중하세요. 이득 볼 가능성 높음 💰",
            "건강 관리에 신경 쓰세요. 규칙적인 운동 추천 🏃",
            "가족/친구와 시간 보내세요. 행복 충전! 🏡",
            "창의적인 취미를 시작해보세요. 재능 발휘될 거예요 🎨"
        ],
        "tarot_cards": {
            "The Fool": "🃏 바보 - 새로운 시작, 모험, 순수한 믿음",
            "The Magician": "🪄 마법사 - 창조력, 능력 발휘, 집중",
            "The High Priestess": "🔮 여사제 - 직감, 신비, 내면의 목소리",
            "The Empress": "👑 여제 - 풍요, 어머니의 사랑, 창작",
            "The Emperor": "♚ 황제 - 안정, 권위, 구조",
            "The Hierophant": "⛪ 교황 - 전통, 스승, 지도",
            "The Lovers": "💕 연인 - 사랑, 조화, 선택",
            "The Chariot": "🚀 전차 - 승리, 의지력, 방향",
            "Strength": "💪 힘 - 용기, 인내, 부드러운 통제",
            "The Hermit": "🏮 은둔자 - 내면 탐구, 지혜, 고독",
            "Wheel of Fortune": "🎡 운명의 수레바퀴 - 변화, 운, 사이클",
            "Justice": "⚖️ 정의 - 공정, 균형, 진실",
            "The Hanged Man": "🙃 매달린 사람 - 희생, 새로운 관점, 기다림",
            "Death": "💀 죽음 - 변화, 끝과 시작, 재생",
            "Temperance": "👼 절제 - 균형, 조화, 인내",
            "The Devil": "😈 악마 - 속박, 유혹, 물질주의",
            "The Tower": "🗼 탑 - 갑작스러운 변화, 파괴와 재건",
            "The Star": "⭐ 별 - 희망, 영감, 치유",
            "The Moon": "🌙 달 - 불안, 환상, 직감",
            "The Sun": "☀️ 태양 - 행복, 성공, 긍정 에너지",
            "Judgement": "📯 심판 - 부활, 깨달음, 용서",
            "The World": "🌍 세계 - 완성, 성취, 전체성"
        },
        "zodiacs": {
            "쥐띠": "🐭 안정 속 새로운 기회! 민첩한 판단으로 성공 잡아요 💰",
            "소띠": "🐮 꾸준함의 결실! 안정된 성장과 행복한 가족운 🏡",
            "호랑이띠": "🐯 대박 띠! 도전과 성공, 리더십 발휘로 큰 성과 🚀",
            "토끼띠": "🐰 삼재 주의! 신중함으로 변화 대처, 안정 추구 ❤️",
            "용띠": "🐲 운기 상승! 리더십과 승진 기회 많음 👑",
            "뱀띠": "🐍 직감과 실속! 예상치 못한 재물운 🤑",
            "말띠": "🐴 본띠 해! 추진력 강하지만 균형이 핵심 ✈️",
            "양띠": "🐑 대박 띠! 편안함과 최고 돈운, 가정 행복 🏠",
            "원숭이띠": "🐵 변화와 재능 발휘! 창의력으로 성공 🎨",
            "닭띠": "🐔 노력 결실! 인정과 승진 가능성 높음 🏆",
            "개띠": "🐶 대박 띠! 귀인 도움과 네트워킹으로 상승 🤝",
            "돼지띠": "🐷 여유와 재물 대박! 즐기는 최고의 해 🐷"
        },
        "mbtis": {
            "INTJ": "🧠 냉철 전략가", "INTP": "💡 아이디어 천재", "ENTJ": "👑 보스", "ENTP": "⚡ 토론왕",
            "INFJ": "🔮 마음 마스터", "INFP": "🎨 감성 예술가", "ENFJ": "🤗 모두 선생님", "ENFP": "🎉 인간 비타민",
            "ISTJ": "📋 규칙 지킴이", "ISFJ": "🛡️ 세상 따뜻함", "ESTJ": "📢 리더", "ESFJ": "💕 분위기 메이커",
            "ISTP": "🔧 고치는 장인", "ISFP": "🌸 감성 힐러", "ESTP": "🏄 모험왕", "ESFP": "🎭 파티 주인공"
        },
        "saju_msgs": [
            "목(木) 기운 강함 → 성장과 발전의 해! 🌱", "화(火) 기운 강함 → 열정 폭발! ❤️",
            "토(土) 기운 강함 → 안정과 재물운 💰", "금(金) 기운 강함 → 결단력 좋음! 👔",
            "수(水) 기운 강함 → 지혜와 흐름 🌊", "오행 균형 → 행복한 한 해 ✨",
            "양기 강함 → 도전 성공 🚀", "음기 강함 → 내면 성찰 😌"
        ],
        "daily_msgs": [
            "재물운 좋음! 작은 투자도 이득 봐요 💰", "연애운 최고! 고백하거나 데이트 좋음 ❤️",
            "건강 주의! 과로 피하고 쉬세요 😴", "전체운 대박! 좋은 일만 생길 거예요 🌟",
            "인간관계 운 좋음! 귀인 만남 가능 🤝", "학업/일 운 최고! 집중력 최고 📚",
            "여행운 좋음! 갑자기 떠나도 괜찮아요 ✈️", "기분 좋은 하루! 웃음이 가득할 거예요 😄"
        ],
        "q_energy": [
            "주말에 친구들이 갑자기 '놀자!' 하면?",
            "모임에서 처음 본 사람들과 대화하는 거?",
            "하루 종일 사람 만난 후에?",
            "생각이 떠오르면?"
        ],
        "q_info": [
            "새로운 카페 가면 뭐가 먼저 눈에 들어?",
            "친구가 고민 상담하면?",
            "책이나 영화 볼 때?",
            "쇼핑할 때?"
        ],
        "q_decision": [
            "친구가 늦어서 화날 때?",
            "팀 프로젝트에서 의견 충돌 시?",
            "누가 울면서 상담하면?",
            "거짓말 탐지 시?"
        ],
        "q_life": [
            "여행 갈 때?",
            "숙제나 과제 마감 앞두고?",
            "방 정리할 때?",
            "선택해야 할 때?"
        ],
        "options_e": ["와 좋아! 바로 나감 (E)", "재밌고 신나! (E)", "아직 에너지 넘쳐! (E)", "바로 말로 풀어냄 (E)"],
        "options_i": ["집에서 쉬고 싶어... (I)", "조금 피곤하고 부담스러워 (I)", "완전 지쳐서 혼자 있고 싶어 (I)", "머릿속에서 먼저 정리함 (I)"],
        "options_s": ["메뉴판 가격과 메뉴 (S)", "지금 상황과 사실 위주로 들어줌 (S)", "스토리와 디테일에 집중 (S)", "필요한 거 보고 바로 사 (S)"],
        "options_n": ["분위기, 인테리어, 컨셉 (N)", "가능성과 미래 방향으로 생각함 (N)", "상징과 숨은 의미 찾는 재미 (N)", "이거 사면 나중에 뭐랑 입히지? 상상함 (N)"],
        "options_t": ["늦었으면 늦었다고 솔직히 말함 (T)", "논리적으로 누가 맞는지 따짐 (T)", "문제 해결 방법 조언해줌 (T)", "바로 지적함 (T)"],
        "options_f": ["기분 상할까 봐 부드럽게 말함 (F)", "다른 사람 기분 상하지 않게 조율 (F)", "일단 공감하고 들어줌 (F)", "상처 줄까 봐 넘김 (F)"],
        "options_j": ["일정 꽉꽉 짜서 효율적으로 (J)", "미리미리 끝냄 (J)", "정해진 기준으로 깔끔히 (J)", "빨리 결정하고 넘김 (J)"],
        "options_p": ["그때그때 기분 따라 즉흥적으로 (P)", "마감 직전에 몰아서 함 (P)", "대충 써도 괜찮아 (P)", "옵션 더 알아보고 싶어 (P)"]
    },
    "en": {
        "title": "🌟 2026 Zodiac + MBTI + Fortune + Today/Tomorrow Luck 🌟",
        "caption": "Completely Free 😄",
        "ad_title": "💳 Curious about rental?",
        "ad_text": "<b>Dananum Rental</b> with partner card: <b>From 0 won/month</b> + <b>Cashback</b>!",
        "ad_btn": "🔗 Check it out",
        "birth": "### Enter Birth Date",
        "name_placeholder": "Enter name (shown in result)",
        "mbti_mode": "How to do MBTI?",
        "direct": "Direct input",
        "test": "Detailed test (16 questions)",
        "test_start": "Detailed test start! Please answer one by one 😊",
        "energy": "Energy Direction",
        "info": "Information Gathering",
        "decision": "Decision Making",
        "life": "Lifestyle",
        "result_btn": "View Result!",
        "fortune_btn": "🔮 View 2026 Fortune!",
        "reset": "Start Over",
        "share_btn": "Share Result with Friends",
        "tarot_btn": "🔮 Draw Today's Tarot Card",
        "tarot_title": "Today's Tarot Card",
        "zodiac_title": "Zodiac Fortune",
        "mbti_title": "MBTI Traits",
        "saju_title": "Fortune Comment",
        "today_title": "Today's Luck",
        "tomorrow_title": "Tomorrow's Luck",
        "combo": "Best Combo!",
        "your_fortune": "'s 2026 Fortune",
        "overall_title": "2026 Annual Luck",
        "combo_title": "Combination Meaning",
        "lucky_color_title": "Lucky Color",
        "lucky_item_title": "Lucky Item",
        "tip_title": "Tip",
        "footer": "For fun only 😊",
        "overall_fortunes": [
            "Growth and wealth together – the best year! Big luck ✨",
            "A year full of stability and happiness! Family joy 🏡",
            "Year of challenge and success! Great achievements 🚀",
            "Romantic year with love blooming ❤️",
            "Year of change and new beginnings! Creativity shines 🎨"
        ],
        "combo_comments": [
            "With {}'s effort and {}'s warmth, you'll become a leader!",
            "{}'s leadership and {}'s creativity make perfect synergy!",
            "{}'s intuition and {}'s logic make an invincible combo!",
            "{}'s stability and {}'s passion lead to big success!",
            "{}'s flexibility and {}'s decisiveness solve everything!"
        ],
        "lucky_colors": ["Gold 💛", "Red ❤️", "Blue 💙", "Green 🌿", "Purple 💜"],
        "lucky_items": ["Golden accessories", "Red wallet", "Blue necklace", "Green plant", "Purple pen"],
        "tips": [
            "Many chances to meet new people. Be proactive!",
            "Focus on small investments. High chance of profit 💰",
            "Take care of health. Regular exercise recommended 🏃",
            "Spend time with family/friends. Recharge happiness! 🏡",
            "Start a creative hobby. Your talent will shine 🎨"
        ],
        "tarot_cards": {
            "The Fool": "🃏 The Fool - New beginnings, adventure, innocence",
            "The Magician": "🪄 The Magician - Manifestation, skill, concentration",
            "The High Priestess": "🔮 The High Priestess - Intuition, mystery, inner voice",
            "The Empress": "👑 The Empress - Abundance, nurturing, creativity",
            "The Emperor": "♚ The Emperor - Stability, authority, structure",
            "The Hierophant": "⛪ The Hierophant - Tradition, guidance, conformity",
            "The Lovers": "💕 The Lovers - Love, harmony, choices",
            "The Chariot": "🚀 The Chariot - Victory, determination, direction",
            "Strength": "💪 Strength - Courage, patience, gentle control",
            "The Hermit": "🏮 The Hermit - Soul searching, wisdom, solitude",
            "Wheel of Fortune": "🎡 Wheel of Fortune - Change, cycles, fate",
            "Justice": "⚖️ Justice - Fairness, truth, balance",
            "The Hanged Man": "🙃 The Hanged Man - Sacrifice, new perspective, waiting",
            "Death": "💀 Death - Transformation, ending, rebirth",
            "Temperance": "👼 Temperance - Balance, harmony, patience",
            "The Devil": "😈 The Devil - Bondage, temptation, materialism",
            "The Tower": "🗼 The Tower - Sudden change, upheaval, revelation",
            "The Star": "⭐ The Star - Hope, inspiration, healing",
            "The Moon": "🌙 The Moon - Illusion, intuition, uncertainty",
            "The Sun": "☀️ The Sun - Joy, success, positivity",
            "Judgement": "📯 Judgement - Rebirth, awakening, forgiveness",
            "The World": "🌍 The World - Completion, fulfillment, wholeness"
        },
        "zodiacs": {
            "Rat": "🐭 New opportunities in stability! Success with quick judgment 💰",
            "Ox": "🐮 Fruits of perseverance! Stable growth and happy family 🏡",
            "Tiger": "🐯 Big luck sign! Challenge and success with leadership 🚀",
            "Rabbit": "🐰 Caution with change! Seek stability ❤️",
            "Dragon": "🐲 Rising fortune! Leadership and promotion opportunities 👑",
            "Snake": "🐍 Intuition and gain! Unexpected wealth 🤑",
            "Horse": "🐴 Year of the Horse! Strong drive but balance is key ✈️",
            "Goat": "🐑 Big luck sign! Comfort and best money luck, happy home 🏠",
            "Monkey": "🐵 Change and talent shine! Success with creativity 🎨",
            "Rooster": "🐔 Effort rewarded! Recognition and promotion 🏆",
            "Dog": "🐶 Big luck sign! Helpful people and networking rise 🤝",
            "Pig": "🐷 Relaxation and wealth jackpot! Enjoy the best year 🐷"
        },
        "mbtis": {
            "INTJ": "🧠 Strategist", "INTP": "💡 Genius Thinker", "ENTJ": "👑 Commander", "ENTP": "⚡ Debater",
            "INFJ": "🔮 Advocate", "INFP": "🎨 Mediator", "ENFJ": "🤗 Protagonist", "ENFP": "🎉 Campaigner",
            "ISTJ": "📋 Logistician", "ISFJ": "🛡️ Defender", "ESTJ": "📢 Executive", "ESFJ": "💕 Consul",
            "ISTP": "🔧 Virtuoso", "ISFP": "🌸 Adventurer", "ESTP": "🏄 Entrepreneur", "ESFP": "🎭 Entertainer"
        },
        "saju_msgs": [
            "Strong Wood → Growth year! 🌱", "Strong Fire → Passion explosion! ❤️",
            "Strong Earth → Stability and wealth 💰", "Strong Metal → Strong determination! 👔",
            "Strong Water → Wisdom and flow 🌊", "Balanced elements → Happy year ✨",
            "Strong Yang → Challenge success 🚀", "Strong Yin → Inner reflection 😌"
        ],
        "daily_msgs": [
            "Good wealth luck! 💰", "Best love luck! ❤️",
            "Health caution 😴", "Overall big luck! 🌟",
            "Good relationships 🤝", "Best for study/work 📚",
            "Good travel luck ✈️", "Happy day full of laughter 😄"
        ],
        "q_energy": [
            "Friends suddenly say 'Let's hang out!' on weekend?",
            "Talking to strangers at a gathering?",
            "After meeting people all day?",
            "When a thought comes to mind?"
        ],
        "q_info": [
            "What catches your eye first in a new cafe?",
            "When friend shares worries?",
            "When reading book or watching movie?",
            "When shopping?"
        ],
        "q_decision": [
            "When friend is late and you're angry?",
            "In team project when opinions clash?",
            "When someone cries while consulting?",
            "When detecting a lie?"
        ],
        "q_life": [
            "When planning a trip?",
            "Before assignment deadline?",
            "When cleaning room?",
            "When needing to choose?"
        ],
        "options_e": ["Yes! Go out right away (E)", "Fun and exciting! (E)", "Still full of energy! (E)", "Express thoughts out loud (E)"],
        "options_i": ["Want to stay home... (I)", "A bit tiring and burdensome (I)", "Totally exhausted, want to be alone (I)", "Organize in head first (I)"],
        "options_s": ["Menu prices and items (S)", "Listen to current facts (S)", "Focus on story and details (S)", "Buy what I need right away (S)"],
        "options_n": ["Atmosphere, interior, concept (N)", "Think about possibilities and future (N)", "Enjoy finding symbols and hidden meanings (N)", "Imagine what to wear it with later (N)"],
        "options_t": ["Say honestly they're late (T)", "Argue logically who's right (T)", "Give advice on solving problem (T)", "Point out immediately (T)"],
        "options_f": ["Say gently to not hurt feelings (F)", "Mediate to not hurt feelings (F)", "First empathize and listen (F)", "Let it go to not hurt (F)"],
        "options_j": ["Plan schedule tightly for efficiency (J)", "Finish early in advance (J)", "Organize neatly by standard (J)", "Decide quickly and move on (J)"],
        "options_p": ["Go with the flow spontaneously (P)", "Do it all at deadline (P)", "It's okay if messy (P)", "Want to explore more options (P)"]
    }
}

# 세션 상태 초기화
if "lang" not in st.session_state:
    st.session_state.lang = "ko"

st.session_state.lang = st.radio("언어 / Language", ["ko", "en"], index=["ko", "en"].index(st.session_state.lang), horizontal=True)

t = translations[st.session_state.lang]

Z = t["zodiacs"]
M = t["mbtis"]
saju_msg = t["saju_msgs"]
daily_msgs = t["daily_msgs"]

def get_zodiac(y):
    z_list = list(Z.keys())
    return z_list[(y - 4) % 12] if 1900 <= y <= 2030 else None

def get_saju(year, month, day):
    total = year + month + day
    index = total % 8
    return saju_msg[index]

def get_daily_fortune(zodiac, offset=0):
    today = datetime.now() + timedelta(days=offset)
    seed = int(today.strftime("%Y%m%d")) + list(Z.keys()).index(zodiac)
    random.seed(seed)
    return random.choice(daily_msgs)

st.set_page_config(page_title=t["title"], layout="centered")

# 세션 상태 초기화
if "mbti" not in st.session_state:
    st.session_state.mbti = None
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

app_url = "https://my-fortune.streamlit.app"

# 초기 화면
if not st.session_state.result_shown:
    st.markdown(f"<h1 style='text-align:center; color:#ff6b6b;'>{t['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#666;'>{t['caption']}</p>", unsafe_allow_html=True)

    st.image("frame.png", use_column_width=True)

    st.markdown(f"""
    <div style="background:#fffbe6;padding:20px;border-radius:20px;text-align:center;margin:30px 0;">
      <h3 style="color:#d35400;">{t['ad_title']}</h3>
      <p>{t['ad_text']}</p>
      <a href="https://www.다나눔렌탈.com" target="_blank">
        <button style="background:#e67e22;color:white;padding:15px 30px;border:none;border-radius:15px;">{t['ad_btn']}</button>
      </a>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input(t["name_placeholder"], value=st.session_state.name)

    st.markdown(f"<h3 style='text-align:center;'>{t['birth']}</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    st.session_state.year = col1.number_input("Year" if st.session_state.lang == "en" else "년", 1900, 2030, st.session_state.year, step=1)
    st.session_state.month = col2.number_input("Month" if st.session_state.lang == "en" else "월", 1, 12, st.session_state.month, step=1)
    st.session_state.day = col3.number_input("Day" if st.session_state.lang == "en" else "일", 1, 31, st.session_state.day, step=1)

    choice = st.radio(t["mbti_mode"], [t["direct"], t["test"]])

    if choice == t["direct"]:
        mbti_input = st.selectbox("MBTI", sorted(M.keys()))
        if st.button(t["fortune_btn"], use_container_width=True):
            st.session_state.mbti = mbti_input
            st.session_state.result_shown = True
            st.rerun()
    else:
        st.markdown(f"<h3 style='text-align:center; color:#3498db;'>{t['test_start']}</h3>", unsafe_allow_html=True)
        e_i = s_n = t_f = j_p = 0

        st.subheader(t["energy"])
        for i in range(4):
            q = t["q_energy"][i]
            opt1 = t["options_e"][i]
            opt2 = t["options_i"][i]
            if st.radio(q, [opt1, opt2], key=f"q{i+1}") == opt1:
                e_i += 1

        st.subheader(t["info"])
        for i in range(4):
            q = t["q_info"][i]
            opt1 = t["options_s"][i]
            opt2 = t["options_n"][i]
            if st.radio(q, [opt1, opt2], key=f"q{i+5}") == opt1:
                s_n += 1

        st.subheader(t["decision"])
        for i in range(4):
            q = t["q_decision"][i]
            opt1 = t["options_t"][i]
            opt2 = t["options_f"][i]
            if st.radio(q, [opt1, opt2], key=f"q{i+9}") == opt1:
                t_f += 1

        st.subheader(t["life"])
        for i in range(4):
            q = t["q_life"][i]
            opt1 = t["options_j"][i]
            opt2 = t["options_p"][i]
            if st.radio(q, [opt1, opt2], key=f"q{i+13}") == opt1:
                j_p += 1

        if st.button(t["result_btn"], use_container_width=True):
            ei = "E" if e_i >= 3 else "I"
            sn = "S" if s_n >= 3 else "N"
            tf = "T" if t_f >= 3 else "F"
            jp = "J" if j_p >= 3 else "P"
            st.session_state.mbti = ei + sn + tf + jp
            st.session_state.result_shown = True
            st.rerun()

# 결과 화면
if st.session_state.result_shown:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(st.session_state.year)
    if zodiac:
        saju = get_saju(st.session_state.year, st.session_state.month, st.session_state.day)
        today = get_daily_fortune(zodiac, 0)
        tomorrow = get_daily_fortune(zodiac, 1)
        zodiac_emoji = Z[zodiac].split(' ',1)[0]
        zodiac_desc = Z[zodiac].split(' ',1)[1] if ' ' in Z[zodiac] else Z[zodiac]
        mbti_emoji = M[mbti].split(' ',1)[0]
        mbti_desc = M[mbti].split(' ',1)[1] if ' ' in M[mbti] else M[mbti]

        name_display = f"{st.session_state.name}{t['your_fortune']}" if st.session_state.name else t["title"]

        overall = random.choice(t["overall_fortunes"])
        combo_comment = random.choice(t["combo_comments"]).format(zodiac, mbti)
        lucky_color = random.choice(t["lucky_colors"])
        lucky_item = random.choice(t["lucky_items"])
        tip = random.choice(t["tips"])

        st.markdown(f"""
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
        <div style="background:linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
                     width:100vw; height:100vh; margin:-80px -20px 0 -20px; padding:8px;
                     box-sizing:border-box; text-align:center; overflow:hidden;
                     font-family:'Noto Sans KR', sans-serif; font-size:0.85em; line-height:1.2;">
          <div style="color:#000000;">
            <h1 style="font-size:1.1em; margin:5px 0; opacity:0.9;">{name_display}</h1>
            <h2 style="font-size:1.2em; margin:8px 0;">
              <span style="font-size:1.4em;">{zodiac_emoji}</span> {zodiac} + <span style="font-size:1.4em;">{mbti_emoji}</span> {mbti}
            </h2>
            <h3 style="font-size:0.9em; margin:4px 0; opacity:0.9;">{t['combo']}</h3>

            <div style="background:#ffffff40; border-radius:18px; padding:10px; margin:10px 8px; backdrop-filter: blur(10px); line-height:1.4; font-size:1.0em;">
              <b>{t['zodiac_title']}</b>: {zodiac_desc}<br>
              <b>{t['mbti_title']}</b>: {mbti_desc}<br>
              <b>{t['saju_title']}</b>: {saju}<br><br>
              <b>{t['today_title']}</b>: {today}<br>
              <b>{t['tomorrow_title']}</b>: {tomorrow}<br><br>
              <b>{t['overall_title']}</b>: {overall}<br>
              <b>{t['combo_title']}</b>: {combo_comment}<br>
              <b>{t['lucky_color_title']}</b>: {lucky_color} | <b>{t['lucky_item_title']}</b>: {lucky_item}<br>
              <b>{t['tip_title']}</b>: {tip}
            </div>

            <div style="background:#ffffff40; border-radius:15px; padding:8px; margin:8px 8px; backdrop-filter: blur(5px); font-size:0.85em;">
              <small style="color:#ff4444; font-weight:bold;">광고</small><br>
              💧 <b>정수기 렌탈 대박!</b><br>
              제휴카드면 <b>월 0원부터</b>!<br>
              설치 당일 <b>최대 50만원 지원</b> + 사은품 듬뿍 ✨<br>
              <a href="https://www.다나눔렌탈.com" target="_blank" style="color:#00bfff; text-decoration:underline;">🔗 다나눔렌탈.com 바로가기</a>
            </div>

            <p style="font-size:0.6em; opacity:0.8; margin:4px 0;">{app_url}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(t["tarot_btn"], use_container_width=True):
            tarot_card = random.choice(list(t["tarot_cards"].keys()))
            tarot_meaning = t["tarot_cards"][tarot_card]
            st.markdown(f"""
            <div style="background:#ffffff40; border-radius:18px; padding:15px; margin:15px 10px; backdrop-filter: blur(10px); text-align:center; color:#000000;">
              <h3 style="margin:5px 0;">{t['tarot_title']}</h3>
              <h2 style="font-size:1.8em; margin:10px 0;">{tarot_card}</h2>
              <p style="font-size:1.1em;">{tarot_meaning}</p>
            </div>
            """, unsafe_allow_html=True)

        share_text = f"{name_display}\\n{zodiac} + {mbti}\\n{t['combo']}\\n{t['today_title']}: {today}\\n{t['tomorrow_title']}: {tomorrow}\\n\\n{app_url}"
        share_component = f"""
        <div style="text-align:center; margin:4px 0;">
            <button style="background:white; color:#6a11cb; padding:7px 30px; border:none; border-radius:30px; font-size:0.85em; font-weight:bold;" onclick="shareResult()">
              {t["share_btn"]}
            </button>
        </div>
        <script>
        function shareResult() {{
            if (navigator.share) {{
                navigator.share({{title: '2026 운세', text: `{share_text}`, url: '{app_url}'}});
            }} else {{
                navigator.clipboard.writeText(`{share_text}`).then(() => {{alert('복사됐어요! 공유해주세요 😊');}});
            }}
        }}
        </script>
        """
        st_html(share_component, height=60)

    if st.button(t["reset"], use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
