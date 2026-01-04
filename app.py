import os
import json
import time
import math
import glob
import hashlib
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
from PIL import Image

# ============================================================
# Config
# ============================================================
APP_TITLE = "운세 + 타로"
DATA_DIR = "data"
DEFAULT_DB_CANDIDATES = [
    os.path.join(DATA_DIR, "fortunes_ko.json"),
    os.path.join(DATA_DIR, "fortunes_ko_NO_COMBOS.json"),
    os.path.join(DATA_DIR, "fortune_db.json"),
]

# Mini-game (stopwatch) settings
# "success window": stop time must be between these seconds (inclusive)
GAME_TARGET_MIN = 20.260
GAME_TARGET_MAX = 20.269
GAME_DEFAULT_ATTEMPTS = 3          # 기본 도전 횟수
GAME_REVIVE_BONUS = 1              # 공유로 부활 1회
GAME_TICK_SEC = 0.05               # 실시간 타이머 업데이트 간격
GAME_MAX_RUN_SEC = 60.0            # 너무 오래 눌러도 끊기게 안전장치

KST_OFFSET = dt.timedelta(hours=9)

# ============================================================
# Helpers: deterministic RNG
# ============================================================
def _stable_int_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def _pick(items: List[str], seed: str) -> str:
    if not items:
        return "—"
    idx = _stable_int_hash(seed) % len(items)
    return items[idx]

def _now_kst() -> dt.datetime:
    # Streamlit Cloud is usually UTC; convert to KST
    return dt.datetime.utcnow() + KST_OFFSET

def _today_kst_date() -> dt.date:
    return _now_kst().date()

# ============================================================
# Zodiac (띠) - "연도 기준 12띠" (현재 구현: 양력 연도 기준)
# ============================================================
ZODIAC_ORDER = ["rat", "ox", "tiger", "rabbit", "dragon", "snake",
                "horse", "goat", "monkey", "rooster", "dog", "pig"]

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
    # 기준: 1900년이 쥐띠
    idx = (year - 1900) % 12
    key = ZODIAC_ORDER[idx]
    return key, ZODIAC_LABELS.get(key, key)

# ============================================================
# DB Loading
# ============================================================
@st.cache_data(show_spinner=False)
def load_db() -> Dict[str, Any]:
    # 1) candidates
    for p in DEFAULT_DB_CANDIDATES:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

    # 2) fallback: any fortunes_ko*.json in data
    for p in sorted(glob.glob(os.path.join(DATA_DIR, "fortunes_ko*.json"))):
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

    return {"__error__": f"DB 파일을 찾을 수 없습니다. data 폴더에 fortunes_ko.json 이 있어야 합니다."}

def get_pool(db: Dict[str, Any]) -> Dict[str, List[str]]:
    # expected: db["pools"]
    pools = db.get("pools", {})
    if isinstance(pools, dict):
        return pools
    return {}

# ============================================================
# Tarot image pick
# ============================================================
def pick_tarot_image(seed: str) -> Optional[str]:
    # assets/tarot/majors/*.png, assets/tarot/minors/*.png, assets/tarot/*.png
    patterns = [
        "assets/tarot/majors/*.png",
        "assets/tarot/minors/*.png",
        "assets/tarot/*.png",
        "assets/tarot/majors/*.jpg",
        "assets/tarot/minors/*.jpg",
        "assets/tarot/*.jpg",
        "assets/tarot/majors/*.webp",
        "assets/tarot/minors/*.webp",
        "assets/tarot/*.webp",
    ]
    candidates: List[str] = []
    for pat in patterns:
        candidates.extend(glob.glob(pat))
    candidates = [c for c in candidates if os.path.exists(c)]

    if not candidates:
        return None

    idx = _stable_int_hash(seed) % len(candidates)
    return candidates[idx]

# ============================================================
# Build result (NO COMBOS)
# ============================================================
MBTI_TRAITS = {
    "ISTJ": "내향 · 감각 · 논리 · 계획",
    "ISFJ": "내향 · 감각 · 감정 · 계획",
    "INFJ": "내향 · 직관 · 감정 · 계획",
    "INTJ": "내향 · 직관 · 논리 · 계획",
    "ISTP": "내향 · 감각 · 논리 · 유연",
    "ISFP": "내향 · 감각 · 감정 · 유연",
    "INFP": "내향 · 직관 · 감정 · 유연",
    "INTP": "내향 · 직관 · 논리 · 유연",
    "ESTP": "외향 · 감각 · 논리 · 유연",
    "ESFP": "외향 · 감각 · 감정 · 유연",
    "ENFP": "외향 · 직관 · 감정 · 유연",
    "ENTP": "외향 · 직관 · 논리 · 유연",
    "ESTJ": "외향 · 감각 · 논리 · 계획",
    "ESFJ": "외향 · 감각 · 감정 · 계획",
    "ENFJ": "외향 · 직관 · 감정 · 계획",
    "ENTJ": "외향 · 직관 · 논리 · 계획",
}

