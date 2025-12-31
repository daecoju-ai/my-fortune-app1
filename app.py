import streamlit as st
from datetime import datetime, timedelta
import random
from streamlit.components.v1 import html as st_html

# 다국어 사전
translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 + 오늘/내일 운세 🌟",
        "caption": "완전 무료 😄",
        "ad_title": "💳 렌탈 궁금할 때?",
        "ad_text": "<b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 페이백</b>!",
        "ad_btn": "🔗 보러가기",
        "birth": "### 생년월일 입력",
        "name_placeholder": "이름 입력 (결과에 표시돼요)",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test": "상세 테스트 (16문제)",
        "test_start": "상세 테스트 시작! 하나씩 답해주세요 😊",
        "energy": "에너지 방향 (외향 E vs 내향 I)",
        "info": "정보 수집 (감각 S vs 직관 N)",
        "decision": "결정 방식 (사고 T vs 감정 F)",
        "life": "생활 방식 (판단 J vs 인식 P)",
        "result_btn": "결과 보기!",
        "fortune_btn": "🔮 2026년 운세 보기!",
        "reset": "처음부터 다시 하기",
        "share_btn": "친구에게 결과 공유",
        "water_purifier": "정수기는 다나눔렌탈",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "combo": "최고 조합!",
        "your_fortune": "님의 2026년 운세",
        "footer": "재미로만 봐주세요 😊",
        "zodiacs": {
            "쥐띠": "🐭 활발한 에너지로 새로운 기회 잡아! 돈운 대박, 투자 주의하며 도전하세요 💰",
            "소띠": "🐮 꾸준한 노력의 결실! 안정된 재물운, 가족과 함께하는 행복한 해 🏡",
            "호랑이띠": "🐯 도전과 성공의 해! 큰 프로젝트 성공, 리더십 발휘 대박 🚀",
            "토끼띠": "🐰 안정과 사랑운 최고! 연애/결혼 운 좋음, 마음 편안한 한 해 ❤️",
            "용띠": "🐲 운기 상승! 리더십으로 주변 끌어당김, 승진/사업 성공 가능성 높음 👑",
            "뱀띠": "🐍 직감과 실속의 해! 예상치 못한 재물운, 조용히 기회 잡으세요 🐍",
            "말띠": "🐴 새 도전과 돈 기회! 이동/여행 운 좋음, 적극적으로 나서보세요 ✈️",
            "양띠": "🐑 편안함과 결혼 운! 가정운 최고, 따뜻한 관계 쌓이는 해 🏠",
            "원숭이띠": "🐵 변화와 재능 발휘! 창의력으로 성공, 새로운 분야 도전 좋음 🎨",
            "닭띠": "🐔 노력의 결실 맺는 해! 인정받고 승진 가능, 꾸준함이 관건 🏆",
            "개띠": "🐶 친구와 돈운 상승! 귀인 도움 많음, 네트워킹 적극적으로 🤝",
            "돼지띠": "🐷 여유와 최고 돈운! 재물 대박, 즐기면서 보내는 최고의 해 🐷"
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
        ]
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
        "energy": "Energy Direction (E vs I)",
        "info": "Information Gathering (S vs N)",
        "decision": "Decision Making (T vs F)",
        "life": "Lifestyle (J vs P)",
        "result_btn": "View Result!",
        "fortune_btn": "🔮 View 2026 Fortune!",
        "reset": "Start Over",
        "share_btn": "Share Result with Friends",
        "water_purifier": "Water Purifier is Dananum Rental",
        "zodiac_title": "Zodiac Fortune",
        "mbti_title": "MBTI Traits",
        "saju_title": "Fortune Comment",
        "today_title": "Today's Luck",
        "tomorrow_title": "Tomorrow's Luck",
        "combo": "Best Combo!",
        "your_fortune": "'s 2026 Fortune",
        "footer": "For fun only 😊",
        "zodiacs": {
            "Rat": "🐭 Grab new opportunities with energy! Great money luck 💰",
            "Ox": "🐮 Steady effort pays off! Stable wealth and happy family 🏡",
            "Tiger": "🐯 Challenge and success! Big project success 🚀",
            "Rabbit": "🐰 Stability and love luck best! Great for romance ❤️",
            "Dragon": "🐲 Rising fortune! Leadership shines 👑",
            "Snake": "🐍 Intuition and gain! Unexpected wealth 🐍",
            "Horse": "🐴 New challenges and money chances! Good for travel ✈️",
            "Goat": "🐑 Comfort and marriage luck! Warm relationships 🏠",
            "Monkey": "🐵 Change and talent shine! Creative success 🎨",
            "Rooster": "🐔 Effort rewarded! Recognition and promotion 🏆",
            "Dog": "🐶 Friends and money rise! Helpful people 🤝",
            "Pig": "🐷 Relaxation and best money luck! Wealth jackpot 🐷"
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
        ]
    },
    "zh": {
        "title": "🌟 2026 生肖 + MBTI + 四柱 + 今日/明日运势 🌟",
        "caption": "完全免费 😄",
        "ad_title": "💳 租赁咨询？",
        "ad_text": "<b>다나눔렌탈</b> 合作信用卡 <b>月租0元起</b> + <b>现金返现</b>!",
        "ad_btn": "🔗 查看详情",
        "birth": "### 输入出生日期",
        "name_placeholder": "输入姓名 (结果中显示)",
        "mbti_mode": "MBTI 如何测试？",
        "direct": "直接输入",
        "test": "详细测试 (16题)",
        "test_start": "详细测试开始！请逐题回答 😊",
        "energy": "能量方向 (E vs I)",
        "info": "信息收集 (S vs N)",
        "decision": "决策方式 (T vs F)",
        "life": "生活方式 (J vs P)",
        "result_btn": "查看结果!",
        "fortune_btn": "🔮 查看2026年运势!",
        "reset": "重新开始",
        "share_btn": "分享结果给朋友",
        "water_purifier": "净水器选 다나눔렌탈",
        "zodiac_title": "生肖运势",
        "mbti_title": "MBTI 特点",
        "saju_title": "四柱一句话",
        "today_title": "今日运势",
        "tomorrow_title": "明日运势",
        "combo": "最佳组合!",
        "your_fortune": "的2026年运势",
        "footer": "仅供娱乐 😊",
        "zodiacs": {
            "鼠": "🐭 活力十足抓住新机会！财运大旺，谨慎投资挑战吧 💰",
            "牛": "🐮 努力结出硕果！稳定财运，家庭幸福年 🏡",
            "虎": "🐯 挑战与成功之年！大项目成功，领导力大放光彩 🚀",
            "兔": "🐰 安定与爱情运最佳！恋爱/结婚运佳，心平气和的一年 ❤️",
            "龙": "🐲 运势上升！领导力吸引众人，升职/创业成功可能性高 👑",
            "蛇": "🐍 直觉与实惠之年！意外财运，静待机会 🐍",
            "马": "🐴 新挑战与财运机会！旅行/搬家运好，积极行动 ✈️",
            "羊": "🐑 舒适与结婚运！家庭运最佳，温暖关系年 🏠",
            "猴": "🐵 变化与才能发挥！创意成功，新领域挑战佳 🎨",
            "鸡": "🐔 努力收获之年！获得认可升职可能，坚持是关键 🏆",
            "狗": "🐶 朋友与财运上升！贵人相助，积极人脉 🤝",
            "猪": "🐷 悠闲与最佳财运！财富大旺，享受的一年 🐷"
        },
        "mbtis": {
            "INTJ": "🧠 冷静战略家", "INTP": "💡 创意天才", "ENTJ": "👑 领导者", "ENTP": "⚡ 辩论王",
            "INFJ": "🔮 洞察大师", "INFP": "🎨 感性艺术家", "ENFJ": "🤗 导师型", "ENFP": "🎉 活力传播者",
            "ISTJ": "📋 规则守护者", "ISFJ": "🛡️ 温暖守护者", "ESTJ": "📢 领导者", "ESFJ": "💕 社交达人",
            "ISTP": "🔧 工艺大师", "ISFP": "🌸 感性治愈者", "ESTP": "🏄 冒险家", "ESFP": "🎭 表演者"
        },
        "saju_msgs": [
            "木气旺 → 成长发展之年! 🌱", "火气旺 → 热情爆发! ❤️",
            "土气旺 → 安定与财运 💰", "金气旺 → 决断力强! 👔",
            "水气旺 → 智慧与流动 🌊", "五行平衡 → 幸福一年 ✨",
            "阳气旺 → 挑战成功 🚀", "阴气旺 → 内省之年 😌"
        ],
        "daily_msgs": [
            "财运好！小投资也有收益 💰", "恋爱运最佳！适合告白或约会 ❤️",
            "注意健康！避免过度劳累 😴", "整体大吉！好事连连 🌟",
            "人际运好！可能遇贵人 🤝", "学业/工作运最佳！集中力超强 📚",
            "旅行运好！突然出发也没问题 ✈️", "愉快的一天！笑容满满 😄"
        ]
    }
}

