# app.py
import json
import hashlib
from datetime import date
from pathlib import Path

import streamlit as st


# -----------------------------
# Config
# -----------------------------
APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세"
DB_PATH = Path(__file__).resolve().parent / "data" / "fortunes_ko.json"


# -----------------------------
# Helpers
# -----------------------------
def load_db(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        st.error(f"DB 로드 오류: {e}\n\n경로: {path.as_posix()}")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"DB JSON 파싱 오류: {e}\n\n파일: {path.as_posix()}")
        st.stop()


def stable_hash_int(text: str) -> int:
    """Stable across sessions / deployments."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def infer_mbti_from_birth(yyyy: int, mm: int, dd: int, mbti_list: list[str]) -> str:
    # Deterministic mapping: same birthdate => same MBTI (not claiming real MBTI)
    key = f"{yyyy:04d}-{mm:02d}-{dd:02d}"
    idx = stable_hash_int(key) % len(mbti_list)
    return mbti_list[idx]


def zodiac_from_year(yyyy: int, zodiacs: list[dict]) -> str:
    """
    Korean 띠 mapping with 2020 == 쥐 (Rat).
    2020: 쥐, 2021: 소, 2022: 호랑이, 2023: 토끼, 2024: 용, 2025: 뱀,
    2026: 말, 2027: 양, 2028: 원숭이, 2029: 닭, 2030: 개, 2031: 돼지
    """
    if not zodiacs:
        return ""
    base_year = 2020
    idx = (yyyy - base_year) % 12
    return zodiacs[idx]["name"]


def pick_tarot_card(yyyy: int, mm: int, dd: int, tarot_cards: list[dict]) -> dict | None:
    if not tarot_cards:
        return None
    key = f"tarot::{yyyy:04d}-{mm:02d}-{dd:02d}"
    idx = stable_hash_int(key) % len(tarot_cards)
    return tarot_cards[idx]


def render_result(name: str, zodiac: str, mbti: str, rec: dict, tarot: dict | None):
    st.subheader("결과")

    # 핵심
    st.markdown(f"**이름:** {name}")
    st.markdown(f"**띠 운세:** {zodiac}")
    st.markdown(f"**MBTI 특징:** {mbti}")

    # 문장들
    st.markdown("---")
    st.markdown("### 사주 한 마디")
    st.write(rec.get("saju_message", ""))

    st.markdown("---")
    st.markdown("### 오늘 운세")
    st.write(rec.get("today", ""))

    st.markdown("### 내일 운세")
    st.write(rec.get("tomorrow", ""))

    st.markdown("---")
    st.markdown("### 2026 전체 운세")
    st.write(rec.get("year_2026", ""))

    # 분야별
    st.markdown("---")
    st.markdown("### 조합 조언")
    st.info(
        "\n".join(
            [
                f"연애운: {rec.get('love','')}",
                f"재물운: {rec.get('money','')}",
                f"일/학업운: {rec.get('work','')}",
                f"건강운: {rec.get('health','')}",
            ]
        )
    )

    # 행운 포인트
    lp = rec.get("lucky_point") or {}
    st.markdown("---")
    st.markdown("### 행운 포인트")
    st.write(
        " · ".join(
            [
                f"색: {lp.get('color','')}",
                f"아이템: {lp.get('item','')}",
                f"숫자: {lp.get('number','')}",
                f"방향: {lp.get('direction','')}",
            ]
        )
    )

    # 액션팁 / 주의
    st.markdown("---")
    st.markdown("### 오늘의 액션팁")
    st.write(rec.get("action_tip", ""))

    st.markdown("### 주의할 점")
    st.write(rec.get("caution", ""))

    # 타로
    if tarot:
        st.markdown("---")
        st.markdown("### 오늘의 타로 카드")
        st.write(f"**{tarot.get('name','')}**")
        if tarot.get("meaning"):
            st.write(tarot["meaning"])


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="2026 Fortune", page_icon="🔮", layout="centered")
st.title(APP_TITLE)
st.caption("완전 무료")

db = load_db(DB_PATH)

# Input
st.header("입력")
name = st.text_input("이름 (결과에 표시돼요)", value="", max_chars=20)

col1, col2, col3 = st.columns(3)
with col1:
    yyyy = st.number_input("년", min_value=1900, max_value=2100, value=2000, step=1)
with col2:
    mm = st.number_input("월", min_value=1, max_value=12, value=1, step=1)
with col3:
    dd = st.number_input("일", min_value=1, max_value=31, value=1, step=1)

# Validate birthdate strictly
try:
    born = date(int(yyyy), int(mm), int(dd))
    valid_birth = True
except ValueError:
    valid_birth = False

if not valid_birth:
    st.warning("생년월일이 올바르지 않아요. (월/일 확인)")
    st.stop()

# Compute deterministic keys
zodiac = zodiac_from_year(int(yyyy), db.get("zodiacs", []))
mbti = infer_mbti_from_birth(int(yyyy), int(mm), int(dd), db.get("mbti_list", []))
combo_key = f"{zodiac}_{mbti}"

# Lookup record
combos = db.get("combos", {})
rec = combos.get(combo_key)

if not rec:
    st.error(f"데이터에 조합 키가 없습니다: {combo_key}")
    # debug hints
    st.info("DB의 combos 키 형식이 '띠_MBTI' 인지 확인하세요. 예: '쥐_ENFP'")
    st.stop()

# Tarot
tarot = pick_tarot_card(int(yyyy), int(mm), int(dd), db.get("tarot_cards", []))

render_result(name or "이름없음", zodiac, mbti, rec, tarot)

st.markdown("---")
st.button("링크 공유하기")
st.caption("버튼을 누르면 '링크 공유' 창이 뜹니다.")
