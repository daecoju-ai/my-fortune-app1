
import os
import json
import time
import math
import hashlib
import glob
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# -----------------------------
# Config
# -----------------------------
APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세"
DB_PATH = os.environ.get("FORTUNE_DB_PATH", "data/fortunes_ko.json")

# Google Sheet (이미 사용자 확정)
SHEET_ID_DEFAULT = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"

# Mini-game success window
GAME_TARGET_MIN = 20.260
GAME_TARGET_MAX = 20.269

# -----------------------------
# Helpers: deterministic RNG
# -----------------------------
def _stable_int_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def _pick(items: List[str], seed: str) -> str:
    if not items:
        return "—"
    idx = _stable_int_hash(seed) % len(items)
    return items[idx]

def _now_kst() -> dt.datetime:
    # Streamlit Cloud is usually UTC; treat as KST for this app
    return dt.datetime.utcnow() + dt.timedelta(hours=9)

# -----------------------------
# Zodiac
# -----------------------------
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
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
    # 기준: 1900년이 쥐띠(전통 단순화, 음력/절기 미반영)
    idx = (year - 1900) % 12
    key = ZODIAC_ORDER[idx]
    return key, ZODIAC_LABELS.get(key, key)

# -----------------------------
# DB loading
# -----------------------------
@st.cache_data(show_spinner=False)
def load_db(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"__error__": f"DB 파일을 찾을 수 없습니다: {path}"}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_pool(db: Dict[str, Any]) -> Dict[str, List[str]]:
    # 지원 스키마: top-level "pools" or legacy top-level keys
    if "pools" in db and isinstance(db["pools"], dict):
        return db["pools"]
    # legacy fallback: many lists at root
    pools = {}
    for k, v in db.items():
        if isinstance(v, list):
            pools[k] = v
    return pools

def get_combos(db: Dict[str, Any]) -> Dict[str, Any]:
    if "combos" in db and isinstance(db["combos"], dict):
        return db["combos"]
    if "pools" in db and isinstance(db["pools"], dict) and "combos" in db["pools"]:
        return db["pools"]["combos"]
    return {}

# -----------------------------
# Fortune composing
# -----------------------------
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]

MBTI_TRAITS = {
    "INTJ":"내향 · 직관 · 논리 · 계획",
    "INTP":"내향 · 직관 · 논리 · 유연",
    "ENTJ":"외향 · 직관 · 논리 · 계획",
    "ENTP":"외향 · 직관 · 논리 · 유연",
    "INFJ":"내향 · 직관 · 감정 · 계획",
    "INFP":"내향 · 직관 · 감정 · 유연",
    "ENFJ":"외향 · 직관 · 감정 · 계획",
    "ENFP":"외향 · 직관 · 감정 · 유연",
    "ISTJ":"내향 · 현실 · 논리 · 계획",
    "ISFJ":"내향 · 현실 · 감정 · 계획",
    "ESTJ":"외향 · 현실 · 논리 · 계획",
    "ESFJ":"외향 · 현실 · 감정 · 계획",
    "ISTP":"내향 · 현실 · 논리 · 유연",
    "ISFP":"내향 · 현실 · 감정 · 유연",
    "ESTP":"외향 · 현실 · 논리 · 유연",
    "ESFP":"외향 · 현실 · 감정 · 유연",
}

