import streamlit as st
import json
import random
import time
from datetime import datetime

# =====================================================
# 기본 설정
# =====================================================
st.set_page_config(
    page_title="2026 운세 | MBTI · 띠 · 타로",
    page_icon="🔮",
    layout="centered"
)

APP_URL = "https://your-app-url.streamlit.app"

# =====================================================
# 세션 상태 초기화
# =====================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"

if "mbti_mode" not in st.session_state:
    st.session_state.mbti_mode = "direct"

if "mbti" not in st.session_state:
    st.session_state.mbti = None

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "used_attempts" not in st.session_state:
    st.session_state.used_attempts = 0

if "game_result" not in st.session_state:
    st.session_state.game_result = None

if "stop_time" not in st.session_state:
    st.session_state.stop_time = None

# =====================================================
# DB 로드
# =====================================================
@st.cache_data
def load_fortune_db():
    with open("data/fortunes_ko.json", "r", encoding="utf-8") as f:
        return json.load(f)

DB = load_fortune_db()

# =====================================================
# 유틸
# =====================================================
def get_zodiac(year: int):
    zodiac = [
        "쥐", "소", "호랑이", "토끼", "용", "뱀",
        "말", "양", "원숭이", "닭", "개", "돼지"
    ]
    return zodiac[(year - 4) % 12]

# =====================================================
# 입력 화면
# =====================================================
def render_input():
    st.markdown("## 🔮 2026 운세 보기")

    name = st.text_input("이름")
    birth = st.date_input("생년월일")

    st.markdown("### MBTI 선택")
    mbti_mode = st.radio(
        "",
        ["직접 선택", "12문항 테스트", "16문항 테스트"],
        index=0
    )

    if mbti_mode == "직접 선택":
        mbti = st.selectbox("MBTI", sorted(DB["mbti"].keys()))
        st.session_state.mbti = mbti

    else:
        st.info("※ 기준 안정판에서는 문항 UI만 복원 (문항 로직은 유지)")
        st.session_state.mbti = "ENFP"

    if st.button("결과 보기"):
        st.session_state.name = name
        st.session_state.birth = birth
        st.session_state.zodiac = get_zodiac(birth.year)
        st.session_state.stage = "result"
        st.rerun()

# =====================================================
# 결과 화면
# =====================================================
def render_result():
    name = st.session_state.name
    zodiac = st.session_state.zodiac
    mbti = st.session_state.mbti

    zodiac_data = DB["zodiac"][zodiac]
    mbti_data = DB["mbti"][mbti]

    st.markdown(f"## ✨ {name}님의 2026 운세")
    st.markdown(f"**띠:** {zodiac}띠 / **MBTI:** {mbti}")

    st.markdown("---")
    st.markdown("### 📅 오늘의 운세")
    st.write(random.choice(zodiac_data["today"]))

    st.markdown("### 📅 내일의 운세")
    st.write(random.choice(zodiac_data["tomorrow"]))

    st.markdown("### 🧧 2026 전체 운세")
    st.write(random.choice(zodiac_data["year_2026"]))

    st.markdown("### 💡 조언")
    st.write(random.choice(zodiac_data["advice"]))

    # =================================================
    # 친구에게 공유하기
    # =================================================
    st.markdown("---")
    if st.button("🔗 친구에게 공유하기"):
        if st.session_state.used_attempts >= 1:
            st.session_state.attempts = 2
        st.success("공유 완료! 미니게임 1회 추가 🎁")

    # =================================================
    # 광고
    # =================================================
    st.markdown("---")
    st.markdown("### 📢 다나눔렌탈")
    st.markdown(
        """
        **정수기 렌탈 제휴카드시 월 0원부터**  
        설치당일 최대 50만원 + 사은품
        """
    )

    # =================================================
    # 미니게임
    # =================================================
    st.markdown("---")
    st.markdown("### 🎁 미니게임 (20.260 ~ 20.269초 맞추기)")
    st.caption("※ 선착순 커피 쿠폰 / 조기 종료 가능")

    if st.session_state.used_attempts >= st.session_state.attempts:
        st.warning("도전 횟수를 모두 사용했습니다.")
        return

    if st.button("START"):
        st.session_state.start_time = time.time()

    if st.button("STOP"):
        elapsed = round(time.time() - st.session_state.start_time, 3)
        st.session_state.used_attempts += 1
        st.session_state.stop_time = elapsed

        if 20.260 <= elapsed <= 20.269:
            st.success(f"🎉 성공! 기록: {elapsed}초")
            st.info("이름 / 전화번호 입력 후 커피 쿠폰 지급")
        else:
            st.error(f"❌ 실패! 기록: {elapsed}초")
            st.info("친구 공유 후 재도전 가능")

    if st.button("← 처음으로"):
        st.session_state.stage = "input"
        st.rerun()

# =====================================================
# 라우터
# =====================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
