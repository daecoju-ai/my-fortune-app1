import os
import json
import glob
import hashlib
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


# -----------------------------
# Config
# -----------------------------
APP_TITLE = "오늘의 운세 + 타로"
DB_CANDIDATES = [
    "data/fortunes_ko_full.json",
    "data/fortunes_ko.json",
    "data/fortunes_ko_normalized.json",
]
TAROT_GLOBS = [
    "assets/tarot/majors/*.png",
    "assets/tarot/minors/*.png",
    "assets/tarot/*.png",
]


# -----------------------------
# Deterministic helpers
# -----------------------------
def _stable_int_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def _pick(items: List[str], seed: str, fallback: str = "-") -> str:
    if not items:
        return fallback
    idx = _stable_int_hash(seed) % len(items)
    val = items[idx]
    return val if (isinstance(val, str) and val.strip()) else fallback


def _now_kst() -> dt.datetime:
    # Streamlit Cloud is usually UTC
    return dt.datetime.utcnow() + dt.timedelta(hours=9)


# -----------------------------
# Zodiac
# -----------------------------
ZODIAC_ORDER = [
    "rat", "ox", "tiger", "rabbit", "dragon", "snake",
    "horse", "goat", "monkey", "rooster", "dog", "pig"
]
ZODIAC_LABELS = {
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


def zodiac_from_year(year: int) -> Tuple[str, str]:
    # 기준: 1900년 = rat(쥐띠)
    idx = (year - 1900) % 12
    key = ZODIAC_ORDER[idx]
    return key, ZODIAC_LABELS.get(key, key)


# -----------------------------
# DB loading
# -----------------------------
@st.cache_data(show_spinner=False)
def load_db() -> Dict[str, Any]:
    last_err = None
    for path in DB_CANDIDATES:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                last_err = f"{path}: {e}"
                continue
    return {"__error__": f"DB 파일을 찾거나 읽지 못했습니다. 마지막 오류: {last_err}"}


def get_zodiac_pool(db: Dict[str, Any], zodiac_key: str) -> Dict[str, List[str]]:
    """
    DB 스키마(현재 너 DB):
      db["pools"]["zodiac"][zodiac_key] = {
        "one_liner": [...],
        "saju_one_liner": [...],
        "today": [...],
        "tomorrow": [...],
        "year_2026": [...],
        "love_advice": [...],
        "money_advice": [...],
        "work_study_advice": [...],
        "health_advice": [...],
        "action_tip": [...],
      }
    """
    pools = db.get("pools", {})
    z = pools.get("zodiac", {})
    pool = z.get(zodiac_key, {})
    # 안전하게 list만 남김
    cleaned: Dict[str, List[str]] = {}
    if isinstance(pool, dict):
        for k, v in pool.items():
            if isinstance(v, list):
                cleaned[k] = v
    return cleaned


def get_combos(db: Dict[str, Any]) -> Dict[str, Any]:
    pools = db.get("pools", {})
    combos = pools.get("combos", {})
    return combos if isinstance(combos, dict) else {}


# -----------------------------
# Tarot image pick
# -----------------------------
def pick_tarot_image(seed: str) -> Optional[str]:
    candidates: List[str] = []
    for pattern in TAROT_GLOBS:
        candidates.extend(glob.glob(pattern))
    candidates = [p for p in candidates if os.path.exists(p)]
    if not candidates:
        return None
    candidates.sort()
    idx = _stable_int_hash(seed) % len(candidates)
    return candidates[idx]


# -----------------------------
# Build result
# -----------------------------
def build_result(db: Dict[str, Any], birth: dt.date, mbti: str) -> Dict[str, str]:
    zodiac_key, zodiac_label = zodiac_from_year(birth.year)
    zpool = get_zodiac_pool(db, zodiac_key)
    combos = get_combos(db)

    now = _now_kst()
    seed_base = f"{birth.isoformat()}|{mbti}|{zodiac_key}|{now.date().isoformat()}"

    def pick_z(field: str) -> str:
        return _pick(zpool.get(field, []), seed_base + f"|z|{field}")

    # ✅ 콤보 키는 label(개띠) 말고 key(dog)로 맞춰야 DB랑 매칭됨
    combo_key = f"{zodiac_key}_{mbti}"
    combo_obj = combos.get(combo_key, {})
    combo_one = "-"
    combo_adv = "-"
    if isinstance(combo_obj, dict):
        combo_one = _pick(combo_obj.get("one_liners", []), seed_base + "|c|one")
        combo_adv = _pick(combo_obj.get("advices", []), seed_base + "|c|adv")

    return {
        "zodiac_key": zodiac_key,
        "zodiac_label": zodiac_label,
        "mbti": mbti,
        "zodiac_one_liner": pick_z("one_liner"),
        "saju_one_liner": pick_z("saju_one_liner"),
        "today_fortune": pick_z("today"),
        "tomorrow_fortune": pick_z("tomorrow"),
        "year_overall": pick_z("year_2026"),
        "love_advice": pick_z("love_advice"),
        "money_advice": pick_z("money_advice"),
        "work_study_advice": pick_z("work_study_advice"),
        "health_advice": pick_z("health_advice"),
        "action_tip": pick_z("action_tip"),
        "combo_one_liner": combo_one,
        "combo_advice": combo_adv,
    }


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="centered")
st.title("🔮 오늘의 운세 + 타로")

db = load_db()
if "__error__" in db:
    st.error(db["__error__"])
    st.stop()

with st.form("input_form"):
    birth = st.date_input("생년월일", value=dt.date(1995, 1, 1))
    mbti = st.text_input("MBTI (예: INTP)", value="INTP").strip().upper()
    submitted = st.form_submit_button("결과 보기")

if not submitted:
    st.caption("생년월일과 MBTI를 입력하고 결과 보기를 눌러줘.")
    st.stop()

if len(mbti) != 4:
    st.warning("MBTI는 4글자 형태로 입력해줘. 예: INTP")
    st.stop()

result = build_result(db, birth, mbti)

st.markdown("---")
st.subheader("결과")

st.markdown(f"**띠 운세:** {result['zodiac_label']}")
st.markdown(f"**MBTI:** {result['mbti']}")

# Tarot image
tarot_path = pick_tarot_image(f"{birth.isoformat()}|{mbti}|{result['zodiac_key']}")
if tarot_path and os.path.exists(tarot_path):
    st.image(tarot_path, use_container_width=True)

st.markdown("---")
st.subheader("띠 한 마디")
st.write(result["zodiac_one_liner"])

st.subheader("사주 한 마디")
st.write(result["saju_one_liner"])

st.subheader("오늘 운세")
st.write(result["today_fortune"])

st.subheader("내일 운세")
st.write(result["tomorrow_fortune"])

st.subheader("2026 전체 운세")
st.write(result["year_overall"])

st.subheader("조합 한 줄")
st.write(result["combo_one_liner"])

st.subheader("조합 조언")
st.write(result["combo_advice"])

with st.expander("추가 조언(카테고리)"):
    st.markdown("**연애:**")
    st.write(result["love_advice"])
    st.markdown("**금전:**")
    st.write(result["money_advice"])
    st.markdown("**일/공부:**")
    st.write(result["work_study_advice"])
    st.markdown("**건강:**")
    st.write(result["health_advice"])
    st.markdown("**행동 팁:**")
    st.write(result["action_tip"])
