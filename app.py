
# app.py
# v2026.0025_3STEP_MINIGAME_UI_FIX

import streamlit as st
import json, random, time, requests
from datetime import datetime, date

# ================= CONFIG =================
APP_VERSION = "v2026.0025_3STEP_MINIGAME_UI_FIX"

ZODIAC_DB_FILE = "zodiac_fortunes_ko_2026.json"

GSHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzqvExf3oVzLK578Rv_AUN3YTzlo90x6gl0VAS8J7exjbapf--4ODxQn_Ovxrr9rKfG/exec"

CLOCK_SOUND = "assets/clock-ticking.mp3"
REVEAL_SOUND = "assets/reveal.mp3"

MINIGAME_MIN = 20.260
MINIGAME_MAX = 20.269
DAILY_ATTEMPTS = 1

# 외부 이동 링크 (간접 검증)
SHARE_OUT_URL = "https://www.kakao.com/"
AD_OUT_URL = "https://incredible-dusk-20d2b5.netlify.app/"

# ================= STEP =================
if "step" not in st.session_state:
    st.session_state.step = 1

# ================= UTILS =================
def today_key():
    return date.today().isoformat()

def fmt(v: float) -> str:
    return f"{v:.3f}"

# ================= DB =================
@st.cache_data(show_spinner=False)
def load_zodiac():
    with open(ZODIAC_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

ZODIAC_MAP = [
    ("rat","쥐"),("ox","소"),("tiger","호랑이"),("rabbit","토끼"),
    ("dragon","용"),("snake","뱀"),("horse","말"),("goat","양"),
    ("monkey","원숭이"),("rooster","닭"),("dog","개"),("pig","돼지"),
]

def get_zodiac(b):
    k, ko = ZODIAC_MAP[(b.year-4)%12]
    return k, ko+"띠"

# ================= TAROT =================
TAROT = [
    "새로운 시작", "기회 포착", "직감", "풍요", "결단",
    "선택", "추진력", "인내", "성찰", "전환점"
]

def daily_tarot(seed):
    random.seed(seed)
    return random.choice(TAROT)

# ================= MINIGAME STATE =================
def reset_daily():
    if st.session_state.get("mg_day") != today_key():
        st.session_state.mg_day = today_key()
        st.session_state.mg_attempts = DAILY_ATTEMPTS
        st.session_state.mg_running = False
        st.session_state.mg_start = None
        st.session_state.mg_last = None
        st.session_state.mg_ok = None
        st.session_state.mg_shared = False
        st.session_state.mg_ad = False
        st.session_state.mg_bonus_pending = None  # "share" | "ad" | None

def send_to_sheet(row):
    try:
        r = requests.post(GSHEET_WEBAPP_URL, json={"row": row}, timeout=8)
        return r.status_code == 200
    except Exception:
        return False

# ================= BONUS PENDING UI =================
def bonus_pending_ui(pending_type, out_url):
    st.markdown("### 🔗 외부 페이지로 이동 후 다시 돌아오세요")
    st.info("페이지를 확인하신 뒤, 아래 버튼을 눌러 게임으로 복귀하면 기회가 1회 추가됩니다.")

    if st.link_button("외부 페이지 열기", out_url, use_container_width=True, key=f"mg_open_{pending_type}"):
        pass

    if st.button("게임으로 돌아와서 재도전하기", use_container_width=True, key=f"mg_back_{pending_type}"):
        # 돌아오면 기회 1회 제공
        st.session_state.mg_attempts = 1
        if pending_type == "share":
            st.session_state.mg_shared = True
        if pending_type == "ad":
            st.session_state.mg_ad = True
        st.session_state.mg_bonus_pending = None
        st.rerun()

# ================= STEP 1 =================
if st.session_state.step == 1:
    st.title("🔮 2026 운세")
    st.caption(APP_VERSION)

    birth = st.date_input("생년월일", value=date(2000,1,1), key="s1_birth")
    mbti = st.text_input("MBTI", key="s1_mbti")

    if st.button("운세 보기", use_container_width=True, key="s1_go"):
        st.session_state.birth = birth
        st.session_state.mbti = mbti
        st.session_state.step = 2
        st.rerun()

# ================= STEP 2 =================
elif st.session_state.step == 2:
    birth = st.session_state.birth
    mbti = st.session_state.mbti

    db = load_zodiac()
    zkey, zko = get_zodiac(birth)
    fortune = random.choice(db.get(zkey, ["운세 준비중입니다."]))

    st.subheader("🧧 띠 운세")
    st.write(zko, fortune)

    st.subheader("🃏 오늘의 타로")
    tarot = daily_tarot(str(birth)+mbti+today_key())
    st.write(tarot)

    st.markdown("---")
    st.info("정수기·생활가전 렌탈 상담 👉 다나눔렌탈 1660-2445")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("← 다시 입력", use_container_width=True, key="s2_back"):
            st.session_state.step = 1
            st.rerun()
    with c2:
        if st.button("🎮 미니게임 하고 ☕ 커피쿠폰 받기", use_container_width=True, key="s2_game"):
            st.session_state.step = 3
            st.rerun()

# ================= STEP 3 =================
elif st.session_state.step == 3:
    reset_daily()

    birth = st.session_state.birth
    mbti = st.session_state.mbti
    _, zko = get_zodiac(birth)

    st.markdown("## 🎮 미니게임: 20.260~20.269초 맞추기")
    st.warning("행사상품 소진 시 공지없이 조기 종료될 수 있습니다.")

    attempts = st.session_state.mg_attempts
    running = st.session_state.mg_running

    now = 0.0
    if running and st.session_state.mg_start:
        now = time.perf_counter() - st.session_state.mg_start

    # ===== Timer Panel (bordered, image-like) =====
    st.markdown(
        f"""
        <div style="border:4px solid #333;border-radius:16px;padding:18px;margin:10px 0;text-align:center;
                    background:linear-gradient(135deg,#111,#333);color:#00ffcc;">
            <div style="font-size:18px;letter-spacing:2px;">TIMER</div>
            <div style="font-size:64px;font-weight:900;line-height:1.1;">{fmt(now)}</div>
            <div style="font-size:14px;color:#ccc;">seconds</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"남은 기회: {attempts}")

    if running:
        st.audio(CLOCK_SOUND, autoplay=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("START", disabled=(attempts<=0 or running), use_container_width=True, key="mg_start"):
            st.session_state.mg_running = True
            st.session_state.mg_start = time.perf_counter()
            st.rerun()
    with c2:
        if st.button("STOP", disabled=(not running), use_container_width=True, key="mg_stop"):
            sec = now
            ok = MINIGAME_MIN <= sec <= MINIGAME_MAX
            st.session_state.mg_running = False
            st.session_state.mg_start = None
            st.session_state.mg_last = sec
            st.session_state.mg_ok = ok
            st.session_state.mg_attempts = max(0, st.session_state.mg_attempts - 1)
            st.audio(REVEAL_SOUND, autoplay=True)
            st.rerun()
    with c3:
        if st.button("← 운세로", use_container_width=True, key="mg_back_to_fortune"):
            st.session_state.step = 2
            st.rerun()

    if running:
        time.sleep(0.03)
        st.rerun()

    # ===== Result =====
    if st.session_state.mg_last is not None:
        if st.session_state.mg_ok:
            st.success(f"🎉 성공! 기록 {fmt(st.session_state.mg_last)}초\n즉시 당첨 대상입니다. 아래 정보를 입력해주세요.")
        else:
            st.error(f"❌ 실패! 기록 {fmt(st.session_state.mg_last)}초")
            st.markdown("### 추첨 응모를 희망하시면 아래 정보를 입력해주세요.")

    # ===== Bonus Flow (external link then return) =====
    if st.session_state.mg_last is not None and not st.session_state.mg_ok:
        st.markdown("### 🔁 재도전 기회 얻기")

        if st.session_state.mg_bonus_pending is None:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("친구공유하고 재도전하기", use_container_width=True, key="mg_bonus_share"):
                    st.session_state.mg_bonus_pending = "share"
                    st.rerun()
            with b2:
                if st.button("광고보고 재도전하기", use_container_width=True, key="mg_bonus_ad"):
                    st.session_state.mg_bonus_pending = "ad"
                    st.rerun()
        else:
            if st.session_state.mg_bonus_pending == "share":
                bonus_pending_ui("share", SHARE_OUT_URL)
            elif st.session_state.mg_bonus_pending == "ad":
                bonus_pending_ui("ad", AD_OUT_URL)

    # ===== Entry Form =====
    if st.session_state.mg_last is not None:
        with st.form("mg_entry_form"):
            name = st.text_input("이름", key="mg_name")
            phone = st.text_input("전화번호", key="mg_phone")
            st.text_input("생년월일", value=str(birth), disabled=True, key="mg_birth")
            consent = st.checkbox("개인정보처리방침 동의", key="mg_consent")

            if st.form_submit_button("응모하기", use_container_width=True):
                if not (name and phone and consent):
                    st.error("모든 정보를 입력하고 동의해주세요.")
                else:
                    row = [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        name, phone, "ko",
                        fmt(st.session_state.mg_last),
                        bool(st.session_state.mg_shared),
                        bool(st.session_state.mg_ad),
                        str(birth),
                    ]
                    if send_to_sheet(row):
                        st.success("응모 완료! 감사합니다 ☕")
                    else:
                        st.warning("전송 실패, 다시 시도해주세요.")
