import streamlit as st
from datetime import date, datetime, timedelta
import json
import hashlib
import random
import re

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

DB_PATH = "data/fortunes_ko.json"  # ✅ GitHub에서는 data/fortunes_ko.json 로 업로드

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

def sha_seed_int(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def seeded_choice(items, seed_str: str, default: str = "") -> str:
    if not items:
        return default
    rnd = random.Random(sha_seed_int(seed_str))
    return rnd.choice(items)

def seeded_multi(items, seed_str: str, k: int = 4):
    if not items:
        return []
    rnd = random.Random(sha_seed_int(seed_str))
    if len(items) <= k:
        return items[:]
    idxs = list(range(len(items)))
    rnd.shuffle(idxs)
    return [items[i] for i in idxs[:k]]

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
# 3) SEO Inject (프론트에 안 보이게)
# =========================================================
def inject_seo():
    # ✅ 화면에는 안 보이지만 검색/AI 노출 힌트가 될 수 있는 meta/JSON-LD 삽입
    title = "2026 운세 | 띠운세 · MBTI · 사주 · 오늘운세 · 내일운세 · 타로"
    description = "무료 2026 운세: 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로. 생년월일 기반으로 결과가 일관되게 제공됩니다."
    keywords = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘운세, 내일운세, 무료운세, 타로, 연애운, 재물운, 건강운, 취업운"

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
    const metas = [
      ['name','description', {json.dumps(description, ensure_ascii=False)}],
      ['name','keywords', {json.dumps(keywords, ensure_ascii=False)}],
      ['property','og:title', {json.dumps(title, ensure_ascii=False)}],
      ['property','og:description', {json.dumps(description, ensure_ascii=False)}],
      ['property','og:type','website'],
      ['property','og:url', {json.dumps(APP_URL, ensure_ascii=False)}],
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
        height=0,
    )

# =========================================================
# 4) Load DB (KO only)
# =========================================================
@st.cache_data(show_spinner=False)
def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_pool(db, key_candidates):
    pools = db.get("pools", {})
    for k in key_candidates:
        v = pools.get(k)
        if isinstance(v, list) and v:
            return v
    return []

# =========================================================
# 5) Google Sheet (컬럼 고정 유지)
#  시간 | 이름 | 전화번호 | 언어 | 기록초 | 공유여부 | 상담신청(O/X)
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
        if 20.260 <= sec <= 20.269:
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

def append_entry(ws, name, phone, seconds, shared_bool, consult_ox=""):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # ✅ 컬럼 순서: 시간 | 이름 | 전화번호 | 언어 | 기록초 | 공유여부 | 상담신청(O/X)
    ws.append_row([now_str, name, phone, "ko", f"{seconds:.3f}", str(bool(shared_bool)), consult_ox])

# =========================================================
# 6) Share Button (시스템 공유창만)
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
      await navigator.share({{ title: "2026 Fortune", text: url, url }});
      // 공유 성공 시 보너스 1회 지급
      window.location.href = url + "?shared=1";
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
# 7) Stopwatch (STOP 시 기록 자동 주입 + 화면 정지 유지)
#    - START/STOP 1회 누르면 비활성화 (무한 도전 방지)
#    - STOP 시 elapsed를 URL에 넣지 않고, streamlit component -> postMessage로 전달
#      (페이지가 위로 튀는 현상 최소화)
# =========================================================
def stopwatch_component(note_text: str, disabled: bool):
    dis = "true" if disabled else "false"
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
      opacity: { "0.45" if disabled else "1" };
    ">START</button>

    <button id="stopBtn" style="
      flex:1; max-width: 240px;
      border:none; border-radius: 999px;
      padding: 12px 14px;
      font-weight:900;
      background:#ff8c50; color:white;
      cursor:pointer;
      opacity: { "0.45" if disabled else "1" };
    ">STOP</button>
  </div>

  <div style="margin-top:10px; font-size:0.92rem; opacity:0.85;">
    {note_text}
  </div>
</div>

<script>
(function() {{
  const disabled = {dis};
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
    if (startedOnce) return; // 1회만
    startedOnce = true;
    startBtn.disabled = true; // START 1회 누르면 비활성화
    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);
  }});

  stopBtn.addEventListener("click", () => {{
    if (!running || stoppedOnce) return;
    stoppedOnce = true;
    stopBtn.disabled = true; // STOP 1회 누르면 비활성화
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    // Streamlit로 값 전달 (페이지 이동 없음)
    const msg = {{ type: "STOPWATCH_TIME", value: v }};
    window.parent.postMessage(msg, "*");
  }});

}})();
</script>
""",
        height=280
    )

# Streamlit이 postMessage를 받을 수 있도록 작은 리스너 컴포넌트
def listen_stopwatch():
    st.components.v1.html(
        """
