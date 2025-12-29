import streamlit as st

# 다국어 사전 (한국어·영어 완벽)
translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 운세 🌟",
        "caption": "완전 무료 😄",
        "qr": "### 📱 QR 코드 스캔!",
        "share": "### 🔗 공유 링크",
        "share_desc": "위 링크 복사해서 보내주세요!",
        "birth": "### 생년월일 입력",
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
        "footer": "재미로만 봐주세요 😊",
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
        "share_desc": "Copy and share the link!",
        "birth": "### Enter Birth Date",
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
        "footer": "For fun only 😊",
        "zodiacs": {"Rat":"🐭 Active growth, money ↑","Ox":"🐮 Effort pays off","Tiger":"🐯 Challenge success, big money","Rabbit":"🐰 Stability, love luck","Dragon":"🐲 Luck ↑ leadership","Snake":"🐍 Practical, intuition","Horse":"🐴 New challenge, money chance","Goat":"🐑 Comfort + marriage luck","Monkey":"🐵 Change, talent","Rooster":"🐔 Effort result","Dog":"🐶 Friends, money ↑","Pig":"🐷 Leisure, best money"},
        "mbtis": {"INTJ":"🧠 Cool strategist","INTP":"💡 Idea genius","ENTJ":"👑 Boss","ENTP":"⚡ Debate king","INFJ":"🔮 Mind master","INFP":"🎨 Emotional artist","ENFJ":"🤗 Teacher to all","ENFP":"🎉 Human vitamin","ISTJ":"📋 Rule keeper","ISFJ":"🛡️ World warmer","ESTJ":"📢 Leader","ESFJ":"💕 Mood maker","ISTP":"🔧 Fixer artisan","ISFP":"🌸 Emotional healer","ESTP":"🏄 Adventure king","ESFP":"🎭 Party protagonist"},
        "saju_msgs": [
            "Wood strong → Growth year! 🌱",
            "Fire strong → Passion explosion! ❤️",
            "Earth strong → Stability & wealth 💰",
            "Metal strong → Good decisiveness! 👔",
            "Water strong → Wisdom & flow 🌊",
            "Balanced elements → Happy year ✨",
            "Yang strong → Challenge success 🚀",
            "Yin strong → Inner reflection 😌"
        ]
    }
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

st.title(t["title"])
st.caption(t["caption"])

app_url = "https://my-fortune.streamlit.app"

st.markdown(t["qr"])
st.image("frame.png", caption="Scan with phone")

st.markdown(t["share"])
st.code(app_url, language=None)
st.write(t["share_desc"])

st.write(t["birth"])
col1, col2, col3 = st.columns(3)
year = col1.number_input("Year", 1900, 2030, 2005, step=1)
month = col2.number_input("Month", 1, 12, 1, step=1)
day = col3.number_input("Day", 1, 31, 1, step=1)

if "mbti" not in st.session_state: 
    st.session_state.mbti = None

if st.session_state.mbti is None:
    c = st.radio(t["mbti_mode"], [t["direct"], t["test"]], key="mode")
    if c == t["direct"]:
        m = st.selectbox("MBTI", sorted(M.keys()), key="direct")
        if st.button(t["fortune_btn"], key="direct_go"):
            st.session_state.mbti = m
            st.rerun()
    else:
        st.write(t["test_start"])
        e_i, s_n, t_f, j_p = 0, 0, 0, 0
        
        st.subheader(t["energy"])
        if st.radio("1.", ["네 (E)", "아니 (I)"], key="ei1") == "네 (E)": e_i += 1
        if st.radio("2.", ["좋아 (E)", "부담 (I)"], key="ei2") == "좋아 (E)": e_i += 1
        if st.radio("3.", ["많이 (I)", "가끔 (E)"], key="ei3") == "많이 (I)": e_i += 1
        if st.radio("4.", ["바로 (E)", "정리 후 (I)"], key="ei4") == "바로 (E)": e_i += 1
        
        st.subheader(t["info"])
        if st.radio("5.", ["네 (S)", "가능성 (N)"], key="sn1") == "네 (S)": s_n += 1
        if st.radio("6.", ["잘해 (S)", "큰 그림 (N)"], key="sn2") == "잘해 (S)": s_n += 1
        if st.radio("7.", ["좋아 (N)", "현재 집중 (S)"], key="sn3") == "좋아 (N)": s_n += 1
        if st.radio("8.", ["네 (S)", "추상 (N)"], key="sn4") == "네 (S)": s_n += 1
        
        st.subheader(t["decision"])
        if st.radio("9.", ["네 (T)", "감정 고려 (F)"], key="tf1") == "네 (T)": t_f += 1
        if st.radio("10.", ["네 (T)", "마음 아파 (F)"], key="tf2") == "네 (T)": t_f += 1
        if st.radio("11.", ["공감 먼저 (F)", "조언 위주 (T)"], key="tf3") == "공감 먼저 (F)": t_f += 1
        if st.radio("12.", ["네 (T)", "상처 주지 않게 (F)"], key="tf4") == "네 (T)": t_f += 1
        
        st.subheader(t["life"])
        if st.radio("13.", ["좋아 (J)", "즉흥 (P)"], key="jp1") == "좋아 (J)": j_p += 1
        if st.radio("14.", ["미리 (J)", "마감 때 (P)"], key="jp2") == "미리 (J)": j_p += 1
        if st.radio("15.", ["빨리 (J)", "열어두기 (P)"], key="jp3") == "빨리 (J)": j_p += 1
        if st.radio("16.", ["좋아 (J)", "괜찮아 (P)"], key="jp4") == "좋아 (J)": j_p += 1
        
        if st.button(t["result_btn"], key="test_go"):
            ei = "E" if e_i >= 3 else "I"
            sn = "S" if s_n >= 3 else "N"
            tf = "T" if t_f >= 3 else "F"
            jp = "J" if j_p >= 3 else "P"
            result = ei + sn + tf + jp
            st.session_state.mbti = result
            st.rerun()

if st.session_state.mbti:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(year)
    if zodiac:
        if st.button(t["fortune_btn"], use_container_width=True, key="fortune"):
            score = 90
            saju = get_saju(year, month, day)
            # 수정된 결과 표시 (split 오류 해결!)
            zodiac_emoji = Z[zodiac].split(' ',1)[0] if ' ' in Z[zodiac] else ""
            zodiac_desc = Z[zodiac].split(' ',1)[1] if ' ' in Z[zodiac] else Z[zodiac]
            mbti_emoji = M[mbti].split(' ',1)[0] if ' ' in M[mbti] else ""
            mbti_desc = M[mbti].split(' ',1)[1] if ' ' in M[mbti] else M[mbti]
            st.success(f"{zodiac_emoji} **{zodiac}** + {mbti_emoji} **{mbti}** 최고 조합!")
            st.metric("운세 점수", f"{score}점", delta="안정적!")
            st.info(f"{t['zodiac_title']}: {zodiac_desc}")
            st.info(f"{t['mbti_title']}: {mbti_desc}")
            st.warning(f"{t['saju_title']}: {saju}")
            st.balloons()

            share_text = f"2026 운세!\n띠: {zodiac}\nMBTI: {mbti}\n사주: {saju}\n점수 {score}점!\n{app_url}"
            st.text_area("공유 텍스트", share_text, height=120)

    if st.button(t["reset"], key="reset"):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
