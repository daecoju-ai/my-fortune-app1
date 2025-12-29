import streamlit as st
from datetime import datetime, timedelta
import hashlib

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
        ]
    },
    "en": {  # 영어 부분은 그대로 두었어요 (필요하면 나중에 번역해도 돼요)
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
        "zodiacs": {
            "Rat": "🐭 Active growth, money ↑",
            "Ox": "🐮 Effort pays off",
            "Tiger": "🐯 Challenge success, big money",
            "Rabbit": "🐰 Stability, love luck",
            "Dragon": "🐲 Luck ↑ leadership",
            "Snake": "🐍 Practical, intuition",
            "Horse": "🐴 New challenge, money chance",
            "Goat": "🐑 Comfort + marriage luck",
            "Monkey": "🐵 Change, talent",
            "Rooster": "🐔 Effort result",
            "Dog": "🐶 Friends, money ↑",
            "Pig": "🐷 Leisure, best money"
        },
        "mbtis": {
            "INTJ": "🧠 Cool strategist",
            "INTP": "💡 Idea genius",
            "ENTJ": "👑 Boss",
            "ENTP": "⚡ Debate king",
            "INFJ": "🔮 Mind master",
            "INFP": "🎨 Emotional artist",
            "ENFJ": "🤗 Teacher to all",
            "ENFP": "🎉 Human vitamin",
            "ISTJ": "📋 Rule keeper",
            "ISFJ": "🛡️ World warmer",
            "ESTJ": "📢 Leader",
            "ESFJ": "💕 Mood maker",
            "ISTP": "🔧 Fixer artisan",
            "ISFP": "🌸 Emotional healer",
            "ESTP": "🏄 Adventure king",
            "ESFP": "🎭 Party protagonist"
        },
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
                    index=0 if st.session_state.lang == "ko" else 1)
st.session_state.lang = "ko" if lang == "한국어" else "en"

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

# 오늘/내일 운세용 메시지 40개 (더 다양하고 재미있게 업그레이드!)
daily_msgs = [
    "오늘은 불꽃처럼 뜨거운 에너지! 도전 GO! 🔥",
    "작은 행운이 계속 쌓이는 날… 미소가 최고의 복 😊",
    "인간관계가 빛나는 하루! 먼저 인사 건네보세요 👋",
    "돈 들어올 기미! 예상치 못한 용돈이? 💸",
    "집중력 200%↑ 중요한 일 오늘 끝내버리자! 💪",
    "조금 느리게 가도 괜찮아… 천천히 깊이 가는 날 🐌",
    "새로운 아이디어 번쩍! 메모 잊지 마세요 📝",
    "감정 컨트롤이 중요한 날… 한 템포 쉬어가기 😌",
    "직감이 딱! 오늘 느낌대로 움직여도 OK 🔮",
    "경쟁 속에서 빛나는 당신! 자신감 최고 ✨",
    "편안한 하루… 집에서 보내도 충전 완료 🏠",
    "창의력 대폭발! 그림·글·음악 뭐든 좋아 🎨",
    "사소한 말 한마디가 큰 변화를 만들 수 있어 🗣️",
    "도와줄 사람이 나타나는 날! 감사 인사 필수 🙏",
    "작은 선물이 큰 기쁨! 주변 챙겨보는 건 어때? 🎁",
    "결정 내리기 딱 좋은 타이밍! 망설이지 말고! ⚡",
    "혼자만의 시간 가져보기… 내면이 답해줄 거야 🧘",
    "몸 움직이면 기분 UP! 산책·운동 강추 🏃‍♂️",
    "금전 흐름 부드럽게! 저축 모멘텀 타기 좋아요 💰",
    "감사하는 마음이 복을 더 불러오는 날 🙌",
    "오늘은 리더십 발휘할 차례! 의견 적극적으로! 👑",
    "예상치 못한 칭찬 받을 가능성 높음 😎",
    "작은 실수도 웃으며 넘기면 더 성장해요 ㅎㅎ",
    "연애운 살짝↑! 눈 맞춘 순간 설렐지도 💕",
    "오늘은 '아니오'라고 말할 용기가 필요한 날 ✊",
    "오래된 친구와 연락하면 큰 위로가 올 거예요 📱",
    "새로운 취미 시작하기 좋은 에너지! 지금이 타이밍 🎸",
    "피로가 쌓였다면… 오늘은 일찍 자는 게 최고 😴",
    "목표에 한 발짝 더 가까워지는 날! 화이팅! 🚀",
    "주변에서 의외의 조언이 큰 도움이 돼요 👂",
    "자기 관리 잘하면 하루가 2배로 빛나요 💅",
    "오늘은 '즐기는 게 최고'라는 걸 깨닫는 날 🎉",
    "작은 변화(헤어스타일·옷차림)도 운을 부를 수 있어요 🔄",
    "스트레스 풀기 최고! 좋아하는 것에 몰두하세요 🎧",
    "오늘 만난 사람이 다음 인연의 시작일지도? 👀",
    "노력한 게 빛을 보는 날… 조금만 더 버텨봐요 🌟",
    "운이 따라주는 날! 복권 한 장? (농담이에요 ㅋㅋ)",
    "마음이 따뜻해지는 말 한마디가 최고의 선물 ❤️",
    "오늘은 '나 자신'에게 칭찬 많이 해주기! 👏",
    "2026년 병오년 기운 받아! 추진력 폭발 예상 🐎💨"
]

