import json
from datetime import date
from pathlib import Path

import streamlit as st

# ===========================
# Config
# ===========================
APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세"
APP_SUBTITLE = "완전 무료"

# DB 파일 위치 후보(레포 구조가 바뀌어도 자동으로 찾도록)
DB_CANDIDATES = [
    Path("data/fortunes_ko.json"),
    Path("fortune_db/fortunes_ko.json"),
    Path("fortunes_ko.json"),
]

DEFAULT_ZODIACS = [
    "쥐",
    "소",
    "호랑이",
    "토끼",
    "용",
    "뱀",
    "말",
    "양",
    "원숭이",
    "닭",
    "개",
    "돼지",
]

MBTI_DIMENSIONS = [
    ("E", "I", "에너지 방향", "사람/활동(외향)", "혼자/내면(내향)"),
    ("S", "N", "정보 수집", "사실/현재(감각)", "의미/가능성(직관)"),
    ("T", "F", "의사결정", "원칙/논리(사고)", "가치/공감(감정)"),
    ("J", "P", "생활양식", "계획/정리(판단)", "유연/즉흥(인식)"),
]


# ===========================
# Helpers
# ===========================
@st.cache_data(show_spinner=False)
def load_db():
    last_err = None
    for p in DB_CANDIDATES:
        try:
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    return json.load(f), str(p)
        except Exception as e:
            last_err = e
    return None, f"DB 파일을 찾지 못했습니다. 후보 경로: {', '.join(map(str, DB_CANDIDATES))}\n마지막 에러: {last_err}"


def get_zodiac_list(db: dict) -> list[str]:
    z = db.get("zodiacs")
    if isinstance(z, list) and z:
        names = []
        for item in z:
            if isinstance(item, dict) and item.get("name"):
                names.append(str(item["name"]))
            elif isinstance(item, str):
                names.append(item)
        if len(names) == 12:
            return names
    return DEFAULT_ZODIACS


def zodiac_from_year(year: int, zodiacs: list[str]) -> str:
    # 2008년 = 쥐(자) 기준으로 12간지 순환
    # index = (year - 2008) % 12
    idx = (year - 2008) % 12
    return zodiacs[idx]


def calc_mbti_from_answers(answers: dict[str, str]) -> str | None:
    # answers: {"E/I": "E" or "I", ...}
    if not answers:
        return None
    letters = []
    for a, b, _, _, _ in MBTI_DIMENSIONS:
        key = f"{a}/{b}"
        v = answers.get(key)
        if v not in (a, b):
            return None
        letters.append(v)
    return "".join(letters)


def safe_get(d: dict, key: str, default: str = "") -> str:
    v = d.get(key, default)
    if v is None:
        return default
    return str(v)


def render_section(title: str, body: str):
    st.markdown(f"### {title}")
    if body.strip():
        st.write(body)
    else:
        st.write("-")


def render_lucky_point(lp: dict):
    if not isinstance(lp, dict):
        st.write("-")
        return
    color = safe_get(lp, "color")
    item = safe_get(lp, "item")
    number = safe_get(lp, "number")
    direction = safe_get(lp, "direction")
    parts = []
    if color:
        parts.append(f"색: {color}")
    if item:
        parts.append(f"아이템: {item}")
    if number:
        parts.append(f"숫자: {number}")
    if direction:
        parts.append(f"방향: {direction}")
    st.write(" · ".join(parts) if parts else "-")


def find_combo(db: dict, combo_key: str) -> dict | None:
    combos = db.get("combos")
    if isinstance(combos, dict) and combo_key in combos and isinstance(combos[combo_key], dict):
        return combos[combo_key]
    return None


# ===========================
# UI
# ===========================
st.set_page_config(page_title="2026 Fortune", page_icon="🔮", layout="centered")

