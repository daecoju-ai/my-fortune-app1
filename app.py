
import os, json, time, math, hashlib, glob, datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# =========================================================
# Config
# =========================================================
st.set_page_config(
    page_title="운세 · 타로",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

APP_TITLE = "운세 · 타로"

# Success window for stopwatch game (seconds)
GAME_TARGET_MIN = 20.260
GAME_TARGET_MAX = 20.269
GAME_MAX_ATTEMPTS_PER_DAY = 3  # reset daily per user

# Data files (we will load the first one that exists)
DB_CANDIDATES = [
    "data/fortunes_ko_NO_COMBOS.json",
    "data/fortunes_ko.json",
    "data/fortunes_ko_FULL_FIXED.json",
    "data/fortune_db.json",
]

TAROT_DB_CANDIDATES = [
    "data/tarot_db_ko.json",
    "data/tarot_db.json",
]

FRAME_IMAGE_CANDIDATES = ["frame.png", "assets/frame.png"]

FONT_CANDIDATES = ["NotoSansKR-Regular.otf", "assets/NotoSansKR-Regular.otf"]

# =========================================================
# Helpers
# =========================================================
def _stable_int_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def _pick(items: List[str], seed: str) -> str:
    if not items:
        return "-"
    idx = _stable_int_hash(seed) % len(items)
    return items[idx]

def _now_kst() -> dt.datetime:
    # Streamlit Cloud is usually UTC. We normalize to KST for "today" logic.
    return dt.datetime.utcnow() + dt.timedelta(hours=9)

# Zodiac (12 animal signs) - YEAR based
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABELS = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
    "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠",
}

def zodiac_from_year_solar(year: int) -> Tuple[str, str]:
    idx = (year - 1900) % 12
    key = ZODIAC_ORDER[idx]
    return key, ZODIAC_LABELS.get(key, key)

@st.cache_data(show_spinner=False)
def load_json_first(paths: List[str]) -> Dict[str, Any]:
    # Expand globs too (defensive)
    expanded: List[str] = []
    for p in paths:
        if any(ch in p for ch in ["*", "?", "["]):
            expanded.extend(sorted(glob.glob(p)))
        else:
            expanded.append(p)

    for path in expanded:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

    # Not found: give readable error
    raise FileNotFoundError(
        "DB 파일을 찾을 수 없습니다. 다음 중 하나가 저장되어 있어야 합니다: "
        + ", ".join(paths)
    )

def get_pool(db: Dict[str, Any]) -> Dict[str, List[str]]:
    # supports both {pools:{...}} and flat
    pools = db.get("pools")
    if isinstance(pools, dict):
        return pools
    # legacy: top-level lists
    return {k: v for k, v in db.items() if isinstance(v, list)}

def pick_tarot_image(seed: str) -> Optional[str]:
    # Prefer local images in assets/tarot/*
    patterns = [
        "assets/tarot/majors/*.png",
        "assets/tarot/minor/*.png",
        "assets/tarot/*.png",
        "assets/tarot/**/*.png",
    ]
    candidates: List[str] = []
    for pat in patterns:
        candidates.extend(sorted(glob.glob(pat, recursive=True)))
    if not candidates:
        return None
    idx = _stable_int_hash(seed + "|tarot") % len(candidates)
    return candidates[idx]

def share_block(title: str, text: str) -> None:
    """
    Web Share API (mobile share sheet).
    Works on most mobile browsers if user action triggers it.
    """
    import streamlit.components.v1 as components
    # We keep the JS minimal; Streamlit wraps in iframe, but on mobile it often still works.
    js = f"""
    <script>
    const shareData = {{
      title: {json.dumps(title)},
      text: {json.dumps(text)},
      url: window.location.href
    }};
    async function doShare(){{
      try {{
        if (navigator.share) {{
          await navigator.share(shareData);
          const el = document.getElementById("share-status");
          if (el) el.innerText = "공유창을 열었습니다.";
        }} else {{
          const el = document.getElementById("share-status");
          if (el) el.innerText = "이 기기는 공유 기능을 지원하지 않습니다. 주소를 복사해 주세요.";
        }}
      }} catch (e) {{
        const el = document.getElementById("share-status");
        if (el) el.innerText = "공유를 취소했거나, 브라우저 제한이 있습니다.";
      }}
    }}
    doShare();
    </script>
    <div id="share-status" style="font-size:14px; opacity:0.8; margin-top:4px;"></div>
    """
    components.html(js, height=40)

def ensure_session_defaults():
    if "page" not in st.session_state:
        st.session_state.page = "home"  # home | result | game
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "game" not in st.session_state:
        st.session_state.game = {
            "running": False,
            "t0": None,
            "last_elapsed": None,
            "attempts": 0,
            "day_key": None,
        }

