import streamlit as st

# 다국어 사전 (쉽게 추가 가능!)
translations = {
    "ko": {  # 한국어
        "title": "🌟 2026 띠 + MBTI + 사주 운세 🌟",
        "caption": "완전 무료 😄",
        "qr": "### 📱 QR 코드 스캔!",
        "share": "### 🔗 공유 링크",
        "share_desc": "위 링크 복사해서 친구들한테 보내주세요!",
        "ad_title": "💳 렌탈 궁금할 때?",
        "ad_text": "<b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 페이백</b>!",
        "ad_btn": "🔗 보러가기",
        "birth": "### 생년월일 입력 (사주 계산을 위해!)",
        "year": "년", "month": "월", "day": "일",
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
        "saju_title": "**사주팔자 한 마디**",
        "special": "특별 메시지",
        "footer": "재미로만 봐주세요! 친구들이랑 같이 해보세요 😊"
    },
    "en": {  # English
        "title": "🌟 2026 Zodiac + MBTI + Fortune 🌟",
        "caption": "Completely Free 😄",
        "qr": "### 📱 Scan QR Code!",
        "share": "### 🔗 Share Link",
        "share_desc": "Copy the link above and share with friends!",
        "ad_title": "💳 Curious about rental?",
        "ad_text": "<b>Dananum Rental</b> with partner card: <b>0 won/month</b> + <b>Cashback</b>!",
        "ad_btn": "🔗 Check it out",
        "birth": "### Enter Birth Date (for Fortune Telling!)",
        "year": "Year", "month": "Month", "day": "Day",
        "mbti_mode": "How to get MBTI?",
        "direct": "Enter directly",
        "test": "Detailed Test (16 questions)",
        "test_start": "Detailed MBTI Test Start! Answer one by one 😊",
        "energy": "Energy Direction",
        "info": "Information Gathering",
        "decision": "Decision Making",
        "life": "Lifestyle",
        "result_btn": "View Results!",
        "fortune_btn": "🔮 View 2026 Fortune!",
        "reset": "Start Over",
        "zodiac_title": "**Zodiac Fortune**",
        "mbti_title": "**MBTI Traits**",
        "saju_title": "**Saju One Word**",
        "special": "Special Message",
        "footer": "For fun only! Try with friends 😊"
    },
    "ja": {  # 일본어
        "title": "🌟 2026 十二支 + MBTI + 四柱推命運勢 🌟",
        "caption": "完全無料 😄",
        "qr": "### 📱 QRコードをスキャン！",
        "share": "### 🔗 共有リンク",
        "share_desc": "上のリンクをコピーして友達に送ってね！",
        "ad_title": "💳 レンタル気になる？",
        "ad_text": "<b>ダナヌムレンタル</b>提携カードで<b>月0円から</b> + <b>キャッシュバック</b>！",
        "ad_btn": "🔗 見てみる",
        "birth": "### 生年月日入力 (四柱推命のため！)",
        "year": "年", "month": "月", "day": "日",
        "mbti_mode": "MBTIはどうする？",
        "direct": "直接入力",
        "test": "詳細テスト (16問)",
        "test_start": "詳細テスト開始！1つずつ答えてね 😊",
        "energy": "エネルギー方向",
        "info": "情報収集",
        "decision": "決定方式",
        "life": "生活スタイル",
        "result_btn": "結果を見る！",
        "fortune_btn": "🔮 2026年運勢を見る！",
        "reset": "最初からやり直す",
        "zodiac_title": "**十二支運勢**",
        "mbti_title": "**MBTI特徴**",
        "saju_title": "**四柱推命一言**",
        "special": "特別メッセージ",
        "footer": "遊びで楽しんでね！友達と一緒にやってみて 😊"
    },
    "zh": {  # 중국어 (간체)
        "title": "🌟 2026 生肖 + MBTI + 四柱运势 🌟",
        "caption": "完全免费 😄",
        "qr": "### 📱 扫描二维码！",
        "share": "### 🔗 分享链接",
        "share_desc": "复制上面的链接发给朋友吧！",
        "ad_title": "💳 租赁感兴趣？",
        "ad_text": "<b>Dananum租赁</b>合作卡<b>月租0元起</b> + <b>现金返现</b>！",
        "ad_btn": "🔗 去看看",
        "birth": "### 输入出生日期 (用于四柱推命！)",
        "year": "年", "month": "月", "day": "日",
        "mbti_mode": "MBTI怎么选？",
        "direct": "直接输入",
        "test": "详细测试 (16题)",
        "test_start": "详细测试开始！一个一个回答哦 😊",
        "energy": "能量方向",
        "info": "信息收集",
        "decision": "决策方式",
        "life": "生活方式",
        "result_btn": "查看结果！",
        "fortune_btn": "🔮 查看2026年运势！",
        "reset": "从头开始",
        "zodiac_title": "**生肖运势**",
        "mbti_title": "**MBTI特征**",
        "saju_title": "**四柱推命一句话**",
        "special": "特别信息",
        "footer": "仅供娱乐！和朋友一起试试吧 😊"
    }
}