def build_result(db: Dict[str, Any], birth: dt.date, mbti: str) -> Dict[str, str]:
    zodiac_key, zodiac_label = zodiac_from_year(birth.year)
    pools = get_pool(db)
    combos = get_combos(db)

    # seed base: birth + today (for today/tomorrow feel), plus mbti + zodiac
    now = _now_kst()
    seed_base = f"{birth.isoformat()}|{mbti}|{zodiac_key}|{now.date().isoformat()}"

    def pick_pool(pool_name: str, extra: str) -> str:
        items = pools.get(pool_name, [])
        return _pick(items, seed_base + "|" + pool_name + "|" + extra)

    # zodiac one-liner (띠별)
    zodiac_one = ""
    if "zodiac_one_liner" in pools:
        zodiac_one = pick_pool("zodiac_one_liner", "zodiac")
    elif "zodiac_one_liners" in pools:
        zodiac_one = pick_pool("zodiac_one_liners", "zodiac")

    # combo advice
    combo_key = f"{zodiac_label}_{mbti}"
    combo_obj = combos.get(combo_key, {})
    combo_one = "—"
    combo_adv = "—"
    if isinstance(combo_obj, dict):
        one_liners = combo_obj.get("combo_one_liner") or combo_obj.get("one_liner") or []
        advices = combo_obj.get("combo_advice") or combo_obj.get("advice") or []
        if isinstance(one_liners, list) and one_liners:
            combo_one = _pick(one_liners, seed_base + "|combo_one")
        if isinstance(advices, list) and advices:
            combo_adv = _pick(advices, seed_base + "|combo_adv")

    result = {
        "zodiac_label": zodiac_label,
        "mbti": mbti,
        "mbti_traits": MBTI_TRAITS.get(mbti, mbti),
        "zodiac_one_liner": zodiac_one or "—",
        "saju_one_liner": pick_pool("saju_one_liner", "saju"),
        "today_fortune": pick_pool("today_fortune", "today"),
        "tomorrow_fortune": pick_pool("tomorrow_fortune", "tomorrow"),
        "year_overall": pick_pool("year_overall", "year"),
        "love_advice": pick_pool("love_advice", "love"),
        "money_advice": pick_pool("money_advice", "money"),
        "work_study_advice": pick_pool("work_study_advice", "work"),
        "health_advice": pick_pool("health_advice", "health"),
        "action_tip": pick_pool("action_tip", "action"),
        "combo_one_liner": combo_one,
        "combo_advice": combo_adv,
    }
    return result

# -----------------------------
# Tarot image pick
# -----------------------------
def pick_tarot_image(seed: str) -> Optional[str]:
    candidates = []
    for pattern in [
        "assets/tarot/majors/*.png",
        "assets/tarot/minors/*.png",
        "assets/tarot/*.png",
    ]:
        candidates.extend(glob.glob(pattern))
    # exclude back image for draw
    candidates = [p for p in candidates if os.path.basename(p).lower() not in ("back.png","back.jpg","back.jpeg")]
    if not candidates:
        return None
    idx = _stable_int_hash(seed + "|tarot") % len(candidates)
    return candidates[idx]

# -----------------------------
# Google Sheet logging
# -----------------------------
def append_to_sheet(
    sheet_id: str,
    name: str,
    phone: str,
    lang: str,
    record: str,
    shared: bool,
    consult: str,
    product: str,
) -> Tuple[bool, str]:
    """
    Column schema (fixed by user):
    A 시간, B 이름, C 전화번호, D 언어, E 기록초, F 공유여부, G 상담신청
    - product는 별도 컬럼이 없으므로, 상담신청 컬럼에 "O(정수기)" 같이 넣음
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except Exception:
        return False, "gspread/credentials 모듈이 없습니다. requirements 및 secrets 확인 필요"

    try:
        creds_info = st.secrets.get("gcp_service_account")
        if not creds_info:
            return False, "st.secrets['gcp_service_account'] 가 비어있습니다."
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(dict(creds_info), scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1
        now = _now_kst().strftime("%Y-%m-%d %H:%M:%S")
        consult_val = consult
        if product:
            consult_val = f"{consult}({product})" if consult else f"({product})"
        ws.append_row([now, name, phone, lang, record, str(shared), consult_val], value_input_option="USER_ENTERED")
        return True, "구글시트 저장 완료"
    except Exception as e:
        return False, f"구글시트 저장 실패: {type(e).__name__}"

# -----------------------------
# UI: styles
# -----------------------------
def inject_styles():
    st.markdown(
        """
<style>
/* base */
.block-container { padding-top: 1.2rem; padding-bottom: 4rem; max-width: 860px; }
h1,h2,h3 { letter-spacing: -0.02em; }