def reset_attempts_if_new_day(user_key: str):
    g = st.session_state.game
    today = _now_kst().date().isoformat()
    day = f"{today}|{user_key}"
    if g.get("day_key") != day:
        g["day_key"] = day
        g["attempts"] = 0
        g["running"] = False
        g["t0"] = None
        g["last_elapsed"] = None

# =========================================================
# Business logic
# =========================================================
def build_result(db: Dict[str, Any], birth: dt.date, mbti: str) -> Dict[str, Any]:
    pools = get_pool(db)

    zodiac_key, zodiac_label = zodiac_from_year_solar(birth.year)

    now = _now_kst()
    today = now.date()
    tomorrow = today + dt.timedelta(days=1)
    year = today.year

    # Seed base: birth + mbti + zodiac + date
    seed_today = f"{birth.isoformat()}|{mbti}|{zodiac_key}|{today.isoformat()}"
    seed_tomorrow = f"{birth.isoformat()}|{mbti}|{zodiac_key}|{tomorrow.isoformat()}"
    seed_year = f"{birth.isoformat()}|{mbti}|{zodiac_key}|{year}"

    def pick_pool(pool_name: str, seed: str) -> str:
        items = pools.get(pool_name, [])
        return _pick(items, seed)

    result = {
        "zodiac_label": zodiac_label,
        "mbti": mbti,

        "saju_one_liner": pick_pool("saju_one_liners", seed_today) if "saju_one_liners" in pools else pick_pool("saju_one_liner", seed_today),
        "today_fortune": pick_pool("today_fortunes", seed_today) if "today_fortunes" in pools else pick_pool("today_fortune", seed_today),
        "tomorrow_fortune": pick_pool("tomorrow_fortunes", seed_tomorrow) if "tomorrow_fortunes" in pools else pick_pool("tomorrow_fortune", seed_tomorrow),
        "year_overall": pick_pool("year_overalls", seed_year) if "year_overalls" in pools else pick_pool("year_overall", seed_year),

        # "조언" (we show pre-defined pool values; no combo logic)
        "advice": {
            "연애": pick_pool("love_advices", seed_today) if "love_advices" in pools else pick_pool("love_advice", seed_today),
            "금전": pick_pool("money_advices", seed_today) if "money_advices" in pools else pick_pool("money_advice", seed_today),
            "일/학업": pick_pool("work_study_advices", seed_today) if "work_study_advices" in pools else pick_pool("work_study_advice", seed_today),
            "건강": pick_pool("health_advices", seed_today) if "health_advices" in pools else pick_pool("health_advice", seed_today),
            "오늘의 액션": pick_pool("action_tips", seed_today) if "action_tips" in pools else pick_pool("action_tip", seed_today),
            "조언": pick_pool("advice", seed_today),
        },
        "tarot_path": pick_tarot_image(seed_today),
    }
    # normalize blanks
    for k in ["saju_one_liner","today_fortune","tomorrow_fortune","year_overall"]:
        if not result.get(k):
            result[k] = "-"
    for k,v in list(result["advice"].items()):
        if not v:
            result["advice"][k] = "-"
    return result

# =========================================================
# UI: Home
# =========================================================
def render_home(db: Dict[str, Any]):
    st.title(APP_TITLE)
    st.caption("생년월일 + MBTI로 오늘의 한 줄 운세와 타로를 보여드려요.")

    with st.form("input_form", clear_on_submit=False):
        birth = st.date_input("생년월일", value=dt.date(1995,1,1), min_value=dt.date(1900,1,1), max_value=_now_kst().date())
        mbti = st.text_input("MBTI (예: INTP)", value="INTP", max_chars=4).upper().strip()
        submit = st.form_submit_button("결과 보기")

    if submit:
        if len(mbti) != 4:
            st.error("MBTI는 4글자여야 해요. 예: INTP, ENFJ")
            return
        result = build_result(db, birth, mbti)
        st.session_state.last_result = result
        st.session_state.page = "result"
        st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏱️ 스톱워치 미니게임"):
            st.session_state.page = "game"
            st.rerun()
    with col2:
        if st.button("📤 친구에게 공유하기"):
            share_block(APP_TITLE, "내 운세/타로 결과 확인해봐!")

