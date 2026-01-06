import os
import json
import re
import random
from datetime import datetime, date, timedelta

import streamlit as st

# ---- Google Sheet ----
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None

# =========================================================
# 0) App Config (고정)
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"

SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_NAME = "시트1"

# 이벤트 성공 구간 (고정)
WIN_MIN = 20.260
WIN_MAX = 20.269

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일",
    page_icon="🔮",
    layout="centered"
)

# =========================================================
# 1) Helpers
# =========================================================
def safe_toast(msg: str):
    if not msg:
        return
    try:
        if hasattr(st, "toast"):
            st.toast(msg)
        else:
            st.success(msg)
    except Exception:
        st.success(msg)

def normalize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone or "")

def load_required_json(path: str, label: str):
    if not os.path.exists(path):
        st.error(f"❌ {label} 파일이 없습니다.\n\n필요 파일 경로:\n`{path}`")
        st.stop()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ {label} JSON 로딩 실패: {e}\n\n파일이 JSON 형식인지 확인하세요.")
        st.stop()

def seed_int(*parts) -> int:
    # 같은 입력이면 항상 같은 결과(신뢰성 고정)
    s = "|".join(map(str, parts))
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return int(h)

# =========================================================
# 2) Query params
# =========================================================
def get_query_params():
    try:
        return dict(st.query_params)
    except Exception:
        try:
            return st.experimental_get_query_params()
        except Exception:
            return {}

def set_query_params(params: dict):
    try:
        st.query_params.clear()
        for k, v in params.items():
            st.query_params[k] = v
    except Exception:
        st.experimental_set_query_params(**params)

def clear_param(param_key: str):
    try:
        params = get_query_params()
        if param_key in params:
            params.pop(param_key, None)
            set_query_params(params)
    except Exception:
        pass

# =========================================================
# 3) SEO Inject (프론트에 안보이게, height=0)
# =========================================================
def inject_seo():
    description = "2026 운세: 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 미니게임 이벤트 + 타로"
    keywords = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, 무료 운세, 타로, 연애운, 재물운, 건강운"
    title = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일"

    try:
        st.components.v1.html(
            f"""
<script>
(function() {{
  try {{
    const metas = [
      ['name','description', {json.dumps(description, ensure_ascii=False)}],
      ['name','keywords', {json.dumps(keywords, ensure_ascii=False)}],
      ['property','og:title', {json.dumps(title, ensure_ascii=False)}],
      ['property','og:description', {json.dumps(description, ensure_ascii=False)}],
      ['property','og:type','website'],
      ['property','og:url', {json.dumps(APP_URL, ensure_ascii=False)}],
      ['name','twitter:card','summary'],
      ['name','robots','index,follow']
    ];
    metas.forEach(([attr, key, val]) => {{
      let el = document.head.querySelector(`meta[${{attr}}="${{key}}"]`);
      if(!el) {{
        el = document.createElement('meta');
        el.setAttribute(attr, key);
        document.head.appendChild(el);
      }}
      el.setAttribute('content', val);
    }});

    let canonical = document.head.querySelector('link[rel="canonical"]');
    if(!canonical) {{
      canonical = document.createElement('link');
      canonical.setAttribute('rel','canonical');
      document.head.appendChild(canonical);
    }}
    canonical.setAttribute('href', {json.dumps(APP_URL, ensure_ascii=False)});
  }} catch(e) {{}}
}})();
</script>
""",
            height=0
        )
    except Exception:
        pass

inject_seo()

