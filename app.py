import streamlit as st
from datetime import datetime, timedelta
import random
from streamlit.components.v1 import html as st_html

# 다국어 사전 (한국어 / English / 中文)
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
        "energy": "에너지 방향",
        "info": "정보 수집",
        "decision": "결정 방식",
        "life": "생활 방식",
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
        "energy": "Energy Direction",
        "info": "Information Gathering",
        "decision": "Decision Making",
        "life": "Lifestyle",
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
        "energy": "能量方向",
        "info": "信息收集",
        "decision": "决策方式",
        "life": "生活方式",
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

# 언어 선택 라디오
st.session_state.lang = st.radio("언어 / Language / 语言", ["ko", "en", "zh"], index=["ko", "en", "zh"].index(st.session_state.lang), horizontal=True)

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

# 초기 화면 (생략 - 이전과 동일)

# 결과 카드 (광고 위치 변경 + 스크롤 가능 + 3언어 지원)
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
                     width:100vw; min-height:100vh; margin:-80px -20px 0 -20px; padding:20px 15px 100px 15px;
                     box-sizing:border-box; color:white; text-align:center; overflow-y:auto;
                     font-family:'Noto Sans KR', sans-serif;">
          <div style="display:flex; flex-direction:column; justify-content:flex-start;">
            <h1 style="font-size:2.0em; margin:10px 0; font-family:'Playfair Display', serif; text-shadow: 2px 2px 10px rgba(0,0,0,0.3);">{name_text}</h1>
            <h2 style="font-size:2.0em; margin:20px 0;">
              <span style="font-size:1.5em;">{zodiac_emoji}</span> {zodiac} + <span style="font-size:1.5em;">{mbti_emoji}</span> {mbti}
            </h2>
            <h3 style="font-size:1.7em; margin:30px 0; color:#fff; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);">{t['combo']}</h3>
            <h1 style="font-size:4.5em; margin:30px 0; color:#ffd700; text-shadow: 3px 3px 15px rgba(0,0,0,0.6);">{score}점</h1>

            <!-- 광고: 최고 조합 아래로 이동 -->
            <div style="font-size:0.9em; font-weight:bold; color:#ffd700; text-shadow: 1px 1px 3px rgba(0,0,0,0.6); background:rgba(255,255,255,0.25); padding:12px 15px; border-radius:20px; margin:20px 40px; line-height:1.4; backdrop-filter: blur(5px);">
              💧 <b>정수기 렌탈 대박!</b><br>
              제휴카드면 <b>월 0원부터</b>!<br>
              설치 당일 <b>최대 50만원 지원</b> + 사은품 듬뿍 ✨
            </div>

            <div style="background:rgba(255,255,255,0.25); border-radius:25px; padding:20px; margin:20px 10px; backdrop-filter: blur(10px);">
              <p style="font-size:1.1em; margin:10px 0;"><b>{t['zodiac_title']}</b>: {zodiac_desc}</p>
              <p style="font-size:1.1em; margin:10px 0;"><b>{t['mbti_title']}</b>: {mbti_desc}</p>
              <p style="font-size:1.1em; margin:10px 0;"><b>{t['saju_title']}</b>: {saju}</p>
              <hr style="border:none; border-top:1px solid rgba(255,255,255,0.5); margin:15px 0;">
              <p style="font-size:1.2em; margin:10px 0;"><b>{t['today_title']}</b>: {today}</p>
              <p style="font-size:1.2em; margin:10px 0;"><b>{t['tomorrow_title']}</b>: {tomorrow}</p>
              <hr style="border:none; border-top:1px solid rgba(255,255,255,0.5); margin:15px 0;">
              <p style="font-size:1.2em; margin:10px 0; color:#ffd700;"><b>2026 전체 운세</b>: 성장과 재물이 함께하는 최고의 해! 대박 기운 가득 ✨</p>
              <p style="font-size:1.1em; margin:10px 0;"><b>조합 한 마디</b>: {zodiac}의 노력과 {mbti}의 따뜻함으로 모두를 이끄는 리더가 될 거예요!</p>
              <p style="font-size:1.1em; margin:10px 0;"><b>럭키 컬러</b>: 골드 💛 | <b>럭키 아이템</b>: 황금 액세서리 or 노란 지갑</p>
              <p style="font-size:1.0em; margin:10px 0; font-style:italic;">"90점: 작은 행동 하나가 큰 행운으로 돌아올 해! 자신을 믿고 도전하세요 🚀"</p>
              <p style="font-size:1.0em; margin:10px 0;">💡 <b>팁</b>: 이번 달 새로운 사람 만나는 기회 많아요. 적극적으로 나서보세요!</p>
            </div>

            <p style="font-size:0.8em; opacity:0.8; margin:20px 0;">{app_url}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.balloons()
        st.snow()

        # 공유 버튼
        share_text = f"{name_text}\\n{zodiac} + {mbti}\\n{t['combo']}\\n{score}점!\\n{t['today_title']}: {today}\\n{t['tomorrow_title']}: {tomorrow}\\n\\n{app_url}"
        share_component = f"""
        <div style="text-align:center; margin:20px 0;">
            <button style="background:white; color:#6a11cb; padding:15px 50px; border:none; border-radius:30px; font-size:1.2em; font-weight:bold;" onclick="shareResult()">
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
        st_html(share_component, height=120)

    if st.button(t["reset"], use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