# =========================================================
# UI: Result
# =========================================================
def render_result():
    result = st.session_state.last_result
    if not result:
        st.warning("결과가 없습니다. 먼저 입력부터 해주세요.")
        if st.button("처음으로"):
            st.session_state.page = "home"
            st.rerun()
        return

    st.title("결과")
    st.write(f"**띠 운세:** {result.get('zodiac_label','-')}")
    st.write(f"**MBTI:** {result.get('mbti','-')}")

    if result.get("tarot_path") and os.path.exists(result["tarot_path"]):
        st.image(result["tarot_path"], use_container_width=True)

    st.markdown("---")
    st.subheader("사주 한 마디")
    st.write(result.get("saju_one_liner","-"))

    st.subheader("오늘 운세")
    st.write(result.get("today_fortune","-"))

    st.subheader("내일 운세")
    st.write(result.get("tomorrow_fortune","-"))

    st.subheader("2026 전체 운세")
    st.write(result.get("year_overall","-"))

    st.subheader("조언")
    # show "조언" pool first if meaningful, then categories
    adv = result.get("advice", {}) if isinstance(result.get("advice"), dict) else {}
    if adv.get("조언") and adv.get("조언") != "-":
        st.write(adv["조언"])
        st.markdown("---")
    for label in ["연애","금전","일/학업","건강","오늘의 액션"]:
        if label in adv and adv[label] and adv[label] != "-":
            st.markdown(f"**{label}:** {adv[label]}")

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ 처음"):
            st.session_state.page = "home"
            st.rerun()
    with c2:
        if st.button("📤 공유"):
            share_block(APP_TITLE, "내 운세/타로 결과 확인해봐!")
    with c3:
        if st.button("⏱️ 게임"):
            st.session_state.page = "game"
            st.rerun()

# =========================================================
# UI: Stopwatch Game
# =========================================================
def render_game():
    st.title("⏱️ 스톱워치 미니게임")
    st.caption(f"{GAME_TARGET_MIN:.3f}~{GAME_TARGET_MAX:.3f}초에 맞추면 성공! (하루 {GAME_MAX_ATTEMPTS_PER_DAY}회)")

    # user key for daily attempts (semi-stable, privacy-safe)
    # Uses browser session id if present, else hash of user agent/time bucket
    user_key = st.session_state.get("_user_key")
    if not user_key:
        # This is not perfect, but good enough for daily attempts per session.
        user_key = hex(_stable_int_hash(str(st.session_state)))[2:10]
        st.session_state["_user_key"] = user_key

    reset_attempts_if_new_day(user_key)

    g = st.session_state.game
    attempts_left = max(0, GAME_MAX_ATTEMPTS_PER_DAY - int(g.get("attempts", 0)))

    # Display
    timer_box = st.empty()
    status_box = st.empty()
    info_box = st.empty()

    now = time.time()
    elapsed = None
    if g.get("running") and g.get("t0") is not None:
        elapsed = now - float(g["t0"])

    # UI controls
    colA, colB, colC = st.columns(3)
    with colA:
        start_disabled = g.get("running") or attempts_left <= 0
        if st.button("START", disabled=start_disabled, use_container_width=True):
            g["running"] = True
            g["t0"] = time.time()
            g["last_elapsed"] = None
            g["attempts"] = int(g.get("attempts", 0)) + 1
            st.rerun()

    with colB:
        stop_disabled = (not g.get("running"))
        if st.button("STOP", disabled=stop_disabled, use_container_width=True):
            g["running"] = False
            if g.get("t0") is not None:
                g["last_elapsed"] = time.time() - float(g["t0"])
            st.rerun()

    with colC:
        if st.button("처음으로", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    # Render timer + status
    shown = elapsed if elapsed is not None else g.get("last_elapsed")
    if shown is None:
        timer_box.markdown("### 0.000 s")
    else:
        timer_box.markdown(f"### {shown:0.3f} s")

    info_box.write(f"남은 도전: **{attempts_left}** / {GAME_MAX_ATTEMPTS_PER_DAY}")

    if (not g.get("running")) and g.get("last_elapsed") is not None:
        val = float(g["last_elapsed"])
        if GAME_TARGET_MIN <= val <= GAME_TARGET_MAX:
            status_box.success("🎉 성공! 완벽합니다.")
        else:
            status_box.error("아쉽! 다시 도전해보세요.")

    # LIVE timer: while running, rerun frequently
    if g.get("running"):
        # throttle (20 fps)
        time.sleep(0.05)
        st.rerun()

# =========================================================
# Main
# =========================================================
def main():
    ensure_session_defaults()

    # Load DB
    try:
        db = load_json_first(DB_CANDIDATES)
    except Exception as e:
        st.error(f"DB 로딩 실패: {e}")
        st.stop()

    # Simple router (session_state 기반)
    page = st.session_state.get("page", "home")

    if page == "home":
        render_home(db)
    elif page == "result":
        render_result()
    elif page == "game":
        render_game()
    else:
        st.session_state.page = "home"
        st.rerun()

if __name__ == "__main__":
    main()