# =========================================================
# 4) 고정 텍스트(한국어만)
# =========================================================
T = {
    "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
    "subtitle": "완전 무료",
    "name": "이름 입력 (결과에 표시돼요)",
    "birth": "생년월일 선택",
    "mbti_mode": "MBTI를 어떻게 할까요?",
    "mbti_direct": "직접 선택",
    "mbti_12": "간단 테스트 (12문항)",
    "mbti_16": "상세 테스트 (16문항)",
    "mbti_submit": "제출하고 MBTI 확정",
    "go_result": "2026년 운세 보기!",
    "reset": "처음부터 다시하기",
    "share_link_btn": "친구에게 공유하기",
    "share_link_hint": "버튼을 누르면 휴대폰 공유 창이 열립니다. (안되면 URL 복사)",
    "share_bonus_done": "공유 확인! 미니게임 1회 추가 지급 🎁",

    "sections": {
        "zodiac": "띠 운세(설날 기준)",
        "mbti": "MBTI 특징",
        "saju": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year_all": "2026 전체 운세",
        "advice": "조언",
    },

    # 광고 고정 문구 (사용자가 준 문구 그대로)
    "ad_title": "[광고] 다나눔렌탈",
    "ad_body": "정수기 렌탈 제휴카드 적용시 월 렌탈비 0원, 설치당일 최대 현금50만원 + 사은품 증정",
    "ad_btn": "무료 상담하기",

    # 미니게임(고정 규칙)
    "mini_title": "🎁 미니게임: 선착순 20명 커피쿠폰",
    "mini_notice": "커피쿠폰 선착순 지급 소진시 조기 종료될 수 있습니다.",
    "mini_desc": f"스톱워치를 **{WIN_MIN:.3f} ~ {WIN_MAX:.3f}초** 사이로 맞추면 성공!\n\n- 기본 1회\n- **친구에게 공유하기** 완료 시 1회 추가\n",
    "mini_try_left": "남은 시도",
    "mini_closed": "이벤트가 종료되었습니다. (선착순 20명 마감)",
    "mini_dup": "이미 참여한 번호입니다. (중복 참여 불가)",
    "stopwatch_note": "START 후 STOP을 누르면 시간이 멈추고 기록이 자동 반영됩니다.",
}

# =========================================================
# 5) DB 로드 (고정 파일명만)
#    ✅ fortunes_ko_2026_year.json 삭제/미사용
#    ✅ fortunes_ko_2026.json 하나에서 year_all + advice 같이 사용
# =========================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

PATH_FORTUNE_2026 = os.path.join(DATA_DIR, "fortunes_ko_2026.json")  # ← year_all 포함
PATH_TODAY = os.path.join(DATA_DIR, "fortunes_ko_today.json")
PATH_TOMORROW = os.path.join(DATA_DIR, "fortunes_ko_tomorrow.json")

PATH_ZODIAC = os.path.join(DATA_DIR, "zodiac_fortunes_ko_2026.json")
PATH_MBTI = os.path.join(DATA_DIR, "mbti_traits_ko.json")
PATH_SAJU = os.path.join(DATA_DIR, "saju_ko.json")
PATH_LNY = os.path.join(DATA_DIR, "lunar_new_year_1920_2026.json")

fortune_2026_db = load_required_json(PATH_FORTUNE_2026, "fortunes_ko_2026.json")
today_db = load_required_json(PATH_TODAY, "fortunes_ko_today.json")
tomorrow_db = load_required_json(PATH_TOMORROW, "fortunes_ko_tomorrow.json")

zodiac_db = load_required_json(PATH_ZODIAC, "zodiac_fortunes_ko_2026.json")
mbti_db = load_required_json(PATH_MBTI, "mbti_traits_ko.json")
saju_db = load_required_json(PATH_SAJU, "saju_ko.json")
lny_db = load_required_json(PATH_LNY, "lunar_new_year_1920_2026.json")

# =========================================================
# 6) Lunar New Year(설날 기준 띠 계산)
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
    "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠"
}

def parse_ymd(s: str) -> date:
    y, m, d = map(int, s.split("-"))
    return date(y, m, d)

def zodiac_key_by_solar_birth(birth: date) -> str:
    y = birth.year
    lny_str = lny_db.get(str(y))
    if not lny_str:
        st.error("설날 테이블 범위를 벗어났습니다. (1920~2026)")
        st.stop()
    lny = parse_ymd(lny_str)
    zodiac_year = y if birth >= lny else (y - 1)
    idx = (zodiac_year - 4) % 12
    return ZODIAC_ORDER[idx]

# =========================================================
# 7) MBTI 12/16 질문(고정)
# =========================================================
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"
]