/* cards */
.card {
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,.08);
  border: 1px solid rgba(255,255,255,.25);
}
.card-result {
  background: linear-gradient(135deg, rgba(160,140,255,.35), rgba(120,200,255,.22));
}
.card-ad {
  background: linear-gradient(135deg, rgba(255,235,195,.55), rgba(255,200,220,.35));
}
.card-game {
  background: linear-gradient(135deg, rgba(210,255,230,.45), rgba(200,220,255,.30));
}

/* small label chips */
.chip {
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0,0,0,.06);
  margin-right: 6px;
  font-size: 0.88rem;
}

/* share button spacing */
.share-area { margin-top: 14px; }

/* hide SEO block */
.seo-hide { display:none; height:0; overflow:hidden; }
</style>
        """,
        unsafe_allow_html=True,
    )

def inject_hidden_seo():
    # 프론트에는 안보이게 (display:none)
    seo = """
<div class="seo-hide">
다나눔렌탈, 정수기 렌탈, 안마의자 렌탈, 가전 렌탈, 제휴카드 월 0원, 설치당일 최대 50만원, 사은품, 성수동 렌탈, MBTI 운세, 2026 띠 운세, 사주, 오늘 운세, 내일 운세, 타로 카드, tarot, gemini, chatgpt, 네이버, 구글 검색
</div>
"""
    st.markdown(seo, unsafe_allow_html=True)

# -----------------------------
# MBTI quick test (12/16 문항 유지)
# -----------------------------
QUESTIONS_12 = [
    ("E","I","사람들과 함께 있을 때 에너지가 차오른다","혼자 있을 때 에너지가 차오른다"),
    ("S","N","현재의 사실/현실이 더 중요하다","가능성과 의미를 더 본다"),
    ("T","F","판단은 논리가 우선이다","판단은 마음/관계가 우선이다"),
    ("J","P","계획대로 진행되는 게 편하다","상황에 맞춰 유연하게 바꾸는 게 편하다"),
    ("E","I","먼저 말을 꺼내는 편이다","상대가 말 걸 때까지 기다린다"),
    ("S","N","경험해본 방식이 안전하다","새로운 방식이 더 끌린다"),
    ("T","F","문제 해결이 가장 중요하다","상대 기분 배려가 중요하다"),
    ("J","P","마감/룰이 있어야 추진된다","마감이 가까워져야 집중된다"),
    ("E","I","사교 모임이 즐겁다","사교 모임은 피곤하다"),
    ("S","N","디테일을 잘 챙긴다","큰 그림을 먼저 본다"),
    ("T","F","피드백은 직설이 좋다","피드백은 부드럽게가 좋다"),
    ("J","P","정리정돈이 되어야 마음이 편하다","어느 정도 어수선해도 괜찮다"),
]

QUESTIONS_16 = QUESTIONS_12 + [
    ("E","I","새로운 사람을 만나면 금방 친해진다","새로운 사람은 시간이 필요하다"),
    ("S","N","증거/근거가 있어야 믿는다","직감이 강한 편이다"),
    ("T","F","공정함이 최우선이다","배려가 최우선이다"),
    ("J","P","결정을 빨리 내리는 편이다","결정을 미루는 편이다"),
]

def mbti_from_answers(answers: List[str]) -> str:
    score = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
    for a in answers:
        if a in score:
            score[a] += 1
    def pick(a,b):
        return a if score[a] >= score[b] else b
    return f"{pick('I','E')}{pick('N','S')}{pick('T','F')}{pick('J','P')}"

# -----------------------------
# Result page open in new tab
# -----------------------------
def build_result_url(birth: dt.date, mbti: str) -> str:
    # same app URL, only query params; new tab will compute result again
    y,m,d = birth.year, birth.month, birth.day
    return f"?page=result&y={y}&m={m}&d={d}&mbti={mbti}"

def open_new_tab_button(label: str, url: str, key: str):
    # HTML button to open new tab (Streamlit buttons can't set target)
    st.components.v1.html(
        f"""
        <div style="margin-top: 8px;">
          <a href="{url}" target="_blank" style="text-decoration:none;">
            <button style="
              width:100%;
              background:#6d55ff;
              color:white;
              padding:14px 16px;
              border:none;
              border-radius:14px;
              font-size:18px;
              font-weight:700;
              cursor:pointer;
            ">{label}</button>
          </a>
        </div>
        """,
        height=70,
    )

# -----------------------------
# Share button
# -----------------------------
def render_share_button(text: str):
    # 모바일은 Web Share API 지원 가능
    st.components.v1.html(
        f"""
        <div class="share-area">
          <button id="shareBtn" style="
              width:100%;
              background:#ffffff;
              color:#222;
              padding:14px 16px;
              border:1px solid rgba(0,0,0,.15);
              border-radius:14px;
              font-size:16px;
              font-weight:700;
              cursor:pointer;
          ">친구에게 공유하기</button>
        </div>
        <script>
        const btn = document.getElementById("shareBtn");
        btn.onclick = async () => {{
          const shareData = {{ title: document.title, text: "{text}", url: window.location.href }};
          try {{
            if (navigator.share) {{
              await navigator.share(shareData);
            }} else {{
              await navigator.clipboard.writeText(window.location.href);
              alert("링크를 복사했어요!");
            }}
          }} catch (e) {{
            // user cancelled
          }}
        }};
        </script>
        """,
        height=90,
    )

# -----------------------------
# Mini-game (Stopwatch)
# -----------------------------
def init_game_state():
    st.session_state.setdefault("game_running", False)
    st.session_state.setdefault("game_start_ts", None)
    st.session_state.setdefault("game_stopped", False)
    st.session_state.setdefault("game_elapsed", None)
    st.session_state.setdefault("game_success", None)
    st.session_state.setdefault("game_retry_unlocked", False)
    st.session_state.setdefault("game_attempts", 0)
    st.session_state.setdefault("game_max_attempts", 2)  # 기본 1회 + 공유 후 1회

def reset_game(hard: bool=False):
    st.session_state.game_running = False
    st.session_state.game_start_ts = None
    st.session_state.game_stopped = False
    st.session_state.game_elapsed = None
    st.session_state.game_success = None
    if hard:
        st.session_state.game_retry_unlocked = False
        st.session_state.game_attempts = 0

def render_game(sheet_id: str):
    init_game_state()
    st.markdown('<div class="card card-game">', unsafe_allow_html=True)
    st.subheader("🎯 미니게임: 20.26초 맞추기")
    st.caption("선착순으로 커피 쿠폰 지급되며 조기종료 될 수 있습니다")

    # status
    attempts_left = st.session_state.game_max_attempts - st.session_state.game_attempts
    st.write(f"남은 시도: **{max(attempts_left,0)}회**")

    # start/stop
    col1, col2 = st.columns(2)
    with col1:
        if st.button("START", use_container_width=True, disabled=st.session_state.game_running or attempts_left<=0):
            st.session_state.game_running = True
            st.session_state.game_stopped = False
            st.session_state.game_start_ts = time.time()
            st.session_state.game_elapsed = None
            st.session_state.game_success = None
            st.session_state.game_attempts += 1

    with col2:
        if st.button("STOP", use_container_width=True, disabled=not st.session_state.game_running):
            elapsed = time.time() - float(st.session_state.game_start_ts)
            st.session_state.game_running = False
            st.session_state.game_stopped = True
            st.session_state.game_elapsed = elapsed
            st.session_state.game_success = (GAME_TARGET_MIN <= elapsed <= GAME_TARGET_MAX)

    # timer display (stop 화면 유지)
    elapsed_show = 0.0
    if st.session_state.game_running and st.session_state.game_start_ts:
        elapsed_show = time.time() - float(st.session_state.game_start_ts)
    elif st.session_state.game_stopped and st.session_state.game_elapsed is not None:
        elapsed_show = float(st.session_state.game_elapsed)

    st.markdown(
        f"""
        <div style="font-size:44px;font-weight:800;letter-spacing:-0.03em;margin:6px 0 10px;">
          {elapsed_show:0.3f}s
        </div>
        """,
        unsafe_allow_html=True,
    )

    # outcome + retry logic
    if st.session_state.game_stopped:
        actual = float(st.session_state.game_elapsed or 0.0)
        if st.session_state.game_success:
            st.success("🎉 성공! 20.26초에 거의 딱 맞췄어요. 커피쿠폰 응모를 진행해 주세요.")
            with st.form("game_win_form", clear_on_submit=False):
                name = st.text_input("이름")
                phone = st.text_input("연락처(휴대폰)")
                agree = st.checkbox("개인정보처리방침에 동의합니다")
                # 옵션 (요청 반영)
                consult = st.selectbox("상담 요청", ["X", "O"], index=0)
                coupon = st.selectbox("커피쿠폰 응모", ["O", "X"], index=0)
                product = st.selectbox("관심 제품", ["", "정수기", "안마의자", "기타가전"], index=0)
                submitted = st.form_submit_button("신청완료", use_container_width=True)
            if submitted:
                if not (name and phone and agree):
                    st.warning("이름/연락처 입력 + 동의가 필요합니다.")
                else:
                    # 규칙: 커피쿠폰 응모 X면 시트 입력 금지 (요청)
                    if coupon == "X":
                        st.info("커피쿠폰 응모를 선택하지 않아 저장하지 않았습니다.")
                    else:
                        ok, msg = append_to_sheet(
                            sheet_id=sheet_id,
                            name=name,
                            phone=phone,
                            lang="ko",
                            record=f"{actual:0.3f}",
                            shared=False,
                            consult=("O" if consult=="O" else ""),
                            product=product,
                        )
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
        else:
            st.error(f"아쉽네요! **{actual:0.3f}s** 입니다. (성공 구간: {GAME_TARGET_MIN:0.3f}~{GAME_TARGET_MAX:0.3f})")

            # retry unlock only once via share button
            if (not st.session_state.game_retry_unlocked) and (st.session_state.game_attempts < st.session_state.game_max_attempts):
                st.caption("재도전 1회는 **친구에게 공유하기**를 누르면 열립니다.")
                if st.button("친구에게 공유하기 (재도전 1회)", use_container_width=True):
                    st.session_state.game_retry_unlocked = True
                    st.session_state.game_max_attempts = 2  # 1회 + 공유로 1회
                    st.success("재도전 1회가 열렸습니다. START를 눌러 다시 도전하세요!")

            if st.button("게임 초기화", use_container_width=True):
                reset_game(hard=False)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Ad / 상담
# -----------------------------
def render_ad(sheet_id: str):
    st.markdown('<div class="card card-ad">', unsafe_allow_html=True)
    st.subheader("📢 다나눔렌탈 광고")
    st.write("**정수기 렌탈 제휴카드시 월 0원부터**  \n설치당일 최대 50만원 + 사은품.")
    with st.expander("상담신청하기", expanded=False):
        with st.form("ad_form", clear_on_submit=False):
            product = st.selectbox("제품 선택", ["정수기", "안마의자", "기타가전"])
            name = st.text_input("이름")
            phone = st.text_input("연락처(휴대폰)")
            agree = st.checkbox("개인정보처리방침에 동의합니다")
            submit = st.form_submit_button("신청완료", use_container_width=True)
        if submit:
            if not (name and phone and agree):
                st.warning("이름/연락처 입력 + 동의가 필요합니다.")
            else:
                ok, msg = append_to_sheet(
                    sheet_id=sheet_id,
                    name=name,
                    phone=phone,
                    lang="ko",
                    record="",
                    shared=False,
                    consult="O",
                    product=product,
                )
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Main screens
# -----------------------------
def render_input_screen(db: Dict[str, Any]):
    st.title(APP_TITLE)
    st.caption("완전 무료")

    # DB path quick check
    if "__error__" in db:
        st.error(f"DB 로딩 실패: {db['__error__']}")
        st.stop()

    # language fixed ko for now (sheet schema has lang)
    sheet_id = st.secrets.get("sheet_id", SHEET_ID_DEFAULT)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("1) 생년월일 입력")
    birth = st.date_input("생년월일", value=dt.date(1995, 1, 1), min_value=dt.date(1900, 1, 1), max_value=dt.date(2030, 12, 31))

    st.subheader("2) MBTI 선택 또는 테스트")
    mode = st.radio("MBTI 입력 방식", ["직접 선택", "12문항 테스트", "16문항 테스트"], horizontal=True)

    mbti = None
    if mode == "직접 선택":
        mbti = st.selectbox("MBTI", MBTI_LIST, index=2)  # ENTJ default-ish
    else:
        questions = QUESTIONS_12 if mode == "12문항 테스트" else QUESTIONS_16
        answers = []
        for i, (a, b, text_a, text_b) in enumerate(questions, start=1):
            choice = st.radio(
                f"Q{i}.",
                [f"{a} - {text_a}", f"{b} - {text_b}"],
                key=f"q_{mode}_{i}",
            )
            answers.append(a if choice.startswith(a) else b)
        mbti = mbti_from_answers(answers)
        st.info(f"테스트 결과: **{mbti}**")

    st.subheader("3) 결과 보기")
    url = build_result_url(birth, mbti)
    open_new_tab_button("결과 보기 (새창)", url, key="open_result")

    st.markdown("</div>", unsafe_allow_html=True)

    # 광고/미니게임 (입력 화면에도 노출)
    render_ad(sheet_id)
    render_game(sheet_id)

def render_result_screen(db: Dict[str, Any]):
    st.title("결과")

    if "__error__" in db:
        st.error(f"DB 로딩 실패: {db['__error__']}")
        st.stop()

    qp = st.query_params
    try:
        y = int(qp.get("y", "1995"))
        m = int(qp.get("m", "1"))
        d = int(qp.get("d", "1"))
        mbti = str(qp.get("mbti", "ENTJ")).upper()
        mbti = mbti if mbti in MBTI_LIST else "ENTJ"
        birth = dt.date(y, m, d)
    except Exception:
        st.error("URL 파라미터가 올바르지 않습니다. 다시 입력 화면에서 진행해 주세요.")
        return

    result = build_result(db, birth, mbti)

    inject_styles()
    inject_hidden_seo()

    # Result card (gradient)
    st.markdown('<div class="card card-result">', unsafe_allow_html=True)
    st.markdown(f"**띠 운세:** {result['zodiac_label']}")
    if result.get("zodiac_one_liner") and result["zodiac_one_liner"] != "—":
        st.info(result["zodiac_one_liner"])

    st.markdown(f"**MBTI 특징:** {result['mbti_traits']}")

    # Tarot image
    tarot_path = pick_tarot_image(f"{birth.isoformat()}|{mbti}|{result['zodiac_label']}")
    if tarot_path and os.path.exists(tarot_path):
        st.image(tarot_path, use_container_width=True)

    st.markdown("---")
    st.subheader("사주 한 마디")
    st.write(result["saju_one_liner"])

    st.subheader("오늘 운세")
    st.write(result["today_fortune"])

    st.subheader("내일 운세")
    st.write(result["tomorrow_fortune"])

    st.subheader("2026 전체 운세")
    st.write(result["year_overall"])

    st.subheader("조합 조언")
    st.write(result["combo_advice"])

    st.markdown("</div>", unsafe_allow_html=True)

    # Share right below result card (요청)
    render_share_button("2026 운세 결과 공유")

    # CTA buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("다시 입력", use_container_width=True):
            st.query_params.clear()
            st.query_params["page"] = "input"
            st.rerun()
    with col2:
        st.link_button("앱 새로고침", url=".", use_container_width=True)

    # 아래에 광고/게임도 이어서 (원하면 유지)
    sheet_id = st.secrets.get("sheet_id", SHEET_ID_DEFAULT)
    render_ad(sheet_id)
    render_game(sheet_id)

# -----------------------------
# App entry
# -----------------------------
def main():
    st.set_page_config(page_title="2026 운세", page_icon="🔮", layout="centered")

    inject_styles()
    inject_hidden_seo()

    db = load_db(DB_PATH)

    page = st.query_params.get("page", "input")
    if page == "result":
        render_result_screen(db)
    else:
        render_input_screen(db)

if __name__ == "__main__":
    main()