def get_daily_fortune_index(year, month, day, target_date):
    combined = f"{year}{month:02d}{day:02d}{target_date.year}{target_date.month:02d}{target_date.day:02d}"
    hash_object = hashlib.sha256(combined.encode())
    hash_hex = hash_object.hexdigest()
    index = int(hash_hex, 16) % len(daily_msgs)
    return index

def get_daily_message(year, month, day, offset=0):
    today = datetime.now().date()
    target_date = today + timedelta(days=offset)
    idx = get_daily_fortune_index(year, month, day, target_date)
    return daily_msgs[idx]

# ────────────────────────────────────────────────
#              여기서부터 앱 시작!
# ────────────────────────────────────────────────

st.title(t["title"])
st.caption(t["caption"])

app_url = "https://my-fortune.streamlit.app"

st.markdown(t["qr"])
st.image("frame.png", caption="Scan with phone")  # frame.png 파일이 있어야 해요!

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
            zodiac_emoji = list(Z.values())[list(Z.keys()).index(zodiac)].split(' ',1)[0]
            zodiac_desc = list(Z.values())[list(Z.keys()).index(zodiac)].split(' ',1)[1] if ' ' in list(Z.values())[list(Z.keys()).index(zodiac)] else ""
            mbti_emoji = list(M.values())[list(M.keys()).index(mbti)].split(' ',1)[0]
            mbti_desc = list(M.values())[list(M.keys()).index(mbti)].split(' ',1)[1] if ' ' in list(M.values())[list(M.keys()).index(mbti)] else ""
            
            combo_msg = "Best combo!" if st.session_state.lang == "en" else "최고 조합!"
            st.success(f"{zodiac_emoji} **{zodiac}** + {mbti_emoji} **{mbti}** {combo_msg}")
            
            st.metric("운세 점수", f"{score}점", delta="Stable!")
            st.info(f"{t['zodiac_title']}: {zodiac_desc}")
            st.info(f"{t['mbti_title']}: {mbti_desc}")
            st.warning(f"{t['saju_title']}: {saju}")
            st.balloons()

            # ───── 오늘 & 내일 운세 추가 ─────
            st.markdown("---")
            st.subheader("🌞 오늘 & 내일의 운세 (매일 달라져요!)")

            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)

            col1, col2 = st.columns(2)

            with col1:
                st.info(f"**오늘 ({today.strftime('%m월 %d일')})**")
                msg_today = get_daily_message(year, month, day, offset=0)
                st.write(msg_today)

            with col2:
                st.info(f"**내일 ({tomorrow.strftime('%m월 %d일')})**")
                msg_tomorrow = get_daily_message(year, month, day, offset=1)
                st.write(msg_tomorrow)

            st.caption("※ 같은 생일 + 같은 날짜 = 항상 똑같은 운세 나와요 (재미로만 봐주세요~)")

    if st.button(t["reset"], key="reset"):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
