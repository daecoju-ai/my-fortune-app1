# app.py
import json
import hashlib
from pathlib import Path
import streamlit as st


# =========================
# Config
# =========================
APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세 (완전 무료)"
DB_REL_PATHS = [
    Path(__file__).parent / "data" / "fortunes_ko.json",  # recommended (repo structure)
    Path(__file__).parent / "fortunes_ko.json",           # fallback (root)
]

# 띠 계산용(12간지) : index = (year % 12)
# 2016 원숭이(0), 2017 닭(1), 2018 개(2), 2019 돼지(3), 2020 쥐(4) ...
ZODIAC_BY_YEAR_MOD12 = [
    "원숭이", "닭", "개", "돼지",
    "쥐", "소", "호랑이", "토끼",
    "용", "뱀", "말", "양",
]


# =========================
# Helpers
# =========================
@st.cache_data(show_spinner=False)
def load_db() -> dict:
    last_err = None
    for p in DB_REL_PATHS:
        try:
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
            last_err = FileNotFoundError(str(p))
        except Exception as e:
            last_err = e
    raise last_err or FileNotFoundError("fortunes_ko.json not found")


def stable_hash_int(text: str) -> int:
    """Deterministic int from text."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def pick_mbti(birth_ymd: str, mbti_list: list[str]) -> str:
    idx = stable_hash_int(birth_ymd + "|mbti") % len(mbti_list)
    return mbti_list[idx]


def zodiac_from_year(year: int) -> str:
    return ZODIAC_BY_YEAR_MOD12[year % 12]


def pick_tarot(birth_ymd: str, tarot_dict: dict) -> tuple[str, str]:
    names = list(tarot_dict.keys())
    idx = stable_hash_int(birth_ymd + "|tarot") % len(names)
    name = names[idx]
    return name, str(tarot_dict.get(name, "")).strip()


def get_combo(db: dict, zodiac: str, mbti: str) -> dict | None:
    combos = db.get("combos", {})
    return combos.get(f"{zodiac}_{mbti}")


def safe_text(x) -> str:
    if x is None:
        return ""
    return str(x).strip()


def render_kv(title: str, value: str):
    st.markdown(f"### {title}")
    if value.strip():
        st.write(value)
    else:
        st.info("데이터가 비어있어요. (DB 확인 필요)")


# =========================
# UI
# =========================
st.set_page_config(page_title="2026 Fortune", page_icon="🔮", layout="centered")
st.title(APP_TITLE)

try:
    db = load_db()
except Exception as e:
    st.error(f"DB 로드 오류: {e}")
    st.stop()

# Inputs
st.subheader("입력")
name = st.text_input("이름 (결과에 표시돼요)", value="")
col1, col2, col3 = st.columns(3)
with col1:
    year = st.number_input("년", min_value=1900, max_value=2100, value=1990, step=1)
with col2:
    month = st.number_input("월", min_value=1, max_value=12, value=1, step=1)
with col3:
    day = st.number_input("일", min_value=1, max_value=31, value=1, step=1)

# Validate date (simple)
birth_ymd = None
try:
    birth_date = datetime.date(int(year), int(month), int(day))
    birth_ymd = birth_date.isoformat()
except Exception:
    st.warning("생년월일이 올바르지 않아요. (월/일 확인)")
    st.stop()

# Derive keys (deterministic by birthdate only)
zodiac = zodiac_from_year(int(year))
mbti_list = db.get("mbti_list") or []
if not mbti_list:
    st.error("DB에 mbti_list 가 없습니다.")
    st.stop()

mbti = pick_mbti(birth_ymd, mbti_list)
combo = get_combo(db, zodiac, mbti)

st.divider()
st.subheader("결과")
if name.strip():
    st.caption(f"이름: {name.strip()}")

st.write(f"**띠:** {zodiac}")
st.write(f"**MBTI:** {mbti}")

if combo is None:
    st.error(f"데이터에 조합 키가 없습니다: {zodiac}_{mbti}")
    st.stop()

# Main blocks (ALL from DB)
render_kv("띠 운세", safe_text(combo.get("zodiac_fortune")))
render_kv("MBTI 특징", safe_text(combo.get("mbti_trait")))
render_kv("MBTI 영향", safe_text(combo.get("mbti_influence")))
render_kv("사주 한 마디", safe_text(combo.get("saju_message")))

st.divider()
render_kv("오늘 운세", safe_text(combo.get("today")))
render_kv("내일 운세", safe_text(combo.get("tomorrow")))
render_kv("2026 전체 운세", safe_text(combo.get("year_2026")))

st.divider()
st.markdown("### 조합 조언")
st.write(f"- **연애운:** {safe_text(combo.get('love'))}")
st.write(f"- **재물운:** {safe_text(combo.get('money'))}")
st.write(f"- **일/학업운:** {safe_text(combo.get('work'))}")
st.write(f"- **건강운:** {safe_text(combo.get('health'))}")

st.divider()
lp = combo.get("lucky_point") or {}
st.markdown("### 행운 포인트")
st.write(
    f"색: **{safe_text(lp.get('color'))}** · "
    f"아이템: **{safe_text(lp.get('item'))}** · "
    f"숫자: **{safe_text(lp.get('number'))}** · "
    f"방향: **{safe_text(lp.get('direction'))}**"
)

render_kv("오늘의 액션팁", safe_text(combo.get("action_tip")))
render_kv("주의할 점", safe_text(combo.get("caution")))

st.divider()
tarot_dict = db.get("tarot_cards") or {}
if tarot_dict:
    tarot_name, tarot_meaning = pick_tarot(birth_ymd, tarot_dict)
    st.markdown("### 오늘의 타로 카드")
    st.write(f"**{tarot_name}**")
    if tarot_meaning:
        st.caption(tarot_meaning)

# Footer
st.caption("※ 결과는 입력한 생년월일 기준으로 항상 동일하게 생성됩니다. (신뢰도/일관성 목적)")
