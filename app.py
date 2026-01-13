# app.py
# v2026.0016_MINIGAME_CLEAN_FULL

import streamlit as st
import json
import random
import time
import os
import requests
from datetime import datetime, date

# =============================
# CONFIG
# =============================
APP_VERSION = "v2026.0016_MINIGAME_CLEAN_FULL"

ZODIAC_DB_FILE = "zodiac_fortunes_ko_2026.json"

GSHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzqvExf3oVzLK578Rv_AUN3YTzlo90x6gl0VAS8J7exjbapf--4ODxQn_Ovxrr9rKfG/exec"

MINIGAME_MIN = 20.260
MINIGAME_MAX = 20.269
MINIGAME_DAILY_ATTEMPTS = 1


# =============================
# UTILS
# =============================
def _today_key():
    return datetime.now().strftime("%Y-%m-%d")


def _fmt_sec(v: float) -> str:
    return f"{v:.3f}"


# =============================
# DB LOAD
# =============================
@st.cache_data(show_spinner=False)
def load_zodiac_db():
    with open(ZODIAC_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================
# ZODIAC
# =============================
ZODIAC_MAP = [
    ("rat", "쥐"),
    ("ox", "소"),
    ("tiger", "호랑이"),
    ("rabbit", "토끼"),
    ("dragon", "용"),
    ("snake", "뱀"),
    ("horse", "말"),
    ("goat", "양"),
    ("monkey", "원숭이"),
    ("rooster", "닭"),
    ("dog", "개"),
    ("pig", "돼지"),
]


def get_zodiac_from_birth(birth: date):
    year = birth.year
    idx = (year - 4) % 12
    key, ko = ZODIAC_MAP[idx]
    return key, f"{ko}띠"


# =============================
# TAROT (simple mock)
# =============================
TAROT_CARDS = [
    "The Fool - 새로운 시작",
    "The Magician - 기회 포착",
    "The High Priestess - 직감",
    "The Empress - 풍요",
    "The Emperor - 결단",
    "The Lovers - 선택",
    "The Chariot - 추진력",
    "Strength - 인내",
    "The Hermit - 성찰",
    "Wheel of Fortune - 전환점",
]


def get_daily_tarot(seed_key: str):
    random.seed(seed_key)
    return random.choice(TAROT_CARDS)


# =============================
# MINIGAME STATE
# =============================
def _reset_minigame_daily():
    today = _today_key()
    if st.session_state.get("minigame_day") != today:
        st.session_state["minigame_day"] = today
        st.session_state["minigame_attempts"] = MINIGAME_DAILY_ATTEMPTS
        st.session_state["minigame_running"] = False
        st.session_state["minigame_start"] = None
        st.session_state["minigame_last"] = None
        st.session_state["minigame_last_ok"] = None
        st.session_state["minigame_records"] = []
        st.session_state["minigame_shared"] = False
        st.session_state["minigame_consult"] = False
        st.session_state["minigame_consent_ok"] = False
        st.session_state["minigame_profile_name"] = ""
        st.session_state["minigame_profile_phone"] = ""


def _append_record(sec: float, ok: bool):
    recs = st.session_state.get("minigame_records") or []
    recs.insert(0, {"ts": datetime.now().strftime("%H:%M:%S"), "sec": sec, "ok": ok})
    st.session_state["minigame_records"] = recs[:20]


# =============================
# SHEET
# =============================
def send_minigame_to_sheet(row: list):
    try:
        r = requests.post(GSHEET_WEBAPP_URL, json={"row": row}, timeout=8)
        if r.status_code == 200:
            return True, "OK"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)


