import streamlit as st
from datetime import datetime, timedelta
import random
import re
import json
import os
import hashlib

# ---- Google Sheet ----
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None

# =========================================================
# 0) App Config
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"
SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_NAME = "시트1"

DB_PATH = os.path.join("fortune_db", "fortunes_ko.json")  # 파일명/폴더명 고정

st.set_page_config(
    page_title="2026 Fortune | 띠+MBTI+사주+오늘/내일",
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

def stable_int_seed(s: str) -> int:
    """
    파이썬 hash()는 실행마다 바뀔 수 있어서(보안 salt),
    hashlib 기반으로 '항상 같은' 정수 seed를 만든다.
    """
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def pick_from_pool(pool: list, seed_key: str) -> str:
    if not pool:
        return ""
    idx = stable_int_seed(seed_key) % len(pool)
    return pool[idx]

def today_seoul_date() -> datetime:
    # Streamlit Cloud에서 서버 TZ가 달라도 흔들릴 수 있어서
    # 단순히 "한국 시간" 기준을 고정하고 싶으면 아래처럼 offset을 고정해도 됨.
    # 여기서는 로컬 now()를 쓰되, 결과가 너무 흔들리면 timezone 적용 버전으로 바꿔줄게.
    return datetime.now()

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
# 3) SEO Inject (안전하게)
# =========================================================
def inject_seo():
    description = "2026년 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로까지 무료로! (한국어 이벤트 포함)"
    keywords = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, 무료 운세, 타로, 연애운, 재물운, 건강운"
    title = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 운세"

    webapp_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": title,
        "url": APP_URL,
        "applicationCategory": "LifestyleApplication",
        "operatingSystem": "Web",
        "description": description
    }

    try:
        st.components.v1.html(
            f"""
<script>
(function() {{
  try {{
    const description = {json.dumps(description, ensure_ascii=False)};
    const keywords = {json.dumps(keywords, ensure_ascii=False)};
    const title = {json.dumps(title, ensure_ascii=False)};
    const appUrl = {json.dumps(APP_URL, ensure_ascii=False)};

    const metas = [
      ['name','description', description],
      ['name','keywords', keywords],
      ['property','og:title', title],
      ['property','og:description', description],
      ['property','og:type','website'],
      ['property','og:url', appUrl],
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
    canonical.setAttribute('href', appUrl);

    const webappLd = {json.dumps(json.dumps(webapp_ld, ensure_ascii=False))};
    let s1 = document.head.querySelector('script[data-jsonld="fortune-webapp"]');
    if(!s1) {{
      s1 = document.createElement('script');
      s1.type = 'application/ld+json';
      s1.setAttribute('data-jsonld','fortune-webapp');
      document.head.appendChild(s1);
    }}
    s1.text = webappLd;

  }} catch(e) {{}}
}})();
</script>
""",
            height=0
        )
    except Exception:
        pass

# =========================================================
# 4) Text (Korean only)
# =========================================================
T = {
    "lang_pick": "언어",
    "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
    "subtitle": "완전 무료",
    "name": "이름 입력 (결과에 표시돼요)",
    "birth": "생년월일 입력",
    "year": "년", "month": "월", "day": "일",
    "mbti_mode": "MBTI를 어떻게 할까요?",
    "mbti_direct": "직접 선택",
    "mbti_12": "간단 테스트 (12문항)",
    "mbti_16": "상세 테스트 (16문항)",
    "mbti_submit": "제출하고 MBTI 확정",
    "go_result": "2026년 운세 보기!",
    "reset": "처음부터 다시하기",
    "share_link_btn": "🔗 친구에게 공유하기",
    "share_link_hint": "버튼을 누르면 ‘공유’ 창이 뜹니다.",
    "share_bonus_done": "공유 확인! 미니게임 1회 추가 지급 🎁",
    "tarot_btn": "오늘의 타로 카드 뽑기",
    "tarot_title": "오늘의 타로 카드",
    "sections": {
        "zodiac": "띠 운세",
        "mbti": "MBTI 특징",
        "saju": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year_all": "2026 전체 운세",
        "advice": "조합 조언",
        "action": "오늘의 액션팁",
    },
    "ad_placeholder": "AD (심사 통과 후 이 위치에 광고가 표시됩니다)",
    "ad_kr_title": "정수기렌탈 대박!",
    "ad_kr_body1": "제휴카드면 월 0원부터!",
    "ad_kr_body2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍",
    "ad_kr_link": "다나눔렌탈.com 바로가기",
    "ad_kr_url": "https://www.다나눔렌탈.com",
    "mini_title": "🎁 미니게임: 선착순 20명 커피쿠폰 도전!",
    "mini_desc": "스톱워치를 **20.16초**에 맞추면 당첨!\n\n- 기본 1회\n- **친구에게 공유하기**를 누르면 1회 추가\n- 목표 구간: **20.160 ~ 20.169초**",
    "mini_try_left": "남은 시도",
    "mini_closed": "이벤트가 종료되었습니다. (선착순 20명 마감)",
    "mini_dup": "이미 참여한 번호입니다. (중복 참여 불가)",
    "win_success_msg": "성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.",
    "fail_msg": "친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.",
    "sheet_fail": "구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유/탭 이름 확인 필요)",
    "sheet_ok": "구글시트 연결 완료",
    "faq_title": "🔎 검색/AI 노출용 정보(FAQ)",
    "stopwatch_note": "START 후 STOP을 누르면 기록이 자동 반영됩니다.",
    "mbti_test_12_title": "MBTI 12문항 (각 축 3문항)",
    "mbti_test_16_title": "MBTI 16문항 (각 축 4문항)",
    "mbti_test_help": "각 문항에서 더 가까운 쪽을 선택하세요.",
    "try_over": "남은 시도가 없습니다.",
    "share_not_supported": "이 기기에서는 시스템 공유가 지원되지 않습니다.",
    "no_tries_block": "남은 시도가 0이라 START/STOP이 비활성화됩니다.",
}