st.markdown(
    """
    <style>
      .hero {
        padding: 22px 18px;
        border-radius: 18px;
        background: linear-gradient(135deg, #d9a7c7 0%, #a1c4fd 100%);
        color: white;
        text-align: center;
        margin-bottom: 18px;
      }
      .hero h1 { margin: 0; font-size: 28px; font-weight: 800; }
      .hero p { margin: 6px 0 0 0; font-size: 14px; opacity: .95; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
      <h1>{APP_TITLE}</h1>
      <p>{APP_SUBTITLE}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load DB
DB, DB_PATH_OR_ERR = load_db()
if DB is None:
    st.error(f"DB 로드 오류: {DB_PATH_OR_ERR}")
    st.stop()

ZODIACS = get_zodiac_list(DB)

# Inputs
st.markdown("## 입력")
name = st.text_input("이름 (결과에 표시돼요)", value="")

col1, col2, col3 = st.columns(3)
with col1:
    year = st.number_input("년", min_value=1900, max_value=2100, value=1990, step=1)
with col2:
    month = st.number_input("월", min_value=1, max_value=12, value=1, step=1)
with col3:
    day = st.number_input("일", min_value=1, max_value=31, value=1, step=1)

# Validate date
birth: date | None = None
try:
    birth = date(int(year), int(month), int(day))
except Exception:
    st.warning("생년월일이 올바르지 않아요. (월/일 확인)")

st.markdown("## MBTI")
mbti_mode = st.radio("MBTI 입력 방식", ["간단 검사", "직접 선택"], horizontal=True)

mbti = None
if mbti_mode == "직접 선택":
    mbti = st.selectbox(
        "MBTI 선택",
        [
            "ISTJ",
            "ISFJ",
            "INFJ",
            "INTJ",
            "ISTP",
            "ISFP",
            "INFP",
            "INTP",
            "ESTP",
            "ESFP",
            "ENFP",
            "ENTP",
            "ESTJ",
            "ESFJ",
            "ENFJ",
            "ENTJ",
        ],
        index=10,  # ENFP
    )
else:
    answers: dict[str, str] = {}
    for a, b, title, left_label, right_label in MBTI_DIMENSIONS:
        key = f"{a}/{b}"
        answers[key] = st.radio(
            f"{title}",
            options=[a, b],
            format_func=lambda x, ll=left_label, rl=right_label, aa=a, bb=b: f"{x} · {ll}" if x == aa else f"{x} · {rl}",
            horizontal=True,
        )
    mbti = calc_mbti_from_answers(answers)

# Action button
st.markdown("---")
if st.button("결과 보기", use_container_width=True):
    if birth is None:
        st.error("생년월일이 올바르지 않아서 결과를 만들 수 없어요.")
        st.stop()

    if not mbti:
        st.error("MBTI를 선택/검사해 주세요.")
        st.stop()

    zodiac = zodiac_from_year(birth.year, ZODIACS)
    combo_key = f"{zodiac}_{mbti}"

    combo = find_combo(DB, combo_key)
    if combo is None:
        st.error(f"데이터에 조합 키가 없습니다: {combo_key}")
        st.stop()

    st.success("결과를 불러왔어요!")

    # Main
    st.markdown("## 결과")
    if name.strip():
        st.write(f"**{name}** 님")

    st.write(f"**띠 운세:** {zodiac}")
    st.write(f"**MBTI:** {mbti}")

    render_section("MBTI 특징", safe_get(combo, "mbti_trait"))
    render_section("사주 한 마디", safe_get(combo, "saju_message"))

    st.markdown("---")
    render_section("오늘 운세", safe_get(combo, "today"))
    render_section("내일 운세", safe_get(combo, "tomorrow"))

    st.markdown("---")
    render_section("2026 전체 운세", safe_get(combo, "year_2026"))

    st.markdown("---")
    st.markdown("## 조합 조언")
    render_section("연애운", safe_get(combo, "love"))
    render_section("재물운", safe_get(combo, "money"))
    render_section("일/학업운", safe_get(combo, "work"))
    render_section("건강운", safe_get(combo, "health"))

    st.markdown("---")
    st.markdown("## 행운 포인트")
    render_lucky_point(combo.get("lucky_point", {}))

    st.markdown("---")
    render_section("오늘의 액션팁", safe_get(combo, "action_tip"))
    render_section("주의할 점", safe_get(combo, "caution"))

    # Share
    st.markdown("---")
    st.button("🔗 링크 공유하기", use_container_width=True, disabled=True)
    st.caption("버튼을 누르면 ‘링크 공유’ 창이 뜹니다. (브라우저에서 공유 기능 사용)")