# 세션 상태 초기화
if "lang" not in st.session_state:
    st.session_state.lang = "ko"

# 언어 선택 라디오 (고정 텍스트)
st.session_state.lang = st.radio("언어 / Language / 语言", ["ko", "en", "zh"], index=["ko", "en", "zh"].index(st.session_state.lang), horizontal=True)

# t 정의
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

st.set_page_config(page_title=t["title"], layout="centered")

# 세션 상태 초기화
if "mbti" not in st.session_state: st.session_state.mbti = None
if "result_shown" not in st.session_state: st.session_state.result_shown = False
if "name" not in st.session_state: st.session_state.name = ""
if "year" not in st.session_state: st.session_state.year = 2005
if "month" not in st.session_state: st.session_state.month = 1
if "day" not in st.session_state: st.session_state.day = 1

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
    st.session_state.year = col1.number_input("Year" if st.session_state.lang in ["en", "zh"] else "년", 1900, 2030, st.session_state.year, step=1)
    st.session_state.month = col2.number_input("Month" if st.session_state.lang in ["en", "zh"] else "월", 1, 12, st.session_state.month, step=1)
    st.session_state.day = col3.number_input("Day" if st.session_state.lang in ["en", "zh"] else "일", 1, 31, st.session_state.day, step=1)

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
        if st.radio("1. 주말에 친구들이 갑자기 '놀자!' 하면?" if st.session_state.lang == "ko" else "1. Friends suddenly say 'Let's hang out!' on weekend?" if st.session_state.lang == "en" else "1. 周末朋友突然说'一起玩吧!'？", ["와 좋아! 바로 나감 (E)", "집에서 쉬고 싶어... (I)"] if st.session_state.lang == "ko" else ["Yes! Go out right away (E)", "Want to stay home... (I)"] if st.session_state.lang == "en" else ["好啊！马上出门 (E)", "想在家休息... (I)"], key="q1") == ("와 좋아! 바로 나감 (E)" if st.session_state.lang == "ko" else "Yes! Go out right away (E)" if st.session_state.lang == "en" else "好啊！马上出门 (E)"): e_i += 1

        if st.radio("2. 모임에서 처음 본 사람들과 대화하는 거?" if st.session_state.lang == "ko" else "2. Talking to strangers at a gathering?" if st.session_state.lang == "en" else "2. 和聚会中新认识的人聊天？", ["재밌고 신나! (E)", "조금 피곤하고 부담스러워 (I)"] if st.session_state.lang == "ko" else ["Fun and exciting! (E)", "A bit tiring and burdensome (I)"] if st.session_state.lang == "en" else ["有趣又兴奋! (E)", "有点累和负担 (I)"], key="q2") == ("재밌고 신나! (E)" if st.session_state.lang == "ko" else "Fun and exciting! (E)" if st.session_state.lang == "en" else "有趣又兴奋! (E)"): e_i += 1

        if st.radio("3. 하루 종일 사람 만난 후에?" if st.session_state.lang == "ko" else "3. After meeting people all day?" if st.session_state.lang == "en" else "3. 一整天见人之后？", ["아직 에너지 넘쳐! (E)", "완전 지쳐서 혼자 있고 싶어 (I)"] if st.session_state.lang == "ko" else ["Still full of energy! (E)", "Totally exhausted, want to be alone (I)"] if st.session_state.lang == "en" else ["还精力充沛! (E)", "完全累了，想一个人待着 (I)"], key="q3") == ("아직 에너지 넘쳐! (E)" if st.session_state.lang == "ko" else "Still full of energy! (E)" if st.session_state.lang == "en" else "还精力充沛! (E)"): e_i += 1

        if st.radio("4. 생각이 떠오르면?" if st.session_state.lang == "ko" else "4. When a thought comes to mind?" if st.session_state.lang == "en" else "4. 想到事情时？", ["바로 말로 풀어냄 (E)", "머릿속에서 먼저 정리함 (I)"] if st.session_state.lang == "ko" else ["Express thoughts out loud (E)", "Organize in head first (I)"] if st.session_state.lang == "en" else ["马上说出来 (E)", "先在脑中整理 (I)"], key="q4") == ("바로 말로 풀어냄 (E)" if st.session_state.lang == "ko" else "Express thoughts out loud (E)" if st.session_state.lang == "en" else "马上说出来 (E)"): e_i += 1

        st.subheader(t["info"])
        if st.radio("5. 새로운 카페 가면 뭐가 먼저 눈에 들어?" if st.session_state.lang == "ko" else "5. What catches your eye first in a new cafe?" if st.session_state.lang == "en" else "5. 新咖啡店先注意到什么？", ["메뉴판 가격과 메뉴 (S)", "분위기, 인테리어, 컨셉 (N)"] if st.session_state.lang == "ko" else ["Menu prices and items (S)", "Atmosphere, interior, concept (N)"] if st.session_state.lang == "en" else ["菜单价格和菜品 (S)", "氛围、装修、概念 (N)"], key="q5") == ("메뉴판 가격과 메뉴 (S)" if st.session_state.lang == "ko" else "Menu prices and items (S)" if st.session_state.lang == "en" else "菜单价格和菜品 (S)"): s_n += 1

        if st.radio("6. 친구가 고민 상담하면?" if st.session_state.lang == "ko" else "6. When friend shares worries?" if st.session_state.lang == "en" else "6. 朋友倾诉烦恼时？", ["지금 상황과 사실 위주로 들어줌 (S)", "가능성과 미래 방향으로 생각함 (N)"] if st.session_state.lang == "ko" else ["Listen to current facts (S)", "Think about possibilities and future (N)"] if st.session_state.lang == "en" else ["听当前事实 (S)", "想可能性和未来 (N)"], key="q6") == ("지금 상황과 사실 위주로 들어줌 (S)" if st.session_state.lang == "ko" else "Listen to current facts (S)" if st.session_state.lang == "en" else "听当前事实 (S)"): s_n += 1

        if st.radio("7. 책이나 영화 볼 때?" if st.session_state.lang == "ko" else "7. When reading book or watching movie?" if st.session_state.lang == "en" else "7. 看书或电影时？", ["스토리와 디테일에 집중 (S)", "상징과 숨은 의미 찾는 재미 (N)"] if st.session_state.lang == "ko" else ["Focus on story and details (S)", "Enjoy finding symbols and hidden meanings (N)"] if st.session_state.lang == "en" else ["关注故事和细节 (S)", "享受寻找象征和隐藏含义 (N)"], key="q7") == ("스토리와 디테일에 집중 (S)" if st.session_state.lang == "ko" else "Focus on story and details (S)" if st.session_state.lang == "en" else "关注故事和细节 (S)"): s_n += 1

        if st.radio("8. 쇼핑할 때?" if st.session_state.lang == "ko" else "8. When shopping?" if st.session_state.lang == "en" else "8. 购物时？", ["필요한 거 보고 바로 사 (S)", "이거 사면 나중에 뭐랑 입히지? 상상함 (N)"] if st.session_state.lang == "ko" else ["Buy what I need right away (S)", "Imagine what to wear it with later (N)"] if st.session_state.lang == "en" else ["看到需要的马上买 (S)", "想象以后怎么搭配 (N)"], key="q8") == ("필요한 거 보고 바로 사 (S)" if st.session_state.lang == "ko" else "Buy what I need right away (S)" if st.session_state.lang == "en" else "看到需要的马上买 (S)"): s_n += 1

        st.subheader(t["decision"])
        if st.radio("9. 친구가 늦어서 화날 때?" if st.session_state.lang == "ko" else "9. When friend is late and you're angry?" if st.session_state.lang == "en" else "9. 朋友迟到生气时？", ["늦었으면 늦었다고 솔직히 말함 (T)", "기분 상할까 봐 부드럽게 말함 (F)"] if st.session_state.lang == "ko" else ["Say honestly they're late (T)", "Say gently to not hurt feelings (F)"] if st.session_state.lang == "en" else ["直接说迟到了 (T)", "温柔地说怕伤感情 (F)"], key="q9") == ("늦었으면 늦었다고 솔직히 말함 (T)" if st.session_state.lang == "ko" else "Say honestly they're late (T)" if st.session_state.lang == "en" else "直接说迟到了 (T)"): t_f += 1

        if st.radio("10. 팀 프로젝트에서 의견 충돌 시?" if st.session_state.lang == "ko" else "10. In team project when opinions clash?" if st.session_state.lang == "en" else "10. 团队项目意见冲突时？", ["논리적으로 누가 맞는지 따짐 (T)", "다른 사람 기분 상하지 않게 조율 (F)"] if st.session_state.lang == "ko" else ["Argue logically who's right (T)", "Mediate to not hurt feelings (F)"] if st.session_state.lang == "en" else ["逻辑上争谁对 (T)", "调解不伤感情 (F)"], key="q10") == ("논리적으로 누가 맞는지 따짐 (T)" if st.session_state.lang == "ko" else "Argue logically who's right (T)" if st.session_state.lang == "en" else "逻辑上争谁对 (T)"): t_f += 1

        if st.radio("11. 누가 울면서 상담하면?" if st.session_state.lang == "ko" else "11. When someone cries while consulting?" if st.session_state.lang == "en" else "11. 有人哭着倾诉时？", ["문제 해결 방법 조언해줌 (T)", "일단 공감하고 들어줌 (F)"] if st.session_state.lang == "ko" else ["Give advice on solving problem (T)", "First empathize and listen (F)"] if st.session_state.lang == "en" else ["给出解决问题建议 (T)", "先共情倾听 (F)"], key="q11") == ("일단 공감하고 들어줌 (F)" if st.session_state.lang == "ko" else "First empathize and listen (F)" if st.session_state.lang == "en" else "先共情倾听 (F)"): t_f += 1

        if st.radio("12. 거짓말 탐지 시?" if st.session_state.lang == "ko" else "12. When detecting a lie?" if st.session_state.lang == "en" else "12. 发现谎言时？", ["바로 지적함 (T)", "상처 줄까 봐 넘김 (F)"] if st.session_state.lang == "ko" else ["Point out immediately (T)", "Let it go to not hurt (F)"] if st.session_state.lang == "en" else ["马上指出 (T)", "怕伤人就忽略 (F)"], key="q12") == ("바로 지적함 (T)" if st.session_state.lang == "ko" else "Point out immediately (T)" if st.session_state.lang == "en" else "马上指出 (T)"): t_f += 1

        st.subheader(t["life"])
        if st.radio("13. 여행 갈 때?" if st.session_state.lang == "ko" else "13. When planning a trip?" if st.session_state.lang == "en" else "13. 旅行时？", ["일정 꽉꽉 짜서 효율적으로 (J)", "그때그때 기분 따라 즉흥적으로 (P)"] if st.session_state.lang == "ko" else ["Plan schedule tightly for efficiency (J)", "Go with the flow spontaneously (P)"] if st.session_state.lang == "en" else ["计划满满高效 (J)", "随心情即兴 (P)"], key="q13") == ("일정 꽉꽉 짜서 효율적으로 (J)" if st.session_state.lang == "ko" else "Plan schedule tightly for efficiency (J)" if st.session_state.lang == "en" else "计划满满高效 (J)"): j_p += 1

        if st.radio("14. 숙제나 과제 마감 앞두고?" if st.session_state.lang == "ko" else "14. Before assignment deadline?" if st.session_state.lang == "en" else "14. 作业截止前？", ["미리미리 끝냄 (J)", "마감 직전에 몰아서 함 (P)"] if st.session_state.lang == "ko" else ["Finish early in advance (J)", "Do it all at deadline (P)"] if st.session_state.lang == "en" else ["提前完成 (J)", "截止前突击 (P)"], key="q14") == ("미리미리 끝냄 (J)" if st.session_state.lang == "ko" else "Finish early in advance (J)" if st.session_state.lang == "en" else "提前完成 (J)"): j_p += 1

        if st.radio("15. 방 정리할 때?" if st.session_state.lang == "ko" else "15. When cleaning room?" if st.session_state.lang == "en" else "15. 整理房间时？", ["정해진 기준으로 깔끔히 (J)", "대충 써도 괜찮아 (P)"] if st.session_state.lang == "ko" else ["Organize neatly by standard (J)", "It's okay if messy (P)"] if st.session_state.lang == "en" else ["按标准整洁 (J)", "乱点也没关系 (P)"], key="q15") == ("정해진 기준으로 깔끔히 (J)" if st.session_state.lang == "ko" else "Organize neatly by standard (J)" if st.session_state.lang == "en" else "按标准整洁 (J)"): j_p += 1

        if st.radio("16. 선택해야 할 때?" if st.session_state.lang == "ko" else "16. When needing to choose?" if st.session_state.lang == "en" else "16. 需要选择时？", ["빨리 결정하고 넘김 (J)", "옵션 더 알아보고 싶어 (P)"] if st.session_state.lang == "ko" else ["Decide quickly and move on (J)", "Want to explore more options (P)"] if st.session_state.lang == "en" else ["快速决定 (J)", "想多看选项 (P)"], key="q16") == ("빨리 결정하고 넘김 (J)" if st.session_state.lang == "ko" else "Decide quickly and move on (J)" if st.session_state.lang == "en" else "快速决定 (J)"): j_p += 1

        if st.button(t["result_btn"], use_container_width=True):
            ei = "E" if e_i >= 3 else "I"
            sn = "S" if s_n >= 3 else "N"
            tf = "T" if t_f >= 3 else "F"
            jp = "J" if j_p >= 3 else "P"
            st.session_state.mbti = ei + sn + tf + jp
            st.session_state.result_shown = True
            st.rerun()