MBTI_Q_12 = [
    ("EI","사람들과 있을 때 에너지가 더 생긴다","혼자 있을 때 에너지가 더 생긴다"),
    ("SN","현실적인 정보가 편하다","가능성/아이디어가 편하다"),
    ("TF","결정은 논리/원칙이 우선","결정은 사람/상황 배려가 우선"),
    ("JP","계획대로 진행해야 마음이 편하다","유연하게 바뀌어도 괜찮다"),

    ("EI","말하며 생각이 정리된다","생각한 뒤 말하는 편이다"),
    ("SN","경험/사실을 믿는 편","직감/영감을 믿는 편"),
    ("TF","피드백은 직설이 낫다","피드백은 부드럽게가 낫다"),
    ("JP","마감 전에 미리 끝내는 편","마감 직전에 몰아서 하는 편"),

    ("EI","주말엔 약속이 있으면 좋다","주말엔 혼자 쉬고 싶다"),
    ("SN","설명은 구체적으로","설명은 큰그림으로"),
    ("TF","갈등은 원인/해결이 우선","갈등은 감정/관계가 우선"),
    ("JP","정리/정돈이 잘 되어야 편하다","어수선해도 일단 진행 가능"),
]

MBTI_Q_16_EXTRA = [
    ("EI","새로운 사람을 만나면 설렌다","새로운 사람은 적응 시간이 필요"),
    ("SN","지금 필요한 현실이 중요","미래 가능성이 더 중요"),
    ("TF","공정함이 최우선","조화로움이 최우선"),
    ("JP","일정이 확정되어야 안심","상황에 따라 바뀌는 게 자연스러움"),
]

def compute_mbti_from_answers(answers):
    scores = {"EI":0, "SN":0, "TF":0, "JP":0}
    counts = {"EI":0, "SN":0, "TF":0, "JP":0}
    for axis, pick_left in answers:
        counts[axis] += 1
        if pick_left:
            scores[axis] += 1

    def decide(axis, left_char, right_char):
        return left_char if scores[axis] >= (counts[axis] / 2) else right_char

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_LIST else "ENFP"

