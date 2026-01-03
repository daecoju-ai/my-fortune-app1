import streamlit as st
import json
import time
import re
from datetime import datetime, date
from pathlib import Path

# Optional (Google Sheets)
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None

# =========================
# Config
# =========================
APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세 (완전 무료)"
DB_PATH = Path("data") / "fortunes_ko.json"

# 다나눔렌탈 광고(원하면 링크만 바꿔서 사용)
DANANUM_RENTAL_NAME = "다나눔렌탈"
DANANUM_RENTAL_URL = "https://다나눔렌탈.com"

# Google Sheet (기본값: 기억해둔 ID)
DEFAULT_SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
DEFAULT_SHEET_TAB = "Sheet1"

TARGET_SECONDS = 20.26
SUCCESS_TOLERANCE = 0.15  # ±0.15초면 성공 처리

# =========================
# UI helpers
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        .stApp{
            background: linear-gradient(135deg, rgba(170,200,255,0.25), rgba(255,190,230,0.18));
        }
        .block-container{ padding-top: 1.0rem; padding-bottom: 2.5rem; }
        .card{
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 18px;
            padding: 14px 14px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        }
        .muted{ color: rgba(0,0,0,0.55); font-size: 0.92rem; }
        .pill{
            display:inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(0,0,0,0.06);
            margin-right: 6px;
            font-size: 0.86rem;
        }
        .seo-hidden{position:absolute; left:-9999px; top:-9999px; height:1px; overflow:hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )

