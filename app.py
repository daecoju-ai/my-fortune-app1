import streamlit as st
from datetime import datetime, timedelta
import hashlib

# ────────────────────────────────────────────────
#                  3개 언어 번역 데이터
# ────────────────────────────────────────────────

translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 운세 🌟",
        "caption": "완전 무료 😄",
        "lang_select": "언어 선택",
        "birth": "### 생년월일 입력",
        "year": "년",
        "month": "월",
        "day": "일",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test": "상세 테스트 (16문제)",
        "test_start": "상세 테스트 시작! 😊",
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
        "daily_title": "🌞 오늘 & 내일의 운세 (매일 달라져요!)",
        "today": "오늘",
        "tomorrow": "내일",
        "footer": "재미로만 봐주세요 😊",
        "best_combo": "최고 조합!",
        "fortune_score": "운세 점수",
        "stable": "안정적!",
    },
    "en": {
        "title": "🌟 2026 Zodiac + MBTI + Saju Fortune 🌟",
        "caption": "Completely Free 😄",
        "lang_select": "Select Language",
        "birth": "### Enter Birth Date",
        "year": "Year",
        "month": "Month",
        "day": "Day",
        "mbti_mode": "How to get MBTI?",
        "direct": "Enter directly",
        "test": "Detailed Test (16 questions)",
        "test_start": "Start detailed test! 😊",
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
        "daily_title": "🌞 Today's & Tomorrow's Fortune (Changes daily!)",
        "today": "Today",
        "tomorrow": "Tomorrow",
        "footer": "Just for fun 😊",
        "best_combo": "Best Combo!",
        "fortune_score": "Fortune Score",
        "stable": "Stable!",
    },
    "zh": {
        "title": "🌟 2026年 生肖 + MBTI + 四柱运势 🌟",
        "caption": "完全免费 😄",
        "lang_select": "选择语言",
        "birth": "### 输入出生日期",
        "year": "年",
        "month": "月",
        "day": "日",
        "mbti_mode": "MBTI怎么选？",
        "direct": "直接输入",
        "test": "详细测试 (16题)",
        "test_start": "开始详细测试！😊",
        "energy": "能量方向",
        "info": "信息收集",
        "decision": "决策方式",
        "life": "生活方式",
        "result_btn": "查看结果！",
        "fortune_btn": "🔮 查看2026年运势！",
        "reset": "重新开始",
        "zodiac_title": "**生肖运势**",
        "mbti_title": "**MBTI特点**",
        "saju_title": "**四柱一句话**",
        "daily_title": "🌞 今日 & 明日运势 (每天不同！)",
        "today": "今天",
        "tomorrow": "明天",
        "footer": "仅供娱乐 😊",
        "best_combo": "最佳组合！",
        "fortune_score": "运势分数",
        "stable": "非常稳定！",
    }
}

