import streamlit as st
from datetime import datetime, timedelta
import hashlib
import random

# ────────────────────────────────────────────────
#                  언어 3개 (한국어·영어·중국어)
# ────────────────────────────────────────────────
translations = {
    "ko": {
        "title": "🔮 2026년 나의 운세",
        "caption": "재미로만 보는 운세예요~ 😄",
        "birth": "### 생년월일 입력",
        "year": "년", "month": "월", "day": "일",
        "next_btn": "✅ 다 적었어! 다음으로 →",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 골라볼래",
        "test": "16문제 풀어볼래",
        "test_start": "상세 테스트 시작! 😊",
        "energy": "에너지 방향",
        "info": "정보 수집",
        "decision": "결정 방식",
        "life": "생활 방식",
        "result_btn": "결과 보기!",
        "fortune_btn": "🔮 2026년 운세 보기!",
        "reset": "처음부터 다시",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한마디",
        "daily_title": "🌞 오늘 & 내일 운세",
        "today": "오늘", "tomorrow": "내일",
        "footer": "재미로만 봐주세요~",
        "best_combo": "최고 조합!",
        "fortune_score": "운세 점수",
        "stable": "안정적!",
        "monthly_title": "2026년 월별 운세 미리보기"
    },
    "en": {
        "title": "🔮 My 2026 Fortune",
        "caption": "Just for fun! 😄",
        "birth": "### Enter Birth Date",
        "year": "Year", "month": "Month", "day": "Day",
        "next_btn": "✅ Done! Go next →",
        "mbti_mode": "How to get MBTI?",
        "direct": "Choose directly",
        "test": "Take 16-question test",
        "test_start": "Start detailed test! 😊",
        "energy": "Energy Direction",
        "info": "Information Gathering",
        "decision": "Decision Making",
        "life": "Lifestyle",
        "result_btn": "See Results!",
        "fortune_btn": "🔮 View 2026 Fortune!",
        "reset": "Start Over",
        "zodiac_title": "Zodiac Fortune",
        "mbti_title": "MBTI Traits",
        "saju_title": "Saju Message",
        "daily_title": "🌞 Today & Tomorrow",
        "today": "Today", "tomorrow": "Tomorrow",
        "footer": "For fun only~",
        "best_combo": "Best Combo!",
        "fortune_score": "Fortune Score",
        "stable": "Stable!",
        "monthly_title": "2026 Monthly Preview"
    },
    "zh": {
        "title": "🔮 2026年我的运势",
        "caption": "仅供娱乐哦 😄",
        "birth": "### 输入出生日期",
        "year": "年", "month": "月", "day": "日",
        "next_btn": "✅ 填好了！下一步 →",
        "mbti_mode": "MBTI怎么选？",
        "direct": "直接选择",
        "test": "16题测试",
        "test_start": "开始详细测试！😊",
        "energy": "能量方向",
        "info": "信息收集",
        "decision": "决策方式",
        "life": "生活方式",
        "result_btn": "查看结果！",
        "fortune_btn": "🔮 查看2026年运势！",
        "reset": "重新开始",
        "zodiac_title": "生肖运势",
        "mbti_title": "MBTI特点",
        "saju_title": "四柱一句话",
        "daily_title": "🌞 今日 & 明日运势",
        "today": "今天", "tomorrow": "明天",
        "footer": "仅供娱乐~",
        "best_combo": "最佳组合！",
        "fortune_score": "运势分数",
        "stable": "非常稳定！",
        "monthly_title": "2026年月度预览"
    }
}

# ────────────────────────────────────────────────
#                  띠, MBTI, 사주, 일일운세 데이터
# ────────────────────────────────────────────────
zodiacs = {
    "ko": ["쥐띠", "소띠", "호랑이띠", "토끼띠", "용띠", "뱀띠", "말띠", "양띠", "원숭이띠", "닭띠", "개띠", "돼지띠"],
    "en": ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"],
    "zh": ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
}