# =========================================================
# 5) Load DB (fortune_db/fortunes_ko.json)
# =========================================================
def load_db():
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_error": str(e)}

DB = load_db()

# =========================================================
# 6) Tarot (localized minimal)
# =========================================================
TAROT = [
    ("운명의 수레바퀴", "변화, 전환점"),
    ("태양", "행복, 성공, 긍정 에너지"),
    ("힘", "용기, 인내"),
    ("세계", "완성, 성취"),
]

# =========================================================
# 7) Zodiac / MBTI from DB
# =========================================================
ZODIAC_ORDER = DB.get("zodiac", {}).get("order", ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"])
ZODIAC_LABELS = DB.get("zodiac", {}).get("labels", {})
ZODIAC_BASE = DB.get("zodiac", {}).get("base_fortune", {})  # key -> list[str]
MBTI_DESC = DB.get("mbti", {}).get("desc", {})
MBTI_LIST = sorted(list(MBTI_DESC.keys())) if MBTI_DESC else [
    "INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"
]

POOLS = DB.get("pools", {})
COMBOS = DB.get("combos", {})

# =========================================================
# 8) MBTI Questions (Korean)
# =========================================================
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

def compute_mbti_from_answers(answers, default="ENFP"):
    scores = {"EI":0, "SN":0, "TF":0, "JP":0}
    counts = {"EI":0, "SN":0, "TF":0, "JP":0}
    for axis, pick_left in answers:
        if axis in scores:
            counts[axis] += 1
            if pick_left:
                scores[axis] += 1

    def decide(axis, left_char, right_char):
        if counts[axis] == 0:
            return left_char
        return left_char if scores[axis] >= (counts[axis]/2) else right_char

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_LIST else default

# =========================================================
# 9) Google Sheet (컬럼 고정 유지 + G열 상담신청 O/X)
#  A:시간 | B:이름 | C:전화 | D:언어 | E:기록초 | F:공유여부 | G:상담신청(O/X)
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
        if len(row) < 6:
            continue
        try:
            sec = float(row[4])
        except Exception:
            continue
        if 20.160 <= sec <= 20.169:
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

def append_entry(ws, name, phone, lang, seconds, shared_bool, consult_ox=""):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # G열 consult_ox는 "" 또는 "O" 또는 "X"
    ws.append_row([now_str, name, phone, lang, f"{seconds:.3f}", str(bool(shared_bool)), consult_ox])

# =========================================================
# 10) Share Button (시스템 공유창만)
# =========================================================
def share_button_native_only(label: str, not_supported_text: str):
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
  const notSupported = {json.dumps(not_supported_text, ensure_ascii=False)};
  btn.addEventListener("click", async () => {{
    if (!navigator.share) {{
      alert(notSupported);
      return;
    }}
    try {{
      await navigator.share({{ title: "2026 Fortune", text: url, url }});
      window.location.href = url + "?shared=1";
    }} catch (e) {{
      // cancelled
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 11) Stopwatch Component (STOP 시 기록을 ?t= 로 자동 주입)
#     + START/STOP 1번 누르면 비활성(한 번 시도 = 한 번 기록)
# =========================================================
def stopwatch_component_auto_fill(note_text: str, tries_left: int):
    disabled = "true" if tries_left <= 0 else "false"
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
    font-size: 54px;
    letter-spacing: 2px;
    padding: 14px 10px;
    border-radius: 14px;
    background: rgba(245,245,255,0.85);
    border: 1px solid rgba(130,95,220,0.20);
    color: #1f1747;
  ">00:00.000</div>

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
    {note_text}
  </div>
</div>

<script>
(function() {{
  const disabled = {disabled};
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  if (disabled) {{
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
    return;
  }}

  let running = false;
  let locked = false; // START/STOP 한번 하면 잠금
  let startTime = 0;
  let rafId = null;
  const display = document.getElementById("display");

  function fmt(ms) {{
    const total = Math.max(0, ms);
    const m = Math.floor(total / 60000);
    const s = Math.floor((total % 60000) / 1000);
    const mm = Math.floor(total % 1000);
    return String(m).padStart(2,'0') + ":" + String(s).padStart(2,'0') + "." + String(mm).padStart(3,'0');
  }}

  function tick() {{
    if (!running) return;
    const now = performance.now();
    display.textContent = fmt(now - startTime);
    rafId = requestAnimationFrame(tick);
  }}

  startBtn.addEventListener("click", () => {{
    if (locked) return;
    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);

    // START를 누르면 다시 START 못 누르게(연속 시작 방지)
    startBtn.disabled = true;
    startBtn.style.opacity = "0.55";
    startBtn.style.cursor = "not-allowed";
  }});

  stopBtn.addEventListener("click", () => {{
    if (locked) return;
    if (!running) return;

    running = false;
    locked = true; // STOP 누르면 완전 잠금
    if (rafId) cancelAnimationFrame(rafId);

    stopBtn.disabled = true;
    stopBtn.style.opacity = "0.55";
    stopBtn.style.cursor = "not-allowed";

    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    try {{
      const u = new URL(window.location.href);
      u.searchParams.set("t", v);
      window.location.href = u.toString();
    }} catch (e) {{
      window.location.href = "?t=" + v;
    }}
  }});
}})();
</script>
""",
        height=270
    )

# =========================================================
# 12) Session State
# =========================================================
if "name" not in st.session_state: st.session_state.name = ""
if "y" not in st.session_state: st.session_state.y = 2005
if "m" not in st.session_state: st.session_state.m = 1
if "d" not in st.session_state: st.session_state.d = 1
if "stage" not in st.session_state: st.session_state.stage = "input"
if "mbti" not in st.session_state: st.session_state.mbti = None
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"

# 미니게임 상태(리셋에서 유지)
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "elapsed_input" not in st.session_state: st.session_state.elapsed_input = ""
if "last_elapsed" not in st.session_state: st.session_state.last_elapsed = None  # STOP 후 기록 유지
if "consult_ui_on" not in st.session_state: st.session_state.consult_ui_on = False

# ---- shared=1 감지(보너스 1회) ----
qp = get_query_params()
shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"

if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        st.session_state.max_attempts = 2
        safe_toast(T["share_bonus_done"])
    clear_param("shared")

# ---- STOP 기록 t= 감지 → 자동 입력 + last_elapsed 유지 ----
t_val = qp.get("t", None)
if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None
if t_val is not None:
    try:
        _v = float(str(t_val).strip())
        st.session_state.elapsed_input = f"{_v:.3f}"
        st.session_state.last_elapsed = float(f"{_v:.3f}")
    except Exception:
        pass
    clear_param("t")

# =========================================================
# 13) Style (디자인 고정)
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2.5rem; max-width: 720px; }
.card {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
}
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
.badge {
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.85rem;
  background: rgba(255,255,255,0.20);
  border: 1px solid rgba(255,255,255,0.25);
  margin-top: 10px;
}
.soft-box {
  background: rgba(245,245,255,0.78);
  border: 1px solid rgba(130,95,220,0.18);
  padding: 12px 12px;
  border-radius: 14px;
  line-height: 1.65;
  font-size: 1.0rem;
  white-space: pre-line;
}
.bigbtn > button {
  border-radius: 999px !important;
  font-weight: 900 !important;
  padding: 0.75rem 1.2rem !important;
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
.adplaceholder {
  background: rgba(255,255,255,0.75);
  border-radius: 18px;
  padding: 14px;
  margin: 12px 0;
  border: 2px dashed rgba(170, 130, 220, 0.55);
  text-align:center;
  color: rgba(60,40,110,0.85);
}
.small-note { font-size: 0.92rem; opacity: 0.88; text-align:center; margin-top: 8px; }
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)

inject_seo()

# =========================================================
# 14) Logic helpers
# =========================================================
def calc_zodiac_key(year: int) -> str:
    idx = (year - 4) % 12
    return ZODIAC_ORDER[idx]

def deterministic_fortune_pack(y, m, d, mbti: str):
    """
    1) 연간/고정: (생년월일+MBTI)만으로 결정
    2) 오늘/내일: (생년월일+MBTI)+날짜로 결정
    """
    birth_key = f"{y:04d}{m:02d}{d:02d}"
    base_seed = f"{birth_key}|{mbti}"

    now = today_seoul_date()
    today_key = now.strftime("%Y%m%d")
    tomorrow_key = (now + timedelta(days=1)).strftime("%Y%m%d")

    # 고정 섹션
    saju = pick_from_pool(POOLS.get("saju_one_liner", []), base_seed + "|saju")
    year_all = pick_from_pool(POOLS.get("year_overall", []), base_seed + "|year")

    love = pick_from_pool(POOLS.get("love_advice", []), base_seed + "|love")
    money = pick_from_pool(POOLS.get("money_advice", []), base_seed + "|money")
    work = pick_from_pool(POOLS.get("work_study_advice", []), base_seed + "|work")
    health = pick_from_pool(POOLS.get("health_advice", []), base_seed + "|health")

    # 액션팁은 “오늘 날짜 기준”으로 고정 (매일 바뀌게)
    action_tip = pick_from_pool(POOLS.get("action_tip", []), base_seed + "|action|" + today_key)

    # 오늘/내일 섹션
    today = pick_from_pool(POOLS.get("today_fortune", []), base_seed + "|today|" + today_key)
    tomorrow = pick_from_pool(POOLS.get("tomorrow_fortune", []), base_seed + "|tomorrow|" + tomorrow_key)

    # 콤보(있으면 우선)
    combo_key = None
    # combos 키는 보통 "닭_ENFP" 같은 형태를 가정
    combo_key = f"{mbti}"
    return {
        "saju": saju,
        "year_all": year_all,
        "today": today,
        "tomorrow": tomorrow,
        "love": love,
        "money": money,
        "work": work,
        "health": health,
        "action_tip": action_tip
    }

# =========================================================
# 15) MBTI Test Renderer
# =========================================================
def render_mbti_test(questions, title: str, key_prefix: str):
    st.markdown(
        f"<div class='card'><b>{title}</b><br><span style='opacity:0.85;'>{T['mbti_test_help']}</span></div>",
        unsafe_allow_html=True
    )
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}.", options=[left_txt, right_txt], index=0, key=f"{key_prefix}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button(T["mbti_submit"], use_container_width=True):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 16) Reset (미니게임 시도/공유는 유지)
# =========================================================
def reset_input_only_keep_minigame():
    keep_keys = {
        "shared", "max_attempts", "attempts_used", "elapsed_input", "last_elapsed",
        "consult_ui_on"
    }
    current = dict(st.session_state)
    st.session_state.clear()
    for k, v in current.items():
        if k in keep_keys:
            st.session_state[k] = v

    st.session_state.name = ""
    st.session_state.y = 2005
    st.session_state.m = 1
    st.session_state.d = 1
    st.session_state.stage = "input"
    st.session_state.mbti = None
    st.session_state.mbti_mode = "direct"

# =========================================================
# 17) Screens
# =========================================================
def render_input():
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">🔮 {T["title"]}</p>
      <p class="hero-sub">{T["subtitle"]}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    # DB 로드 오류 표시(원인 제거용)
    if DB.get("_error"):
        st.error(f"DB 로드 오류: {DB.get('_error')}\n\n경로: {DB_PATH}")

    st.session_state.name = st.text_input(T["name"], value=st.session_state.name)

    st.markdown(f"<div class='card'><b>{T['birth']}</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.y = c1.number_input(T["year"], 1900, 2030, st.session_state.y, 1)
    st.session_state.m = c2.number_input(T["month"], 1, 12, st.session_state.m, 1)
    st.session_state.d = c3.number_input(T["day"], 1, 31, st.session_state.d, 1)

    st.markdown(f"<div class='card'><b>{T['mbti_mode']}</b></div>", unsafe_allow_html=True)
    try:
        mode = st.radio(
            "",
            [T["mbti_direct"], T["mbti_12"], T["mbti_16"]],
            index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
            horizontal=True
        )
    except TypeError:
        mode = st.radio(
            "",
            [T["mbti_direct"], T["mbti_12"], T["mbti_16"]],
            index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2)
        )

    if mode == T["mbti_direct"]:
        st.session_state.mbti_mode = "direct"
    elif mode == T["mbti_12"]:
        st.session_state.mbti_mode = "12"
    else:
        st.session_state.mbti_mode = "16"

    if st.session_state.mbti_mode == "direct":
        idx = MBTI_LIST.index(st.session_state.mbti) if st.session_state.mbti in MBTI_LIST else (MBTI_LIST.index("ENFP") if "ENFP" in MBTI_LIST else 0)
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=idx)

    elif st.session_state.mbti_mode == "12":
        done = render_mbti_test(MBTI_Q_12, T["mbti_test_12_title"], "q12")
        if done:
            st.success(f"MBTI: {st.session_state.mbti}")

    else:
        questions = MBTI_Q_12 + MBTI_Q_16_EXTRA
        done = render_mbti_test(questions, T["mbti_test_16_title"], "q16")
        if done:
            st.success(f"MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button(T["go_result"], use_container_width=True):
        if not st.session_state.mbti:
            st.session_state.mbti = "ENFP"
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_result():
    s = T["sections"]

    y = st.session_state.y
    m = st.session_state.m
    d = st.session_state.d

    zodiac_key = calc_zodiac_key(y)
    zodiac_label = ZODIAC_LABELS.get(zodiac_key, "띠")
    zodiac_desc = pick_from_pool(ZODIAC_BASE.get(zodiac_key, []), f"{y}{m}{d}|{zodiac_key}|zodiac") or ""

    mbti = st.session_state.mbti or "ENFP"
    mbti_line = MBTI_DESC.get(mbti, mbti)

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    pack = deterministic_fortune_pack(y, m, d, mbti)

    # 결과 헤더
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{zodiac_label} · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    # 본문 카드 (태그 보임 방지: 텍스트는 st.markdown 일반 사용)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['zodiac']}**: {zodiac_desc}")
    st.markdown(f"**{s['mbti']}**: {mbti_line}")
    st.markdown(f"**{s['saju']}**: {pack['saju']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['today']}**: {pack['today']}")
    st.markdown(f"**{s['tomorrow']}**: {pack['tomorrow']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['year_all']}**: {pack['year_all']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # 조합 조언 + 액션팁
    advice_text = (
        f"연애운: {pack['love']}\n"
        f"재물운: {pack['money']}\n"
        f"일/학업운: {pack['work']}\n"
        f"건강운: {pack['health']}"
    )

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['advice']}**")
    st.markdown(f"<div class='soft-box'>{advice_text}</div>", unsafe_allow_html=True)
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['action']}**")
    st.markdown(f"<div class='soft-box'>{pack['action_tip']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tarot ----
    if st.button(T["tarot_btn"], use_container_width=True):
        key = pick_from_pool([x[0] for x in TAROT], f"{y}{m}{d}|{mbti}|tarot") or TAROT[0][0]
        meaning = dict(TAROT).get(key, "행운의 메시지")
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900;color:#6b4fd6;">{T["tarot_title"]}</div>
          <div style="font-size:1.45rem;font-weight:900;margin-top:6px;">{key}</div>
          <div style="margin-top:10px;" class="soft-box">{meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Share ----
    share_button_native_only(T["share_link_btn"], T["share_not_supported"])
    st.caption(T["share_link_hint"])

    # ---- 광고 위치: 미니게임 바로 위 ----
    st.markdown(f"<div class='adplaceholder'>{T['ad_placeholder']}</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">{T["ad_kr_title"]}</div>
      <div style="margin-top:6px;">{T["ad_kr_body1"]}</div>
      <div>{T["ad_kr_body2"]}</div>
      <div style="margin-top:10px;">
        <a href="{T["ad_kr_url"]}" target="_blank"
           style="display:inline-block;background:#ff8c50;color:white;
           padding:10px 16px;border-radius:999px;font-weight:900;text-decoration:none;">
          {T["ad_kr_link"]}
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- 미니게임 (한국어만) ----
    st.markdown(
        f"<div class='card'><div style='font-weight:900;font-size:1.2rem;'>{T['mini_title']}</div>"
        f"<div style='margin-top:8px;' class='soft-box'>{T['mini_desc']}</div></div>",
        unsafe_allow_html=True
    )

    ws = get_sheet()
    sheet_ready = ws is not None
    if not sheet_ready:
        st.warning(T["sheet_fail"])
    else:
        st.success(T["sheet_ok"])

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

    if tries_left <= 0:
        st.info(T["no_tries_block"])

    if closed:
        st.info(T["mini_closed"])
    else:
        stopwatch_component_auto_fill(T["stopwatch_note"], tries_left)

        # 기록은 자동으로 들어오고, 화면에 유지(스톱 후에도 보이게)
        if st.session_state.last_elapsed is not None:
            st.markdown(f"<div class='card'><b>기록</b>: {st.session_state.last_elapsed:.3f}s</div>", unsafe_allow_html=True)

            # 기록 처리(기록제출 버튼 제거: STOP 순간 기록을 받지만, 시도 차감은 여기서 1회만)
            # t 파라미터가 들어와서 last_elapsed가 갱신될 때마다 1회 처리되도록 방지 필요
            # => last_elapsed 처리 여부를 따로 저장
        else:
            st.markdown(f"<div class='small-note'>START → STOP을 눌러 기록을 남겨주세요.</div>", unsafe_allow_html=True)

        # STOP으로 기록이 들어온 순간에만 "1회 시도 차감 + 성공/실패 판정"을 해야 함
        if "last_elapsed_handled" not in st.session_state:
            st.session_state.last_elapsed_handled = None

        if st.session_state.last_elapsed is not None and st.session_state.last_elapsed_handled != st.session_state.last_elapsed:
            # 새 기록 들어옴 → 1회 차감 + 판정
            if tries_left > 0:
                st.session_state.attempts_used += 1
            st.session_state.last_elapsed_handled = st.session_state.last_elapsed

            elapsed_val = st.session_state.last_elapsed
            if 20.160 <= elapsed_val <= 20.169:
                st.success(T["win_success_msg"])
                # 성공자는 상담신청 UI OFF
                st.session_state.consult_ui_on = False

                # 성공 기록은 바로 시트 저장(이름/전화번호 수집 없이 지금 단계에서는 '기록만' 저장할 수도 있음)
                # 너가 "정보수집은 별도"라고 했던 흐름이 계속 바뀌어서,
                # 지금은 "성공 메시지 + (필요 시 다음 단계에서 번호수집)"로 멈춤.
                # 저장을 원하면 다음 턴에서 '성공자 이름/전화 수집'을 다시 붙여줄게.
            else:
                st.info(T["fail_msg"])
                # 실패자는 상담신청 UI ON
                st.session_state.consult_ui_on = True

        # 실패자 상담신청 O/X (G열)
        if st.session_state.consult_ui_on:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 다나눔렌탈 상담신청 선택")
            st.markdown("상담신청을 **O**로 선택하면 커피쿠폰 응모로 처리됩니다.\n\nX를 누르면 저장하지 않습니다.")
            cO, cX = st.columns(2)
            if cO.button("O (상담신청)", use_container_width=True):
                if not sheet_ready:
                    st.error(T["sheet_fail"])
                else:
                    # 실패자라도 O를 고르면 시트에 기록 남김(기록초는 last_elapsed)
                    try:
                        # 전화번호 수집을 안 하는 현재 구조에서는 중복 방지 불가 → 이름/전화 수집을 붙이면 완벽해짐
                        append_entry(ws, (st.session_state.name or "").strip(), "", "ko", float(st.session_state.last_elapsed or 0.0), st.session_state.shared, consult_ox="O")
                        st.success("커피쿠폰 응모되셨습니다.")
                        st.session_state.consult_ui_on = False
                    except Exception as e:
                        st.error(f"저장 중 오류: {e}")

            if cX.button("X (신청 안함)", use_container_width=True):
                st.session_state.consult_ui_on = False
            st.markdown("</div>", unsafe_allow_html=True)

    # ---- 검색/AI 노출 섹션 ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {T['faq_title']}")
    st.markdown("- **2026 운세/띠운세/MBTI 운세/사주/오늘운세/내일운세/타로**를 무료로 제공합니다.")
    st.markdown("- **같은 생년월일+MBTI는 항상 같은 결과**가 나오도록 설계했습니다.")
    st.markdown("- 오늘/내일 운세는 날짜에 따라 바뀌며, 하루 동안은 동일하게 유지됩니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(T["reset"], use_container_width=True):
        reset_input_only_keep_minigame()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 18) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