# 12간지 설명 (3개 언어)
zodiacs = {
    "ko": {
        "Rat": "🐭 쥐띠 - 활발·성장, 돈↑",
        "Ox": "🐮 소띠 - 노력 결실",
        "Tiger": "🐯 호랑이띠 - 도전 성공, 돈 대박",
        "Rabbit": "🐰 토끼띠 - 안정·사랑 운",
        "Dragon": "🐲 용띠 - 운↑ 리더십",
        "Snake": "🐍 뱀띠 - 실속·직감",
        "Horse": "🐴 말띠 - 새 도전·돈 기회",
        "Goat": "🐑 양띠 - 편안+결혼 운",
        "Monkey": "🐵 원숭이띠 - 변화·재능",
        "Rooster": "🐔 닭띠 - 노력 결과",
        "Dog": "🐶 개띠 - 친구·돈↑",
        "Pig": "🐷 돼지띠 - 여유·돈 최고"
    },
    "en": {
        "Rat": "🐭 Rat - Active growth, money ↑",
        "Ox": "🐮 Ox - Effort pays off",
        "Tiger": "🐯 Tiger - Challenge success, big money",
        "Rabbit": "🐰 Rabbit - Stability & love luck",
        "Dragon": "🐲 Dragon - Luck ↑ leadership",
        "Snake": "🐍 Snake - Practical & intuition",
        "Horse": "🐴 Horse - New challenge & money chance",
        "Goat": "🐑 Goat - Comfort + marriage luck",
        "Monkey": "🐵 Monkey - Change & talent",
        "Rooster": "🐔 Rooster - Effort brings results",
        "Dog": "🐶 Dog - Friends & money ↑",
        "Pig": "🐷 Pig - Relaxed & best money luck"
    },
    "zh": {
        "Rat": "🐭 鼠 - 活跃成长，财运上升",
        "Ox": "🐮 牛 - 努力有回报",
        "Tiger": "🐯 虎 - 挑战成功，大财",
        "Rabbit": "🐰 兔 - 稳定+爱情运",
        "Dragon": "🐲 龙 - 运势大涨+领导力",
        "Snake": "🐍 蛇 - 务实+直觉强",
        "Horse": "🐴 马 - 新挑战+赚钱机会",
        "Goat": "🐑 羊 - 舒适+婚姻运",
        "Monkey": "🐵 猴 - 变化+才华",
        "Rooster": "🐔 鸡 - 努力见成果",
        "Dog": "🐶 狗 - 朋友运+财运",
        "Pig": "🐷 猪 - 悠闲+财运最佳"
    }
}

