import streamlit as st
import json
import random
import datetime
from pathlib import Path

DATA_DIR = Path("data")

# -----------------------------
# 공통 유틸
# -----------------------------
def load_json(name):
    path = DATA_DIR / name
    if not path.exists():
        st.error(f"필수 DB 파일을 읽을 수 없습니다: {path}")
        st.stop()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def seeded_choice(arr, seed):
    random.seed(seed)
    return random.choice(arr)

today = datetime.date.today()
seed_base = int(today.strftime("%Y%m%d"))

# -----------------------------
# DB 로드
# -----------------------------
year_db = load_json("fortunes_ko_2026.json")
today_db = load_json("fortunes_ko_today.json")
tomorrow_db = load_json("fortunes_ko_tomorrow.json")
zodiac_db = load_json("zodiac_fortunes_ko_2026.json")
mbti_db = load_json("mbti_traits_ko.json")
saju_db = load_json("saju_ko.json")
tarot_db = load_json("tarot_db_ko.json")

# -----------------------------
# UI
# -----------------------------
st.title("2026년 운세")

tab1, tab2, tab3, tab4 = st.tabs([
    "오늘의 운세",
    "내일의 운세",
    "2026년 전체 운세",
    "성향/확장 운세"
])

# -----------------------------
# 오늘 운세
# -----------------------------
with tab1:
    zodiac = st.selectbox("띠 선택", list(today_db.keys()))
    data = today_db.get(zodiac, {})
    texts = data if isinstance(data, list) else data.get("today", [])

    if texts:
        st.write(seeded_choice(texts, seed_base))
    else:
        st.warning("해당 띠의 오늘 운세 데이터가 없습니다.")

# -----------------------------
# 내일 운세
# -----------------------------
with tab2:
    zodiac = st.selectbox("띠 선택 ", list(tomorrow_db.keys()))
    data = tomorrow_db.get(zodiac, {})
    texts = data if isinstance(data, list) else data.get("tomorrow", [])

    if texts:
        st.write(seeded_choice(texts, seed_base + 1))
    else:
        st.warning("해당 띠의 내일 운세 데이터가 없습니다.")

# -----------------------------
# 연간 운세
# -----------------------------
with tab3:
    zodiac = st.selectbox("띠 선택  ", list(zodiac_db.keys()))
    year_texts = zodiac_db[zodiac].get("year", [])

    if year_texts:
        st.write(seeded_choice(year_texts, seed_base))
    else:
        st.warning("연간 운세 데이터가 없습니다.")

# -----------------------------
# 확장 운세
# -----------------------------
with tab4:
    st.subheader("MBTI 운세")
    mbti = st.selectbox("MBTI 선택", list(mbti_db.keys()))

    mbti_data = mbti_db.get(mbti)
    if mbti_data:
        st.write("**설명**")
        st.write(mbti_data.get("description", ""))

        if "strengths" in mbti_data:
            st.write("**강점**")
            st.write(seeded_choice(mbti_data["strengths"], seed_base))

        if "weaknesses" in mbti_data:
            st.write("**주의점**")
            st.write(seeded_choice(mbti_data["weaknesses"], seed_base))
    else:
        st.warning("MBTI 데이터 없음")

    st.divider()

    st.subheader("사주 오행")
    element = st.selectbox("오행 선택", list(saju_db.keys()))
    element_data = saju_db.get(element)

    if element_data:
        st.write(seeded_choice(element_data.get("texts", []), seed_base))
    else:
        st.warning("사주 데이터 없음")

    st.divider()

    st.subheader("타로 카드")
    card = seeded_choice(list(tarot_db.keys()), seed_base)
    card_data = tarot_db[card]

    st.write(f"**{card}**")
    st.write(card_data.get("meaning", ""))
