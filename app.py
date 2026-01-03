# app.py
# Streamlit Fortune App (KO only) - stable & DB-driven
# - Robust DB path discovery (data/fortunes_ko.json first)
# - Safe session_state access (no AttributeError)
# - 4-axis MBTI mini test (E/I, S/N, T/F, J/P)
# - Deterministic results for same (birthdate + MBTI)
# - All texts come from DB (no auto-generated action tip text)

from __future__ import annotations

import json
import hashlib
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import streamlit as st


def stable_hash_int(s: str) -> int:
    """Stable across runs (unlike Python's built-in hash())."""
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def ss_get(key: str, default: Any = None) -> Any:
    return st.session_state.get(key, default)


def ss_setdefault(key: str, default: Any) -> Any:
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def safe_str(v: Any) -> str:
    return "" if v is None else str(v)


def find_db_file() -> Optional[Path]:
    """
    Priority:
      1) ./data/fortunes_ko.json
      2) ./fortune_db/fortunes_ko.json  (older structure)
      3) ./data/fortune_db/fortunes_ko.json (accidental nesting)
      4) ./fortunes_ko.json (repo root)
    """
    candidates = [
        Path("data") / "fortunes_ko.json",
        Path("fortune_db") / "fortunes_ko.json",
        Path("data") / "fortune_db" / "fortunes_ko.json",
        Path("fortunes_ko.json"),
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    return None


@st.cache_data(show_spinner=False)
def load_db() -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    db_path = find_db_file()
    if not db_path:
        root = Path(".")
        visible = []
        for p in root.rglob("*.json"):
            visible.append(str(p))
            if len(visible) >= 25:
                break
        msg = (
            "DB 파일을 찾을 수 없습니다.\n\n"
            "찾는 파일명: fortunes_ko.json\n"
            "찾는 경로 후보: data/, fortune_db/, repo root\n\n"
            "현재 발견된 json(최대 25개):\n- " + "\n- ".join(visible)
        )
        return None, None, msg

    try:
        db = json.loads(db_path.read_text(encoding="utf-8"))
    except Exception as e:
        return None, str(db_path), f"DB 로드 실패: {e}"

    if not isinstance(db, dict) or "combos" not in db or not isinstance(db["combos"], dict):
        return None, str(db_path), "DB 구조가 올바르지 않습니다. (최상위에 'combos' 딕셔너리가 필요)"
    return db, str(db_path), None


ZODIAC_KO = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
ANCHOR_YEAR = 2008  # 2008=쥐


def zodiac_from_year(y: int) -> str:
    return ZODIAC_KO[(y - ANCHOR_YEAR) % 12]


def mbti_from_answers(ei: str, sn: str, tf: str, jp: str) -> str:
    return f"{ei}{sn}{tf}{jp}".upper()


def infer_mbti_from_birth(y: int, m: int, d: int) -> str:
    key = f"{y:04d}-{m:02d}-{d:02d}"
    x = stable_hash_int(key)
    ei = "E" if (x & 1) else "I"
    sn = "S" if (x & 2) else "N"
    tf = "T" if (x & 4) else "F"
    jp = "J" if (x & 8) else "P"
    return mbti_from_answers(ei, sn, tf, jp)


def init_state():
    ss_setdefault("stage", "input")  # input -> mbti -> result
    ss_setdefault("name", "")
    ss_setdefault("y", 2000)
    ss_setdefault("m", 1)
    ss_setdefault("d", 1)
    ss_setdefault("mbti_answers", {"ei": None, "sn": None, "tf": None, "jp": None})
    ss_setdefault("mbti_final", None)
    ss_setdefault("last_combo_key", None)


def go(stage: str):
    st.session_state["stage"] = stage


def reset_all():
    st.session_state.clear()
    init_state()
    go("input")


def render_header():
    st.markdown(
        """
        <div style="padding:18px 16px;border-radius:18px;background:linear-gradient(90deg,#c7b5ff,#b7e2ff);">
          <div style="font-size:22px;font-weight:800;">🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세</div>
          <div style="opacity:.9;margin-top:6px;">완전 무료</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")


def render_input():
    st.subheader("입력")
    st.text_input("이름 (결과에 표시돼요)", key="name")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input("년", min_value=1900, max_value=2100, step=1, key="y")
    with col2:
        st.number_input("월", min_value=1, max_value=12, step=1, key="m")
    with col3:
        st.number_input("일", min_value=1, max_value=31, step=1, key="d")

    y, m, d = int(ss_get("y")), int(ss_get("m")), int(ss_get("d"))
    try:
        date(y, m, d)
        valid = True
    except Exception:
        valid = False

    if not valid:
        st.warning("생년월일이 올바르지 않아요. (월/일 확인)")
        return

    c1, c2 = st.columns(2)
    with c1:
        if st.button("MBTI 간단 검사로 진행"):
            go("mbti")
    with c2:
        if st.button("바로 결과 보기 (MBTI 자동 추정)"):
            st.session_state["mbti_final"] = infer_mbti_from_birth(y, m, d)
            go("result")

    st.caption("※ 같은 생년월일 + 같은 MBTI면 결과는 항상 동일하게 나오도록 설계했습니다.")


def render_mbti():
    st.subheader("MBTI 간단 검사 (4문항)")
    st.caption("각 축에서 더 가까운 쪽을 하나씩 골라주세요. (결과는 DB 조합키에 그대로 사용됩니다.)")

    a = ss_get("mbti_answers", {"ei": None, "sn": None, "tf": None, "jp": None})

    a["ei"] = st.radio(
        "에너지 방향",
        ["E", "I"],
        format_func=lambda x: "E · 외향(사람/활동)" if x == "E" else "I · 내향(혼자/집중)",
        index=0 if a.get("ei") in (None, "E") else 1,
    )
    a["sn"] = st.radio(
        "정보 인식",
        ["S", "N"],
        format_func=lambda x: "S · 사실/연새(감각)" if x == "S" else "N · 의미/가능성(직관)",
        index=0 if a.get("sn") in (None, "S") else 1,
    )
    a["tf"] = st.radio(
        "의사결정",
        ["T", "F"],
        format_func=lambda x: "T · 원칙/논리(사고)" if x == "T" else "F · 가치/공감(감정)",
        index=0 if a.get("tf") in (None, "T") else 1,
    )
    a["jp"] = st.radio(
        "생활양식",
        ["J", "P"],
        format_func=lambda x: "J · 계획/정리(판단)" if x == "J" else "P · 유연/즉흥(인식)",
        index=0 if a.get("jp") in (None, "J") else 1,
    )

    st.session_state["mbti_answers"] = a

    mbti = mbti_from_answers(a["ei"], a["sn"], a["tf"], a["jp"])
    st.info(f"선택된 MBTI: **{mbti}**")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("결과 보기"):
            st.session_state["mbti_final"] = mbti
            go("result")
    with c2:
        if st.button("처음으로"):
            go("input")


def pick_record(db: Dict[str, Any], zodiac: str, mbti: str) -> Tuple[Optional[Dict[str, Any]], str]:
    key = f"{zodiac}_{mbti}"
    rec = db.get("combos", {}).get(key)
    return rec, key


def render_result(db: Dict[str, Any]):
    st.subheader("결과")

    y, m, d = int(ss_get("y")), int(ss_get("m")), int(ss_get("d"))
    zodiac = zodiac_from_year(y)
    mbti = ss_get("mbti_final") or infer_mbti_from_birth(y, m, d)

    rec, combo_key = pick_record(db, zodiac, mbti)
    st.session_state["last_combo_key"] = combo_key

    st.write(f"**띠 운세:** {zodiac}")
    st.write(f"**MBTI 특징:** {mbti}")
    st.write("")

    if not rec:
        st.error(f"데이터에 조합 키가 없습니다: {combo_key}")
        combos = db.get("combos", {})
        similar = [k for k in combos.keys() if k.startswith(zodiac + "_")]
        if similar:
            st.info(f"DB에 '{zodiac}_'로 시작하는 키 예시(최대 20개):\n- " + "\n- ".join(similar[:20]))
        else:
            st.info(f"DB에서 '{zodiac}_'로 시작하는 키가 하나도 없습니다. (띠 이름 표기/철자 확인 필요)")
        if st.button("다시 입력"):
            go("input")
        return

    def section(title: str, body: str):
        if body.strip():
            st.markdown(f"### {title}")
            st.write(body)

    section("사주 한 마디", safe_str(rec.get("saju_message")))
    section("오늘 운세", safe_str(rec.get("today")))
    section("내일 운세", safe_str(rec.get("tomorrow")))
    section("2026 전체 운세", safe_str(rec.get("year_2026")))

    st.divider()
    st.markdown("### 조합 조언")

    box_lines = []
    for label, k in [("연애운", "love"), ("재물운", "money"), ("일/학업운", "work"), ("건강운", "health")]:
        v = safe_str(rec.get(k))
        box_lines.append(f"**{label}:** {v}" if v else f"**{label}:**")
    st.info("\n\n".join(box_lines))

    lp = rec.get("lucky_point") or {}
    if isinstance(lp, dict) and any(str(lp.get(x, "")).strip() for x in ["color", "item", "number", "direction"]):
        st.markdown("### 행운 포인트")
        st.write(
            f"색: {safe_str(lp.get('color'))} · 아이템: {safe_str(lp.get('item'))} · 숫자: {safe_str(lp.get('number'))} · 방향: {safe_str(lp.get('direction'))}"
        )

    action_tip = safe_str(rec.get("action_tip"))
    caution = safe_str(rec.get("caution"))

    if action_tip.strip():
        st.markdown("### 오늘의 액션팁")
        st.write(action_tip)

    if caution.strip():
        st.markdown("### 주의할 점")
        st.write(caution)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("처음으로"):
            go("input")
    with c2:
        if st.button("전체 초기화"):
            reset_all()


def main():
    st.set_page_config(page_title="2026 Fortune", page_icon="🔮", layout="centered")
    init_state()
    render_header()

    db, db_path, err = load_db()
    if err:
        st.error(err)
        return
    st.caption(f"DB 경로: {db_path}")

    stage = ss_get("stage", "input")
    if stage not in ("input", "mbti", "result"):
        st.session_state["stage"] = "input"
        stage = "input"

    if stage == "input":
        render_input()
    elif stage == "mbti":
        render_mbti()
    else:
        render_result(db)


if __name__ == "__main__":
    main()