# 기본 언어 한국어
if "lang" not in st.session_state:
    st.session_state.lang = "ko"

# 상단 언어 선택
lang = st.selectbox("🌐 Language / 언어 / 言語 / 语言", ["한국어", "English", "日本語", "中文"], 
                    index=["ko", "en", "ja", "zh"].index(st.session_state.lang), key="lang_select")
st.session_state.lang = {"한국어": "ko", "English": "en", "日本語": "ja", "中文": "zh"}[lang]

t = translations[st.session_state.lang]

Z = {"쥐띠":"🐭 활발·성장, 돈↑","소띠":"🐮 노력 결실","호랑이띠":"🐯 도전 성공, 돈 대박","토끼띠":"🐰 안정·사랑 운","용띠":"🐲 운↑ 리더십","뱀띠":"🐍 실속·직감","말띠":"🐴 새 도전·돈 기회","양띠":"🐑 편안+결혼 운","원숭이띠":"🐵 변화·재능","닭띠":"🐔 노력 결과","개띠":"🐶 친구·돈↑","돼지띠":"🐷 여유·돈 최고"}

M = {"INTJ":"🧠 냉철 전략가","INTP":"💡 아이디어 천재","ENTJ":"👑 보스","ENTP":"⚡ 토론왕","INFJ":"🔮 마음 마스터","INFP":"🎨 감성 예술가","ENFJ":"🤗 모두 선생님","ENFP":"🎉 인간 비타민","ISTJ":"📋 규칙 지킴이","ISFJ":"🛡️ 세상 따뜻함","ESTJ":"📢 리더","ESFJ":"💕 분위기 메이커","ISTP":"🔧 고치는 장인","ISFP":"🌸 감성 힐러","ESTP":"🏄 모험왕","ESFP":"🎭 파티 주인공"}

def get_zodiac(y): 
    z = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
    return z[(y-4)%12] if 1900<=y<=2030 else None

saju_msg = [
    "목(木) 기운 강함 → 성장과 발전의 해! 🌱",
    "화(火) 기운 강함 → 열정 폭발! ❤️",
    "토(土) 기운 강함 → 안정과 재물운 💰",
    "금(金) 기운 강함 → 결단력 좋음! 👔",
    "수(水) 기운 강함 → 지혜와 흐름 🌊",
    "오행 균형 → 행복한 한 해 ✨",
    "양기 강함 → 도전 성공 🚀",
    "음기 강함 → 내면 성찰 😌"
]

def get_saju(year, month, day):
    total = year + month + day
    index = total % 8
    return saju_msg[index]

st.set_page_config(page_title="띠MBTI 사주 운세", layout="centered")
st.title(t["title"])
st.caption(t["caption"])

app_url = "https://my-fortune.streamlit.app"

st.markdown(t["qr"])
st.image("frame.png", caption=t.get("qr", "Scan with phone"))

st.markdown(t["share"])
st.code(app_url, language=None)
st.write(t["share_desc"])

st.markdown(f"""
<div style="background:#ffeb3b;padding:15px;border-radius:15px;text-align:center;margin:20px 0;">
  <h3>{t["ad_title"]}</h3>
  <p>{t["ad_text"]}</p>
  <a href="https://www.다나눔렌탈.com" target="_blank">
    <button style="background:#ff5722;color:white;padding:10px 25px;border:none;border-radius:10px;">{t["ad_btn"]}</button>
  </a>
</div>
""", unsafe_allow_html=True)

