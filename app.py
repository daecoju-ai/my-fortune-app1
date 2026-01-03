import streamlit as st
from datetime import datetime
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

# 미니게임 목표
TARGET_MIN = 20.260
TARGET_MAX = 20.269

st.set_page_config(
    page_title="2026 운세 | 띠+MBTI+사주+오늘/내일",
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

def sha_seed(s: str) -> int:
    # 결정론 seed: stable
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def valid_date(y: int, m: int, d: int) -> bool:
    try:
        datetime(y, m, d)
        return True
    except Exception:
        return False

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
# 3) SEO Inject (키워드 노출용)
# =========================================================
def inject_seo_ko():
    description = "2026 운세 무료: 띠운세 + MBTI 운세 + 사주 + 오늘운세/내일운세 + 타로. 20.26초 스톱워치 미니게임 이벤트."
    keywords = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘운세, 내일운세, 무료운세, 타로, 연애운, 재물운, 건강운, 20.26초, 스톱워치 이벤트, 커피쿠폰"
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

# =========================================================
# 4) Fortune DB (Korean only)
# =========================================================
# 기대 파일: data/fortunes_ko.json
def load_fortune_db():
    # repo 구조 대응(로컬/streamlit cloud)
    candidates = [
        "data/fortunes_ko.json",
        "./data/fortunes_ko.json",
        "fortunes_ko.json",
        "./fortunes_ko.json",
    ]
    for p in candidates:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return None

FORTUNE_DB = load_fortune_db()

ZODIAC_ORDER = ["쥐","소","호랑이","토끼","용","뱀","말","양","원숭이","닭","개","돼지"]

def zodiac_from_year(year: int) -> str:
    # 1900~2030 범위 기준. 4 기준은 기존 코드 관례(쥐띠=4)
    idx = (year - 4) % 12
    return ZODIAC_ORDER[idx]

def pick_from_pool(pool, seed_int: int, salt: str):
    if not pool:
        return ""
    idx = sha_seed(f"{seed_int}_{salt}") % len(pool)
    return pool[idx]

def build_result_from_db(y, m, d, mbti):
    """
    결과는 '결정론적'이어야 함:
    seed = YYYYMMDD + MBTI
    """
    if not FORTUNE_DB:
        return None, "DB 파일(data/fortunes_ko.json)을 찾지 못했어요."

    birth_key = f"{y:04d}{m:02d}{d:02d}"
    seed_int = sha_seed(f"{birth_key}_{mbti}")

    zodiac = zodiac_from_year(y)
    combo_key = f"{zodiac}_{mbti}"

    pools = FORTUNE_DB.get("pools", {})
    combos = FORTUNE_DB.get("combos", {})

    # 각 섹션 풀
    today = pick_from_pool(pools.get("today", []), seed_int, "today")
    tomorrow = pick_from_pool(pools.get("tomorrow", []), seed_int, "tomorrow")
    year_all = pick_from_pool(pools.get("year_2026", []), seed_int, "year_2026")
    love = pick_from_pool(pools.get("love", []), seed_int, "love")
    money = pick_from_pool(pools.get("money", []), seed_int, "money")
    work = pick_from_pool(pools.get("work", []), seed_int, "work")
    health = pick_from_pool(pools.get("health", []), seed_int, "health")
    action_tip = pick_from_pool(pools.get("action_tip", []), seed_int, "action_tip")
    caution = pick_from_pool(pools.get("caution", []), seed_int, "caution")

    # 조합 문구
    combo = combos.get(combo_key, {})
    one_liner = pick_from_pool(combo.get("one_liner", []), seed_int, "one_liner")
    advice = pick_from_pool(combo.get("advice", []), seed_int, "advice")

    # 띠 설명은 pools 또는 combos에 별도 있으면 쓰고, 없으면 기본 문장
    zodiac_pool = pools.get("zodiac_desc", {})
    zodiac_desc_list = []
    if isinstance(zodiac_pool, dict):
        zodiac_desc_list = zodiac_pool.get(zodiac, [])
    zodiac_desc = pick_from_pool(zodiac_desc_list, seed_int, "zodiac_desc") or f"{zodiac}띠는 2026년에 흐름을 잘 타면 기회가 커져요."

    mbti_pool = pools.get("mbti_desc", {})
    mbti_desc_list = []
    if isinstance(mbti_pool, dict):
        mbti_desc_list = mbti_pool.get(mbti, [])
    mbti_desc = pick_from_pool(mbti_desc_list, seed_int, "mbti_desc") or f"{mbti} 성향은 상황을 해석하는 방식이 뚜렷해서, 장점이 운을 끌어당겨요."

    saju = pick_from_pool(pools.get("saju", []), seed_int, "saju") or "사주 한 마디: 과하지 않게 균형을 잡으면 대길!"

    return {
        "birth_key": birth_key,
        "seed": seed_int,
        "zodiac": zodiac,
        "zodiac_desc": zodiac_desc,
        "mbti": mbti,
        "mbti_desc": mbti_desc,
        "saju": saju,
        "today": today,
        "tomorrow": tomorrow,
        "year_all": year_all,
        "love": love,
        "money": money,
        "work": work,
        "health": health,
        "action_tip": action_tip,
        "caution": caution,
        "one_liner": one_liner,
        "advice": advice,
    }, None

# =========================================================
# 5) MBTI
# =========================================================
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

MBTI_HELP = "각 문항에서 더 가까운 쪽을 고르세요."

# (axis, left, right)
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

def compute_mbti(answers):
    scores = {"EI":0, "SN":0, "TF":0, "JP":0}
    counts = {"EI":0, "SN":0, "TF":0, "JP":0}
    for axis, left_pick in answers:
        counts[axis] += 1
        if left_pick:
            scores[axis] += 1

    def decide(axis, left_char, right_char):
        if counts[axis] == 0:
            return left_char
        return left_char if scores[axis] >= (counts[axis]/2) else right_char

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_LIST else "ENFP"

# =========================================================
# 6) Google Sheet (컬럼 유지 + G열 상담신청)
#  A 시간 | B 이름 | C 전화번호 | D 언어 | E 기록초 | F 공유여부 | G 상담신청(O/X)
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

def phone_exists(ws, phone_norm: str) -> bool:
    values = read_all_rows(ws)
    for row in values[1:] if len(values) > 1 else []:
        if len(row) >= 3 and normalize_phone(row[2]) == phone_norm and phone_norm:
            return True
    return False

def count_coupon_entries(ws) -> int:
    """
    선착순 20명 카운트 기준:
    - 기록이 TARGET 범위면 당첨(응모)
    - 또는 상담신청 'O'면 응모
    """
    values = read_all_rows(ws)
    cnt = 0
    for row in values[1:] if len(values) > 1 else []:
        consult = row[6] if len(row) >= 7 else ""
        sec_ok = False
        if len(row) >= 5:
            try:
                sec = float(row[4])
                sec_ok = (TARGET_MIN <= sec <= TARGET_MAX)
            except Exception:
                sec_ok = False
        if sec_ok or (str(consult).strip().upper() == "O"):
            cnt += 1
    return cnt

def append_entry(ws, name, phone, seconds, shared_bool, consult_ox):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lang = "ko"
    # 상담신청은 O/X만 허용
    consult_ox = "O" if str(consult_ox).strip().upper() == "O" else "X"
    ws.append_row([now_str, name, phone, lang, f"{seconds:.3f}", str(bool(shared_bool)), consult_ox])

# =========================================================
# 7) Share Button (시스템 공유창만 + shared=1 보너스)
# =========================================================
def share_button_native_only(label: str):
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
      alert("이 기기에서는 시스템 공유가 지원되지 않습니다.");
      return;
    }}
    try {{
      await navigator.share({{ title: "2026 운세", text: url, url }});
      const u = new URL(window.location.href);
      u.searchParams.set("shared", "1");
      window.location.href = u.toString();
    }} catch (e) {{
      // 취소 시 아무 것도 안 함
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 8) Stopwatch Component
# - 실시간 표시
# - STOP 시 기록을 session으로 넘김 (query param t=)
# - START/STOP: 한 시도에서 1번씩만 가능하도록 JS에서 잠금
# =========================================================
def stopwatch_component(tries_left: int, initial_display: str = None):
    disabled = "true" if tries_left <= 0 else "false"
    initial_display = initial_display or "00:00.000"

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
    ⏱️ STOPWATCH (목표: 20.26초)
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
  ">{initial_display}</div>

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
    START 후 STOP을 누르면 기록이 자동으로 판정됩니다.
  </div>
</div>

<script>
(function() {{
  const disabled = {disabled};
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const display = document.getElementById("display");
  if (disabled) {{
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
    return;
  }}

  let running = false;
  let startedOnce = false;
  let stoppedOnce = false;
  let startTime = 0;
  let rafId = null;

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
    if (startedOnce || stoppedOnce) return;
    startedOnce = true;
    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);

    // START는 1회만
    startBtn.disabled = true;
    startBtn.style.opacity = "0.6";
    startBtn.style.cursor = "not-allowed";
  }});

  stopBtn.addEventListener("click", () => {{
    if (!running || stoppedOnce) return;
    stoppedOnce = true;
    running = false;
    if (rafId) cancelAnimationFrame(rafId);

    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    // STOP도 1회만
    stopBtn.disabled = true;
    stopBtn.style.opacity = "0.6";
    stopBtn.style.cursor = "not-allowed";

    // 현재 URL 유지 + t 기록 전달
    try {{
      const u = new URL(window.location.href);
      u.searchParams.set("t", v);
      window.location.href = u.toString();
    }} catch (e) {{
      window.location.href = {json.dumps(APP_URL)} + "?t=" + v;
    }}
  }});
}})();
</script>
""",
        height=270
    )

# =========================================================
# 9) Session State Init
# =========================================================
if "stage" not in st.session_state: st.session_state.stage = "input"

# 입력
if "name" not in st.session_state: st.session_state.name = ""
if "y" not in st.session_state: st.session_state.y = 2005
if "m" not in st.session_state: st.session_state.m = 1
if "d" not in st.session_state: st.session_state.d = 1

# MBTI
if "mbti" not in st.session_state: st.session_state.mbti = None
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"  # direct / 12 / 16

# 미니게임
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "last_time" not in st.session_state: st.session_state.last_time = None
if "last_time_display" not in st.session_state: st.session_state.last_time_display = "00:00.000"
if "last_try_status" not in st.session_state: st.session_state.last_try_status = None  # "win" / "fail"
if "show_success_form" not in st.session_state: st.session_state.show_success_form = False

# 실패 후 상담신청 흐름
if "show_consult_flow" not in st.session_state: st.session_state.show_consult_flow = False

# =========================================================
# 10) Query param handling (shared=1, t=)
# =========================================================
qp = get_query_params()

# shared=1 → 보너스 1회(딱 1번)
shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"

if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        st.session_state.max_attempts = 2
        safe_toast("공유 확인! 미니게임 1회 추가 지급 🎁")
    clear_param("shared")

# t= → STOP 기록
t_val = qp.get("t", None)
if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None

if t_val is not None:
    try:
        sec = float(str(t_val).strip())
        st.session_state.last_time = sec
        # 표시용 00:00.000
        mm = int(sec * 1000) % 1000
        total_s = int(sec)
        s = total_s % 60
        m = total_s // 60
        st.session_state.last_time_display = f"{m:02d}:{s:02d}.{mm:03d}"

        # STOP이 일어났으므로 시도 1회 차감 + 자동 판정
        tries_left_before = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
        if tries_left_before > 0:
            st.session_state.attempts_used += 1

            if TARGET_MIN <= sec <= TARGET_MAX:
                st.session_state.last_try_status = "win"
                st.session_state.show_success_form = True
                st.session_state.show_consult_flow = False
            else:
                st.session_state.last_try_status = "fail"
                st.session_state.show_success_form = False
                st.session_state.show_consult_flow = True
    except Exception:
        pass
    clear_param("t")

# =========================================================
# 11) Styles (디자인 고정)
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
.small-note { font-size: 0.92rem; opacity: 0.88; text-align:center; margin-top: 8px; }
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)

# SEO 주입(한국어)
inject_seo_ko()

# =========================================================
# 12) UI - MBTI test render
# =========================================================
def render_mbti_test(mode: str):
    questions = MBTI_Q_12 + (MBTI_Q_16_EXTRA if mode == "16" else [])
    st.markdown(f"<div class='card'><b>{'MBTI 12문항' if mode=='12' else 'MBTI 16문항'}</b><br><span style='opacity:0.85;'>{MBTI_HELP}</span></div>", unsafe_allow_html=True)
    answers = []
    for i, (axis, left, right) in enumerate(questions, start=1):
        pick = st.radio(f"{i}. {axis}", [left, right], index=0, key=f"mbti_{mode}_{i}")
        answers.append((axis, pick == left))

    if st.button("제출하고 MBTI 확정", use_container_width=True):
        st.session_state.mbti = compute_mbti(answers)
        st.success(f"MBTI 확정: {st.session_state.mbti}")

# =========================================================
# 13) Screens
# =========================================================
def render_input():
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세</p>
      <p class="hero-sub">완전 무료</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름 입력 (결과에 표시돼요)", value=st.session_state.name)

    st.markdown("<div class='card'><b>생년월일 입력</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.y = c1.number_input("년", 1900, 2030, st.session_state.y, 1)
    st.session_state.m = c2.number_input("월", 1, 12, st.session_state.m, 1)
    st.session_state.d = c3.number_input("일", 1, 31, st.session_state.d, 1)

    st.markdown("<div class='card'><b>MBTI를 어떻게 할까요?</b></div>", unsafe_allow_html=True)
    mode = st.radio("", ["직접 선택", "간단 테스트 (12문항)", "상세 테스트 (16문항)"],
                    index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
                    horizontal=True)

    if mode == "직접 선택":
        st.session_state.mbti_mode = "direct"
    elif mode == "간단 테스트 (12문항)":
        st.session_state.mbti_mode = "12"
    else:
        st.session_state.mbti_mode = "16"

    if st.session_state.mbti_mode == "direct":
        idx = MBTI_LIST.index(st.session_state.mbti) if st.session_state.mbti in MBTI_LIST else MBTI_LIST.index("ENFP")
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=idx)
    elif st.session_state.mbti_mode == "12":
        render_mbti_test("12")
    else:
        render_mbti_test("16")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("2026년 운세 보기!", use_container_width=True):
        if not valid_date(st.session_state.y, st.session_state.m, st.session_state.d):
            st.error("생년월일이 올바르지 않습니다. (예: 2월 30일 불가)")
            return
        if not st.session_state.mbti:
            st.session_state.mbti = "ENFP"
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_result():
    # 결과 생성(DB 기반 결정론)
    res, err = build_result_from_db(st.session_state.y, st.session_state.m, st.session_state.d, st.session_state.mbti or "ENFP")
    if err:
        st.error(err)
        st.info("GitHub에 data/fortunes_ko.json 파일이 실제로 존재하는지 확인하세요.")
        return

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{res["zodiac"]}띠 · {res["mbti"]}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if res.get("one_liner"):
        st.markdown(f"**한 줄 총평**: {res['one_liner']}")
        st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    st.markdown(f"**띠 운세**: {res['zodiac_desc']}")
    st.markdown(f"**MBTI 특징**: {res['mbti_desc']}")
    st.markdown(f"**사주 한 마디**: {res['saju']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**오늘 운세**: {res['today']}")
    st.markdown(f"**내일 운세**: {res['tomorrow']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**2026 전체 운세**: {res['year_all']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**조합 조언**")
    if res.get("advice"):
        st.markdown(res["advice"])
    else:
        st.markdown("연애/재물/일/건강에서 강점을 살리면 운이 커집니다.")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**연애운**: {res['love']}")
    st.markdown(f"**재물운**: {res['money']}")
    st.markdown(f"**일/학업운**: {res['work']}")
    st.markdown(f"**건강운**: {res['health']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**오늘의 액션팁**: {res['action_tip']}")
    st.markdown(f"**주의 포인트**: {res['caution']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- 친구에게 공유하기 (실제 시스템 공유창만) ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**친구에게 공유하기** (공유하면 미니게임 1회 추가)")
    share_button_native_only("🔗 링크 공유하기")
    st.caption("모바일에서 누르면 ‘갤러리/카톡 등 공유 화면’이 뜨는 방식입니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- 광고 (다나눔렌탈) ----
    st.markdown(f"""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">정수기렌탈 궁금할 때?</div>
      <div style="margin-top:6px;"><b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b></div>
      <div>설치당일 최대 <b>현금 50만원 페이백</b> + 사은품</div>
      <div style="margin-top:10px;">
        <a href="https://www.다나눔렌탈.com" target="_blank"
           style="display:inline-block;background:#ff8c50;color:white;
           padding:10px 16px;border-radius:999px;font-weight:900;text-decoration:none;">
          다나눔렌탈.com 바로가기
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- 미니게임 ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🎁 미니게임: 20.26초 맞추기 (선착순 20명 커피쿠폰)")
    st.markdown(f"<div class='soft-box'>STOP을 눌렀을 때 기록이 <b>{TARGET_MIN:.3f} ~ {TARGET_MAX:.3f}</b>초면 성공!<br>"
                f"기본 1회, <b>친구에게 공유하기</b>를 하면 1회 추가됩니다.</div>", unsafe_allow_html=True)

    ws = get_sheet()
    if ws is None:
        st.warning("구글시트 연결이 아직 안 되어 있어요. (secrets/requirements/시트 공유/탭 이름 확인)")
    else:
        try:
            current_entries = count_coupon_entries(ws)
            if current_entries >= 20:
                st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
                st.markdown("</div>", unsafe_allow_html=True)
                return
        except Exception:
            pass

    tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    st.markdown(f"<div class='small-note'>남은 시도: <b>{tries_left}</b> / {st.session_state.max_attempts}</div>", unsafe_allow_html=True)

    # stopwatch
    stopwatch_component(tries_left, initial_display=st.session_state.last_time_display)

    # 결과 표시(STOP 후 자동 판정)
    if st.session_state.last_time is not None:
        sec = st.session_state.last_time
        diff = sec - 20.260
        sign = "+" if diff >= 0 else "-"
        st.markdown(f"<div class='card'><b>기록</b>: {sec:.3f}s (차이: {sign}{abs(diff):.3f}s)</div>", unsafe_allow_html=True)

    # 성공 폼
    if st.session_state.show_success_form and st.session_state.last_time is not None:
        st.success("성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎉 당첨자 정보 입력")

        nm = st.text_input("이름", value=(st.session_state.name or "").strip(), key="win_name")
        ph = st.text_input("전화번호", value="", key="win_phone")
        ph_norm = normalize_phone(ph)

        consent = st.checkbox(
            "개인정보 수집·이용 동의(필수)\n\n이벤트 경품 발송을 위해 이름/전화번호를 수집하며, 목적 달성 후 지체 없이 파기합니다. 동의 거부 시 참여가 제한됩니다.",
            value=False,
            key="win_consent"
        )

        if st.button("제출", use_container_width=True):
            if ws is None:
                st.error("구글시트 연결 오류")
            elif not consent:
                st.warning("동의가 필요합니다.")
            elif nm.strip() == "" or ph_norm == "":
                st.warning("이름/전화번호를 정확히 입력해주세요.")
            else:
                try:
                    if phone_exists(ws, ph_norm):
                        st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                    else:
                        if count_coupon_entries(ws) >= 20:
                            st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
                        else:
                            # 성공자는 상담신청 OFF → G열 'X'
                            append_entry(ws, nm.strip(), ph_norm, float(st.session_state.last_time), st.session_state.shared, "X")
                            st.success("접수 완료! 커피쿠폰 발송 대상에 등록되었습니다.")
                            # 성공 후 폼 닫기
                            st.session_state.show_success_form = False
                            st.session_state.show_consult_flow = False
                except Exception as e:
                    st.error(f"저장 중 오류: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # 실패 흐름
    if st.session_state.last_try_status == "fail" and st.session_state.show_consult_flow:
        st.warning("실패! 친구 공유 후 재도전 또는 상담신청으로 응모할 수 있어요.")

        # 1) 공유로 1회 추가(이미 공유했으면 추가 없음)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### 1) 친구 공유 후 재도전 (1회 추가)")
        st.caption("‘친구에게 공유하기’를 누르고 공유를 완료하면 1회 추가됩니다.")
        share_button_native_only("🔗 친구에게 공유하기")
        st.markdown("</div>", unsafe_allow_html=True)

        # 2) 상담신청으로 응모
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### 2) 정수기 렌탈 상담신청으로 커피쿠폰 응모")
        choice = st.radio("상담 신청하시겠어요?", ["O", "X"], index=1, horizontal=True, key="consult_choice")
        if choice == "O":
            st.info("상담신청(O)을 선택하셨습니다. 아래 정보를 입력하면 커피쿠폰 응모로 저장됩니다.")
            nm2 = st.text_input("이름", value=(st.session_state.name or "").strip(), key="consult_name")
            ph2 = st.text_input("전화번호", value="", key="consult_phone")
            ph2_norm = normalize_phone(ph2)

            consent2 = st.checkbox(
                "개인정보 수집·이용 동의(필수)\n\n상담/경품 발송을 위해 이름/전화번호를 수집하며, 목적 달성 후 지체 없이 파기합니다. 동의 거부 시 참여가 제한됩니다.",
                value=False,
                key="consult_consent"
            )

            if st.button("상담신청으로 응모 저장", use_container_width=True):
                if ws is None:
                    st.error("구글시트 연결 오류")
                elif not consent2:
                    st.warning("동의가 필요합니다.")
                elif nm2.strip() == "" or ph2_norm == "":
                    st.warning("이름/전화번호를 정확히 입력해주세요.")
                else:
                    try:
                        if phone_exists(ws, ph2_norm):
                            st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                        else:
                            if count_coupon_entries(ws) >= 20:
                                st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
                            else:
                                sec_val = float(st.session_state.last_time) if st.session_state.last_time is not None else 0.0
                                append_entry(ws, nm2.strip(), ph2_norm, sec_val, st.session_state.shared, "O")
                                st.success("커피쿠폰 응모가 완료되었습니다. (상담신청 O 저장됨)")
                                # 실패 흐름 종료
                                st.session_state.show_consult_flow = False
                    except Exception as e:
                        st.error(f"저장 중 오류: {e}")
        else:
            st.caption("X 선택 시에는 저장되지 않습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- 검색/AI 노출 섹션(텍스트 유지) ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🔎 검색/AI 노출용 정보(FAQ)")
    st.markdown("- **2026 운세/띠운세/MBTI 운세/사주/오늘운세/내일운세/타로**를 무료로 제공합니다.")
    st.markdown("- 생년월일+MBTI 기반으로 **항상 같은 결과(결정론)**가 나오도록 설계되어 신뢰도를 높였습니다.")
    st.markdown("- 20.26초 스톱워치 미니게임 이벤트(선착순 20명 커피쿠폰)도 함께 진행합니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- 전체 초기화(삭제하지 말 것) ----
    if st.button("처음부터 다시하기", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 14) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
