import os
import json
import datetime as dt
import streamlit as st

# -----------------------------
# Zodiac mapping (핵심 수정)
# -----------------------------

ZODIAC_ORDER = [
    "rat", "ox", "tiger", "rabbit",
    "dragon", "snake", "horse", "goat",
    "monkey", "rooster", "dog", "pig"
]

ZODIAC_LABELS_KO = {
    "rat": "쥐띠",
    "ox": "소띠",
    "tiger": "호랑이띠",
    "rabbit": "토끼띠",
    "dragon": "용띠",
    "snake": "뱀띠",
    "horse": "말띠",
    "goat": "양띠",
    "monkey": "원숭이띠",
    "rooster": "닭띠",
    "dog": "개띠",
    "pig": "돼지띠",
}

def zodiac_from_year(year: int):
    idx = (year - 1900) % 12
    key = ZODIAC_ORDER[idx]
    label = ZODIAC_LABELS_KO[key]
    return key, label


# -----------------------------
# DB loading
# -----------------------------

@st.cache_data(show_spinner=False)
def load_db():
    with open("data/fortunes_ko_NO_COMBOS.json", "r", encoding="utf-8") as f:
        return json.load(f)

DB = load_db()

# -----------------------------
# UI
# -----------------------------

st.title("🔮 오늘의 운세")

birth = st.date_input(
    "생년월일",
    min_value=dt.date(1900, 1, 1),
    max_value=dt.date.today()
)

if st.button("운세 보기"):
    zodiac_key, zodiac_label = zodiac_from_year(birth.year)

    # 🔥 여기서 더 이상 KeyError 안 남
    zodiac_data = DB["zodiac"].get(zodiac_key)

    if not zodiac_data:
        st.error("해당 띠 데이터가 없습니다.")
        st.stop()

    st.subheader(f"{zodiac_label} 운세")

    st.markdown("### 오늘 운세")
    st.write(zodiac_data.get("today_fortune", "—"))

    st.markdown("### 내일 운세")
    st.write(zodiac_data.get("tomorrow_fortune", "—"))

    st.markdown("### 2026 전체 운세")
    st.write(zodiac_data.get("year_overall", "—"))