mbtis = {
    "ko": ["INTJ: 🧠 냉철 전략가", "INTP: 💡 아이디어 천재", "ENTJ: 👑 보스", "ENTP: ⚡ 토론왕",
           "INFJ: 🔮 마음 마스터", "INFP: 🎨 감성 예술가", "ENFJ: 🤗 모두 선생님", "ENFP: 🎉 인간 비타민",
           "ISTJ: 📋 규칙 지킴이", "ISFJ: 🛡️ 세상 따뜻함", "ESTJ: 📢 리더", "ESFJ: 💕 분위기 메이커",
           "ISTP: 🔧 고치는 장인", "ISFP: 🌸 감성 힐러", "ESTP: 🏄 모험왕", "ESFP: 🎭 파티 주인공"],
    "en": ["INTJ: 🧠 Strategic", "INTP: 💡 Idea Genius", "ENTJ: 👑 Boss", "ENTP: ⚡ Debater",
           "INFJ: 🔮 Insightful", "INFP: 🎨 Dreamer", "ENFJ: 🤗 Teacher", "ENFP: 🎉 Enthusiast",
           "ISTJ: 📋 Responsible", "ISFJ: 🛡️ Protector", "ESTJ: 📢 Leader", "ESFJ: 💕 Supporter",
           "ISTP: 🔧 Craftsman", "ISFP: 🌸 Artist", "ESTP: 🏄 Adventurer", "ESFP: 🎭 Performer"],
    "zh": ["INTJ: 🧠 冷静战略家", "INTP: 💡 创意天才", "ENTJ: 👑 领袖", "ENTP: ⚡ 辩论王",
           "INFJ: 🔮 心灵大师", "INFP: 🎨 感性艺术家", "ENFJ: 🤗 万人导师", "ENFP: 🎉 人类维生素",
           "ISTJ: 📋 规则守护者", "ISFJ: 🛡️ 温暖守护者", "ESTJ: 📢 高效领导", "ESFJ: 💕 气氛制造者",
           "ISTP: 🔧 修理大师", "ISFP: 🌸 感性治疗师", "ESTP: 🏄 冒险王", "ESFP: 🎭 派对主角"]
}

saju_msgs = {
    "ko": ["목 기운 강함 → 성장·발전의 해!", "화 기운 강함 → 열정 폭발!", "토 기운 강함 → 안정·재물", "금 기운 → 결단력 UP",
           "수 기운 → 지혜·흐름", "오행 균형 → 행복한 해", "양기 강함 → 도전 성공", "음기 강함 → 내면 성찰"],
    "en": ["Strong Wood → Growth!", "Strong Fire → Passion!", "Strong Earth → Stability!", "Strong Metal → Decisiveness!",
           "Strong Water → Wisdom!", "Balanced → Happy year!", "Strong Yang → Success!", "Strong Yin → Reflection!"],
    "zh": ["木气旺 → 成长！", "火气旺 → 热情！", "土气旺 → 稳定！", "金气旺 → 决断！",
           "水气旺 → 智慧！", "平衡 → 幸福！", "阳气旺 → 成功！", "阴气旺 → 反省！"]
}

daily_messages = {
    "ko": ["에너지 충만! GO GO!", "천천히 가도 괜찮아~", "돈 들어올 조짐!", "친구랑 놀면 최고!",
           "공부 집중 잘 돼!", "조금 피곤... 쉬어!", "새로운 도전 OK!", "소통이 중요!", "직감 믿어!", "자신감 UP!"],
    "en": ["Energy full! GO!", "Take it slow~", "Money coming!", "Friends make it best!", "Study focus good!", "Rest a bit!", "New challenge OK!", "Talk more!", "Trust gut!", "Confidence UP!"],
    "zh": ["能量满满！冲！", "慢慢来也没关系~", "财运来了！", "和朋友玩最棒！", "学习超专注！", "有点累…休息！", "新挑战OK！", "沟通最重要！", "相信直觉！", "自信爆棚！"]
}

# 2026년 띠별 한 줄 운세 (12개)
yearly_fortunes = {
    "쥐띠": "돈이 들어오고 나갈 때 많아! 잘 관리하면 대박",
    "소띠": "꾸준히 하면 결실 보는 해! 인내가 최고",
    "호랑이띠": "도전하면 다 성공! 네가 제일 빛나는 해",
    "토끼띠": "사랑·결혼 운 좋음! 따뜻한 한 해",
    "용띠": "리더십 발휘! 승진·사업 기회 많아",
    "뱀띠": "직감이 딱! 투자·부동산 잘 맞음",
    "말띠": "에너지 최고! 하지만 무리하지 마",
    "양띠": "관계가 중요! 친구·가족과 행복",
    "원숭이띠": "재능 폭발! 창의적인 일 최고",
    "닭띠": "노력의 결실! 서서히 빛남",
    "개띠": "도움 많이 받는 해! 인맥이 복",
    "돼지띠": "여유롭게 즐기며 큰 복 받음"
}

# ────────────────────────────────────────────────
#                  앱 시작
# ────────────────────────────────────────────────

if "lang" not in st.session_state:
    st.session_state.lang = "ko"

lang_map = {"한국어": "ko", "English": "en", "中文": "zh"}
selected = st.selectbox("🌐 Language", list(lang_map.keys()))
lang = lang_map[selected]

t = translations[lang]

st.title(t["title"])
st.caption(t["caption"])

# 생년월일
st.write(t["birth"])
col1, col2, col3 = st.columns(3)
year = col1.number_input(t["year"], 1900, 2030, 2005)
month = col2.number_input(t["month"], 1, 12, 1)
day = col3.number_input(t["day"], 1, 31, 1)

# 다음 버튼
if st.button(t["next_btn"], type="primary", use_container_width=True):
    st.session_state.birth_done = True
    st.balloons()
    st.success("좋아! 이제 MBTI 고르자~")
    st.rerun()