<script>
(function() {
  window.addEventListener("message", (event) => {
    try {
      if (event.data && event.data.type === "STOPWATCH_TIME") {
        const v = event.data.value;
        const u = new URL(window.location.href);
        u.searchParams.set("t", v);
        window.location.href = u.toString(); // ✅ t만 갱신(한 번만)
      }
    } catch(e) {}
  });
})();
</script>
""",
        height=0
    )

# =========================================================
# 8) Session State
# =========================================================
if "name" not in st.session_state: st.session_state.name = ""
if "y" not in st.session_state: st.session_state.y = 2005
if "m" not in st.session_state: st.session_state.m = 1
if "d" not in st.session_state: st.session_state.d = 1
if "stage" not in st.session_state: st.session_state.stage = "input"

# MBTI
MBTI_LIST = ["INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP","ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"]
if "mbti" not in st.session_state: st.session_state.mbti = "ENFP"
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"

# 미니게임 상태(리셋해도 유지)
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "elapsed_input" not in st.session_state: st.session_state.elapsed_input = ""
if "result_msg" not in st.session_state: st.session_state.result_msg = ""
if "need_consult" not in st.session_state: st.session_state.need_consult = False
if "allow_win_form" not in st.session_state: st.session_state.allow_win_form = False
if "win_seconds" not in st.session_state: st.session_state.win_seconds = None

# shared=1 감지(보너스 1회)
qp = get_query_params()
shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"
if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        st.session_state.max_attempts = 2
        safe_toast("공유 확인! 미니게임 1회 추가 지급 🎁")
    clear_param("shared")

# STOP 기록 t= 감지 → 자동 입력
t_val = qp.get("t", None)
if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None
if t_val is not None:
    try:
        _v = float(str(t_val).strip())
        st.session_state.elapsed_input = f"{_v:.3f}"
    except Exception:
        pass
    clear_param("t")

# =========================================================
# 9) Style (기본 디자인 큰틀 유지)
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

# =========================================================
# 10) MBTI 12/16 (변화금지: 직접선택 + 12 + 16 유지)
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

def render_mbti_test(questions, title: str, key_prefix: str):
    st.markdown(f"<div class='card'><b>{title}</b><br><span style='opacity:0.85;'>각 문항에서 더 가까운 쪽을 선택하세요.</span></div>", unsafe_allow_html=True)
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}. {axis}", options=[left_txt, right_txt], index=0, key=f"{key_prefix}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button("제출하고 MBTI 확정", use_container_width=True):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 11) Screens
# =========================================================
def reset_input_only_keep_minigame():
    keep_keys = {"shared","max_attempts","attempts_used"}
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
    st.session_state.mbti = "ENFP"
    st.session_state.mbti_mode = "direct"
    st.session_state.elapsed_input = ""
    st.session_state.result_msg = ""
    st.session_state.need_consult = False
    st.session_state.allow_win_form = False
    st.session_state.win_seconds = None

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
    mode = st.radio("", ["직접 선택", "간단 테스트 (12문항)", "상세 테스트 (16문항)"], horizontal=True)

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
        done = render_mbti_test(MBTI_Q_12, "MBTI 12문항 (각 축 3문항)", "q12")
        if done: st.success(f"MBTI: {st.session_state.mbti}")
    else:
        done = render_mbti_test(MBTI_Q_12 + MBTI_Q_16_EXTRA, "MBTI 16문항 (각 축 4문항)", "q16")
        if done: st.success(f"MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("2026년 운세 보기!", use_container_width=True):
        # 결과는 새창(쿼리 param)으로 열리게: output=1
        params = get_query_params()
        params["output"] = "1"
        # 입력값도 URL에 넣어 새창에서 동일 결과 재현
        params["y"] = str(st.session_state.y)
        params["m"] = str(st.session_state.m)
        params["d"] = str(st.session_state.d)
        params["mbti"] = st.session_state.mbti
        params["name"] = st.session_state.name
        set_query_params(params)
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def parse_input_from_query():
    qp = get_query_params()
    def first(v, default=""):
        if isinstance(v, list):
            return v[0] if v else default
        return v if v is not None else default
    try:
        y = int(first(qp.get("y"), st.session_state.y))
        m = int(first(qp.get("m"), st.session_state.m))
        d = int(first(qp.get("d"), st.session_state.d))
        name = str(first(qp.get("name"), st.session_state.name))
        mbti = str(first(qp.get("mbti"), st.session_state.mbti))
        return y, m, d, name, mbti
    except Exception:
        return st.session_state.y, st.session_state.m, st.session_state.d, st.session_state.name, st.session_state.mbti

def render_result():
    db = load_db()

    y, m, d, name, mbti = parse_input_from_query()
    display_name = (name.strip() + "님") if name.strip() else ""

    # ✅ Seed 규칙 (A, C 적용)
    # - year_all: 생년월일 기반 고정
    # - today_all: 생년월일 + 오늘 날짜 기반
    # - tomorrow_all: 생년월일 + 내일 날짜 기반
    today_dt = date.today()
    tomorrow_dt = today_dt + timedelta(days=1)

    year_pool = get_pool(db, ["year_all", "year_2026_fortune"])
    today_pool = get_pool(db, ["today_all", "today_fortune"])
    tomorrow_pool = get_pool(db, ["tomorrow_all", "tomorrow_fortune"])
    advice_pool = get_pool(db, ["advice", "tips", "action_tip"])  # 조합X: 그냥 조언 풀에서 뽑음

    year_msg = seeded_choice(year_pool, f"{y:04d}-{m:02d}-{d:02d}-year", default="(연간 운세 DB가 비어있습니다)")
    today_msg = seeded_choice(today_pool, f"{y:04d}-{m:02d}-{d:02d}-{today_dt.isoformat()}-today", default="(오늘 운세 DB가 비어있습니다)")
    tomorrow_msg = seeded_choice(tomorrow_pool, f"{y:04d}-{m:02d}-{d:02d}-{tomorrow_dt.isoformat()}-tomorrow", default="(내일 운세 DB가 비어있습니다)")
    advice_msg = seeded_choice(advice_pool, f"{y:04d}-{m:02d}-{d:02d}-advice", default="오늘은 작은 약속부터 지켜보세요.")

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    # 결과 카드 (가독성)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**오늘 운세**")
    st.markdown(f"<div class='soft-box'>{today_msg}</div>", unsafe_allow_html=True)
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("**내일 운세**")
    st.markdown(f"<div class='soft-box'>{tomorrow_msg}</div>", unsafe_allow_html=True)
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("**2026 전체 운세**")
    st.markdown(f"<div class='soft-box'>{year_msg}</div>", unsafe_allow_html=True)
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("**조언**")
    st.markdown(f"<div class='soft-box'>{advice_msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ✅ 결과 바로 밑: 친구에게 공유하기 버튼
    share_button_native_only("친구에게 공유하기")
    st.caption("버튼을 누르면 ‘갤러리에서 공유’처럼 시스템 공유 창이 뜹니다. (지원 기기 한정)")

    # ✅ 광고: 다나눔렌탈 (복구)
    st.markdown("""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">정수기 렌탈 제휴카드시 월 0원부터</div>
      <div style="margin-top:6px;">설치당일 최대 50만원 + 사은품.</div>
    </div>
    """, unsafe_allow_html=True)

    # 상담신청 폼 (실패자만 ON으로 만들려면 미니게임 결과에 따라 활성화)
    # 여기서는 UI만 유지. 실제 ON/OFF는 아래 미니게임 결과에서 제어.
    with st.expander("상담신청하기", expanded=st.session_state.need_consult):
        nm = st.text_input("이름", value=(name or "").strip(), key="consult_name")
        ph = st.text_input("연락처", value="", key="consult_phone")
        consent = st.checkbox("개인정보처리방침 동의(필수)", value=False, key="consult_consent")
        ox = st.radio("상담 신청(O/X)", ["O", "X"], horizontal=True, key="consult_ox")

        if st.button("신청완료", use_container_width=True):
            if ox == "X":
                st.info("X 선택: 구글시트에 저장하지 않습니다.")
            else:
                ws = get_sheet()
                if ws is None:
                    st.error("구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유/탭 이름 확인)")
                else:
                    pn = normalize_phone(ph)
                    if nm.strip() == "" or pn == "" or not consent:
                        st.warning("이름/연락처/동의(필수)를 확인해주세요.")
                    else:
                        # 상담신청은 기록초 없이 저장할 수 있도록 seconds=0.0, shared=False, consult=O
                        append_entry(ws, nm.strip(), pn, 0.0, st.session_state.shared, consult_ox="O")
                        st.success("상담 신청이 접수되었습니다.")

    # ✅ 미니게임 (스톱워치 20.260~20.269 성공)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🎁 미니게임: 선착순 20명 커피쿠폰 도전!")
    st.markdown("<div class='soft-box'>선착순으로 커피 쿠폰 지급되며 조기종료 될 수 있습니다.<br><br>"
                "스톱워치를 <b>20.26초</b>에 맞추면 당첨!<br>"
                "- 기본 1회<br>"
                "- <b>친구에게 공유하기</b> 성공 시 1회 추가<br>"
                "- 목표 구간: <b>20.260 ~ 20.269초</b></div>", unsafe_allow_html=True)

    ws = get_sheet()
    sheet_ready = ws is not None
    if sheet_ready:
        st.success("구글시트 연동 완료")
    else:
        st.warning("구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유/탭 이름 확인)")

    closed = False
    if sheet_ready:
        try:
            closed = (count_winners(ws) >= 20)
        except Exception:
            closed = False

    tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    st.markdown(f"<div class='small-note'>남은 시도: <b>{tries_left}</b> / {st.session_state.max_attempts}</div>", unsafe_allow_html=True)

    if closed:
        st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
    else:
        listen_stopwatch()
        disable_sw = (tries_left <= 0)
        stopwatch_component("START 후 STOP을 누르면 기록이 자동 입력됩니다.", disabled=disable_sw)

        # 자동 입력만 보여주고, '기록제출' 버튼은 제거 (요청사항)
        st.text_input("STOP을 누르면 기록이 자동으로 들어옵니다.", value=st.session_state.elapsed_input, key="elapsed_input", disabled=True)

        # 기록이 들어오면 즉시 판정(단, 1회만)
        if st.session_state.elapsed_input and st.session_state.result_msg == "":
            try:
                elapsed_val = float(st.session_state.elapsed_input)
            except Exception:
                elapsed_val = None

            if elapsed_val is not None and tries_left > 0:
                st.session_state.attempts_used += 1

                if 20.260 <= elapsed_val <= 20.269:
                    st.session_state.allow_win_form = True
                    st.session_state.win_seconds = elapsed_val
                    st.session_state.need_consult = False  # 성공자는 상담 OFF
                    st.session_state.result_msg = "성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다."
                else:
                    st.session_state.allow_win_form = False
                    st.session_state.win_seconds = elapsed_val
                    st.session_state.need_consult = True   # 실패자는 상담 ON
                    st.session_state.result_msg = f"친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.\n(당신의 기록: {elapsed_val:.3f}s)"

        if st.session_state.result_msg:
            st.markdown(f"<div class='soft-box'>{st.session_state.result_msg.replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)

        # 성공자: 이름/전화번호 입력 후 저장 (상담신청 기능 OFF)
        if st.session_state.allow_win_form and st.session_state.win_seconds is not None:
            st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
            st.markdown("#### 🎉 당첨! 정보 입력", unsafe_allow_html=True)

            nm = st.text_input("이름", value=(name or "").strip(), key="win_name")
            ph = st.text_input("전화번호", value="", key="win_phone")
            consent = st.checkbox("개인정보 수집·이용 동의(필수) — 경품 발송 목적, 목적 달성 후 지체 없이 파기, 거부 시 참여 제한", value=False, key="win_consent")

            if st.button("제출", use_container_width=True):
                if not sheet_ready:
                    st.error("구글시트 연결이 아직 안 되어 있어요.")
                else:
                    pn = normalize_phone(ph)
                    if nm.strip() == "" or pn == "" or not consent:
                        st.warning("이름/전화번호/동의(필수)를 확인해주세요.")
                    elif phone_exists(ws, pn):
                        st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                    elif count_winners(ws) >= 20:
                        st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
                    else:
                        append_entry(ws, nm.strip(), pn, float(st.session_state.win_seconds), st.session_state.shared, consult_ox="")
                        st.success("접수 완료! 커피쿠폰 발송 대상에 등록되었습니다.")
                        # 성공 후 입력 폼 OFF
                        st.session_state.allow_win_form = False
                        st.session_state.need_consult = False

    st.markdown("</div>", unsafe_allow_html=True)

    # 처음부터 다시하기 (입력만 초기화, 게임 시도 유지)
    if st.button("처음부터 다시하기", use_container_width=True):
        reset_input_only_keep_minigame()
        st.rerun()

# =========================================================
# 12) Run
# =========================================================
inject_seo()

# output=1이면 결과 화면으로
qp = get_query_params()
out = qp.get("output", "0")
if isinstance(out, list):
    out = out[0] if out else "0"

if str(out) == "1":
    render_result()
else:
    render_input()
