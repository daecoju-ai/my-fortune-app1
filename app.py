import os
import json
import time
import hashlib
import datetime as dt
from dataclasses import dataclass

import streamlit as st

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="2026 띠 + MBTI + 사주 + 오늘/내일 운세 (완전 무료)",
    page_icon="🔮",
    layout="centered",
)

APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세"
APP_SUB = "완전 무료"

DB_PATH = "data/fortunes_ko.json"  # ✅ data 폴더에 있는 fortunes_ko.json 사용

ZODIAC_ORDER_EN = [
    "rat", "ox", "tiger", "rabbit", "dragon", "snake",
    "horse", "goat", "monkey", "rooster", "dog", "pig"
]

# =========================================================
# 유틸
# =========================================================
def stable_hash_int(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def normalize_zodiac_label(label: str) -> str:
    """Normalize zodiac label for DB key matching."""
    if not label:
        return ""
    s = str(label).strip()
    # common variants: '개띠' -> '개'
    if s.endswith("띠"):
        s = s[:-1].strip()
    return s

def load_db(path: str) -> tuple[dict | None, str | None]:
    if not os.path.exists(path):
        return None, f"DB 파일을 찾을 수 없습니다: {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            db = json.load(f)
        return db, None
    except Exception as e:
        return None, f"DB 로딩 실패: {e}"

def zodiac_from_year(year: int, db: dict | None = None) -> str:
    """Return Korean zodiac label (no trailing '띠'), with robust fallback."""
    try:
        y = int(year)
    except Exception:
        return ""
    idx = (y - 1984) % 12  # 1984 is rat
    zodiac_en = ZODIAC_ORDER_EN[idx]

    # Prefer DB mapping if present
    if isinstance(db, dict):
        z = db.get("zodiacs")
        if isinstance(z, list):
            for item in z:
                if isinstance(item, dict) and item.get("en") == zodiac_en:
                    return normalize_zodiac_label(item.get("name", ""))
        elif isinstance(z, dict):
            # legacy: dict with labels mapping
            labels = z.get("labels") if isinstance(z, dict) else None
            if isinstance(labels, dict) and zodiac_en in labels:
                return normalize_zodiac_label(labels[zodiac_en])

    # Hard fallback (DB 매핑이 깨져도 무조건 나옴)
    ko_names = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
    return ko_names[idx]

def get_combo_key(zodiac_label_ko: str, mbti_code: str) -> str:
    zl = normalize_zodiac_label(zodiac_label_ko)
    mb = (mbti_code or "").strip().upper()
    return f"{zl}_{mb}" if zl and mb else ""

def pick_field(combo: dict, key: str, default: str = "") -> str:
    if not isinstance(combo, dict):
        return default
    v = combo.get(key, default)
    if v is None:
        return default
    if isinstance(v, list):
        # list면 첫 값(혹은 join)로 표시
        return v[0] if v else default
    return str(v)

# =========================================================
# MBTI (직접 선택 / 12문항 / 16문항) — 구조 유지
# =========================================================
MBTI_LIST = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ",
]

MBTI_INFO = {
    "ISTJ": {"traits":"내향 · 현실 · 논리 · 계획"},
    "ISFJ": {"traits":"내향 · 현실 · 공감 · 계획"},
    "INFJ": {"traits":"내향 · 직관 · 공감 · 계획"},
    "INTJ": {"traits":"내향 · 직관 · 논리 · 계획"},
    "ISTP": {"traits":"내향 · 현실 · 논리 · 유연"},
    "ISFP": {"traits":"내향 · 현실 · 공감 · 유연"},
    "INFP": {"traits":"내향 · 직관 · 공감 · 유연"},
    "INTP": {"traits":"내향 · 직관 · 논리 · 유연"},
    "ESTP": {"traits":"외향 · 현실 · 논리 · 유연"},
    "ESFP": {"traits":"외향 · 현실 · 공감 · 유연"},
    "ENFP": {"traits":"외향 · 직관 · 공감 · 유연"},
    "ENTP": {"traits":"외향 · 직관 · 논리 · 유연"},
    "ESTJ": {"traits":"외향 · 현실 · 논리 · 계획"},
    "ESFJ": {"traits":"외향 · 현실 · 공감 · 계획"},
    "ENFJ": {"traits":"외향 · 직관 · 공감 · 계획"},
    "ENTJ": {"traits":"외향 · 직관 · 논리 · 계획"},
}