def build_result(db: Dict[str, Any], birth: dt.date, mbti: str) -> Dict[str, Any]:
    pools = get_pool(db)

    zodiac_key, zodiac_label = zodiac_from_year(birth.year)

    # seed base: birth + today
    today = _today_kst_date()
    seed_base = f"{birth.isoformat()}|{mbti}|{zodiac_key}|{today.isoformat()}"

    def pick_pool(pool_name: str, extra: str = "") -> str:
        items = pools.get(pool_name, [])
        return _pick(items, seed_base + "|" + pool_name + "|" + extra)

    # 띠 한마디: zodiac_one_liner or zodiac_one_liners
    zodiac_one = "—"
    if "zodiac_one_liner" in pools:
        zodiac_one = pick_pool("zodiac_one_liner", zodiac_key)
    elif "zodiac_one_liners" in pools:
        zodiac_one = pick_pool("zodiac_one_liners", zodiac_key)

    result = {
        "zodiac_key": zodiac_key,
        "zodiac_label": zodiac_label,
        "mbti": mbti,
        "mbti_traits": MBTI_TRAITS.get(mbti, "—"),
        "zodiac_one_liner": zodiac_one or "—",
        "saju_one_liner": pick_pool("saju_one_liners", "saju"),
        "today_fortune": pick_pool("today_fortunes", "today"),
        "tomorrow_fortune": pick_pool("tomorrow_fortunes", "tomorrow"),
        "year_overall": pick_pool("year_overall_2026", "2026"),
        # 조언(조합X): 그냥 advice 풀에서 뽑아서 보여줌
        "advice": pick_pool("general_advice", "advice"),
        # 추가 조언(카테고리)
        "love_advice": pick_pool("love_advice", "love"),
        "money_advice": pick_pool("money_advice", "money"),
        "work_study_advice": pick_pool("work_study_advice", "work"),
        "health_advice": pick_pool("health_advice", "health"),
        "action_tip": pick_pool("action_tip", "action"),
    }
    return result

# ============================================================
# UI helpers
# ============================================================
def inject_styles():
    st.markdown(
        """
        <style>
          .card {
            border-radius: 14px;
            padding: 16px 18px;
            border: 1px solid rgba(0,0,0,0.08);
            background: rgba(255,255,255,0.7);
            backdrop-filter: blur(6px);
          }
          .card-result {
            background: linear-gradient(135deg, rgba(255, 240, 246, 0.7), rgba(240, 248, 255, 0.7));
          }
          .small-muted { color: rgba(0,0,0,0.55); font-size: 0.92rem; }
          .big { font-size: 2.1rem; font-weight: 800; margin: 0.4rem 0 0.2rem 0; }
          .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
          .game-box {
            border-radius: 14px;
            padding: 14px 16px;
            border: 1px dashed rgba(0,0,0,0.18);
            background: rgba(255,255,255,0.55);
          }
          .pill {
            display:inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid rgba(0,0,0,0.12);
            background: rgba(255,255,255,0.75);
            margin-right: 6px;
            font-size: 0.9rem;
          }
        </style>
        """,
        unsafe_allow_html=True
    )

def copy_url_button(label: str = "친구에게 공유하기 (URL 복사)"):
    # JS clipboard copy
    st.components.v1.html(
        f"""
        <button id="copyBtn" style="
            width:100%;
            padding:12px 14px;
            border-radius:12px;
            border:1px solid rgba(0,0,0,0.15);
            background:white;
            font-weight:700;
            cursor:pointer;
        ">{label}</button>
        <script>
          const btn = document.getElementById("copyBtn");
          btn.addEventListener("click", async () => {{
            try {{
              await navigator.clipboard.writeText(window.location.href);
              btn.innerText = "복사 완료! (붙여넣기 하면 돼요)";
              setTimeout(()=>btn.innerText="{label}", 1600);
            }} catch (e) {{
              btn.innerText = "복사 실패: 브라우저 권한 확인";
              setTimeout(()=>btn.innerText="{label}", 1600);
            }}
          }});
        </script>
        """,
        height=60
    )