# MBTI 특징 (3개 언어, 간략 버전)
mbtis = {
    "ko": {
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
    "en": {
        "INTJ": "🧠 Strategic Mastermind",
        "INTP": "💡 Innovative Thinker",
        "ENTJ": "👑 Commander",
        "ENTP": "⚡ Debater",
        "INFJ": "🔮 Insightful Counselor",
        "INFP": "🎨 Idealistic Dreamer",
        "ENFJ": "🤗 Charismatic Teacher",
        "ENFP": "🎉 Enthusiastic Campaigner",
        "ISTJ": "📋 Responsible Inspector",
        "ISFJ": "🛡️ Caring Protector",
        "ESTJ": "📢 Efficient Executive",
        "ESFJ": "💕 Supportive Host",
        "ISTP": "🔧 Practical Craftsman",
        "ISFP": "🌸 Sensitive Artist",
        "ESTP": "🏄 Bold Adventurer",
        "ESFP": "🎭 Entertaining Performer"
    },
    "zh": {
        "INTJ": "🧠 冷静战略家",
        "INTP": "💡 创意天才",
        "ENTJ": "👑 领袖",
        "ENTP": "⚡ 辩论王",
        "INFJ": "🔮 心灵大师",
        "INFP": "🎨 感性艺术家",
        "ENFJ": "🤗 万人导师",
        "ENFP": "🎉 人类维生素",
        "ISTJ": "📋 规则守护者",
        "ISFJ": "🛡️ 温暖守护者",
        "ESTJ": "📢 高效领导",
        "ESFJ": "💕 气氛制造者",
        "ISTP": "🔧 修理大师",
        "ISFP": "🌸 感性治疗师",
        "ESTP": "🏄 冒险王",
        "ESFP": "🎭 派对主角"
    }
}

# 사주 한마디 (3개 언어)
saju_msgs = {
    "ko": [
        "목(木) 기운 강함 → 성장과 발전의 해! 🌱",
        "화(火) 기운 강함 → 열정 폭발! ❤️",
        "토(土) 기운 강함 → 안정과 재물운 💰",
        "금(金) 기운 강함 → 결단력 좋음! 👔",
        "수(水) 기운 강함 → 지혜와 흐름 🌊",
        "오행 균형 → 행복한 한 해 ✨",
        "양기 강함 → 도전 성공 🚀",
        "음기 강함 → 내면 성찰 😌"
    ],
    "en": [
        "Strong Wood → Year of growth & development! 🌱",
        "Strong Fire → Passion explosion! ❤️",
        "Strong Earth → Stability & wealth 💰",
        "Strong Metal → Sharp decisiveness! 👔",
        "Strong Water → Wisdom & flow 🌊",
        "Balanced elements → Happy year ✨",
        "Strong Yang → Challenges to success 🚀",
        "Strong Yin → Deep inner reflection 😌"
    ],
    "zh": [
        "木气旺盛 → 成长与发展之年！🌱",
        "火气旺盛 → 热情爆发！❤️",
        "土气旺盛 → 稳定与财运 💰",
        "金气旺盛 → 决断力优秀！👔",
        "水气旺盛 → 智慧与流动 🌊",
        "五行平衡 → 幸福的一年 ✨",
        "阳气旺盛 → 挑战成功 🚀",
        "阴气旺盛 → 内心反省 😌"
    ]
}

# 오늘/내일 운세 메시지 (각 40개 예시, 실제로는 더 늘려도 좋음)
daily_messages = {
    "ko": [
        "에너지 충만! 새로운 시작 딱 좋은 날 🔥",
        "인내가 필요한 하루… 작은 성취가 쌓이는 날 🐢",
        "뜻밖의 인연이 생길 수 있는 날 💞",
        "재물운 상승! 지갑이 두둑해질 조짐 💰",
        "집중력 최고봉! 중요한 일 마무리 GO 📊",
        "조금 피곤할 수 있음… 휴식 필수 😴",
        "변화의 바람이 부는 날! 새로운 시도 OK 🌬️",
        "주변 사람들과의 소통이 중요해지는 날 🗣️",
        "직감이 예리해지는 날! 믿고 따라가세요 🔮",
        "경쟁에서 이길 운! 자신감 UP 💪",
        "안정감이 주는 하루… 천천히 가도 좋아 🏡",
        "창의력 폭발! 아이디어 쏟아지는 날 🎨",
        "감정 기복 주의… 차분함 유지하기 🙏",
        "도움이 필요한 순간에 손 내밀어줄 사람이 나타남 🤝",
        "작은 행운이 연속으로! 미소 잊지 마세요 😊",
        "결단력이 빛나는 날! 망설이지 말고 GO! ⚡",
        "내면 성찰의 시간… 조용히 생각 정리하기 🧘",
        "활동적인 하루! 몸을 움직이면 기분 UP 🏃",
        "금전 흐름이 좋아지는 날! 투자 타이밍? 🤔",
        "감사하는 마음이 더 큰 복을 부르는 날 🙌",
        # 연애운
        "오늘 눈 맞춘 사람이 운명일지도…? 설렘 주의 💘",
        "고백 타이밍 최고! 용기 내 볼까? 😳",
        "상대방이 먼저 연락 올 확률 업↑ 📱💕",
        "작은 스킨십에도 심쿵! 오늘은 살짝 가까이 가봐 ❤️",
        "오랜 짝사랑이 조금씩 움직이기 시작하는 날 🌸",
        "연애 대화가 술술 풀리는 마법 같은 하루 💬",
        "오늘은 '너무 좋아'라는 말이 저절로 나올 거야 😍",
        "연애운이 반짝! 소개팅이나 만남 잡아보는 건 어때? ✨",
        "서로의 마음이 가까워지는 순간이 올지도… 기대돼요 💞",
        "애매했던 관계에 명확한 신호가 올 수 있는 날 🔍"
        # ... 20개 더 추가 가능
    ],
    "en": [
        "Energy full! Perfect day to start something new 🔥",
        "Patience needed… Small achievements building up 🐢",
        "Unexpected connections might happen 💞",
        "Money luck rising! Unexpected cash coming? 💸",
        "Super focused today! Finish important tasks 📊",
        "A bit tired… Rest is essential 😴",
        "Wind of change! Try something new 🌬️",
        "Communication becomes key today 🗣️",
        "Your intuition is spot on! Trust it 🔮",
        "Shine in competition! Confidence max 💪",
        # ... (영어 40개 버전으로 확장)
        "Eye contact today might be fate… Heart-fluttering alert 💘",
        "Perfect timing for confession! Go for it? 😳",
        "High chance your crush messages you first 📱💕",
        # ...
    ],
    "zh": [
        "能量满满！非常适合新开始的一天 🔥",
        "需要耐心…小成就正在积累 🐢",
        "可能有意外缘分出现 💞",
        "财运上升！钱包变厚 💰",
        "专注力巅峰！今天完成大事 📊",
        "有点累…休息是必须的 😴",
        "变化之风吹来！尝试新事物 🌬️",
        "沟通成为关键的一天 🗣️",
        "直觉很准！相信你的直觉 🔮",
        "在竞争中闪耀！自信爆棚 💪",
        # 연애운
        "今天眼神对上的人可能是缘分…心动警告 💘",
        "表白最佳时机！要不要试试？😳",
        "对方主动联系的概率很高 📱💕",
        # ...
    ]
}

# ────────────────────────────────────────────────
#                   함수들
# ────────────────────────────────────────────────

def get_zodiac(y):
    z_list = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", 
              "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
    return z_list[(y - 4) % 12] if 1900 <= y <= 2030 else None

def get_saju(year, month, day, lang):
    total = year + month + day
    index = total % len(saju_msgs[lang])
    return saju_msgs[lang][index]

def get_daily_index(year, month, day, target_date):
    combined = f"{year}{month:02d}{day:02d}{target_date.year}{target_date.month:02d}{target_date.day:02d}"
    hash_object = hashlib.sha256(combined.encode())
    return int(hash_object.hexdigest(), 16) % len(daily_messages[lang])

# ────────────────────────────────────────────────
#                   앱 시작
# ────────────────────────────────────────────────

if "lang" not in st.session_state:
    st.session_state.lang = "ko"

lang_options = {"한국어": "ko", "English": "en", "中文": "zh"}
selected_lang = st.selectbox("🌐 Language", list(lang_options.keys()))
lang = lang_options[selected_lang]

t = translations[lang]

st.title(t["title"])
st.caption(t["caption"])

# 생년월일 입력
st.write(t["birth"])
col1, col2, col3 = st.columns(3)
year = col1.number_input(t["year"], 1900, 2030, 2005, step=1)
month = col2.number_input(t["month"], 1, 12, 1, step=1)
day = col3.number_input(t["day"], 1, 31, 1, step=1)

# MBTI 부분 (기존 코드 유지, 생략)

if st.session_state.get("mbti"):
    mbti = st.session_state.mbti
    zodiac_key = get_zodiac(year)
    if zodiac_key:
        if st.button(t["fortune_btn"], use_container_width=True):
            zodiac_text = zodiacs[lang][zodiac_key]
            mbti_text = mbtis[lang][mbti]
            saju = get_saju(year, month, day, lang)

            st.success(f"{zodiac_text} + {mbti_text} → {t['best_combo']}")
            st.metric(t["fortune_score"], "92", delta=t["stable"])

            st.info(f"{t['zodiac_title']}: {zodiac_text.split(' - ')[1]}")
            st.info(f"{t['mbti_title']}: {mbti_text}")
            st.warning(f"{t['saju_title']}: {saju}")

            st.markdown("---")
            st.subheader(t["daily_title"])

            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)

            col1, col2 = st.columns(2)

            with col1:
                idx = get_daily_index(year, month, day, today)
                st.info(f"**{t['today']} ({today.strftime('%m월 %d일')})**")
                st.write(daily_messages[lang][idx])

            with col2:
                idx = get_daily_index(year, month, day, tomorrow)
                st.info(f"**{t['tomorrow']} ({tomorrow.strftime('%m월 %d일')})**")
                st.write(daily_messages[lang][idx])

            st.balloons()

    if st.button(t["reset"]):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
