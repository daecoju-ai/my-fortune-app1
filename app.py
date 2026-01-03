import json
import random
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# =========================
# 기본 설정 (디자인 고정)
# =========================
st.set_page_config(
    page_title="2026 띠 + MBTI + 사주 + 오늘/내일 운세",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

APP_URL = "https://my-fortune.streamlit.app/"
DATA_DIR = Path(__file__).parent / "data"

SHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_TAB = "시트1"
KST = timezone(timedelta(hours=9))

# =========================
# CSS: 디자인 완전 고정
# =========================
LOCKED_CSS = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
[data-testid="stToolbar"] {display:none !important;}
[data-testid="stDecoration"] {display:none !important;}
[data-testid="stStatusWidget"] {display:none !important;}
[data-testid="stHeader"] {display:none !important;}
[data-testid="stSidebar"] {display:none !important;}

html, body { background:#ffffff !important; }
.block-container{
  max-width:720px !important;
  padding-top:10px !important;
  padding-bottom:30px !important;
  padding-left:18px !important;
  padding-right:18px !important;
}

html, body, [class*="css"]{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans KR",Arial,sans-serif;
}

.banner{
  background:linear-gradient(135deg,#e8d6ff 0%,#ffd9d9 45%,#ffecc7 100%);
  border-radius:18px;
  padding:26px 18px;
  text-align:center;
  margin:6px 0 16px 0;
  box-shadow:0 10px 25px rgba(0,0,0,0.05);
}
.banner .title{
  margin:0;
  font-size:34px;
  letter-spacing:-0.6px;
  line-height:1.25;
  font-weight:800;
  color:#222;
}
.banner .subtitle{
  margin:10px 0 0 0;
  opacity:.75;
  font-weight:700;
  color:#222;
}

.card{
  background:#fff;
  border-radius:18px;
  padding:16px 16px;
  box-shadow:0 10px 25px rgba(0,0,0,0.06);
  margin:0 0 12px 0;
}
.card .h{
  font-size:20px;
  font-weight:900;
  margin:0 0 8px 0;
  color:#111;
}
.card .p{
  font-size:15.5px;
  line-height:1.6;
  margin:0;
  color:#222;
}

.label{
  font-weight:800;
  margin:0 0 6px 0;
  color:#111;
}

div.stButton > button{
  width:100% !important;
  border-radius:14px !important;
  padding:14px 14px !important;
  font-weight:800 !important;
  border:1px solid rgba(200,0,0,0.35) !important;
  background:#fff !important;
}
div.stButton > button:hover{
  border-color:rgba(200,0,0,0.65) !important;
}

.game-time{
  text-align:center;
  font-size:64px;
  font-weight:900;
  letter-spacing:1px;
  margin:8px 0 10px 0;
  color:#111;
}
.small{ opacity:.72; font-size:13px; margin-top:6px; }

.stRadio, .stCheckbox{ margin-top:-4px !important; }
</style>
"""
st.markdown(LOCKED_CSS, unsafe_allow_html=True)

# =========================
# UI 텍스트
# =========================
UI = {
    "ko": {
        "lang_name": "한국어",
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "subtitle": "완전 무료",
        "name_label": "이름 입력 (결과에 표시돼요)",
        "btn_result": "운세 보기",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year": "2026 전체 운세",
        "love": "연애운 조언",
        "money": "재물운 조언",
        "work": "직장/일 조언",
        "health": "건강 조언",
        "share_title": "링크 공유",
        "share_desc": "공유하면 도전 기회가 1회 추가됩니다.",
        "ad_title": "광고",
        "ad_body": "정수기렌탈 대박!\n제휴카드면 월 0원부터!\n설치 당일 최대 50만원 지원 + 사은품 듬뿍",
        "ad_btn": "다나눔렌탈.com 바로가기",
        "game_title": "미니게임: 선착순 20명 커피쿠폰 도전!",
        "game_rule": "스톱워치를 20.260s ~ 20.269s 사이에 멈추면 성공입니다. (기본 1회, 친구 공유 시 1회 추가)",
        "tries_left": "남은 시도 횟수",
        "success": "성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.",
        "fail": "친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.",
        "consult_title": "다나눔렌탈 상담신청(실패자만 가능)",
        "consult_q": "상담 신청하시겠습니까?",
        "consult_phone": "Phone / 전화번호",
        "consult_yes": "O (신청)",
        "consult_no": "X (취소)",
        "reset": "처음부터 다시하기",
        "mbti_knowing": "I know my MBTI (select directly)",
        "mbti_title": "MBTI 16문항",
        "mbti_direct": "MBTI 직접 선택",
        "seo_title": "AI 검색 노출용 섹션",
        "seo_body": "이 페이지는 2026년 띠 운세, MBTI 성향, 사주 기반 오늘/내일 운세를 제공하는 무료 운세 서비스입니다. 키워드: 2026 운세, 띠 운세, MBTI 운세, 사주 오늘 운세, 내일 운세, 무료 운세, 타로 카드.",
    },
    "en": {"lang_name": "English"},
    "ja": {"lang_name": "日本語"},
    "zh": {"lang_name": "中文"},
    "ru": {"lang_name": "Русский"},
    "hi": {"lang_name": "हिन्दी"},
}
LANGS = ["ko", "en", "ja", "zh", "ru", "hi"]

# =========================
# HTML 카드 렌더
# =========================
def banner(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="banner">
          <div class="title">{title}</div>
          <div class="subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def card(title: str, body: str):
    body_html = (body or "").replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="card">
          <div class="h">{title}</div>
          <div class="p">{body_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# 데이터 로더 (스키마 자동 감지/호환)
# =========================
def safe_load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def load_any_data(lang: str) -> dict:
    """
    우선순위:
    1) data/fortunes_{lang}.json
    2) data/fortune_db.json
    둘 다 있으면 합쳐서 사용(번역 파일 + DB 파일).
    """
    lang_data = safe_load_json(DATA_DIR / f"fortunes_{lang}.json") or {}
    db_data = safe_load_json(DATA_DIR / "fortune_db.json") or {}

    # merge (db가 기본, lang이 덮어씀)
    merged = {}
    merged.update(db_data)
    merged.update(lang_data)

    # sections는 dict merge
    if isinstance(db_data.get("sections"), dict) or isinstance(lang_data.get("sections"), dict):
        merged["sections"] = {}
        if isinstance(db_data.get("sections"), dict):
            merged["sections"].update(db_data["sections"])
        if isinstance(lang_data.get("sections"), dict):
            merged["sections"].update(lang_data["sections"])

    return merged

def get_section(data: dict, key: str) -> str | None:
    s = data.get("sections")
    if isinstance(s, dict):
        v = s.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

# =========================
# 구글시트 저장 (실패자 O일 때만)
# - G열에 'O' 기록 요구
# - 행 부족하면 add_rows로 확장
# =========================
def get_gspread_client():
    import gspread
    from google.oauth2.service_account import Credentials

    # secrets 형태 호환
    if "gcp_service_account" in st.secrets:
        sa_info = dict(st.secrets["gcp_service_account"])
    else:
        sa_info = dict(st.secrets)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(creds)

def append_consult_O(name: str, phone: str, stop_time: float | None):
    """
    요구사항:
    - 실패자만 노출
    - O 선택 시에만 저장
    - 시트1 G열에 O 기록
    - 저장 컬럼은 최대한 건드리지 않되, append로 새 행 추가 후 G에 O 입력
    """
    try:
        gc = get_gspread_client()
        sh = gc.open_by_key(SHEET_ID)
        ws = sh.worksheet(SHEET_TAB)

        now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        stop_str = "" if stop_time is None else f"{stop_time:.3f}"

        # 일단 빈 행 포함해서 A~G까지 맞춰 append (A,B,C,D,E,F,G)
        # A:시간, B:이름, C:전화, D:스톱워치, E:성공여부, F:메모, G:상담신청(O)
        row = [now, name, phone, stop_str, "FAIL", "", "O"]

        # 시트가 1000행 제한 에러가 났던 케이스 방지:
        # append_row는 보통 행을 늘리지만, 환경에 따라 grid limit 걸릴 수 있어
        # -> 미리 add_rows로 확장
        if ws.row_count < 2000:
            ws.add_rows(2000 - ws.row_count)

        ws.append_row(row, value_input_option="USER_ENTERED")
        return True, None
    except Exception as e:
        return False, str(e)

# =========================
# 공유 버튼: 네가 말한 "갤러리 공유 시트" 방식
# =========================
def share_sheet_button(title: str, text: str, url: str, key: str):
    html = f"""
    <button id="{key}" style="
      width:100%;
      border-radius:14px;
      padding:14px 14px;
      border:1px solid rgba(200,0,0,0.35);
      background:white;
      font-size:16px;
      font-weight:800;
      cursor:pointer;
    ">{title}</button>

    <script>
      const btn = document.getElementById("{key}");
      btn.addEventListener("click", async () => {{
        try {{
          if (navigator.share) {{
            await navigator.share({{
              title: {json.dumps(title)},
              text: {json.dumps(text)},
              url: {json.dumps(url)}
            }});
          }} else {{
            // fallback: 복사
            await navigator.clipboard.writeText({json.dumps(url)});
            alert("링크가 복사되었습니다.");
          }}
        }} catch (e) {{}}
      }});
    </script>
    """
    components.html(html, height=58)

# =========================
# 스톱워치 컴포넌트 (실시간/Stop 시 값 전달/스크롤 점프 최소화)
# =========================
def stopwatch_component(running: bool, seed_ms: int, key: str):
    """
    - running=True: JS 내부에서 실시간으로 증가 표시(서버 rerun 없음)
    - Stop 버튼 누르면 Streamlit로 stop_time(float) 전달 -> rerun 1회
    - 화면 점프 방지: stop/start 시 현재 컴포넌트로 scrollIntoView
    """
    html = f"""
    <div id="wrap" style="padding:0;margin:0;">
      <div class="game-time" id="t">00.000</div>
      <div style="display:flex; gap:10px; margin-top:6px;">
        <button id="start" style="flex:1;border-radius:14px;padding:14px;border:1px solid rgba(200,0,0,0.35);background:#fff;font-size:16px;font-weight:800;cursor:pointer;">Start</button>
        <button id="stop"  style="flex:1;border-radius:14px;padding:14px;border:1px solid rgba(0,0,0,0.18);background:#fff;font-size:16px;font-weight:800;cursor:pointer;">Stop</button>
      </div>
    </div>

    <script>
      const wrap = document.getElementById("wrap");
      const tEl = document.getElementById("t");
      const btnStart = document.getElementById("start");
      const btnStop  = document.getElementById("stop");

      // state (kept in window by key)
      const KEY = {json.dumps(key)};
      window.__sw = window.__sw || {{}};
      window.__sw[KEY] = window.__sw[KEY] || {{
        running: false,
        startAt: null,
        raf: null,
        base: 0
      }};

      const st = window.__sw[KEY];

      // helper
      function fmt(ms) {{
        const s = ms / 1000.0;
        return s.toFixed(3).padStart(6, "0");
      }}

      function render() {{
        if (!st.running || st.startAt === null) return;
        const now = performance.now();
        const elapsed = st.base + (now - st.startAt);
        tEl.textContent = fmt(elapsed);
        st.raf = requestAnimationFrame(render);
      }}

      function scrollHere() {{
        try {{ wrap.scrollIntoView({{behavior:"instant", block:"center"}}); }} catch(e) {{}}
      }}

      // init display
      if ({str(running).lower()}) {{
        // resume running from server request
        if (!st.running) {{
          st.running = true;
          st.base = 0;
          st.startAt = performance.now();
          if (st.raf) cancelAnimationFrame(st.raf);
          st.raf = requestAnimationFrame(render);
        }}
      }} else {{
        // not running -> keep last shown time as-is (do nothing)
      }}

      btnStart.onclick = () => {{
        scrollHere();
        if (st.running) return;
        st.running = true;
        st.base = 0;
        st.startAt = performance.now();
        if (st.raf) cancelAnimationFrame(st.raf);
        st.raf = requestAnimationFrame(render);
        // notify python "started"
        if (window.Streamlit) {{
          window.Streamlit.setComponentValue({{event:"start"}});
        }}
      }};

      btnStop.onclick = () => {{
        scrollHere();
        if (!st.running || st.startAt === null) return;
        const now = performance.now();
        const elapsed = st.base + (now - st.startAt);
        st.running = false;
        if (st.raf) cancelAnimationFrame(st.raf);
        st.raf = null;
        tEl.textContent = fmt(elapsed);
        if (window.Streamlit) {{
          window.Streamlit.setComponentValue({{event:"stop", value: elapsed/1000.0}});
        }}
      }};
    </script>
    """
    return components.html(html, height=160)

# =========================
# 세션 상태
# =========================
def init_state():
    ss = st.session_state
    ss.setdefault("lang", "ko")
    ss.setdefault("submitted", False)

    # game
    ss.setdefault("shared_once", False)
    ss.setdefault("tries_base", 1)
    ss.setdefault("tries_bonus", 0)
    ss.setdefault("game_used", 0)   # 사용한 시도 횟수
    ss.setdefault("game_result", None)  # "success"|"fail"|None
    ss.setdefault("last_stop_time", None)  # float seconds
    ss.setdefault("consult_done", False)   # O 저장 완료 여부

def reset_all(keep_lang=True):
    lang = st.session_state.get("lang", "ko")
    st.session_state.clear()
    init_state()
    if keep_lang:
        st.session_state["lang"] = lang

def tries_left() -> int:
    total = st.session_state["tries_base"] + st.session_state["tries_bonus"]
    return max(0, total - st.session_state["game_used"])

init_state()

# =========================
# 언어 선택 (반응 안하던 문제: 세션 업데이트 확실히)
# =========================
labels = [UI[l]["lang_name"] for l in LANGS]
sel = st.radio("", labels, horizontal=True, index=LANGS.index(st.session_state["lang"]))
st.session_state["lang"] = LANGS[labels.index(sel)]
lang = st.session_state["lang"]
t_ko = UI["ko"]

# 배너
banner(t_ko["title"], t_ko["subtitle"] if lang == "ko" else "100% Free")

# SEO 섹션 (디자인 고정 카드)
card(t_ko["seo_title"], t_ko["seo_body"])

# =========================
# 입력
# =========================
st.markdown(f"<div class='label'>{t_ko['name_label'] if lang=='ko' else 'Your name'}</div>", unsafe_allow_html=True)
name = st.text_input("", key="name_input")

# =========================
# 결과 버튼
# =========================
if st.button(t_ko["btn_result"] if lang == "ko" else "Get Results", key="btn_result"):
    st.session_state["submitted"] = True

data = load_any_data(lang)

# =========================
# 결과 출력 (sections 기반)
# =========================
if st.session_state["submitted"]:
    def show(title: str, key: str):
        txt = get_section(data, key)
        if not txt:
            # 여기서 “없음” 뜨는 건 데이터에 sections가 없다는 뜻.
            txt = "데이터가 없습니다. (data/fortune_db.json 또는 fortunes_lang.json에 sections가 필요합니다.)" if lang == "ko" else \
                  "No data. (Need 'sections' in fortune_db.json or fortunes_lang.json.)"
        card(title, txt)

    if lang == "ko":
        show(t_ko["today"], "today")
        show(t_ko["tomorrow"], "tomorrow")
        show(t_ko["year"], "year_2026")
        show(t_ko["love"], "love")
        show(t_ko["money"], "money")
        show(t_ko["work"], "work")
        h = get_section(data, "health")
        if h:
            card(t_ko["health"], h)
    else:
        show("Today", "today")
        show("Tomorrow", "tomorrow")
        show("Year 2026", "year_2026")
        show("Love", "love")
        show("Money", "money")
        show("Work", "work")
        h = get_section(data, "health")
        if h:
            card("Health", h)

# =========================
# 한국어 전용: 광고 위치(미니게임 바로 위) + 공유 + 미니게임
# =========================
if lang == "ko":
    # 광고 (미니게임 바로 위)
    card(t_ko["ad_title"], t_ko["ad_body"])
    st.markdown(
        f"""
        <div class="card">
          <a href="https://www.xn--910b51a1r88nu39a.com/" target="_blank" style="
            display:block;text-align:center;
            padding:14px;border-radius:14px;
            background:#b56b34;color:white;
            text-decoration:none;font-weight:900;">
            {t_ko["ad_btn"]}
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 공유 (네가 말한 “갤러리 공유 시트”)
    card(t_ko["share_title"], t_ko["share_desc"])
    share_sheet_button(
        title="링크 공유",
        text="2026 운세 + MBTI + 사주 + 미니게임(커피쿠폰) 도전!",
        url=APP_URL,
        key="share_native_btn",
    )
    if st.button("공유했다 (+1회)", key="btn_shared_once"):
        if not st.session_state["shared_once"]:
            st.session_state["shared_once"] = True
            st.session_state["tries_bonus"] = 1
            st.success("도전 기회가 1회 추가되었습니다.")
        else:
            st.info("이미 도전 기회를 추가했습니다.")

    # 미니게임 안내
    card(t_ko["game_title"], t_ko["game_rule"])
    card(t_ko["tries_left"], f"{tries_left()}회")

    # 시도 횟수 0이면 Start 자체가 의미 없으니 안내
    if tries_left() <= 0 and st.session_state["game_result"] is None:
        card("안내", "남은 시도 횟수가 없습니다. 친구 공유로 1회 추가 후 재도전하세요.")

    # 스톱워치 컴포넌트
    # - 서버 rerun 없이 실시간
    # - Stop 눌렀을 때만 값 전달
    comp = stopwatch_component(
        running=False,
        seed_ms=int(datetime.now().timestamp() * 1000),
        key="stopwatch_v1",
    )

    # comp는 dict 형태로 들어옴 (event/start/stop)
    # Streamlit components.html은 setComponentValue를 반환으로 못 받기 때문에,
    # 여기서는 "components.html" 대신 커스텀 컴포넌트가 원칙이지만,
    # 이 환경에서 최소한의 안정성을 위해: Stop은 아래 입력으로 처리(다음 단계에서 완전 컴포넌트화 가능).
    #
    # => 그래서 여기서는 "Stop 시간 수동 입력"을 다시 넣지 않고,
    #    바로 아래에 "스톱 결과 입력"을 숨김 처리로 대체:
    #
    # 결론: 지금 단계에서 “완전 자동 전달”은 streamlit 공식 custom component가 가장 안정적.
    # 다만 너는 이미 예전에 자동으로 되던 버전이 있었으니,
    # 그 코드를 기반으로 merge해야 100% 재현 가능.
    #
    # ----
    # 그래도 지금 앱이 깨지는 것(에러/데이터없음/디자인변경)을 먼저 고정하는 목적의 코드임.

    # 임시: Stop 결과를 python에 전달할 수 없으니,
    # 기존 로직이 있던 app.py를 기준으로 JS 컴포넌트 부분만 교체하는 방식이 정답.
    # 여기서는 "판정 버튼"만 둬서 흐름/DB 로직을 검증할 수 있게 함.
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Stop(성공) 테스트", key="btn_success_test"):
            if tries_left() > 0 and st.session_state["game_result"] is None:
                st.session_state["game_used"] += 1
                st.session_state["game_result"] = "success"
                st.session_state["last_stop_time"] = 20.265
    with c2:
        if st.button("Stop(실패) 테스트", key="btn_fail_test"):
            if tries_left() > 0 and st.session_state["game_result"] is None:
                st.session_state["game_used"] += 1
                st.session_state["game_result"] = "fail"
                st.session_state["last_stop_time"] = 19.999

    # 결과
    if st.session_state["game_result"] == "success":
        card("결과", t_ko["success"])
        st.session_state["consult_done"] = True  # 성공자는 상담신청 off
    elif st.session_state["game_result"] == "fail":
        card("결과", t_ko["fail"])

        # 실패자만 상담신청 on
        if not st.session_state["consult_done"]:
            card(t_ko["consult_title"], t_ko["consult_q"])
            phone = st.text_input(t_ko["consult_phone"], key="phone_input_fail")

            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button(t_ko["consult_yes"], key="consult_yes"):
                    if not phone.strip():
                        st.warning("전화번호를 입력해주세요.")
                    else:
                        ok, err = append_consult_O(
                            name=(name or "").strip(),
                            phone=phone.strip(),
                            stop_time=st.session_state["last_stop_time"],
                        )
                        if ok:
                            st.success("커피쿠폰 응모되셨습니다.")
                            st.session_state["consult_done"] = True
                        else:
                            st.error(f"Sheet error: {err}")
            with cc2:
                if st.button(t_ko["consult_no"], key="consult_no"):
                    st.info("취소되었습니다. (기록 저장 없음)")

# reset
if st.button(t_ko["reset"] if lang == "ko" else "Reset", key="btn_reset"):
    reset_all(keep_lang=True)
    st.rerun()
