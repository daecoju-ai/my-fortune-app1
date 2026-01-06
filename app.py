import streamlit as st
import json
import random
from datetime import date

# =============================
# 기본 설정
# =============================
st.set_page_config(page_title="2026년 운세", layout="centered")

DATA_PATH = "data/"

# =============================
# 공통 유틸
# =============================
def load_json(filename: str):
    try:
        with open(DATA_PATH + filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"필수 DB 파일을 읽을 수 없습니다: {filename}\n{e}")
        st.stop()

def seeded_choice(items, seed):
    rng = random.Random(seed)
    return rng.choice(items)

def today_seed(extra=0):
    return int(date.today().strftime("%Y%m%d")) + extra

# =============================
# DB 로드
# =============================
year_db = load_json("fortunes_ko_2026.json")
today_db = load_json("fortunes_ko_today.json")
tomorrow_db = load_json("fortunes_ko_tomorrow.json")
zodiac_db = load_json("zodiac_fortunes_ko_2026.json")
mbti_db = load_json("mbti_traits_ko.json")
saju_db = load_json("saju_ko.json")

# =============================
# 헤더 (디자인 고정)
# =============================
st.markdown("## 2026년 운세")
st.caption("타로 포함 · 완전 무료")

birth = st.date_input("생년월일", value=date(2000, 1, 1))
mbti = st.selectbox(
    "MBTI",
    sorted(mbti_db.keys())
)

# =============================
# 기본 시드
# =============================
base_seed = int(birth.strftime("%Y%m%d"))

# =============================
# 연간 운세
# =============================
st.markdown("### 2026년 전체 운세")
year_text = seeded_choice(year_db["texts"], base_seed)
st.info(year_text)

# =============================
# 오늘 운세
# =============================
st.markdown("### 오늘 운세")
today_text = seeded_choice(today_db["texts"], today_seed())
st.success(today_text)

# =============================
# 내일 운세
# =============================
st.markdown("### 내일 운세")
tomorrow_text = seeded_choice(tomorrow_db["texts"], today_seed(1))
st.warning(tomorrow_text)

# =============================
# MBTI 해석
# =============================
st.markdown("### MBTI 운세 해석")
if mbti in mbti_db and isinstance(mbti_db[mbti], list):
    mbti_text = seeded_choice(mbti_db[mbti], base_seed + 20)
    st.info(mbti_text)
else:
    st.error(f"MBTI DB 구조 오류: {mbti}")

# =============================
# 띠 계산
# =============================
ZODIAC_ORDER = [
    "rat", "ox", "tiger", "rabbit", "dragon", "snake",
    "horse", "goat", "monkey", "rooster", "dog", "pig"
]

zodiac_index = (birth.year - 4) % 12
zodiac_key = ZODIAC_ORDER[zodiac_index]

# =============================
# 띠별 운세
# =============================
st.markdown("### 띠별 운세")

if zodiac_key in zodiac_db:
    z = zodiac_db[zodiac_key]

    z_today = seeded_choice(z["today"], today_seed())
    z_tomorrow = seeded_choice(z["tomorrow"], today_seed(1))
    z_year = seeded_choice(z["year"], base_seed)

    st.success(f"오늘 ({zodiac_key})\n\n{z_today}")
    st.warning(f"내일 ({zodiac_key})\n\n{z_tomorrow}")
    st.info(f"2026년 ({zodiac_key})\n\n{z_year}")
else:
    st.error(f"띠 DB 구조 오류: {zodiac_key}")

# =============================
# 사주 요약
# =============================
st.markdown("### 사주 한 줄 요약")

year_key = str(birth.year)
if year_key in saju_db:
    saju_text = seeded_choice(saju_db[year_key], base_seed + 50)
    st.info(saju_text)
else:
    st.caption("사주 데이터가 없는 연도입니다.")

# =============================
# 하단 광고 (문구 고정)
# =============================
st.markdown("---")
st.markdown("### 다나눔렌탈 상담 / 이벤트")
st.markdown(
    """
[광고]  
정수기 렌탈 제휴카드 적용 시 **월 렌탈비 0원**,  
설치 당일 **최대 현금 50만원 + 사은품 증정**

👉 이름 · 전화번호 작성 → 무료 상담
"""
)

if st.button("친구에게 공유하기"):
    st.warning("모바일 환경에서는 URL 복사 버튼을 이용해주세요.")

if st.button("URL 복사"):
    st.success("URL이 복사되었습니다.")
