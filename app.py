import os
import json
import time
import base64
import hashlib
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote, unquote

import streamlit as st
import streamlit.components.v1 as components

# Optional: Google Sheets
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None


# =========================
# 기본 설정
# =========================
APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세"
DEFAULT_LANG = "ko"

# DB 파일 경로 (data 폴더 내부)
DB_PATH = Path("data") / "fortunes_ko.json"

# Google Sheet (사용자 메모에 저장된 ID)
DEFAULT_SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
DEFAULT_SHEET_TAB = "시트1"

# 광고(다나눔렌탈)
AD_TITLE = "다나눔렌탈"
AD_LINE1 = "정수기 렌탈 제휴카드시 월 0원부터"
AD_LINE2 = "설치당일 최대 50만원 + 사은품."
AD_BUTTON_TEXT = "상담신청하기"
AD_URL = "https://다나눔렌탈.com"  # 필요시 변경

# 미니게임 규칙
TARGET_MIN = 20.260
TARGET_MAX = 20.269

# SEO 키워드(프론트에 안 보이게)
SEO_KEYWORDS = [
    "2026 운세", "오늘 운세", "내일 운세", "사주", "띠 운세", "MBTI 운세",
    "정수기 렌탈", "안마의자 렌탈", "다나눔렌탈", "커피쿠폰", "이벤트"
]


# =========================
# 유틸
# =========================
def _b64url_encode_json(obj: dict) -> str:
    raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

def _b64url_decode_json(s: str) -> dict:
    pad = "=" * ((4 - len(s) % 4) % 4)
    raw = base64.urlsafe_b64decode((s + pad).encode("ascii"))
    return json.loads(raw.decode("utf-8"))

def stable_int_hash(text: str) -> int:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def pick_from_list(items, seed_int: int):
    if not items:
        return ""
    idx = seed_int % len(items)
    return items[idx]

def today_seed(y: int, m: int, d: int) -> str:
    return f"{y:04d}{m:02d}{d:02d}"

def safe_get(d: dict, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def zodiac_from_year(year: int, db: dict) -> str:
    """
    db["zodiac"]["order"] : ["rat","ox",...]
    db["zodiac"]["labels"] : {"rat":"쥐띠", ...}
    """
    order = safe_get(db, "zodiac", "order", default=[])
    labels = safe_get(db, "zodiac", "labels", default={})
    if not order or len(order) != 12:
        return "—"
    # 기준: 1900년=쥐띠(일반적으로 많이 쓰는 매핑)
    idx = (year - 1900) % 12
    animal_key = order[idx]
    return labels.get(animal_key, animal_key)

def combo_key_from_zodiac_label(zodiac_label: str, mbti: str) -> str:
    """
    combos 키는 예: "말_ENTJ" 형태(띠 글자에서 '띠' 제거)
    zodiac_label이 "말띠"면 "말"로 변환
    """
    z = zodiac_label.replace("띠", "")
    return f"{z}_{mbti}"

def sheets_available() -> bool:
    return (gspread is not None) and (Credentials is not None) and ("gcp_service_account" in st.secrets)

def append_to_sheet(row: dict, sheet_id: str = DEFAULT_SHEET_ID, tab: str = DEFAULT_SHEET_TAB) -> bool:
    if not sheets_available():
        st.warning("구글시트 연동이 설정되어 있지 않습니다. (st.secrets에 gcp_service_account 필요)")
        return False

    creds_info = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)

    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(tab)

    # 헤더 확인
    existing_header = ws.row_values(1)
    cols = list(row.keys())

    if not existing_header:
        ws.append_row(cols, value_input_option="RAW")
        existing_header = cols

    missing = [c for c in cols if c not in existing_header]
    if missing:
        new_header = existing_header + missing
        ws.update("1:1", [new_header])
        existing_header = new_header

    values = [row.get(c, "") for c in existing_header]
    ws.append_row(values, value_input_option="RAW")
    return True