def card(title: str, body_md: str):
    st.markdown(
        f"""
        <div class="card">
          <div style="font-weight:800; font-size:1.05rem; margin-bottom:6px;">{title}</div>
          <div>{body_md}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def seo_keywords_block():
    # 검색 키워드(네이버/구글/제미나이/챗지피티 검색 대비)
    keywords = [
        "2026 운세", "띠운세", "사주", "오늘 운세", "내일 운세", "MBTI 운세",
        "무료 운세", "2026 띠+MBTI", "스톱워치 게임", "20.26초 맞추기",
        "안마의자 렌탈", "정수기 렌탈", "가전 렌탈", "다나눔렌탈",
    ]
    st.markdown(
        f"<div class='seo-hidden'>{' · '.join(keywords)}</div>",
        unsafe_allow_html=True
    )

# =========================
# Data / logic
# =========================
def load_db():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")
    data = json.loads(DB_PATH.read_text(encoding="utf-8"))

    if "combos" not in data or not isinstance(data["combos"], dict) or len(data["combos"]) == 0:
        raise ValueError("DB 구조 오류: combos 키가 없거나 비어있습니다.")
    if "zodiacs" not in data or not isinstance(data["zodiacs"], list) or len(data["zodiacs"]) < 12:
        raise ValueError("DB 구조 오류: zodiacs(12띠 목록)가 없습니다.")
    return data

def zodiac_from_year(year: int, db) -> str:
    # 1984년이 쥐띠(=Rat) 기준
    idx = (year - 1984) % 12
    try:
        return db["zodiacs"][idx]["name"]
    except Exception:
        # fallback
        names = ["쥐","소","호랑이","토끼","용","뱀","말","양","원숭이","닭","개","돼지"]
        return names[idx]

def stable_hash_int(s: str) -> int:
    # 파이썬 기본 hash는 실행마다 바뀔 수 있어서, 직접 안정 해시 사용
    h = 2166136261
    for ch in s.encode("utf-8"):
        h ^= ch
        h = (h * 16777619) & 0xFFFFFFFF
    return h

def get_combo_key(zodiac_ko: str, mbti: str) -> str:
    return f"{zodiac_ko}_{mbti.upper()}"

def pick_field(combo: dict, *keys, default=""):
    for k in keys:
        if k in combo and combo[k]:
            return combo[k]
    return default

def get_lucky_point(combo: dict):
    # DB가 lucky_point 객체를 가지기도 하고, lucky_colors/items/numbers/directions로 나뉘기도 함.
    lp = combo.get("lucky_point")
    if isinstance(lp, dict):
        return {
            "color": lp.get("color",""),
            "item": lp.get("item",""),
            "number": lp.get("number",""),
            "direction": lp.get("direction",""),
        }
    # fallback: plural keys
    colors = combo.get("lucky_colors") or []
    items = combo.get("lucky_items") or []
    numbers = combo.get("lucky_numbers") or []
    directions = combo.get("lucky_directions") or []
    return {
        "color": colors[0] if colors else "",
        "item": items[0] if items else "",
        "number": numbers[0] if numbers else "",
        "direction": directions[0] if directions else "",
    }

# =========================
# MBTI quiz (변화금지)
# =========================
MBTI_12 = [
    ("E","I","새 사람 만나면 에너지가 난다 / 혼자 있으면 에너지가 난다"),
    ("E","I","말로 먼저 풀어야 된다 / 생각 정리 후 말한다"),
    ("E","I","모임이 많을수록 신난다 / 적을수록 편하다"),
    ("S","N","현실/사실이 중요 / 의미/가능성이 중요"),
    ("S","N","디테일이 강점 / 큰 그림이 강점"),
    ("S","N","경험이 우선 / 아이디어가 우선"),
    ("T","F","원칙/논리가 우선 / 가치/공감이 우선"),
    ("T","F","문제 해결이 먼저 / 사람 마음이 먼저"),
    ("T","F","팩트가 중요 / 분위기가 중요"),
    ("J","P","계획대로가 편함 / 유연하게가 편함"),
    ("J","P","마감 전에 끝냄 / 막판 집중"),
    ("J","P","정리정돈 선호 / 즉흥적 배치도 OK"),
]

MBTI_16 = [
    # 각 축 4문항(총 16)
    ("E","I","낯선 자리에서도 먼저 인사한다 / 조용히 관찰 후 다가간다"),
    ("E","I","생각보다 말이 먼저 나온다 / 말 전에 생각이 길다"),
    ("E","I","스트레스는 사람 만나 풀린다 / 혼자 쉬어야 풀린다"),
    ("E","I","즉흥 약속도 OK / 약속은 미리 잡는 편"),
    ("S","N","지금 당장 가능한가가 중요 / 언젠가 가능성이 중요"),
    ("S","N","설명은 구체적으로 / 설명은 비유로"),
    ("S","N","현재 사실에 집중 / 미래 상상에 집중"),
    ("S","N","실용성이 최고 / 독창성이 최고"),
    ("T","F","감정보다 판단이 빠르다 / 판단보다 감정이 먼저다"),
    ("T","F","직설적으로 말한다 / 돌려 말한다"),
    ("T","F","정답을 찾는다 / 사람을 챙긴다"),
    ("T","F","논쟁도 괜찮다 / 갈등은 피하고 싶다"),
    ("J","P","일정을 세우면 마음이 편하다 / 일정은 상황 보며 바꾼다"),
    ("J","P","결정이 빠르다 / 결정은 더 고민한다"),
    ("J","P","정리된 환경 선호 / 자유로운 환경 선호"),
    ("J","P","할 일 리스트 필수 / 그때그때 처리"),
]

def run_mbti_quiz(kind: str) -> str:
    questions = MBTI_12 if kind == "12문항" else MBTI_16
    scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}

    st.markdown("#### MBTI 간단 검사")
    st.markdown("<div class='muted'>모르면 아래 문항으로 빠르게 확인해보세요.</div>", unsafe_allow_html=True)

    for idx,(a,b,text) in enumerate(questions, start=1):
        left, right = text.split(" / ")
        choice = st.radio(
            f"{idx}. {text}",
            [a, b],
            format_func=lambda x: f"{x} · {left}" if x==a else f"{x} · {right}",
            key=f"q_{kind}_{idx}",
            horizontal=False,
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
# Google Sheets
# =========================
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

    # 헤더 자동 생성(없으면 1행에 컬럼 생성)
    existing_header = ws.row_values(1)
    cols = list(row.keys())

    if not existing_header:
        ws.append_row(cols, value_input_option="RAW")
        existing_header = cols

    # header에 없는 컬럼은 뒤에 추가
    missing = [c for c in cols if c not in existing_header]
    if missing:
        # expand header row
        new_header = existing_header + missing
        ws.update("1:1", [new_header])
        existing_header = new_header

    values = [row.get(c, "") for c in existing_header]
    ws.append_row(values, value_input_option="RAW")
    return True

def render_sheet_columns_guide():
    st.markdown("#### 구글시트 컬럼 추천(복붙용)")
    cols = [
        "timestamp", "name", "phone",
        "product_category", "consult_request", "coffee_coupon",
        "game_result", "game_time_sec",
        "birthdate", "zodiac", "mbti",
        "combo_key",
    ]
    st.code(", ".join(cols), language="text")
    st.markdown("<div class='muted'>시트 1행(헤더)에 위 컬럼을 넣어두면 정리가 쉬워요. 없어도 앱이 자동으로 헤더를 만들어줍니다.</div>", unsafe_allow_html=True)

# =========================
# Stopwatch mini game
# =========================
def game_init_state():
    ss = st.session_state
    ss.setdefault("game_running", False)
    ss.setdefault("game_start_ts", None)
    ss.setdefault("game_last_time", None)
    ss.setdefault("game_last_result", None)  # "SUCCESS"/"FAIL"
    ss.setdefault("retry_granted", False)
    ss.setdefault("retry_used", False)

def game_reset():
    ss = st.session_state
    ss["game_running"] = False
    ss["game_start_ts"] = None
    ss["game_last_time"] = None
    ss["game_last_result"] = None
    ss["retry_granted"] = False
    ss["retry_used"] = False

def stopwatch_ui():
    game_init_state()
    ss = st.session_state

    st.markdown("### 🎮 미니게임: 스톱워치 20.26초 정확히 맞추기")
    st.markdown("<div class='muted'>정확히 20.26초(±0.15초)로 STOP을 누르면 성공!</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,2])

    with c1:
        if st.button("START", use_container_width=True, disabled=ss["game_running"]):
            ss["game_running"] = True
            ss["game_start_ts"] = time.time()
            ss["game_last_time"] = None
            ss["game_last_result"] = None

    with c2:
        if st.button("STOP", use_container_width=True, disabled=not ss["game_running"]):
            elapsed = time.time() - float(ss["game_start_ts"])
            ss["game_running"] = False
            ss["game_last_time"] = float(elapsed)

            if abs(elapsed - TARGET_SECONDS) <= SUCCESS_TOLERANCE:
                ss["game_last_result"] = "SUCCESS"
            else:
                ss["game_last_result"] = "FAIL"

    with c3:
        if ss["game_running"]:
            st.info("⏱️ 실행 중... STOP을 눌러 기록을 확정하세요.")
        elif ss["game_last_time"] is not None:
            st.success(f"기록: {ss['game_last_time']:.2f}초") if ss["game_last_result"]=="SUCCESS" else st.error(f"기록: {ss['game_last_time']:.2f}초")

    # 실패 시: 공유로 1회 재도전
    if ss["game_last_result"] == "FAIL":
        if (not ss["retry_granted"]) and (not ss["retry_used"]):
            st.warning("아깝다! 친구에게 공유하면 **재도전 1회**를 드립니다.")
            if st.button("친구에게 공유하고 재도전 1회 받기"):
                ss["retry_granted"] = True
                st.success("재도전 1회가 활성화되었습니다. 다시 START 해보세요!")
        elif ss["retry_granted"] and (not ss["retry_used"]):
            st.info("재도전 1회 가능 상태입니다. 다시 START → STOP!")
        else:
            st.info("재도전 기회를 이미 사용했습니다.")

    # 재도전 사용 처리: FAIL에서 retry_granted 상태로 다시 STOP을 누르면 retry_used로 처리
    if ss["retry_granted"] and ss["game_last_time"] is not None and ss["game_last_result"] == "FAIL":
        # 첫 실패 후 재도전 granted 상태에서, 다시 FAIL이 확정되는 순간 retry_used 처리
        # (이미 한 번 FAIL 후 granted 된 상태에서 STOP을 눌렀다는 뜻이므로)
        if not ss["retry_used"]:
            ss["retry_used"] = True

    return ss["game_last_result"], ss["game_last_time"]

# =========================
# Main app
# =========================
def ensure_state():
    ss = st.session_state
    ss.setdefault("stage", "input")  # input -> result
    ss.setdefault("name", "")
    ss.setdefault("birth_y", 1990)
    ss.setdefault("birth_m", 1)
    ss.setdefault("birth_d", 1)
    ss.setdefault("mbti_mode", "직접 선택")
    ss.setdefault("mbti_selected", "ENFP")
    ss.setdefault("mbti_quiz_kind", "12문항")
    ss.setdefault("mbti_from_quiz", None)
    ss.setdefault("result_payload", None)

def valid_date(y,m,d) -> bool:
    try:
        date(y,m,d)
        return True
    except Exception:
        return False

def render_header():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="centered")
    inject_css()

    st.markdown(f"## {APP_TITLE}")
    st.markdown("<div class='muted'>띠 + MBTI + 사주 + 오늘/내일 + 2026 전체 운세</div>", unsafe_allow_html=True)

    # 광고 카드
    card(
        f"📣 광고: {DANANUM_RENTAL_NAME}",
        f"""
        <div style="margin-bottom:8px;">안마의자 · 정수기 · 기타가전 <b>렌탈 상담</b>이 필요하면 아래로!</div>
        <a href="{DANANUM_RENTAL_URL}" target="_blank" style="text-decoration:none;">
          <div class="pill">다나눔렌탈 바로가기</div>
        </a>
        """,
    )

    seo_keywords_block()

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
        ss["mbti_from_quiz"] = mbti
        st.info(f"예상 MBTI: **{mbti}**")

    st.markdown("---")

    # 미니게임
    game_result, game_time = stopwatch_ui()

    st.markdown("---")
    # 결과보기 버튼 (같은 페이지 + 새창 링크 제공)
    if st.button("결과 보기", use_container_width=True):
        ss["result_payload"] = {
            "name": ss["name"],
            "birth": f"{int(ss['birth_y']):04d}-{int(ss['birth_m']):02d}-{int(ss['birth_d']):02d}",
            "birth_y": int(ss["birth_y"]),
            "mbti": mbti,
            "game_result": game_result,
            "game_time": game_time,
        }
        ss["stage"] = "result"
        st.query_params["view"] = "result"
        st.rerun()

    st.markdown(
        "<div class='muted'>TIP) 결과를 새 창으로 보고 싶으면 결과 화면에서 ‘새 창으로 결과보기’를 눌러주세요.</div>",
        unsafe_allow_html=True,
    )

def render_result(db):
    ss = st.session_state
    payload = ss.get("result_payload") or {}

    name = payload.get("name","")
    birth_y = int(payload.get("birth_y", 1990))
    mbti = (payload.get("mbti") or "ENFP").upper()
    birth = payload.get("birth","")
    zodiac = zodiac_from_year(birth_y, db)
    combo_key = get_combo_key(zodiac, mbti)

    st.markdown("## 결과")
    st.markdown(f"<span class='pill'>DB 경로: {DB_PATH.as_posix()}</span>", unsafe_allow_html=True)

    # 새 창 링크(현재 결과를 새 탭으로)
    st.markdown(
        "<div style='margin:8px 0 14px 0;'>"
        "<a href='?view=result' target='_blank' style='text-decoration:none;'>"
        "<div class='pill'>🔗 새 창으로 결과보기</div>"
        "</a>"
        "</div>",
        unsafe_allow_html=True,
    )

    # combo 존재 확인
    if combo_key not in db["combos"]:
        st.error(f"데이터에 조합 키가 없습니다: {combo_key}")
        st.info("DB의 combos 키에 '띠_MBTI' 형식으로 존재하는지 확인해 주세요. (예: 개_ENTJ)")
        if st.button("다시 입력"):
            ss["stage"] = "input"
            st.query_params.clear()
            st.rerun()
        return

    combo = db["combos"][combo_key]

    # 뽑기
    zodiac_fortune = pick_field(combo, "zodiac_fortune", default="")
    mbti_trait = pick_field(combo, "mbti_trait", "mbti_traits", default="")
    saju_message = pick_field(combo, "saju_message", "saju_messages", default="")
    today = pick_field(combo, "today", "daily_today", default="")
    tomorrow = pick_field(combo, "tomorrow", "daily_tomorrow", default="")
    year_2026 = pick_field(combo, "year_2026", default="")

    love = pick_field(combo, "love", default="")
    money = pick_field(combo, "money", default="")
    work = pick_field(combo, "work", default="")
    health = pick_field(combo, "health", default="")

    lucky = get_lucky_point(combo)
    action_tip = pick_field(combo, "action_tip", "action_tips", default="")
    caution = pick_field(combo, "caution", "cautions", default="")

    card("띠 운세", f"<b>{zodiac}</b><br/>{zodiac_fortune}")
    card("MBTI 특징", f"<b>{mbti}</b><br/>{mbti_trait}")
    card("사주 한 마디", saju_message if saju_message else "—")
    card("오늘 운세", today if today else "—")
    card("내일 운세", tomorrow if tomorrow else "—")
    card("2026 전체 운세", year_2026 if year_2026 else "—")

    st.markdown("### 조합 조언")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**연애운:** {love or '—'}")
    st.markdown(f"**재물운:** {money or '—'}")
    st.markdown(f"**일/학업운:** {work or '—'}")
    st.markdown(f"**건강운:** {health or '—'}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 행운 포인트")
    lp_line = f"색: {lucky.get('color','—')} · 아이템: {lucky.get('item','—')} · 숫자: {lucky.get('number','—')} · 방향: {lucky.get('direction','—')}"
    card("행운 포인트", lp_line)

    if action_tip:
        card("오늘의 액션팁", action_tip)
    if caution:
        card("주의할 점", caution)

    # =====================
    # 리드(이름/전화번호) 수집
    # =====================
    st.markdown("---")
    st.markdown("## 🎁 이벤트/상담 신청")

    # 미니게임 성공이면 반드시 입력
    game_result = payload.get("game_result")
    game_time = payload.get("game_time")
    if game_result == "SUCCESS":
        st.success("미니게임 성공! 🎉 커피쿠폰 응모/상담 신청을 진행해 주세요.")
    elif game_result == "FAIL":
        st.warning("미니게임은 실패했어요. 그래도 상담 신청은 가능해요.")
    else:
        st.info("미니게임 기록이 없어요. 그래도 상담 신청은 가능해요.")

    with st.expander("📌 (중요) 구글시트 컬럼은 어떻게 만들까요?"):
        render_sheet_columns_guide()

    product_category = st.selectbox("관심 품목", ["안마의자", "정수기", "기타가전"], index=0)

    consult_request = st.radio("상담 요청", ["O", "X"], horizontal=True, index=0)
    coffee_coupon = st.radio("커피쿠폰 응모", ["O", "X"], horizontal=True, index=0)

    # 규칙: '상담 요청 O + 커피쿠폰 X'면 구글시트 입력 금지(요청대로)
    will_write_sheet = (coffee_coupon == "O")

    if consult_request == "O" and coffee_coupon == "X":
        st.info("안내: **상담 요청 O + 커피쿠폰 X** 선택 시, 구글시트에는 저장하지 않습니다.")

    lead_name = st.text_input("이름", value=name or "")
    lead_phone = st.text_input("전화번호", placeholder="예) 010-1234-5678")

    if st.button("제출", use_container_width=True):
        # 간단 전화번호 검사
        phone_clean = re.sub(r"[^0-9]", "", lead_phone or "")
        if len(phone_clean) < 9:
            st.error("전화번호를 정확히 입력해 주세요.")
            return

        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": lead_name.strip() if lead_name else "",
            "phone": lead_phone.strip(),
            "product_category": product_category,
            "consult_request": consult_request,
            "coffee_coupon": coffee_coupon,
            "game_result": game_result or "",
            "game_time_sec": f"{float(game_time):.2f}" if isinstance(game_time,(int,float)) else "",
            "birthdate": birth,
            "zodiac": zodiac,
            "mbti": mbti,
            "combo_key": combo_key,
        }

        if will_write_sheet:
            ok = append_to_sheet(row, sheet_id=DEFAULT_SHEET_ID, tab=DEFAULT_SHEET_TAB)
            if ok:
                st.success("제출 완료! (구글시트 저장 완료)")
            else:
                st.warning("제출은 되었지만 구글시트 저장은 실패했어요. 설정을 확인해 주세요.")
        else:
            st.success("제출 완료! (설정에 따라 구글시트에는 저장하지 않았어요)")

    st.markdown("---")
    colA, colB = st.columns(2)
    with colA:
        if st.button("전체 초기화", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.query_params.clear()
            st.rerun()
    with colB:
        if st.button("다시 입력", use_container_width=True):
            ss["stage"] = "input"
            st.query_params.clear()
            st.rerun()

def main():
    ensure_state()
    render_header()

    # query param으로 새창 결과보기 지원
    view = st.query_params.get("view", "")
    if view == "result" and st.session_state.get("result_payload"):
        st.session_state["stage"] = "result"

    try:
        db = load_db()
    except Exception as e:
        st.error(f"DB 로딩 실패: {e}")
        st.stop()

    if st.session_state["stage"] == "input":
        render_input(db)
    else:
        render_result(db)

if __name__ == "__main__":
    main()