# 결과 카드
if st.session_state.result_shown:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(st.session_state.year)
    if zodiac:
        score = 90
        saju = get_saju(st.session_state.year, st.session_state.month, st.session_state.day)
        today = get_daily_fortune(zodiac, 0)
        tomorrow = get_daily_fortune(zodiac, 1)
        zodiac_emoji = Z[zodiac].split(' ',1)[0]
        zodiac_desc = Z[zodiac].split(' ',1)[1] if ' ' in Z[zodiac] else ""
        mbti_emoji = M[mbti].split(' ',1)[0]
        mbti_desc = M[mbti].split(' ',1)[1] if ' ' in M[mbti] else ""
        name_text = f"{st.session_state.name}{t['your_fortune']}" if st.session_state.name else t["title"]

        st.markdown(f"""
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
        <div style="background:linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
                     width:100vw; height:100vh; margin:-80px -20px 0 -20px; padding:10px 10px;
                     box-sizing:border-box; display:flex; flex-direction:column; color:white; text-align:center;
                     font-family:'Noto Sans KR', sans-serif;">
          <div style="position:absolute; top:10px; right:10px; font-size:0.85em; font-weight:bold; color:#ffd700; text-shadow: 1px 1px 3px rgba(0,0,0,0.6); background:rgba(255,255,255,0.2); padding:8px 10px; border-radius:15px; max-width:150px; line-height:1.3;">
            💧 <b>정수기 렌탈 대박!</b><br>
            제휴카드면 <b>월 0원부터</b>!<br>
            설치 당일 <b>최대 50만원</b><br>지원 + 사은품 듬뿍 ✨
          </div>
          <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
            <h1 style="font-size:1.8em; margin:5px 0; font-family:'Playfair Display', serif; text-shadow: 2px 2px 10px rgba(0,0,0,0.3);">{name_text}</h1>
            <h2 style="font-size:1.8em; margin:10px 0;">
              <span style="font-size:1.5em;">{zodiac_emoji}</span> {zodiac} + <span style="font-size:1.5em;">{mbti_emoji}</span> {mbti}
            </h2>
            <h3 style="font-size:1.5em; margin:10px 0; color:#fff; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);">{t['combo']}</h3>
            <h1 style="font-size:4.0em; margin:15px 0; color:#ffd700; text-shadow: 3px 3px 15px rgba(0,0,0,0.6);">{score}점</h1>
          </div>
          <div style="background:rgba(255,255,255,0.25); border-radius:25px; padding:12px; margin:0 5px; backdrop-filter: blur(10px);">
            <p style="font-size:0.95em; margin:6px 0;"><b>{t['zodiac_title']}</b>: {zodiac_desc}</p>
            <p style="font-size:0.95em; margin:6px 0;"><b>{t['mbti_title']}</b>: {mbti_desc}</p>
            <p style="font-size:0.95em; margin:6px 0;"><b>{t['saju_title']}</b>: {saju}</p>
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.5); margin:8px 0;">
            <p style="font-size:1.0em; margin:6px 0;"><b>{t['today_title']}</b>: {today}</p>
            <p style="font-size:1.0em; margin:6px 0;"><b>{t['tomorrow_title']}</b>: {tomorrow}</p>
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.5); margin:8px 0;">
            <p style="font-size:1.0em; margin:6px 0; color:#ffd700;"><b>2026 전체 운세</b>: 성장과 재물이 함께하는 최고의 해! 대박 기운 가득 ✨</p>
            <p style="font-size:1.0em; margin:6px 0;"><b>조합 한 마디</b>: {zodiac}의 노력과 {mbti}의 따뜻함으로 모두를 이끄는 리더가 될 거예요!</p>
            <p style="font-size:1.0em; margin:6px 0;"><b>럭키 컬러</b>: 골드 💛 | <b>럭키 아이템</b>: 황금 액세서리 or 노란 지갑</p>
            <p style="font-size:0.9em; margin:6px 0; font-style:italic;">"90점: 작은 행동 하나가 큰 행운으로 돌아올 해! 자신을 믿고 도전하세요 🚀"</p>
            <p style="font-size:0.9em; margin:6px 0;">💡 <b>팁</b>: 이번 달 새로운 사람 만나는 기회 많아요. 적극적으로 나서보세요!</p>
          </div>
          <p style="font-size:0.7em; opacity:0.8; margin:10px 0;">{app_url}</p>
        </div>
        """, unsafe_allow_html=True)

        st.balloons()
        st.snow()

        share_text = f"{name_text}\\n{zodiac} + {mbti}\\n{t['combo']}\\n{score}점!\\n{t['today_title']}: {today}\\n{t['tomorrow_title']}: {tomorrow}\\n\\n{app_url}"
        share_component = f"""
        <div style="text-align:center; margin:15px 0;">
            <button style="background:white; color:#6a11cb; padding:10px 40px; border:none; border-radius:30px; font-size:1.1em; font-weight:bold;" onclick="shareResult()">
              {t["share_btn"]}
            </button>
        </div>
        <script>
        function shareResult() {{
            if (navigator.share) {{
                navigator.share({{
                    title: '내 2026년 운세 결과',
                    text: `{share_text}`,
                    url: '{app_url}'
                }});
            }} else {{
                navigator.clipboard.writeText(`{share_text}`).then(() => {{
                    alert('운세 결과가 복사되었습니다! 카톡, 라인, X 등에 붙여넣기 해서 공유해주세요 😊');
                }});
            }}
        }}
        </script>
        """
        st_html(share_component, height=100)

    if st.button(t["reset"], use_container_width=True):
        st.session_state.clear()
        st.rerun()

# footer (항상 표시)
st.caption(t["footer"])