# =========================================================
# 결과 화면
# =========================================================
def render_result(payload: dict, db: dict):
    combos = db.get("combos", {}) if isinstance(db, dict) else {}
    y, m, d = payload.get("y"), payload.get("m"), payload.get("d")
    mbti_code = (payload.get("mbti") or "").strip().upper()

    zodiac_label = zodiac_from_year(y, db)  # ✅ 여기서 반드시 '개' 형태로 확보
    combo_key = get_combo_key(zodiac_label, mbti_code)

    if not combo_key:
        st.error("조합 키 생성에 실패했습니다. 생년/MBTI를 확인해주세요.")
        st.stop()

    combo = combos.get(combo_key, {})

    mbti_desc = MBTI_INFO.get(mbti_code, {})
    mbti_traits = mbti_desc.get("traits", "")

    # ✅ combos 키/필드명에 맞춰 가져옴 (너가 올린 DB 구조 기준)
    zodiac_fortune = pick_field(combo, "zodiac_fortune", "")
    saju_message   = pick_field(combo, "saju_message", "")
    today_fortune  = pick_field(combo, "today_fortune", "")
    tomorrow_fortune = pick_field(combo, "tomorrow_fortune", "")
    year_2026 = pick_field(combo, "year_2026", "")
    combo_advice = pick_field(combo, "combo_advice", "")

    # UI
    st.markdown("---")
    st.markdown("## 결과")

    st.markdown(f"**띠 운세:** {zodiac_label}띠" if zodiac_label else "**띠 운세:**")
    if zodiac_fortune:
        st.info(zodiac_fortune)

    st.markdown(f"**MBTI 특징:** {mbti_traits}" if mbti_traits else f"**MBTI:** {mbti_code}")

    st.markdown("### 사주 한 마디:")
    st.write(saju_message if saju_message else "—")

    st.markdown("### 오늘 운세:")
    st.write(today_fortune if today_fortune else "—")

    st.markdown("### 내일 운세:")
    st.write(tomorrow_fortune if tomorrow_fortune else "—")

    st.markdown("### 2026 전체 운세:")
    st.write(year_2026 if year_2026 else "—")

    st.markdown("### 조합 조언:")
    st.write(combo_advice if combo_advice else "—")

    st.markdown("---")
    # 결과 바로 밑 공유 버튼은 너가 원하던 구조대로 유지
    if st.button("친구에게 공유하기", use_container_width=True):
        st.success("공유하기 버튼 클릭! (여기에 공유 로직/카운트 연결)")

    if st.button("다시 입력", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

# =========================================================
# 메인
# =========================================================
def main():
    db, err = load_db(DB_PATH)
    if err:
        st.error(err)
        st.stop()

    st.markdown(
        f"""
        <div style="padding:16px 18px;border-radius:18px;background:linear-gradient(135deg,#c9b6ff,#bde6ff);box-shadow:0 10px 30px rgba(0,0,0,.08);">
          <div style="font-size:28px;font-weight:800;line-height:1.15;margin-bottom:6px;">{APP_TITLE}</div>
          <div style="font-size:16px;opacity:.9;">{APP_SUB}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.caption(f"DB 경로: {DB_PATH}")

    if "stage" not in st.session_state:
        st.session_state.stage = "input"
    if "payload" not in st.session_state:
        st.session_state.payload = {}

    # -----------------------------
    # 입력 화면 (간단 유지)
    # -----------------------------
    if st.session_state.stage == "input":
        st.markdown("## 입력")
        name = st.text_input("이름 (결과에 표시돼요)", value=st.session_state.payload.get("name",""))
        y = st.number_input("년", min_value=1900, max_value=2100, value=int(st.session_state.payload.get("y", 1990)))
        m = st.number_input("월", min_value=1, max_value=12, value=int(st.session_state.payload.get("m", 1)))
        d = st.number_input("일", min_value=1, max_value=31, value=int(st.session_state.payload.get("d", 1)))

        st.markdown("## MBTI")
        mbti_mode = st.radio("선택 방식", ["직접 선택", "모르면 12문항", "모르면 16문항"], horizontal=True)

        chosen_mbti = st.session_state.payload.get("mbti", "ENTJ")

        if mbti_mode == "직접 선택":
            chosen_mbti = st.selectbox("MBTI를 선택하세요", MBTI_LIST, index=MBTI_LIST.index(chosen_mbti) if chosen_mbti in MBTI_LIST else 0)
        else:
            # 여기서 12/16문항 UI는 기존 코드가 있다면 그대로 붙이면 됨
            # 지금은 구조만 유지(변화 금지 요청)
            st.info("12/16 문항 버전은 기존 그대로 유지해서 붙여주세요. (현재는 구조만 유지)")

        if st.button("결과 보기", use_container_width=True):
            st.session_state.payload = {"name": name, "y": int(y), "m": int(m), "d": int(d), "mbti": chosen_mbti}
            st.session_state.stage = "result"
            st.rerun()

    # -----------------------------
    # 결과 화면
    # -----------------------------
    elif st.session_state.stage == "result":
        render_result(st.session_state.payload, db)


if __name__ == "__main__":
    main()