# =============================
# MINIGAME UI
# =============================
def mini_game_ui(birth: date, mbti: str, zodiac_ko: str):
    _reset_minigame_daily()

    st.markdown("### ⏱️ 미니게임: 20.260~20.269초 맞추기")
    st.caption("START → STOP으로 기록을 맞추세요 (소수점 3자리)")
    st.info("※ 선착순 이벤트, 커피쿠폰 조기 소진 시 공지 없이 종료될 수 있습니다.")

    attempts = int(st.session_state.get("minigame_attempts", 0))
    running = bool(st.session_state.get("minigame_running", False))
    start_t = st.session_state.get("minigame_start", None)

    now_sec = 0.0
    if running and isinstance(start_t, (int, float)):
        now_sec = max(0.0, time.perf_counter() - float(start_t))

    st.markdown(
        f"<div style='font-size:40px;font-weight:800;text-align:center'>{_fmt_sec(now_sec)} s</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"남은 기회: {attempts}회")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("START", use_container_width=True, disabled=(attempts <= 0 or running)):
            st.session_state["minigame_running"] = True
            st.session_state["minigame_start"] = time.perf_counter()
            st.rerun()

    with c2:
        if st.button("STOP", use_container_width=True, disabled=(not running)):
            sec = now_sec
            ok = (MINIGAME_MIN <= sec <= MINIGAME_MAX)
            st.session_state["minigame_running"] = False
            st.session_state["minigame_start"] = None
            st.session_state["minigame_attempts"] = max(0, attempts - 1)
            st.session_state["minigame_last"] = sec
            st.session_state["minigame_last_ok"] = ok
            _append_record(sec, ok)
            st.rerun()

    with c3:
        if st.button("RESET", use_container_width=True):
            st.session_state["minigame_running"] = False
            st.session_state["minigame_start"] = None
            st.rerun()

    if running:
        time.sleep(0.03)
        st.rerun()

    last = st.session_state.get("minigame_last", None)
    last_ok = st.session_state.get("minigame_last_ok", None)
    last_sec_str = _fmt_sec(float(last)) if last is not None else ""

    if last is not None:
        if last_ok:
            st.success(f"성공! 기록 {last_sec_str}s")
        else:
            st.error(f"실패! 기록 {last_sec_str}s")

    # 재도전
    if last is not None and not last_ok:
        st.markdown("#### 🔁 재도전 기회 얻기")

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("공유 완료 +1", use_container_width=True):
                st.session_state["minigame_attempts"] += 1
                st.session_state["minigame_shared"] = True
                st.success("기회 +1")

        with b2:
            if st.button("광고 보기 +1", use_container_width=True):
                st.session_state["minigame_attempts"] += 1
                st.success("기회 +1")

        with b3:
            if st.button("다나눔렌탈 +1", use_container_width=True):
                st.session_state["minigame_attempts"] += 1
                st.session_state["minigame_consult"] = True
                st.success("기회 +1")
                st.link_button("무료 상담 페이지", "https://incredible-dusk-20d2b5.netlify.app/")

    # 기록
    recs = st.session_state.get("minigame_records") or []
    if recs:
        with st.expander("📒 내 기록"):
            for r in recs:
                st.write(f"{r['ts']} · {_fmt_sec(r['sec'])}s · {'성공' if r['ok'] else '실패'}")

    # 응모 폼
    st.markdown("#### ☕ 커피쿠폰 응모")

    with st.form("minigame_entry_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            entry_name = st.text_input("이름", value=st.session_state.get("minigame_profile_name", ""))
        with col2:
            entry_phone = st.text_input("전화번호", value=st.session_state.get("minigame_profile_phone", ""))

        st.text_input("생년월일", value=str(birth), disabled=True)
        st.text_input("MBTI", value=mbti, disabled=True)
        st.text_input("띠", value=zodiac_ko, disabled=True)

        consent = st.checkbox("개인정보처리방침에 동의합니다.")

        submitted = st.form_submit_button("응모/저장하기", use_container_width=True)

        if submitted:
            valid = True

            if not entry_name.strip():
                st.error("이름을 입력해주세요.")
                valid = False

            if not entry_phone.strip():
                st.error("전화번호를 입력해주세요.")
                valid = False

            if not consent:
                st.error("개인정보 동의가 필요합니다.")
                valid = False

            if not last_sec_str:
                st.error("STOP으로 기록을 만든 뒤 응모해주세요.")
                valid = False

            if valid:
                row = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    entry_name.strip(),
                    entry_phone.strip(),
                    "ko",
                    last_sec_str,
                    bool(st.session_state.get("minigame_shared", False)),
                    bool(st.session_state.get("minigame_consult", False)),
                    str(birth),
                ]

                ok_send, msg = send_minigame_to_sheet(row)
                if ok_send:
                    st.success("저장 완료!")
                    st.session_state["minigame_profile_name"] = entry_name.strip()
                    st.session_state["minigame_profile_phone"] = entry_phone.strip()
                else:
                    st.warning("전송 실패")
                    st.code(row, language="json")


# =============================
# MAIN UI
# =============================
st.set_page_config(page_title="2026 운세", layout="centered")

st.title("🔮 2026 운세 + 미니게임")
st.caption(APP_VERSION)

name = st.text_input("이름")
birth = st.date_input("생년월일", value=date(2000, 1, 1))
mbti = st.text_input("MBTI (예: ESTJ)")

if st.button("운세 보기"):
    zodiac_db = load_zodiac_db()
    zodiac_key, zodiac_ko = get_zodiac_from_birth(birth)
    fortune_list = zodiac_db.get(zodiac_key, [])
    fortune = random.choice(fortune_list) if fortune_list else "운세 데이터 없음"

    st.markdown("---")
    st.subheader("🧧 띠 운세")
    st.write(f"{zodiac_ko} · {fortune}")

    st.subheader("🃏 오늘의 타로")
    tarot = get_daily_tarot(f"{birth}-{mbti}-{_today_key()}")
    st.write(tarot)

    st.markdown("---")
    mini_game_ui(birth, mbti, zodiac_ko)