# ============================================================
# Mini-game state stored in URL query params + session
# ============================================================
def _get_query_int(key: str, default: int) -> int:
    try:
        # Streamlit new API
        v = st.query_params.get(key, None)
        if v is None:
            return default
        if isinstance(v, list):
            v = v[0] if v else None
        return int(v)
    except Exception:
        return default

def _set_query_int(key: str, value: int):
    try:
        st.query_params[key] = str(value)
    except Exception:
        # fallback for older streamlit
        st.experimental_set_query_params(**{key: str(value)})

def _get_query_str(key: str, default: str = "") -> str:
    try:
        v = st.query_params.get(key, None)
        if v is None:
            return default
        if isinstance(v, list):
            v = v[0] if v else ""
        return str(v)
    except Exception:
        return default

def _set_query_str(key: str, value: str):
    try:
        st.query_params[key] = value
    except Exception:
        st.experimental_set_query_params(**{key: value})

def init_game_state():
    if "game_inited" in st.session_state:
        return

    # attempts persisted in URL
    attempts = _get_query_int("attempts", GAME_DEFAULT_ATTEMPTS)
    revived_day = _get_query_str("revived_day", "")

    st.session_state.game_attempts = max(0, attempts)
    st.session_state.game_revived_day = revived_day
    st.session_state.game_running = False
    st.session_state.game_start_ts = None
    st.session_state.game_last_stop = None
    st.session_state.game_message = ""
    st.session_state.game_inited = True

def persist_attempts():
    _set_query_int("attempts", int(st.session_state.game_attempts))

def can_revive_today() -> bool:
    today = _today_kst_date().isoformat()
    return st.session_state.game_revived_day != today

def mark_revived_today():
    today = _today_kst_date().isoformat()
    st.session_state.game_revived_day = today
    _set_query_str("revived_day", today)

def start_game():
    if st.session_state.game_attempts <= 0:
        st.session_state.game_message = "도전 횟수가 없어요. 공유로 1회 부활할 수 있어요."
        return
    st.session_state.game_attempts -= 1
    persist_attempts()

    st.session_state.game_running = True
    st.session_state.game_start_ts = time.time()
    st.session_state.game_last_stop = None
    st.session_state.game_message = "시작! 목표 구간에 맞춰 STOP!"

def stop_game():
    if not st.session_state.game_running or not st.session_state.game_start_ts:
        return
    elapsed = time.time() - st.session_state.game_start_ts
    st.session_state.game_running = False
    st.session_state.game_last_stop = elapsed

    if GAME_TARGET_MIN <= elapsed <= GAME_TARGET_MAX:
        st.session_state.game_message = f"✅ 성공! {elapsed:.3f}s (목표 {GAME_TARGET_MIN:.3f}~{GAME_TARGET_MAX:.3f})"
    else:
        st.session_state.game_message = f"❌ 실패… {elapsed:.3f}s (목표 {GAME_TARGET_MIN:.3f}~{GAME_TARGET_MAX:.3f})"

