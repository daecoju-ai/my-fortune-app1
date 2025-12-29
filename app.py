import streamlit as st
from datetime import datetime, timedelta
import hashlib

# 언어 번역 (한국어, 영어, 중국어 3개만)
translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 운세 🌟",
        "caption": "완전 무료 😄",
        "birth": "### 생년월일 입력",
        "year": "년",
        "month": "월",
        "day": "일",
        "next_btn": "✅ 생년월일 다 적었어! 다음으로 →",
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
        "birth": "### Enter Birth Date",
        "year": "Year",
        "month": "Month",
        "day": "Day",
        "next_btn": "✅ Done with birthday! Go next →",
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
        "birth": "### 输入出生日期",
        "year": "年",
        "month": "月",
        "day": "日",
        "next_btn": "✅ 生日日期填好了！下一步 →",
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

# 간단한 12띠 (3개 언어)
zodiacs = {
    "ko": ["쥐띠", "소띠", "호랑이띠", "토끼띠", "용띠", "뱀띠", "말띠", "양띠", "원숭이띠", "닭띠", "개띠", "돼지띠"],
    "en": ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"],
    "zh": ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
}

# 간단한 MBTI 특징 (3개 언어)
mbtis = {
    "ko": ["INTJ: 🧠 냉철 전략가", "INTP: 💡 아이디어 천재", "ENTJ: 👑 보스", "ENTP: ⚡ 토론왕",
           "INFJ: 🔮 마음 마스터", "INFP: 🎨 감성 예술가", "ENFJ: 🤗 모두 선생님", "ENFP: 🎉 인간 비타민",
           "ISTJ: 📋 규칙 지킴이", "ISFJ: 🛡️ 세상 따뜻함", "ESTJ: 📢 리더", "ESFJ: 💕 분위기 메이커",
           "ISTP: 🔧 고치는 장인", "ISFP: 🌸 감성 힐러", "ESTP: 🏄 모험왕", "ESFP: 🎭 파티 주인공"],
    "en": ["INTJ: 🧠 Strategic Mastermind", "INTP: 💡 Innovative Thinker", "ENTJ: 👑 Commander", "ENTP: ⚡ Debater",
           "INFJ: 🔮 Insightful Counselor", "INFP: 🎨 Idealistic Dreamer", "ENFJ: 🤗 Charismatic Teacher", "ENFP: 🎉 Enthusiastic Campaigner",
           "ISTJ: 📋 Responsible Inspector", "ISFJ: 🛡️ Caring Protector", "ESTJ: 📢 Efficient Executive", "ESFJ: 💕 Supportive Host",
           "ISTP: 🔧 Practical Craftsman", "ISFP: 🌸 Sensitive Artist", "ESTP: 🏄 Bold Adventurer", "ESFP: 🎭 Entertaining Performer"],
    "zh": ["INTJ: 🧠 冷静战略家", "INTP: 💡 创意天才", "ENTJ: 👑 领袖", "ENTP: ⚡ 辩论王",
           "INFJ: 🔮 心灵大师", "INFP: 🎨 感性艺术家", "ENFJ: 🤗 万人导师", "ENFP: 🎉 人类维生素",
           "ISTJ: 📋 规则守护者", "ISFJ: 🛡️ 温暖守护者", "ESTJ: 📢 高效领导", "ESFJ: 💕 气氛制造者",
           "ISTP: 🔧 修理大师", "ISFP: 🌸 感性治疗师", "ESTP: 🏄 冒险王", "ESFP: 🎭 派对主角"]
}

# 간단한 오늘/내일 운세 메시지 (각 언어 10개씩 예시)
daily_messages = {
    "ko": ["에너지 충만! 새로운 시작 GO! 🔥", "인내가 필요한 날… 천천히 가자 🐢", "뜻밖의 인연이 생길지도 💞",
           "돈 들어올 기미! 💰", "집중력 최고! 오늘 끝내버려 📊", "조금 피곤… 푹 쉬어 😴",
           "변화의 날! 새 도전 OK 🌬️", "소통이 중요한 날 🗣️", "직감 예리! 믿고 가 🔮", "경쟁에서 이길 운! 💪"],
    "en": ["Full energy! New start GO! 🔥", "Patience day… Take it slow 🐢", "Unexpected connection? 💞",
           "Money coming! 💰", "Max focus! Finish today 📊", "A bit tired… Rest 😴",
           "Change day! Try new things 🌬️", "Communication key 🗣️", "Intuition sharp 🔮", "Win the competition! 💪"],
    "zh": ["能量满满！新开始GO！🔥", "需要耐心的日子…慢慢来 🐢", "可能有意外缘分 💞",
           "财运来了！💰", "专注力巅峰！今天搞定 📊", "有点累…好好休息 😴",
           "变化之日！尝试新事物 🌬️", "沟通重要的一天 🗣️", "直觉很准 🔮", "竞争中获胜！💪"]
}

def get_zodiac(y):
    idx = (y - 4) % 12
    return zodiacs[st.session_state.lang][idx]

def get_daily_message(year, month, day, offset=0):
    target = datetime.now().date() + timedelta(days=offset)
    combined = f"{year}{month:02d}{day:02d}{target.year}{target.month:02d}{target.day:02d}"
    hash_val = int(hashlib.sha256(combined.encode()).hexdigest(), 16)
    idx = hash_val % len(daily_messages[st.session_state.lang])
    return daily_messages[st.session_state.lang][idx]

# ────────────────────────────────────────────────
#                    앱 시작
# ────────────────────────────────────────────────

if "lang" not in st.session_state:
    st.session_state.lang = "ko"

lang_map = {"한국어": "ko", "English": "en", "中文": "zh"}
selected = st.selectbox("🌐 Language / 语言", list(lang_map.keys()))
st.session_state.lang = lang_map[selected]

t = translations[st.session_state.lang]

st.title(t["title"])
st.caption(t["caption"])

st.write(t["birth"])
col1, col2, col3 = st.columns(3)
year = col1.number_input(t["year"], 1900, 2030, 2005, step=1)
month = col2.number_input(t["month"], 1, 12, 1, step=1)
day = col3.number_input(t["day"], 1, 31, 1, step=1)

# ★★★ 여기!!! 생년월일 입력 후 다음으로 가는 버튼 ★★★
if st.button(t["next_btn"], type="primary", use_container_width=True):
    st.balloons()
    st.success("좋아! 이제 MBTI 선택할 차례야~ ↓↓↓")

# MBTI 선택 부분 (간단히 직접 입력만 넣음 - 테스트는 생략)
if "mbti" not in st.session_state:
    st.session_state.mbti = None

if st.session_state.mbti is None:
    st.write(t["mbti_mode"])
    mbti_choice = st.selectbox("MBTI", mbtis[st.session_state.lang])
    if st.button(t["fortune_btn"]):
        st.session_state.mbti = mbti_choice.split(":")[0].strip()  # INTJ, INTP 등만 추출
        st.rerun()

# 결과 화면
if st.session_state.mbti:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(year)
    
    if st.button(t["fortune_btn"], use_container_width=True):
        st.success(f"{zodiac} + {mbti} → {t['best_combo']}")
        st.metric(t["fortune_score"], "92점", delta=t["stable"])
        
        st.markdown("---")
        st.subheader(t["daily_title"])
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**{t['today']}** ({today.strftime('%m월 %d일')})")
            st.write(get_daily_message(year, month, day, 0))
        with col2:
            st.info(f"**{t['tomorrow']}** ({tomorrow.strftime('%m월 %d일')})")
            st.write(get_daily_message(year, month, day, 1))
        
        st.balloons()

    if st.button(t["reset"]):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