# =========================================================
# 8) Google Sheet (컬럼 구조 고정)
# =========================================================
def get_sheet():
    try:
        if gspread is None or Credentials is None:
            return None
        if "gcp_service_account" not in st.secrets:
            return None
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        info = dict(st.secrets["gcp_service_account"])
        if "private_key" in info and isinstance(info["private_key"], str):
            info["private_key"] = info["private_key"].replace("\\n", "\n")

        creds = Credentials.from_service_account_info(info, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(SHEET_NAME)
        return ws
    except Exception:
        return None

def read_all_rows(ws):
    try:
        return ws.get_all_values()
    except Exception:
        return []

def count_winners(ws) -> int:
    values = read_all_rows(ws)
    winners = 0
    for row in values[1:] if len(values) > 1 else []:
        if len(row) < 4:
            continue
        try:
            sec = float(row[3])
        except Exception:
            continue
        if WIN_MIN <= sec <= WIN_MAX:
            winners += 1
    return winners

def phone_exists(ws, phone_norm: str) -> bool:
    values = read_all_rows(ws)
    for row in values[1:] if len(values) > 1 else []:
        if len(row) < 3:
            continue
        if normalize_phone(row[2]) == phone_norm and phone_norm != "":
            return True
    return False

def append_row(ws, name, phone, seconds, shared_bool, entry_type, consult_ox):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([
        now_str,                   # A
        name,                      # B
        phone,                     # C
        f"{seconds:.3f}",          # D
        "TRUE" if shared_bool else "FALSE",  # E
        entry_type,                # F
        consult_ox                 # G
    ])

# =========================================================
# 9) Share (시스템 공유창 + 실패 시 URL복사 버튼)
# =========================================================
def get_query_params_value(qp, key, default=None):
    v = qp.get(key, default)
    if isinstance(v, list):
        return v[0] if v else default
    return v

def share_native_with_copy(label: str):
    st.components.v1.html(
        f"""
<div style="margin: 8px 0;">
  <button id="btnShare" style="
    width:100%;
    border:none;border-radius:999px;
    padding:12px 14px;
    font-weight:900;
    background:#6b4fd6;color:white;
    cursor:pointer;
  ">{label}</button>
</div>

<script>
(function() {{
  const btn = document.getElementById("btnShare");
  const url = {json.dumps(APP_URL, ensure_ascii=False)};
  btn.addEventListener("click", async () => {{
    if (!navigator.share) {{
      return;
    }}
    try {{
      await navigator.share({{ title: "2026 운세", text: url, url }});
      const u = new URL(window.location.href);
      u.searchParams.set("shared", "1");
      window.location.href = u.toString();
    }} catch (e) {{}}
  }});
}})();
</script>
""",
        height=70
    )

def copy_url_button():
    st.components.v1.html(
        f"""
<div style="margin: 6px 0;">
  <button id="btnCopy" style="
    width:100%;
    border:none;border-radius:999px;
    padding:12px 14px;
    font-weight:900;
    background:#ffffff;color:#6b4fd6;
    cursor:pointer;
    box-shadow:0 6px 18px rgba(107,79,214,0.18);
  ">URL 복사하기</button>
</div>
<script>
(function(){{
  const btn = document.getElementById("btnCopy");
  const url = {json.dumps(APP_URL, ensure_ascii=False)};
  btn.addEventListener("click", async ()=>{{
    try {{
      await navigator.clipboard.writeText(url);
      alert("URL이 복사되었습니다!");
    }} catch(e) {{
      prompt("아래 URL을 길게 눌러 복사하세요:", url);
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 10) Stopwatch (00.000 표시 / STOP 시 정지 화면 유지 / START·STOP 1회 누르면 비활성)
# =========================================================
def stopwatch_component(tries_left: int):
    disabled_all = "true" if tries_left <= 0 else "false"

    st.components.v1.html(
        f"""
<div style="
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 16px;
  border: 1px solid rgba(140,120,200,0.18);
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
  text-align:center;
">
  <div style="font-weight:900;font-size:1.15rem;color:#2b2350;margin-bottom:10px;">
    ⏱️ STOPWATCH
  </div>

  <div id="display" style="
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
    font-weight:900;
    font-size: 56px;
    letter-spacing: 2px;
    padding: 14px 10px;
    border-radius: 14px;
    background: rgba(245,245,255,0.85);
    border: 1px solid rgba(130,95,220,0.20);
    color: #1f1747;
  ">00.000</div>

  <div style="display:flex; gap:10px; justify-content:center; margin-top:12px;">
    <button id="startBtn" style="
      flex:1; max-width: 240px;
      border:none; border-radius: 999px;
      padding: 12px 14px;
      font-weight:900;
      background:#6b4fd6; color:white;
      cursor:pointer;
      opacity: { "0.45" if tries_left <= 0 else "1" };
    ">START</button>

    <button id="stopBtn" style="
      flex:1; max-width: 240px;
      border:none; border-radius: 999px;
      padding: 12px 14px;
      font-weight:900;
      background:#ff8c50; color:white;
      cursor:pointer;
      opacity: { "0.45" if tries_left <= 0 else "1" };
    ">STOP</button>
  </div>

  <div style="margin-top:10px; font-size:0.92rem; opacity:0.85;">
    {T["stopwatch_note"]}
  </div>
</div>

<script>
(function() {{
  const disabledAll = {disabled_all};
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const display = document.getElementById("display");

  if (disabledAll) {{
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
    return;
  }}

  let running = false;
  let startTime = 0;
  let rafId = null;
  let startedOnce = false;
  let stoppedOnce = false;

  function fmt(ms) {{
    const sec = Math.max(0, ms) / 1000.0;
    return sec.toFixed(3);
  }}

  function tick() {{
    if (!running) return;
    const now = performance.now();
    display.textContent = fmt(now - startTime);
    rafId = requestAnimationFrame(tick);
  }}

  startBtn.addEventListener("click", () => {{
    if (startedOnce) return;
    if (stoppedOnce) return;
    startedOnce = true;

    running = true;
    startTime = performance.now();
    display.textContent = "00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);

    startBtn.disabled = true;
    startBtn.style.opacity = "0.55";
    startBtn.style.cursor = "not-allowed";
  }});

  stopBtn.addEventListener("click", () => {{
    if (stoppedOnce) return;
    if (!running) return;
    stoppedOnce = true;

    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    display.textContent = v;

    stopBtn.disabled = true;
    stopBtn.style.opacity = "0.55";
    stopBtn.style.cursor = "not-allowed";

    try {{
      const u = new URL(window.location.href);
      u.searchParams.set("t", v);
      window.location.href = u.toString();
    }} catch (e) {{
      window.location.href = {json.dumps(APP_URL, ensure_ascii=False)} + "?t=" + v;
    }}
  }});
}})();
</script>
""",
        height=300
    )

# =========================================================
# 11) Style (디자인 큰틀 고정)
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2.5rem; max-width: 720px; }
.header-hero {
  border-radius: 20px;
  padding: 18px 16px;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
  color: white;
  text-align: center;
  box-shadow: 0 12px 30px rgba(0,0,0,0.18);
  margin-bottom: 14px;
}
.hero-title { font-size: 1.5rem; font-weight: 900; margin: 0; }
.hero-sub { font-size: 0.95rem; opacity: 0.95; margin-top: 6px; }

.card {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
}
.result-card {
  background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(245,245,255,0.92));
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
}
.adbox {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 16px;
  margin: 12px 0;
  border: 2px solid rgba(255, 140, 80, 0.55);
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
  text-align:center;
}
.minibox {
  background: rgba(245,245,255,0.82);
  border-radius: 18px;
  padding: 16px;
  margin: 12px 0;
  border: 1px solid rgba(130,95,220,0.18);
  box-shadow: 0 10px 28px rgba(0,0,0,0.06);
}
.bigbtn > button {
  border-radius: 999px !important;
  font-weight: 900 !important;
  padding: 0.75rem 1.2rem !important;
}
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
.small-note { font-size: 0.92rem; opacity: 0.88; text-align:center; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 12) Session State
# =========================================================
if "stage" not in st.session_state: st.session_state.stage = "input"

if "name" not in st.session_state: st.session_state.name = ""
if "birth" not in st.session_state: st.session_state.birth = date(2000, 1, 1)

if "mbti" not in st.session_state: st.session_state.mbti = "ENFP"
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"

if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0

if "last_stop_time" not in st.session_state: st.session_state.last_stop_time = None
if "last_result_msg" not in st.session_state: st.session_state.last_result_msg = ""
if "win_pending" not in st.session_state: st.session_state.win_pending = False
if "fail_pending" not in st.session_state: st.session_state.fail_pending = False
if "consult_enabled" not in st.session_state: st.session_state.consult_enabled = False

qp = get_query_params()
shared_val = get_query_params_value(qp, "shared", "0")
if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        st.session_state.max_attempts = 2
        safe_toast(T["share_bonus_done"])
    clear_param("shared")

t_val = get_query_params_value(qp, "t", None)
if t_val is not None:
    try:
        st.session_state.last_stop_time = float(str(t_val).strip())
    except Exception:
        st.session_state.last_stop_time = None
    clear_param("t")

# =========================================================
# 13) 운세 선택(씨드 고정)
# =========================================================
def pick_from_pool(db: dict, pool_path: list, s: int) -> str:
    cur = db
    for k in pool_path:
        if not isinstance(cur, dict) or k not in cur:
            st.error(f"DB 구조 오류: {'.'.join(pool_path)} 경로가 없습니다.")
            st.stop()
        cur = cur[k]
    if not isinstance(cur, list) or len(cur) == 0:
        st.error(f"DB 리스트가 비었습니다: {'.'.join(pool_path)}")
        st.stop()
    rng = random.Random(s)
    return rng.choice(cur)

def make_result(birth: date, mbti: str):
    zkey = zodiac_key_by_solar_birth(birth)
    zlabel = ZODIAC_LABEL.get(zkey, zkey)

    base = seed_int(birth.isoformat(), mbti, "2026")

    zodiac_text = pick_from_pool(zodiac_db, ["zodiac", zkey, "texts"], base + 11)
    mbti_trait = pick_from_pool(mbti_db, ["mbti", mbti, "traits"], base + 22)
    saju_line = pick_from_pool(saju_db, ["saju", "lines"], base + 33)

    today_key = date.today().isoformat()
    tomorrow_key = (date.today() + timedelta(days=1)).isoformat()

    today_msg = pick_from_pool(today_db, ["pools", "today"], seed_int(birth.isoformat(), mbti, today_key, "today"))
    tomorrow_msg = pick_from_pool(tomorrow_db, ["pools", "tomorrow"], seed_int(birth.isoformat(), mbti, tomorrow_key, "tomorrow"))

    # ✅ year_all도 fortunes_ko_2026.json에서 읽음 (요구 반영)
    year_all = pick_from_pool(fortune_2026_db, ["pools", "year_all"], base + 44)
    advice = pick_from_pool(fortune_2026_db, ["pools", "advice"], base + 55)

    return {
        "zodiac_label": zlabel,
        "zodiac_text": zodiac_text,
        "mbti_trait": mbti_trait,
        "saju_line": saju_line,
        "today_msg": today_msg,
        "tomorrow_msg": tomorrow_msg,
        "year_all": year_all,
        "advice": advice
    }

# =========================================================
# 14) MBTI 테스트 렌더
# =========================================================
def render_mbti_test(questions, title: str, key_prefix: str):
    st.markdown(f"<div class='card'><b>{title}</b><br><span style='opacity:0.85;'>각 문항에서 더 가까운 쪽을 선택하세요.</span></div>", unsafe_allow_html=True)
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}.", options=[left_txt, right_txt], index=0, key=f"{key_prefix}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button(T["mbti_submit"], use_container_width=True):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 15) Reset (입력만 초기화, 게임 시도횟수는 유지)
# =========================================================
def reset_input_only_keep_game():
    keep = {
        "shared","max_attempts","attempts_used",
        "last_stop_time","last_result_msg",
        "win_pending","fail_pending",
        "consult_enabled",
    }
    current = dict(st.session_state)
    st.session_state.clear()
    for k, v in current.items():
        if k in keep:
            st.session_state[k] = v

    st.session_state.stage = "input"
    st.session_state.name = ""
    st.session_state.birth = date(2000, 1, 1)
    st.session_state.mbti = "ENFP"
    st.session_state.mbti_mode = "direct"

# =========================================================
# 16) Screens
# =========================================================
def render_input():
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">🔮 {T["title"]}</p>
      <p class="hero-sub">{T["subtitle"]}</p>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input(T["name"], value=st.session_state.name)

    st.markdown(f"<div class='card'><b>{T['birth']}</b></div>", unsafe_allow_html=True)
    st.session_state.birth = st.date_input(
        "",
        value=st.session_state.birth,
        min_value=date(1920, 1, 1),
        max_value=date(2026, 12, 31),
    )

    st.markdown(f"<div class='card'><b>{T['mbti_mode']}</b></div>", unsafe_allow_html=True)
    mode = st.radio(
        "",
        [T["mbti_direct"], T["mbti_12"], T["mbti_16"]],
        index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
        horizontal=True
    )

    if mode == T["mbti_direct"]:
        st.session_state.mbti_mode = "direct"
    elif mode == T["mbti_12"]:
        st.session_state.mbti_mode = "12"
    else:
        st.session_state.mbti_mode = "16"

    if st.session_state.mbti_mode == "direct":
        idx = MBTI_LIST.index(st.session_state.mbti) if st.session_state.mbti in MBTI_LIST else MBTI_LIST.index("ENFP")
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=idx)
    elif st.session_state.mbti_mode == "12":
        done = render_mbti_test(MBTI_Q_12, "MBTI 12문항 (각 축 3문항)", "q12")
        if done:
            st.success(f"MBTI 확정: {st.session_state.mbti}")
    else:
        q = MBTI_Q_12 + MBTI_Q_16_EXTRA
        done = render_mbti_test(q, "MBTI 16문항 (12문항 + 추가 4문항)", "q16")
        if done:
            st.success(f"MBTI 확정: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button(T["go_result"], use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_result():
    birth = st.session_state.birth
    mbti = st.session_state.mbti or "ENFP"
    res = make_result(birth, mbti)

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{res["zodiac_label"]} · {mbti}</p>
    </div>
    """, unsafe_allow_html=True)

    s = T["sections"]
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['zodiac']}**: {res['zodiac_text']}")
    st.markdown(f"**{s['mbti']}**: {res['mbti_trait']}")
    st.markdown(f"**{s['saju']}**: {res['saju_line']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['today']}**: {res['today_msg']}")
    st.markdown(f"**{s['tomorrow']}**: {res['tomorrow_msg']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['year_all']}**: {res['year_all']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['advice']}**: {res['advice']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # 결과 바로 아래: 공유
    share_native_with_copy(T["share_link_btn"])
    copy_url_button()
    st.caption(T["share_link_hint"])

    # 광고(고정)
    st.markdown(f"""
    <div class="adbox">
      <div style="font-weight:900;color:#e74c3c;">{T["ad_title"]}</div>
      <div style="margin-top:8px; font-weight:800;">{T["ad_body"]}</div>
    </div>
    """, unsafe_allow_html=True)

    ws = get_sheet()
    if ws is None:
        st.warning("구글시트 연동이 아직 안되어있습니다. (Secrets/시트 공유/탭 이름 확인)")
    else:
        with st.expander("무료 상담하기 (이름/전화번호 입력)"):
            ad_name = st.text_input("이름", value=name, key="ad_name")
            ad_phone = st.text_input("전화번호", value="", key="ad_phone")
            ad_cons = st.checkbox("개인정보처리방침 동의(필수)", value=False, key="ad_cons")

            if st.button(T["ad_btn"], use_container_width=True):
                pn = normalize_phone(ad_phone)
                if not ad_cons:
                    st.warning("동의가 필요합니다.")
                elif ad_name.strip() == "" or pn == "":
                    st.warning("이름/전화번호를 입력해주세요.")
                else:
                    try:
                        append_row(ws, ad_name.strip(), pn, 0.0, st.session_state.shared, "광고상담", "")
                        st.success("신청 완료! 곧 연락드리겠습니다.")
                    except Exception as e:
                        st.error(f"저장 오류: {e}")

    # 미니게임
    st.markdown(f"""
    <div class="minibox">
      <div style="font-weight:900;font-size:1.15rem;">{T["mini_title"]}</div>
      <div style="margin-top:6px; opacity:0.85;">{T["mini_notice"]}</div>
      <div style="margin-top:10px; line-height:1.7;">
        {T["mini_desc"].replace("\n","<br/>")}
      </div>
    </div>
    """, unsafe_allow_html=True)

    sheet_ready = (ws is not None)
    closed = False
    if sheet_ready:
        try:
            closed = (count_winners(ws) >= 20)
        except Exception:
            closed = False

    tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    st.markdown(
        f"<div class='small-note'>{T['mini_try_left']}: <b>{tries_left}</b> / {st.session_state.max_attempts}</div>",
        unsafe_allow_html=True
    )

    if closed:
        st.info(T["mini_closed"])
    else:
        stopwatch_component(tries_left)

        if st.session_state.last_stop_time is not None:
            sec = float(st.session_state.last_stop_time)
            marker = f"@{sec:.3f}"

            if tries_left <= 0:
                st.warning("남은 시도가 없습니다.")
            else:
                if not st.session_state.last_result_msg.endswith(marker):
                    st.session_state.attempts_used += 1

                    if WIN_MIN <= sec <= WIN_MAX:
                        st.session_state.win_pending = True
                        st.session_state.fail_pending = False
                        st.session_state.consult_enabled = False
                        st.session_state.last_result_msg = f"성공! {sec:.3f}초 기록. 쿠폰지급을 위해 이름, 전화번호 입력해주세요{marker}"
                    else:
                        st.session_state.win_pending = False
                        st.session_state.fail_pending = True
                        st.session_state.consult_enabled = True
                        st.session_state.last_result_msg = f"실패! {sec:.3f}초 기록 친구공유시 도전기회 1회추가 또는 정수기렌탈 상담신청 후 커피쿠폰 응모{marker}"

            if st.session_state.last_result_msg:
                st.markdown(f"<div class='card'><b>결과</b><br/>{st.session_state.last_result_msg.split('@')[0]}</div>", unsafe_allow_html=True)

        if st.session_state.win_pending:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### ✅ 성공! 정보 입력")
            win_name = st.text_input("이름", value=(st.session_state.name or "").strip(), key="win_name")
            win_phone = st.text_input("전화번호", value="", key="win_phone")
            win_cons = st.checkbox("개인정보 수집·이용 동의(필수)", value=False, key="win_cons")
            st.caption("이벤트 경품 발송을 위해 이름/전화번호를 수집하며 목적 달성 후 지체 없이 파기합니다.")

            if st.button("제출", use_container_width=True):
                if not sheet_ready:
                    st.error("구글시트 연동이 필요합니다.")
                elif not win_cons:
                    st.warning("동의가 필요합니다.")
                else:
                    pn = normalize_phone(win_phone)
                    if win_name.strip() == "" or pn == "":
                        st.warning("이름/전화번호를 정확히 입력해주세요.")
                    else:
                        try:
                            if phone_exists(ws, pn):
                                st.warning(T["mini_dup"])
                            elif count_winners(ws) >= 20:
                                st.info(T["mini_closed"])
                            else:
                                append_row(
                                    ws=ws,
                                    name=win_name.strip(),
                                    phone=pn,
                                    seconds=float(st.session_state.last_stop_time or 0.0),
                                    shared_bool=st.session_state.shared,
                                    entry_type="미니게임",
                                    consult_ox=""
                                )
                                st.success("성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.")
                                st.session_state.win_pending = False
                                st.session_state.last_stop_time = None
                        except Exception as e:
                            st.error(f"저장 오류: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.fail_pending and st.session_state.consult_enabled:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### ☕ 커피쿠폰 응모를 원하시나요?")
            st.markdown("- **친구에게 공유하기** 완료 시 1회 추가\n- 또는 정수기 렌탈 상담 신청 후 커피쿠폰 응모")
            choice = st.radio("상담신청 여부 (O/X)", ["O", "X"], horizontal=True, key="consult_ox")

            if st.button("선택 완료", use_container_width=True):
                if choice == "X":
                    st.info("X 선택: DB 저장 없이 종료합니다.")
                    st.session_state.fail_pending = False
                    st.session_state.last_stop_time = None
                else:
                    if not sheet_ready:
                        st.error("구글시트 연동이 필요합니다.")
                    else:
                        st.success("O 선택: 상담 정보 입력 후 커피쿠폰 응모가 진행됩니다.")
            st.markdown("</div>", unsafe_allow_html=True)

            if choice == "O":
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 상담 신청 정보 입력")
                c_name = st.text_input("이름", value=(st.session_state.name or "").strip(), key="c_name")
                c_phone = st.text_input("전화번호", value="", key="c_phone")
                c_cons = st.checkbox("개인정보처리방침 동의(필수)", value=False, key="c_cons")

                if st.button("상담 신청 + 커피쿠폰 응모", use_container_width=True):
                    if not c_cons:
                        st.warning("동의가 필요합니다.")
                    else:
                        pn = normalize_phone(c_phone)
                        if c_name.strip() == "" or pn == "":
                            st.warning("이름/전화번호를 입력해주세요.")
                        else:
                            try:
                                append_row(
                                    ws=ws,
                                    name=c_name.strip(),
                                    phone=pn,
                                    seconds=float(st.session_state.last_stop_time or 0.0),
                                    shared_bool=st.session_state.shared,
                                    entry_type="상담",
                                    consult_ox="O"
                                )
                                st.success("커피쿠폰 응모되셨습니다.")
                                st.session_state.fail_pending = False
                                st.session_state.last_stop_time = None
                                st.session_state.consult_enabled = False
                            except Exception as e:
                                st.error(f"저장 오류: {e}")
                st.markdown("</div>", unsafe_allow_html=True)

    if st.button(T["reset"], use_container_width=True):
        reset_input_only_keep_game()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 17) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