# MBTI 선택
if st.session_state.get("birth_done", False):
    if "mbti" not in st.session_state:
        st.session_state.mbti = None

    if st.session_state.mbti is None:
        c = st.radio(t["mbti_mode"], [t["direct"], t["test"]])
        if c == t["direct"]:
            m = st.selectbox("MBTI", [m.split(":")[0] for m in mbtis[lang]])
            if st.button("결정!"):
                st.session_state.mbti = m
                st.rerun()
        else:
            st.write(t["test_start"])
            e_i = s_n = t_f = j_p = 0

            questions = [
                ("1. 사람 많은 곳에서 에너지 충전?", "E", "I"),
                ("2. 새로운 사람 만나는 게 좋아?", "E", "I"),
                ("3. 세세한 사실 잘 기억해?", "S", "N"),
                ("4. 큰 그림·미래 생각 좋아해?", "S", "N"),
                ("5. 논리·사실로 판단해?", "T", "F"),
                ("6. 사람 감정 먼저 고려해?", "T", "F"),
                ("7. 계획 세우고 따라가는 게 편해?", "J", "P"),
                ("8. 즉흥적인 게 재미있어?", "J", "P"),
                ("9. 혼자 있을 때 더 편안해?", "E", "I"),
                ("10. 상상력·아이디어 떠올리는 게 좋아?", "S", "N"),
                ("11. 옳고 그름이 명확해야 해?", "T", "F"),
                ("12. 다른 사람 기분 맞춰주는 게 중요해?", "T", "F"),
                ("13. 일정표·목록 좋아해?", "J", "P"),
                ("14. 갑자기 결정하는 게 좋아?", "J", "P"),
                ("15. 친구들과 자주 어울려?", "E", "I"),
                ("16. 창의적인 활동 즐겨?", "S", "N")
            ]

            for i, (q, yes, no) in enumerate(questions, 1):
                ans = st.radio(f"Q{i}. {q}", ["네!", "아니요~"], key=f"q{i}")
                if ans == "네!":
                    if yes == "E": e_i += 1
                    if yes == "I": e_i -= 1
                    if yes == "S": s_n += 1
                    if yes == "N": s_n -= 1
                    if yes == "T": t_f += 1
                    if yes == "F": t_f -= 1
                    if yes == "J": j_p += 1
                    if yes == "P": j_p -= 1

            if st.button(t["result_btn"]):
                ei = "E" if e_i >= 0 else "I"
                sn = "N" if s_n >= 0 else "S"
                tf = "T" if t_f >= 0 else "F"
                jp = "J" if j_p >= 0 else "P"
                st.session_state.mbti = ei + sn + tf + jp
                st.success(f"너의 MBTI는 **{st.session_state.mbti}** 이야!")
                st.rerun()

# 결과 화면
if st.session_state.get("mbti"):
    mbti = st.session_state.mbti
    zodiac_idx = (year - 4) % 12
    zodiac = zodiacs[lang][zodiac_idx]

    if st.button(t["fortune_btn"], type="primary", use_container_width=True):
        st.balloons()
        st.success(f"{zodiac} + {mbti} → {t['best_combo']}")

        # 2026년 전체 운세
        st.subheader("2026년 전체 운세")
        st.write(random.choice(["열정 폭발하는 해! 도전하면 성공!", "변화의 해! 새로운 시작 최고!", "꾸준히 하면 결실 보는 해!"]))

        # MBTI 조언
        st.subheader("MBTI 기반 2026년 조언")
        st.write(random.choice(["너의 강점 살려서 리더 되어봐!", "아이디어 폭발! 창의적인 일 해봐!", "감정 잘 다루면 인기 많아질 거야!"]))

        # 오늘·내일 운세
        st.subheader(t["daily_title"])
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"{t['today']} ({today.strftime('%m/%d')})")
            st.write(random.choice(daily_messages[lang]))
        with col2:
            st.info(f"{t['tomorrow']} ({tomorrow.strftime('%m/%d')})")
            st.write(random.choice(daily_messages[lang]))

        # 월별 운세 표
        st.subheader(t["monthly_title"])
        st.markdown("""
        | 월 | 운세 요약 |
        |---|----------|
        | 1~2월 | 새해 시작! 계획 세우기 최고 |
        | 3~4월 | 기회 많음! 적극적으로 움직여 |
        | 5~6월 | 재물·성공 타이밍 |
        | 7~8월 | 열정 폭발! 무리 주의 |
        | 9~10월 | 성과 수확기 |
        | 11~12월 | 한 해 잘 마무리! |
        """)

        # 홍보
        st.markdown("---")
        st.markdown("### 💧 생활 편하게! **다나눔렌탈** 문의 GO!")
        st.markdown("""
        정수기 / 안마의자 / 공기청정기 / 주방가전 / 서빙로봇 / 인터넷 가입  
        **정수기 렌탈료 제휴카드 → 월 0원~**  
        **설치 당일 최대 50만원 페이백!**  
        👉 [www.다나눔렌탈.com](http://www.다나눔렌탈.com)
        """)

    if st.button(t["reset"]):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