# ============================================================
# Main
# ============================================================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="centered")
    inject_styles()

    DB = load_db()
    if "__error__" in DB:
        st.error(DB["__error__"])
        st.stop()

    st.title("🔮 운세 + 타로")
    st.caption("생년월일 + MBTI로 오늘/내일/연간 운세와 타로를 보여줘요.")

    # Input
    with st.form("input_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            birth = st.date_input("생년월일", value=dt.date(2000, 1, 1), min_value=dt.date(1900, 1, 1), max_value=dt.date(2100, 12, 31))
        with col2:
            mbti = st.selectbox("MBTI", options=list(MBTI_TRAITS.keys()), index=list(MBTI_TRAITS.keys()).index("INTJ"))
        submitted = st.form_submit_button("결과 보기")

    if not submitted:
        st.stop()

    # Build result
    result = build_result(DB, birth, mbti)

    # Result header card
    st.markdown('<div class="card card-result">', unsafe_allow_html=True)
    st.markdown(f"**띠 운세:** {result['zodiac_label']}")
    st.markdown(f"**MBTI 특징:** {result['mbti_traits']}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")

    # Tarot image
    tarot_seed = f"{birth.isoformat()}|{mbti}|{result['zodiac_key']}|{_today_kst_date().isoformat()}"
    tarot_path = pick_tarot_image(tarot_seed)
    if tarot_path and os.path.exists(tarot_path):
        try:
            img = Image.open(tarot_path)
            st.image(img, use_container_width=True)
        except Exception:
            st.image(tarot_path, use_container_width=True)

    st.markdown("---")

    # Sections
    st.subheader("띠 한 마디")
    st.write(result["zodiac_one_liner"] or "—")

    st.subheader("사주 한 마디")
    st.write(result["saju_one_liner"] or "—")

    st.subheader("오늘 운세")
    st.write(result["today_fortune"] or "—")

    st.subheader("내일 운세")
    st.write(result["tomorrow_fortune"] or "—")

    st.subheader("2026 전체 운세")
    st.write(result["year_overall"] or "—")

    st.subheader("조언")
    st.write(result["advice"] or "—")

    with st.expander("추가 조언(카테고리)", expanded=False):
        st.markdown(f"- ❤️ 연애: {result['love_advice']}")
        st.markdown(f"- 💰 금전: {result['money_advice']}")
        st.markdown(f"- 📚 일/공부: {result['work_study_advice']}")
        st.markdown(f"- 🧘 건강: {result['health_advice']}")
        st.markdown(f"- ✅ 오늘의 액션팁: {result['action_tip']}")

    st.markdown("---")

    # ========================================================
    # Mini-game (Stopwatch) - restored version
    # ========================================================
    st.subheader("🎯 스톱워치 미니게임")
    st.caption("STOP을 목표 구간에 맞추면 성공! (실시간 타이머)")

    init_game_state()

    # attempts / revive info
    st.markdown(
        f"""
        <div class="game-box">
          <div class="pill">남은 도전: <b>{st.session_state.game_attempts}</b>회</div>
          <div class="pill">목표: <span class="mono">{GAME_TARGET_MIN:.3f}~{GAME_TARGET_MAX:.3f}s</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")

    # Controls
    colA, colB = st.columns(2)
    with colA:
        if st.button("▶️ START", use_container_width=True, disabled=st.session_state.game_running):
            start_game()
    with colB:
        if st.button("⏹️ STOP", use_container_width=True, disabled=not st.session_state.game_running):
            stop_game()

    # Live timer area
    timer_box = st.empty()

    if st.session_state.game_running and st.session_state.game_start_ts:
        # run live update loop for this rerun
        start_ts = st.session_state.game_start_ts
        # keep updating for a short time in this script run;
        # if user hits STOP, streamlit reruns and will exit loop naturally
        t0 = time.time()
        while st.session_state.game_running:
            elapsed = time.time() - start_ts
            timer_box.markdown(f"<div class='big mono'>{elapsed:0.3f}s</div>", unsafe_allow_html=True)

            # safety cutoff
            if elapsed >= GAME_MAX_RUN_SEC or (time.time() - t0) > GAME_MAX_RUN_SEC:
                st.session_state.game_running = False
                st.session_state.game_last_stop = elapsed
                st.session_state.game_message = f"시간 초과로 종료 ({elapsed:.3f}s)"
                break

            time.sleep(GAME_TICK_SEC)
            # allow UI to breathe
            st.session_state.game_running = st.session_state.game_running
        # after loop ends, show final time
        if st.session_state.game_last_stop is not None:
            timer_box.markdown(f"<div class='big mono'>{st.session_state.game_last_stop:0.3f}s</div>", unsafe_allow_html=True)
    else:
        # not running
        if st.session_state.game_last_stop is not None:
            timer_box.markdown(f"<div class='big mono'>{st.session_state.game_last_stop:0.3f}s</div>", unsafe_allow_html=True)
        else:
            timer_box.markdown(f"<div class='big mono'>0.000s</div>", unsafe_allow_html=True)

    if st.session_state.game_message:
        st.info(st.session_state.game_message)

    st.write("")

    # Share + revive (once per day)
    st.markdown("**친구에게 공유하면 부활 찬스 1회! (하루 1번)**")
    copy_url_button("친구에게 공유하기 (URL 복사)")

    if st.button("공유 완료했어요 → 부활 1회 받기", use_container_width=True):
        if can_revive_today():
            st.session_state.game_attempts += GAME_REVIVE_BONUS
            persist_attempts()
            mark_revived_today()
            st.success("부활 1회 지급 완료! 남은 도전 횟수가 늘었어요.")
        else:
            st.warning("오늘은 이미 부활을 받았어요. 내일 다시 받을 수 있어요.")

    st.caption("※ 도전 횟수는 URL에 저장되어 새로고침해도 유지됩니다.")

if __name__ == "__main__":
    main()