# =========================
# CSS / UI
# =========================
def inject_css():
    st.markdown(
        """
        <style>
          .muted { color: rgba(0,0,0,0.55); font-size: 0.92rem; }
          .card {
            border-radius: 16px;
            padding: 16px 16px;
            border: 1px solid rgba(0,0,0,0.08);
            margin: 10px 0;
            box-shadow: 0 6px 18px rgba(0,0,0,0.06);
          }
          .card.result {
            background: linear-gradient(135deg, rgba(120, 80, 255, 0.16), rgba(60, 180, 255, 0.12));
          }
          .card.ad {
            background: linear-gradient(135deg, rgba(255, 170, 90, 0.18), rgba(255, 80, 160, 0.10));
          }
          .card.game {
            background: linear-gradient(135deg, rgba(60, 60, 80, 0.10), rgba(120, 120, 255, 0.10));
          }
          .pill {
            display:inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid rgba(0,0,0,0.08);
            background: rgba(255,255,255,0.7);
            font-size: 0.9rem;
          }
          .btn-like {
            display:inline-block;
            padding: 10px 14px;
            border-radius: 999px;
            background: #6b5cff;
            color: white;
            font-weight: 700;
            text-decoration:none;
          }
          .btn-like.gray {
            background: #f2f2f2;
            color: #222;
            border: 1px solid rgba(0,0,0,0.10);
          }
          /* SEO 블록 숨김 */
          .seo-hidden { display:none !important; height:0; overflow:hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def card(title: str, body_html: str, kind: str = "result"):
    st.markdown(f"<div class='card {kind}'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-weight:800; font-size:1.12rem; margin-bottom:8px;'>{title}</div>", unsafe_allow_html=True)
    st.markdown(body_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def seo_block():
    kw = " , ".join(SEO_KEYWORDS)
    st.markdown(
        f"<div class='seo-hidden'>keywords: {kw}</div>",
        unsafe_allow_html=True
    )


# =========================
# MBTI (직접/12/16) - 구조 변화 금지
# =========================
MBTI_12 = [
    ("E/I", "사람들과 함께 있으면 에너지가 오른다", ("E","I"), "외향", "내향"),
    ("E/I", "혼자만의 시간이 꼭 필요하다", ("I","E"), "내향", "외향"),
    ("S/N", "현재 상황과 사실이 더 중요하다", ("S","N"), "감각", "직관"),
    ("S/N", "가능성과 아이디어를 떠올리는 게 즐겁다", ("N","S"), "직관", "감각"),
    ("T/F", "결정할 때 논리와 원칙이 우선이다", ("T","F"), "사고", "감정"),
    ("T/F", "결정할 때 사람의 마음과 가치가 우선이다", ("F","T"), "감정", "사고"),
    ("J/P", "계획을 세우고 정리하는 게 편하다", ("J","P"), "판단", "인식"),
    ("J/P", "즉흥적으로 유연하게 하는 게 편하다", ("P","J"), "인식", "판단"),
    ("E/I", "처음 보는 사람과도 쉽게 말이 나온다", ("E","I"), "외향", "내향"),
    ("S/N", "실용적인 해결책을 찾는 편이다", ("S","N"), "감각", "직관"),
    ("T/F", "감정보다 사실을 말하는 편이다", ("T","F"), "사고", "감정"),
    ("J/P", "마감 전에 미리 끝내놓는다", ("J","P"), "판단", "인식"),
]

MBTI_16 = MBTI_12 + [
    ("E/I", "모임 후에도 피곤함이 덜하다", ("E","I"), "외향", "내향"),
    ("S/N", "경험/검증된 방법이 더 믿음직하다", ("S","N"), "감각", "직관"),
    ("T/F", "공정함이 가장 중요하다고 느낀다", ("T","F"), "사고", "감정"),
    ("J/P", "선택지를 열어두는 게 마음 편하다", ("P","J"), "인식", "판단"),
]

def run_mbti_quiz(kind: str) -> str:
    questions = MBTI_12 if kind == "12문항" else MBTI_16
    scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}

    st.markdown(f"#### 🔎 MBTI 간단 검사 ({kind})")
    for idx, (dim, text, (a,b), left, right) in enumerate(questions, start=1):
        choice = st.radio(
            f"{idx}. {text}",
            [a, b],
            format_func=lambda x: f"{x} · {left}" if x==a else f"{x} · {right}",
            key=f"q_{kind}_{idx}",
        )
        scores[choice] += 1

    mbti = (
        ("E" if scores["E"]>=scores["I"] else "I") +
        ("S" if scores["S"]>=scores["N"] else "N") +
        ("T" if scores["T"]>=scores["F"] else "F") +
        ("J" if scores["J"]>=scores["P"] else "P")
    )
    return mbti


# =========================
# 미니게임 상태
# =========================
def game_init_state():
    ss = st.session_state
    ss.setdefault("game_running", False)
    ss.setdefault("game_start_ts", None)
    ss.setdefault("game_last_time", None)
    ss.setdefault("game_last_result", None)  # "SUCCESS"/"FAIL"
    ss.setdefault("retry_granted", False)
    ss.setdefault("retry_used", False)
    ss.setdefault("shared_clicked", False)

def game_start():
    ss = st.session_state
    ss["game_running"] = True
    ss["game_start_ts"] = time.time()
    ss["game_last_time"] = None
    ss["game_last_result"] = None

def game_stop():
    ss = st.session_state
    elapsed = time.time() - float(ss["game_start_ts"])
    ss["game_running"] = False
    ss["game_last_time"] = float(elapsed)

    if TARGET_MIN <= elapsed <= TARGET_MAX:
        ss["game_last_result"] = "SUCCESS"
    else:
        ss["game_last_result"] = "FAIL"

def stopwatch_ui():
    game_init_state()
    ss = st.session_state

    card(
        "🎮 미니게임: 스톱워치 20.26초 정확히 맞추기",
        """
        <div class='muted'>
          선착순으로 커피 쿠폰 지급되며 조기종료 될 수 있습니다.<br/>
          규칙: <b>20.260 ~ 20.269초</b> 사이에 STOP하면 성공!
        </div>
        """,
        kind="game"
    )

    c1, c2, c3 = st.columns([1,1,2])

    with c1:
        if st.button("START", use_container_width=True, disabled=ss["game_running"]):
            # 재도전 제한:
            # - 최초 FAIL 이후, 공유로 1회만 재도전 가능
            # - retry_used=True면 더 이상 시작 못하게 막음
            if ss["retry_used"] and ss["game_last_result"] == "FAIL":
                st.warning("재도전 기회(1회)를 이미 사용했습니다.")
            else:
                game_start()

    with c2:
        if st.button("STOP", use_container_width=True, disabled=not ss["game_running"]):
            game_stop()

    with c3:
        if ss["game_running"]:
            st.info("⏱️ 실행 중... STOP을 눌러 기록을 확정하세요.")
        elif ss["game_last_time"] is not None:
            t = ss["game_last_time"]
            if ss["game_last_result"] == "SUCCESS":
                st.success(f"성공! 기록: {t:.3f}초 ✅")
            else:
                st.error(f"실패… 기록: {t:.3f}초 ❌ (실제 스톱시간 포함)")

    # 실패 시: 공유로 1회 재도전
    if ss["game_last_result"] == "FAIL":
        if (not ss["retry_granted"]) and (not ss["retry_used"]):
            st.warning("아깝다! **친구에게 공유하면 재도전 1회**를 드립니다.")
            if st.button("친구에게 공유하고 재도전 1회 받기", use_container_width=True):
                ss["retry_granted"] = True
                ss["shared_clicked"] = True
                st.success("재도전 1회가 활성화되었습니다. 다시 START → STOP!")
        elif ss["retry_granted"] and (not ss["retry_used"]):
            st.info("재도전 1회 가능 상태입니다. 다시 START → STOP!")
        else:
            st.info("재도전 기회를 이미 사용했습니다.")

    # 재도전 사용 처리:
    # retry_granted 상태에서 다시 STOP을 눌러 FAIL이 확정되면 retry_used 처리
    if ss["retry_granted"] and (ss["game_last_time"] is not None) and (ss["game_last_result"] == "FAIL"):
        if not ss["retry_used"]:
            ss["retry_used"] = True

    return ss["game_last_result"], ss["game_last_time"], ss["shared_clicked"]


# =========================
# DB 로드 + 결과 생성(핵심 수정)
# =========================
@st.cache_data(show_spinner=False)
def load_db():
    if not DB_PATH.exists():
        return None, f"DB 파일을 찾을 수 없습니다: {DB_PATH.as_posix()}"
    try:
        db = json.loads(DB_PATH.read_text(encoding="utf-8"))
        # 최소 구조 체크
        if "pools" not in db or "combos" not in db or "zodiac" not in db:
            return None, "DB 구조 오류: pools/combos/zodiac 키가 필요합니다."
        return db, None
    except Exception as e:
        return None, f"DB 로딩 실패: {e}"

def build_result(db: dict, birth_y: int, birth_m: int, birth_d: int, mbti: str):
    zodiac_label = zodiac_from_year(birth_y, db)          # 예: "말띠"
    combo_key = combo_key_from_zodiac_label(zodiac_label, mbti)  # 예: "말_ENTJ"
    combo = db["combos"].get(combo_key)

    # 시드(결정론적): 생년월일 + MBTI + 오늘 날짜
    today = date.today()
    seed_text = f"{birth_y:04d}-{birth_m:02d}-{birth_d:02d}|{mbti}|{today_seed(today.year,today.month,today.day)}"
    seed_int = stable_int_hash(seed_text)

    pools = db["pools"]

    # pools에서 뽑기
    saju_one = pick_from_list(pools.get("saju_one_liner", []), seed_int + 11)
    today_text = pick_from_list(pools.get("daily_today", []), seed_int + 21)
    tomorrow_text = pick_from_list(pools.get("daily_tomorrow", []), seed_int + 31)
    year_2026_text = pick_from_list(pools.get("year_2026_fortune", []), seed_int + 41)

    love = pick_from_list(pools.get("love_luck", []), seed_int + 51)
    money = pick_from_list(pools.get("money_luck", []), seed_int + 61)
    work = pick_from_list(pools.get("work_study_advice", []), seed_int + 71)
    health = pick_from_list(pools.get("health_advice", []), seed_int + 81)
    action_tip = pick_from_list(pools.get("action_tip", []), seed_int + 91)

    # combo에서 뽑기
    combo_one = ""
    combo_adv = ""
    mbti_trait = ""

    if combo:
        combo_one = pick_from_list(combo.get("combo_one_liner", []), seed_int + 101)
        combo_adv = pick_from_list(combo.get("combo_advice", []), seed_int + 111)
        # mbti trait은 pools에 따로 없으니 combo에 있다면 사용
        mbti_trait = pick_from_list(combo.get("mbti_trait", []), seed_int + 121) if isinstance(combo.get("mbti_trait"), list) else (combo.get("mbti_trait") or "")
    else:
        # combo가 없을 때도 최소는 보이게
        combo_one = ""
        combo_adv = ""

    return {
        "zodiac": zodiac_label,
        "mbti": mbti,
        "combo_key": combo_key,
        "combo_one_liner": combo_one,
        "combo_advice": combo_adv,
        "mbti_trait": mbti_trait,
        "saju_one": saju_one,
        "today": today_text,
        "tomorrow": tomorrow_text,
        "year_2026": year_2026_text,
        "love": love,
        "money": money,
        "work": work,
        "health": health,
        "action_tip": action_tip,
        "seed_text": seed_text,
    }


# =========================
# 상태
# =========================
def ensure_state():
    ss = st.session_state
    ss.setdefault("stage", "input")  # input / result
    ss.setdefault("name", "")
    ss.setdefault("birth_y", 1990)
    ss.setdefault("birth_m", 1)
    ss.setdefault("birth_d", 1)
    ss.setdefault("mbti_mode", "직접 선택")
    ss.setdefault("mbti_selected", "ENFP")
    ss.setdefault("result_payload", None)

    # 상담/쿠폰
    ss.setdefault("consult_name", "")
    ss.setdefault("consult_phone", "")
    ss.setdefault("agree_privacy", False)
    ss.setdefault("consult_request", False)
    ss.setdefault("coffee_coupon", True)  # 기본 O로 두는 편이 전환율 좋음
    ss.setdefault("product_category", "정수기")

def valid_date(y,m,d) -> bool:
    try:
        date(y,m,d)
        return True
    except Exception:
        return False


# =========================
# 새창 결과 열기(핵심)
# =========================
def open_result_new_tab(payload: dict):
    """
    payload를 b64로 URL에 실어 새 탭에서 결과 화면 재구성
    """
    p = _b64url_encode_json(payload)
    js = f"""
    <script>
      const url = window.location.origin + window.location.pathname + "?view=result&p={p}";
      window.open(url, "_blank");
    </script>
    """
    components.html(js, height=0)


# =========================
# 화면: 헤더 + 광고 + 입력
# =========================
def render_header():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="centered")
    inject_css()
    seo_block()

    st.markdown(f"## {APP_TITLE}")
    st.markdown("<div class='muted'>띠 + MBTI + 사주 + 오늘/내일 + 2026 전체 운세</div>", unsafe_allow_html=True)

def render_ad_and_form():
    # 광고 카드
    card(
        f"📣 광고: {AD_TITLE}",
        f"""
        <div style="font-weight:800; font-size:1.02rem; margin-bottom:6px;">{AD_LINE1}</div>
        <div style="margin-bottom:10px;">{AD_LINE2}</div>
        <a href="{AD_URL}" target="_blank" class="btn-like" style="margin-right:10px;">{AD_TITLE} 바로가기</a>
        """,
        kind="ad"
    )

    with st.expander(f"✅ {AD_BUTTON_TEXT} (이름/연락처 입력)"):
        ss = st.session_state

        ss["product_category"] = st.selectbox("원하시는 렌탈", ["정수기", "안마의자", "기타가전"], index=["정수기","안마의자","기타가전"].index(ss["product_category"]))
        ss["consult_name"] = st.text_input("이름", value=ss["consult_name"])
        ss["consult_phone"] = st.text_input("연락처", value=ss["consult_phone"])

        ss["consult_request"] = st.radio("상담 요청", ["O", "X"], index=0 if ss["consult_request"] else 1) == "O"
        ss["coffee_coupon"] = st.radio("커피쿠폰 응모", ["O", "X"], index=0 if ss["coffee_coupon"] else 1) == "O"
        ss["agree_privacy"] = st.checkbox("개인정보처리방침 동의", value=ss["agree_privacy"])

        st.caption("※ 규칙: 상담신청 O + 커피쿠폰 응모 X 인 경우 구글시트 입력되지 않습니다.")

        if st.button("신청완료", use_container_width=True):
            if not ss["agree_privacy"]:
                st.error("개인정보처리방침 동의가 필요합니다.")
                return

            # 입력 금지 조건
            if ss["consult_request"] and (not ss["coffee_coupon"]):
                st.warning("규칙에 따라 (상담 O + 쿠폰 X) 조합은 구글시트에 저장하지 않습니다.")
                return

            row = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "이름": ss["consult_name"],
                "전화번호": ss["consult_phone"],
                "언어": DEFAULT_LANG,
                "기록초": "",
                "공유여부": False,
                "상담신청": ss["consult_request"],
                "제품": ss["product_category"],
                "커피쿠폰": ss["coffee_coupon"],
            }
            ok = append_to_sheet(row)
            if ok:
                st.success("신청이 완료되었습니다. (구글시트 저장 완료)")


def render_input(db):
    ss = st.session_state

    st.markdown("### 입력")
    ss["name"] = st.text_input("이름 (결과에 표시돼요)", value=ss["name"])

    col1, col2, col3 = st.columns(3)
    with col1:
        ss["birth_y"] = st.number_input("년", min_value=1900, max_value=2100, value=int(ss["birth_y"]), step=1)
    with col2:
        ss["birth_m"] = st.number_input("월", min_value=1, max_value=12, value=int(ss["birth_m"]), step=1)
    with col3:
        ss["birth_d"] = st.number_input("일", min_value=1, max_value=31, value=int(ss["birth_d"]), step=1)

    if not valid_date(int(ss["birth_y"]), int(ss["birth_m"]), int(ss["birth_d"])):
        st.warning("생년월일이 올바르지 않아요. (월/일 확인)")
        return

    st.markdown("---")
    st.markdown("### MBTI 선택")
    ss["mbti_mode"] = st.radio(
        "MBTI를 어떻게 할까요?",
        ["직접 선택", "모르면 간단 검사(12문항)", "모르면 간단 검사(16문항)"],
        index=["직접 선택", "모르면 간단 검사(12문항)", "모르면 간단 검사(16문항)"].index(ss["mbti_mode"]),
    )

    mbti = None
    if ss["mbti_mode"] == "직접 선택":
        all_types = [
            "ISTJ","ISFJ","INFJ","INTJ",
            "ISTP","ISFP","INFP","INTP",
            "ESTP","ESFP","ENFP","ENTP",
            "ESTJ","ESFJ","ENFJ","ENTJ",
        ]
        ss["mbti_selected"] = st.selectbox("MBTI", all_types, index=all_types.index(ss["mbti_selected"]) if ss["mbti_selected"] in all_types else 10)
        mbti = ss["mbti_selected"]
    else:
        kind = "12문항" if "12" in ss["mbti_mode"] else "16문항"
        mbti = run_mbti_quiz(kind)
        st.info(f"예상 MBTI: **{mbti}**")

    st.markdown("---")

    # 광고 + 상담 폼
    render_ad_and_form()

    st.markdown("---")

    # 미니게임
    game_result, game_time, shared_clicked = stopwatch_ui()

    st.markdown("---")

    # 결과보기: 새창(새탭)으로
    if st.button("결과 보기", use_container_width=True):
        payload = {
            "name": ss["name"],
            "birth_y": int(ss["birth_y"]),
            "birth_m": int(ss["birth_m"]),
            "birth_d": int(ss["birth_d"]),
            "mbti": mbti,
            "game_result": game_result,
            "game_time": game_time,
            "shared_clicked": shared_clicked,
        }
        ss["result_payload"] = payload
        open_result_new_tab(payload)
        st.success("결과를 새 창으로 열었습니다. (팝업 차단 시 해제 필요)")
        # 같은 창에서도 결과 화면으로 이동은 유지
        ss["stage"] = "result"
        st.rerun()


# =========================
# 결과 화면
# =========================
def render_share_button():
    # 결과 카드 바로 밑(요구사항)
    st.markdown(
        """
        <div style="margin: 10px 0 18px 0;">
          <a class="btn-like" href="#" onclick="navigator.share ? navigator.share({title:document.title, url:window.location.href}) : alert('공유 기능이 지원되지 않는 브라우저입니다. 주소를 복사해 공유해주세요.'); return false;">
            친구에게 공유하기
          </a>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_game_claim_form_if_success(game_result, game_time, shared_clicked):
    """
    성공 시: 이름/전화번호 입력 → 구글시트 저장
    실패 시: 저장 X (단, 공유 여부는 result_payload로 남김)
    """
    ss = st.session_state

    if game_result != "SUCCESS":
        return

    st.markdown("---")
    card("🎁 미니게임 성공! 커피쿠폰 응모", "<div class='muted'>이름/연락처 입력 후 동의하면 응모 완료됩니다.</div>", kind="game")

    with st.form("coupon_claim_form"):
        name = st.text_input("이름", value=ss.get("consult_name",""))
        phone = st.text_input("연락처", value=ss.get("consult_phone",""))
        agree = st.checkbox("개인정보처리방침 동의", value=False)

        submitted = st.form_submit_button("응모 완료(구글시트 저장)", use_container_width=True)

    if submitted:
        if not agree:
            st.error("개인정보처리방침 동의가 필요합니다.")
            return

        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "이름": name,
            "전화번호": phone,
            "언어": DEFAULT_LANG,
            "기록초": f"{(game_time or 0):.3f}",
            "공유여부": bool(shared_clicked),
            "상담신청": False,
            "제품": "",
            "커피쿠폰": True,
            "게임결과": "SUCCESS",
        }
        ok = append_to_sheet(row)
        if ok:
            st.success("응모 완료! (구글시트 저장 완료)")