st.write(t["birth"])
col1, col2, col3 = st.columns(3)
year = col1.number_input(t["year"], 1900, 2030, 2005, step=1)
month = col2.number_input(t["month"], 1, 12, 1, step=1)
day = col3.number_input(t["day"], 1, 31, 1, step=1)

if "mbti" not in st.session_state: 
    st.session_state.mbti = None

if st.session_state.mbti is None:
    c = st.radio(t["mbti_mode"], [t["direct"], t["test"]], key="mode")
    if c == t["direct"]:
        m = st.selectbox("MBTI", sorted(M.keys()), key="direct")
        if st.button(t.get("fortune_btn", "운세 보기"), key="direct_go"):
            st.session_state.mbti = m
            st.rerun()
    else:
        st.write(t["test_start"])
        e_i, s_n, t_f, j_p = 0, 0, 0, 0
        
        st.subheader(t["energy"])
        if st.radio("1. 사람 많을수록 좋아?", ["네 (E)", "아니 (I)"], key="ei1") == "네 (E)": e_i += 1
        if st.radio("2. 새로운 사람 만나는 거 좋아?", ["좋아 (E)", "부담 (I)"], key="ei2") == "좋아 (E)": e_i += 1
        if st.radio("3. 혼자 시간 필요해?", ["많이 (I)", "가끔 (E)"], key="ei3") == "많이 (I)": e_i += 1
        if st.radio("4. 생각 바로 말해?", ["바로 (E)", "정리 후 (I)"], key="ei4") == "바로 (E)": e_i += 1
        
        st.subheader(t["info"])
        if st.radio("5. 구체적 사실 중요?", ["네 (S)", "가능성 (N)"], key="sn1") == "네 (S)": s_n += 1
        if st.radio("6. 세부 기억 잘해?", ["잘해 (S)", "큰 그림 (N)"], key="sn2") == "잘해 (S)": s_n += 1
        if st.radio("7. 미래 상상 좋아?", ["좋아 (N)", "현재 집중 (S)"], key="sn3") == "좋아 (N)": s_n += 1
        if st.radio("8. 실제 경험 선호?", ["네 (S)", "추상 (N)"], key="sn4") == "네 (S)": s_n += 1
        
        st.subheader(t["decision"])
        if st.radio("9. 논리 우선?", ["네 (T)", "감정 고려 (F)"], key="tf1") == "네 (T)": t_f += 1
        if st.radio("10. 비판 논리로 받아?", ["네 (T)", "마음 아파 (F)"], key="tf2") == "네 (T)": t_f += 1
        if st.radio("11. 공감 잘 해?", ["공감 먼저 (F)", "조언 위주 (T)"], key="tf3") == "공감 먼저 (F)": t_f += 1
        if st.radio("12. 진실 중요?", ["네 (T)", "상처 주지 않게 (F)"], key="tf4") == "네 (T)": t_f += 1
        
        st.subheader(t["life"])
        if st.radio("13. 계획 좋아?", ["좋아 (J)", "즉흥 (P)"], key="jp1") == "좋아 (J)": j_p += 1
        if st.radio("14. 미리 끝내?", ["미리 (J)", "마감 때 (P)"], key="jp2") == "미리 (J)": j_p += 1
        if st.radio("15. 빨리 결정?", ["빨리 (J)", "열어두기 (P)"], key="jp3") == "빨리 (J)": j_p += 1
        if st.radio("16. 정리정돈 좋아?", ["좋아 (J)", "괜찮아 (P)"], key="jp4") == "좋아 (J)": j_p += 1
        
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
            st.success(f"{Z[zodiac][0]} **{zodiac}** + {M[mbti][0]} **{mbti}** 최고 조합!")
            st.metric("운세 점수", f"{score}점", delta="안정적!")
            st.info(f"{t['zodiac_title']}: {Z[zodiac].split(' ',1)[1]}")
            st.info(f"{t['mbti_title']}: {M[mbti].split(' ',1)[1]}")
            st.warning(f"{t['saju_title']}: {saju}")
            st.balloons()

            share_text = f"2026 운세!\n띠: {zodiac}\nMBTI: {mbti}\n사주: {saju}\n점수 {score}점!\n{app_url}"
            st.text_area("공유 텍스트 (복사해서 보내세요)", share_text, height=120)

    if st.button(t["reset"], key="reset"):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
