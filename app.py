import os
import json
import math
import time
import glob
import hashlib
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# ============================================================
# Config
# ============================================================

APP_TITLE = "운세 · 타로"
APP_ICON = "🔮"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Default DB path (must exist in GitHub repo)
DB_PATH = os.path.join(DATA_DIR, "fortunes_ko.json")

# Mini-game settings
GAME_WINDOW_MIN = 20.260
GAME_WINDOW_MAX = 20.269
GAME_MAX_ATTEMPTS_PER_DAY = 3
GAME_DURATION_SEC = 20

# ============================================================
# Helpers: deterministic RNG
# ============================================================

def _stable_int_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def _pick(items: List[str], seed: str) -> str:
    if not items:
        return "•"
    idx = _stable_int_hash(seed) % len(items)
    return items[idx]

def _now_kst() -> dt.datetime:
    # Streamlit Cloud is usually UTC; convert to KST
    return dt.datetime.utcnow() + dt.timedelta(hours=9)

def _date_kst() -> dt.date:
    return _now_kst().date()

# ============================================================
# DB loading / schema utilities
# ============================================================

@st.cache_data(show_spinner=False)
def load_db(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        # provide helpful debug listing
        existing = []
        if os.path.isdir(DATA_DIR):
            existing = sorted([f for f in os.listdir(DATA_DIR) if f.lower().endswith(".json")])
        return {
            "__error__": f"DB 파일을 찾을 수 없습니다: {path}",
            "__existing__": existing,
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_pool(db: Dict[str, Any]) -> Dict[str, List[str]]:
    pools = db.get("pools", {})
    if isinstance(pools, dict):
        return pools
    return {}

def get_zodiac_maps(db: Dict[str, Any]) -> Tuple[List[str], Dict[str, str]]:
    """
    Returns (order, labels) for zodiac. Works with both:
    - db["zodiac"] = {"order":[...], "labels":{...}}
    - missing -> fallback defaults
    """
    zodiac = db.get("zodiac", {})
    order = []
    labels = {}
    if isinstance(zodiac, dict):
        order = zodiac.get("order", []) if isinstance(zodiac.get("order", []), list) else []
        labels = zodiac.get("labels", {}) if isinstance(zodiac.get("labels", {}), dict) else {}

    if not order:
        order = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
    if not labels:
        labels = {
            "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
            "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠",
        }
    return order, labels

def zodiac_from_solar_year(year: int, db: Dict[str, Any]) -> Tuple[str, str]:
    """
    Solar-year based zodiac (simple, stable).
    Many people use lunar new year boundary; implementing that accurately
    requires a lunar calendar table/library. We keep solar-year by default.
    """
    order, labels = get_zodiac_maps(db)
    idx = (year - 1900) % 12
    key = order[idx]
    return key, labels.get(key, key)

def zodiac_from_birthdate(birth: dt.date, db: Dict[str, Any], mode: str) -> Tuple[str, str, str]:
    """
    mode:
      - "solar": year-based
      - "lunar_try": try lunar conversion if a library exists, else fallback to solar
    """
    if mode == "lunar_try":
        # Optional: try lunardate / korean_lunar_calendar if installed (not required)
        try:
            from korean_lunar_calendar import KoreanLunarCalendar  # type: ignore
            cal = KoreanLunarCalendar()
            cal.setSolarDate(birth.year, birth.month, birth.day)
            ly, lm, ld = cal.LunarIsoFormat().split("-")
            lunar_year = int(ly)
            k, label = zodiac_from_solar_year(lunar_year, db)
            return k, label, f"음력 기준(라이브러리): {lunar_year}년"
        except Exception:
            k, label = zodiac_from_solar_year(birth.year, db)
            return k, label, "음력 기준(라이브러리 없음) → 양력 연도 대체"
    else:
        k, label = zodiac_from_solar_year(birth.year, db)
        return k, label, "양력 연도 기준"

def pick_tarot_image(seed: str) -> Optional[str]:
    patterns = [
        os.path.join(ASSETS_DIR, "tarot", "majors", "*.png"),
        os.path.join(ASSETS_DIR, "tarot", "minor", "*.png"),
        os.path.join(ASSETS_DIR, "tarot", "*.png"),
        os.path.join(ASSETS_DIR, "tarot", "**", "*.png"),
    ]
    candidates: List[str] = []
    for p in patterns:
        candidates.extend(glob.glob(p, recursive=True))
    candidates = sorted(list({c for c in candidates if os.path.isfile(c)}))
    if not candidates:
        return None
    idx = _stable_int_hash(seed) % len(candidates)
    return candidates[idx]

# ============================================================
# Share / client-side helpers
# ============================================================

def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .card {
          border: 1px solid rgba(0,0,0,0.08);
          border-radius: 16px;
          padding: 16px 16px 8px 16px;
          margin: 12px 0;
          background: rgba(255,255,255,0.9);
        }
        .pill {
          display:inline-block;
          padding:4px 10px;
          border-radius:999px;
          background: rgba(0,0,0,0.06);
          margin-right: 6px;
          font-size: 13px;
        }
        .muted { color: rgba(0,0,0,0.55); font-size: 13px; }
        .small { font-size: 14px; }
        .hr { border-top:1px solid rgba(0,0,0,0.08); margin: 14px 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def share_widget() -> None:
    """
    A reliable share/copy widget on mobile:
    - First tries navigator.share
    - Fallback: copy URL to clipboard
    """
    st.markdown("### 공유하기")
    st.markdown('<div class="muted">친구에게 링크를 보내기 쉽게: <b>공유</b> 또는 <b>복사</b></div>', unsafe_allow_html=True)
    st.components.v1.html(
        f"""
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin:8px 0 4px 0;">
          <button id="btnShare" style="padding:10px 14px; border-radius:12px; border:1px solid #ddd; background:white; font-weight:600;">
            📤 공유
          </button>
          <button id="btnCopy" style="padding:10px 14px; border-radius:12px; border:1px solid #ddd; background:white; font-weight:600;">
            🔗 링크 복사
          </button>
          <span id="msg" style="align-self:center; font-size:13px; color:#666;"></span>
        </div>
        <script>
          const url = window.location.href;
          const msg = document.getElementById("msg");
          document.getElementById("btnShare").onclick = async () => {{
            msg.textContent = "";
            try {{
              if (navigator.share) {{
                await navigator.share({{ title: "{APP_TITLE}", text: "운세 결과 보기", url }});
                msg.textContent = "공유창을 열었어요.";
              }} else {{
                await navigator.clipboard.writeText(url);
                msg.textContent = "공유 기능이 없어 링크를 복사했어요.";
              }}
            }} catch (e) {{
              // user canceled or permission denied
              try {{
                await navigator.clipboard.writeText(url);
                msg.textContent = "공유가 취소되어 링크를 복사했어요.";
              }} catch (e2) {{
                msg.textContent = "복사 권한이 없어요. 주소창의 URL을 길게 눌러 복사해 주세요.";
              }}
            }}
          }};
          document.getElementById("btnCopy").onclick = async () => {{
            msg.textContent = "";
            try {{
              await navigator.clipboard.writeText(url);
              msg.textContent = "링크를 복사했어요.";
            }} catch (e) {{
              msg.textContent = "복사 권한이 없어요. 주소창의 URL을 길게 눌러 복사해 주세요.";
            }}
          }};
        </script>
        """,
        height=70,
    )

def timer_widget(end_ts: float) -> None:
    """
    Client-side countdown timer (doesn't block Streamlit).
    """
    st.components.v1.html(
        f"""
        <div style="margin:10px 0 2px 0; font-size:14px; color:#444;">
          ⏳ 남은 시간: <b id="tleft">--</b>초
        </div>
        <script>
          const end = {end_ts} * 1000;
          const el = document.getElementById("tleft");
          function tick(){{
            const now = Date.now();
            const left = Math.max(0, Math.ceil((end - now)/1000));
            el.textContent = left;
            if(left <= 0) return;
            requestAnimationFrame(()=>setTimeout(tick, 200));
          }}
          tick();
        </script>
        """,
        height=40,
    )

# ============================================================
# Business logic: build result
# ============================================================

def build_result(db: Dict[str, Any], birth: dt.date, mbti: str, zodiac_mode: str) -> Dict[str, str]:
    pools = get_pool(db)
    today = _date_kst()
    tomorrow = today + dt.timedelta(days=1)

    zodiac_key, zodiac_label, zodiac_note = zodiac_from_birthdate(birth, db, zodiac_mode)

    # seed base
    seed_base = f"{birth.isoformat()}|{mbti}|{zodiac_key}"

    def pick_pool(pool_name: str, extra: str) -> str:
        items = pools.get(pool_name, [])
        return _pick(items, seed_base + "|" + pool_name + "|" + extra)

    # pools key compatibility
    year_key = "year_2026_fortune" if "year_2026_fortune" in pools else ("year_overall" if "year_overall" in pools else "")
    advice_key = "advice" if "advice" in pools else ("action_tip" if "action_tip" in pools else "")

    result = {
        "zodiac_label": zodiac_label,
        "zodiac_note": zodiac_note,
        "mbti": mbti,
        "saju_one_liner": pick_pool("saju_one_liner", "static"),
        "today_fortune": pick_pool("today_fortune", today.isoformat()),
        "tomorrow_fortune": pick_pool("tomorrow_fortune", tomorrow.isoformat()),
        "year_2026": pick_pool(year_key, "2026") if year_key else "•",
        "advice": pick_pool(advice_key, today.isoformat()) if advice_key else "•",
    }
    return result

# ============================================================
# Mini game
# ============================================================

def init_game_state() -> None:
    if "game_day" not in st.session_state:
        st.session_state.game_day = ""
    if "game_attempts_used" not in st.session_state:
        st.session_state.game_attempts_used = 0
    if "game_running" not in st.session_state:
        st.session_state.game_running = False
    if "game_end_ts" not in st.session_state:
        st.session_state.game_end_ts = 0.0
    if "game_message" not in st.session_state:
        st.session_state.game_message = ""
    if "game_last_roll" not in st.session_state:
        st.session_state.game_last_roll = None

def sync_game_day() -> None:
    day = _date_kst().isoformat()
    if st.session_state.game_day != day:
        st.session_state.game_day = day
        st.session_state.game_attempts_used = 0
        st.session_state.game_running = False
        st.session_state.game_end_ts = 0.0
        st.session_state.game_message = ""
        st.session_state.game_last_roll = None

def game_section() -> None:
    st.markdown("## 🎮 미니게임")
    st.markdown('<div class="muted">하루 <b>3번</b>만 도전 가능 · 타이머는 앱이 멈추지 않게 <b>브라우저에서</b> 실시간으로 돌아가요.</div>', unsafe_allow_html=True)

    init_game_state()
    sync_game_day()

    remaining = max(0, GAME_MAX_ATTEMPTS_PER_DAY - int(st.session_state.game_attempts_used))
    st.markdown(f'<div class="pill">남은 도전: <b>{remaining}</b> / {GAME_MAX_ATTEMPTS_PER_DAY}</div>', unsafe_allow_html=True)

    now = time.time()
    if st.session_state.game_running and now >= st.session_state.game_end_ts:
        st.session_state.game_running = False
        st.session_state.game_message = "⏰ 시간이 끝났어요! 내일 다시 도전해요."
        st.session_state.game_last_roll = None

    col1, col2 = st.columns(2)

    with col1:
        start_disabled = st.session_state.game_running or (remaining <= 0)
        if st.button("게임 시작", use_container_width=True, disabled=start_disabled):
            st.session_state.game_running = True
            st.session_state.game_end_ts = time.time() + GAME_DURATION_SEC
            st.session_state.game_message = "시작! 아래에서 '도전!' 버튼을 눌러보세요."
            st.session_state.game_last_roll = None
            st.rerun()

    with col2:
        if st.button("게임 규칙", use_container_width=True):
            st.info(f"버튼을 누를 때마다 숫자(0~100)가 생성돼요. "
                    f"{GAME_WINDOW_MIN:.3f} ~ {GAME_WINDOW_MAX:.3f} 사이면 성공! "
                    f"(하루 {GAME_MAX_ATTEMPTS_PER_DAY}번 도전)")

    if st.session_state.game_running:
        timer_widget(st.session_state.game_end_ts)

    # Attempt button
    attempt_disabled = (not st.session_state.game_running) or (remaining <= 0)
    if st.button("도전! (숫자 생성)", use_container_width=True, disabled=attempt_disabled):
        st.session_state.game_attempts_used += 1
        roll_seed = f"{st.session_state.game_day}|{st.session_state.game_attempts_used}|{_stable_int_hash(st.session_state.game_day)}"
        # deterministic-but-feels-random roll
        x = (_stable_int_hash(roll_seed) % 1000000) / 10000.0  # 0.0000 ~ 99.9999
        st.session_state.game_last_roll = x

        if GAME_WINDOW_MIN <= x <= GAME_WINDOW_MAX:
            st.session_state.game_message = f"🎉 성공! {x:.4f} (축하해요)"
            st.session_state.game_running = False
        else:
            left = max(0, GAME_MAX_ATTEMPTS_PER_DAY - int(st.session_state.game_attempts_used))
            if left <= 0:
                st.session_state.game_message = f"😵 실패… {x:.4f} (오늘 도전 끝!)"
                st.session_state.game_running = False
            else:
                st.session_state.game_message = f"아쉽! {x:.4f} (남은 도전 {left}번)"
        st.rerun()

    if st.session_state.game_last_roll is not None:
        st.markdown(f"### 결과: **{st.session_state.game_last_roll:.4f}**")

    if st.session_state.game_message:
        st.info(st.session_state.game_message)

# ============================================================
# App UI
# ============================================================

def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="centered")
    inject_styles()

    db = load_db(DB_PATH)
    if "__error__" in db:
        st.error(db["__error__"])
        existing = db.get("__existing__", [])
        if existing:
            st.write("현재 data/ 폴더에 있는 JSON 파일:")
            st.code("\n".join(existing))
        st.write("해결 방법:")
        st.write("- GitHub 저장소에 **data/fortunes_ko.json** 파일이 있는지 확인")
        st.write("- 파일명이 다르면 app.py의 DB_PATH를 실제 파일명으로 수정")
        st.stop()

    st.title(APP_TITLE)

    # Inputs
    st.markdown("### 입력")
    c1, c2 = st.columns(2)
    with c1:
        birth = st.date_input("생년월일", value=dt.date(1995, 1, 1), min_value=dt.date(1900, 1, 1), max_value=dt.date(2100, 12, 31))
    with c2:
        mbti = st.text_input("MBTI (예: INTP)", value="INTP", max_chars=4).upper().strip()

    zodiac_mode = st.selectbox(
        "띠 기준",
        options=[
            ("solar", "양력 연도 기준(빠르고 안정적)"),
            ("lunar_try", "음력 기준 시도(라이브러리 있으면 적용)"),
        ],
        format_func=lambda x: x[1],
        index=0,
    )[0]

    if not mbti or len(mbti) != 4:
        st.warning("MBTI는 4글자로 입력해 주세요. 예: INTP")
        st.stop()

    # Build
    result = build_result(db, birth, mbti, zodiac_mode)

    # Header pills
    st.markdown(
        f"""
        <div class="card">
          <div class="pill">띠: <b>{result["zodiac_label"]}</b></div>
          <div class="pill">MBTI: <b>{result["mbti"]}</b></div>
          <div class="muted" style="margin-top:8px;">{result["zodiac_note"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tarot
    tarot_path = pick_tarot_image(f"{birth.isoformat()}|{mbti}|{result['zodiac_label']}")
    if tarot_path:
        st.image(tarot_path, use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Results
    st.subheader("사주 한 마디")
    st.write(result["saju_one_liner"])

    st.subheader("오늘 운세")
    st.write(result["today_fortune"])

    st.subheader("내일 운세")
    st.write(result["tomorrow_fortune"])

    st.subheader("2026 전체 운세")
    st.write(result["year_2026"])

    st.subheader("조언")
    st.write(result["advice"])

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    share_widget()

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    game_section()

    st.markdown('<div class="muted" style="margin-top:18px;">※ 본 앱은 재미용 콘텐츠이며, 중요한 결정은 본인의 판단을 우선해 주세요.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
