import streamlit as st
from datetime import datetime, timedelta
import random
from streamlit.components.v1 import html

# 다국어 사전 (한국어)
translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 + 오늘/내일 운세 🌟",
        "caption": "완전 무료 😄",
        "qr": "### 📱 QR 코드 스캔!",
        "share": "### 🔗 공유 링크",
        "share_desc": "위 링크 복사해서 친구들한테 보내주세요!",
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
            "쥐띠": "🐭 활발·성장, 돈↑", "소띠": "🐮 노력 결실", "호랑이띠": "🐯 도전 성공, 돈 대박",
            "토끼띠": "🐰 안정·사랑 운", "용띠": "🐲 운↑ 리더십", "뱀띠": "🐍 실속·직감",
            "말띠": "🐴 새 도전·돈 기회", "양띠": "🐑 편안+결혼 운", "원숭이띠": "🐵 변화·재능",
            "닭띠": "🐔 노력 결과", "개띠": "🐶 친구·돈↑", "돼지띠": "🐷 여유·돈 최고"
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
    }
}

t = translations["ko"]
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

st.set_page_config(page_title="운세", layout="centered")

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
    st.session_state.year = col1.number_input("Year", 1900, 2030, st.session_state.year, step=1)
    st.session_state.month = col2.number_input("Month", 1, 12, st.session_state.month, step=1)
    st.session_state.day = col3.number_input("Day", 1, 31, st.session_state.day, step=1)

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
        if st.radio("1.", ["네 (E)", "아니 (I)"], key="q1") == "네 (E)": e_i += 1
        if st.radio("2.", ["좋아 (E)", "부담 (I)"], key="q2") == "좋아 (E)": e_i += 1
        if st.radio("3.", ["많이 (I)", "가끔 (E)"], key="q3") == "많이 (I)": e_i += 1
        if st.radio("4.", ["바로 (E)", "정리 후 (I)"], key="q4") == "바로 (E)": e_i += 1

        st.subheader(t["info"])
        if st.radio("5.", ["네 (S)", "가능성 (N)"], key="q5") == "네 (S)": s_n += 1
        if st.radio("6.", ["잘해 (S)", "큰 그림 (N)"], key="q6") == "잘해 (S)": s_n += 1
        if st.radio("7.", ["좋아 (N)", "현재 집중 (S)"], key="q7") == "좋아 (N)": s_n += 1
        if st.radio("8.", ["네 (S)", "추상 (N)"], key="q8") == "네 (S)": s_n += 1

        st.subheader(t["decision"])
        if st.radio("9.", ["네 (T)", "감정 고려 (F)"], key="q9") == "네 (T)": t_f += 1
        if st.radio("10.", ["네 (T)", "마음 아파 (F)"], key="q10") == "네 (T)": t_f += 1
        if st.radio("11.", ["공감 먼저 (F)", "조언 위주 (T)"], key="q11") == "공감 먼저 (F)": t_f += 1
        if st.radio("12.", ["네 (T)", "상처 주지 않게 (F)"], key="q12") == "네 (T)": t_f += 1

        st.subheader(t["life"])
        if st.radio("13.", ["좋아 (J)", "즉흥 (P)"], key="q13") == "좋아 (J)": j_p += 1
        if st.radio("14.", ["미리 (J)", "마감 때 (P)"], key="q14") == "미리 (J)": j_p += 1
        if st.radio("15.", ["빨리 (J)", "열어두기 (P)"], key="q15") == "빨리 (J)": j_p += 1
        if st.radio("16.", ["좋아 (J)", "괜찮아 (P)"], key="q16") == "좋아 (J)": j_p += 1

        if st.button(t["result_btn"], use_container_width=True):
            ei = "E" if e_i >= 3 else "I"
            sn = "S" if s_n >= 3 else "N"
            tf = "T" if t_f >= 3 else "F"
            jp = "J" if j_p >= 3 else "P"
            st.session_state.mbti = ei + sn + tf + jp
            st.session_state.result_shown = True
            st.rerun()

# 결과 카드 (공유 버튼 완벽 작동)
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
        name_text = f"{st.session_state.name}{t['your_fortune']}" if st.session_state.name else "2026년 운세"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                     width:100vw; height:100vh; margin:-80px -20px 0 -20px; padding:15px 10px;
                     box-sizing:border-box; display:flex; flex-direction:column; color:white; text-align:center;">
          <div style="position:absolute; top:10px; right:10px; font-size:0.7em; opacity:0.8;">
            {t["water_purifier"]}
          </div>
          <div style="flex:1; display:flex; flex-direction:column; justify-content:center;">
            <h1 style="font-size:1.8em; margin:5px 0;">{name_text}</h1>
            <h2 style="font-size:1.8em; margin:10px 0;">
              {zodiac_emoji} {zodiac} + {mbti_emoji} {mbti}
            </h2>
            <h3 style="font-size:1.5em; margin:10px 0;">{t['combo']}</h3>
            <h1 style="font-size:3.8em; margin:15px 0; color:#ffd700;">{score}점</h1>
          </div>
          <div style="background:rgba(255,255,255,0.18); border-radius:20px; padding:10px;">
            <p style="font-size:0.95em; margin:5px 0;"><b>{t['zodiac_title']}</b>: {zodiac_desc}</p>
            <p style="font-size:0.95em; margin:5px 0;"><b>{t['mbti_title']}</b>: {mbti_desc}</p>
            <p style="font-size:0.95em; margin:5px 0;"><b>{t['saju_title']}</b>: {saju}</p>
            <hr style="border:none; border-top:1px solid rgba(255,255,255,0.4); margin:8px 0;">
            <p style="font-size:1.0em; margin:5px 0;"><b>{t['today_title']}</b>: {today}</p>
            <p style="font-size:1.0em; margin:5px 0;"><b>{t['tomorrow_title']}</b>: {tomorrow}</p>
          </div>
          <div style="margin:15px 0;">
            <button onclick="shareResult()" style="background:white; color:#6a11cb; padding:12px 50px; border:none; border-radius:30px; font-size:1.2em; font-weight:bold;">
              {t["share_btn"]}
            </button>
          </div>
          <p style="font-size:0.7em; opacity:0.7; margin:0;">{app_url}</p>
        </div>
        """, unsafe_allow_html=True)

        st.balloons()
        st.snow()

        # 공유 기능 (완벽 작동 - st.components.v1.html 사용)
        share_text = f"{name_text}\\n{zodiac} + {mbti}\\n{t['combo']}\\n{score}점!\\n{t['today_title']}: {today}\\n{t['tomorrow_title']}: {tomorrow}\\n\\n{app_url}"
        share_js = f"""
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
        html(share_js, height=0)

    if st.button(t["reset"], use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.caption(t["footer"])