def render_result(db, payload: dict):
    name = payload.get("name","")
    birth_y = int(payload.get("birth_y", 1990))
    birth_m = int(payload.get("birth_m", 1))
    birth_d = int(payload.get("birth_d", 1))
    mbti = (payload.get("mbti") or "ENFP").upper()

    game_result = payload.get("game_result")
    game_time = payload.get("game_time")
    shared_clicked = bool(payload.get("shared_clicked", False))

    result = build_result(db, birth_y, birth_m, birth_d, mbti)

    st.markdown("# 결과")

    # 상단 한 줄 요약(수집 욕구 고급 카드 느낌)
    summary = result["combo_one_liner"] or "오늘은 흐름을 정리하면 운이 열리는 날이에요."
    card(
        f"띠 운세: {result['zodiac']}",
        f"""
        <div style="font-size:1.05rem; font-weight:800; margin-bottom:8px;">{summary}</div>
        <div class='muted'>MBTI 특징: {result['mbti_trait'] or '외향 · 직관 · 논리 · 계획'}</div>
        """,
        kind="result"
    )

    # ✅ 요구: 결과 카드 바로 밑 공유 버튼
    render_share_button()

    # 본문 카드들
    card("사주 한 마디", result["saju_one"] or "—", kind="result")
    card("오늘 운세", result["today"] or "—", kind="result")
    card("내일 운세", result["tomorrow"] or "—", kind="result")
    card("2026 전체 운세", result["year_2026"] or "—", kind="result")

    # 조합 조언(4가지)
    card(
        "조합 조언",
        f"""
        <div><b>연애운:</b> {result["love"] or "—"}</div>
        <div><b>재물운:</b> {result["money"] or "—"}</div>
        <div><b>일/학업운:</b> {result["work"] or "—"}</div>
        <div><b>건강운:</b> {result["health"] or "—"}</div>
        """,
        kind="result"
    )

    card("오늘의 액션팁", result["action_tip"] or "—", kind="result")

    # 미니게임 결과 문구(실패 시 실제 기록 포함)
    st.markdown("---")
    if game_result == "SUCCESS":
        st.success(f"미니게임 결과: 성공 ✅ (기록 {game_time:.3f}초)")
    elif game_result == "FAIL":
        if game_time is not None:
            st.error(f"미니게임 결과: 실패 ❌ (실제 스톱시간 {game_time:.3f}초)")
        else:
            st.error("미니게임 결과: 실패 ❌")
    else:
        st.info("미니게임 결과: 참여 전")

    # 성공 시 응모 폼 + 구글시트 저장
    render_game_claim_form_if_success(game_result, game_time, shared_clicked)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("다시 입력", use_container_width=True):
            st.session_state["stage"] = "input"
            st.rerun()
    with c2:
        # 주소 복사용 안내
        st.markdown("<div class='muted' style='padding-top:10px;'>공유가 안되면 주소를 복사해 보내세요.</div>", unsafe_allow_html=True)


# =========================
# 엔트리
# =========================
def main():
    ensure_state()
    render_header()

    db, err = load_db()
    if err:
        st.error(err)
        st.stop()

    # URL 파라미터로 result 새탭 진입 지원
    qp = st.query_params
    view = qp.get("view", [""])[0] if isinstance(qp.get("view"), list) else qp.get("view", "")
    p = qp.get("p", [""])[0] if isinstance(qp.get("p"), list) else qp.get("p", "")

    if view == "result" and p:
        try:
            payload = _b64url_decode_json(p)
            render_result(db, payload)
            return
        except Exception:
            st.error("결과 payload 해석 실패. 다시 입력에서 결과를 열어주세요.")
            st.session_state["stage"] = "input"

    # 일반 플로우
    if st.session_state["stage"] == "input":
        render_input(db)
    else:
        payload = st.session_state.get("result_payload")
        if not payload:
            st.session_state["stage"] = "input"
            st.rerun()
        render_result(db, payload)

if __name__ == "__main__":
    main()
