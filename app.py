import streamlit as st
from datetime import datetime, date, timedelta
import json, os, re, hashlib, random

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
APP_URL = "https://my-fortune.streamlit.app"  # 필요하면 본인 URL로 수정
SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_NAME = "시트1"
DB_PATH = os.path.join("data", "fortunes_ko.json")

# Tarot assets (GitHub에 올린 경로 기준)
TAROT_MAJORS_DIR = os.path.join("assets", "tarot", "majors")
TAROT_BACK = os.path.join("assets", "tarot", "back.png")

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 오늘/내일 + 타로",
    page_icon="🔮",
    layout="centered"
)

# =========================================================
# 1) Helpers
# =========================================================
def normalize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone or "")

def sha_seed(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def seeded_pick(pool: list, seed_str: str) -> str:
    if not isinstance(pool, list) or len(pool) == 0:
        raise ValueError("DB pool is empty.")
    r = random.Random(sha_seed(seed_str))
    return pool[r.randrange(0, len(pool))]

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

def clear_param(k: str):
    try:
        p = get_query_params()
        if k in p:
            p.pop(k, None)
            set_query_params(p)
    except Exception:
        pass

def hard_stop(msg: str):
    st.error(msg)
    st.stop()

# =========================================================
# 2) SEO Inject (프론트에는 안 보이게)
# =========================================================
def inject_seo():
    description = "2026 운세, 띠운세, MBTI, 오늘 운세, 내일 운세, 무료 타로"
    keywords = "2026 운세, 띠운세, MBTI 운세, 오늘 운세, 내일 운세, 타로, 무료"
    title = "2026 운세 | 띠 + MBTI + 오늘/내일 + 타로"
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
      ['name','robots','index,follow']
    ];
    metas.forEach(([attr,key,val]) => {{
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

# =========================================================
# 3) DB Load (fallback 금지)
# =========================================================
@st.cache_data(show_spinner=False)
def load_db():
    if not os.path.exists(DB_PATH):
        return None
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_db(db):
    if not isinstance(db, dict):
        return False, "DB를 읽지 못했습니다."
    if "pools" not in db or not isinstance(db["pools"], dict):
        return False, "DB 구조 오류: pools 없음"
    pools = db["pools"]
    for k in ["today", "tomorrow", "year_all", "advice"]:
        if k not in pools:
            return False, f"DB 구조 오류: pools.{k} 없음"
        if not isinstance(pools[k], list) or len(pools[k]) == 0:
            return False, f"DB 비어 있음: pools.{k}"
    return True, ""

DB = load_db()
ok, err = validate_db(DB)
if not ok:
    hard_stop(
        "DB 오류: "
        + err
        + "\n\n해결:\n- GitHub에 data/fortunes_ko.json 파일이 존재하는지\n- 내용이 비어있지 않은지\n- JSON 형식이 깨지지 않았는지 확인하세요."
    )

# =========================================================
# 4) Google Sheet
#    컬럼(확정): A시간 | B이름 | C연락처 | D기록초 | E공유여부 | F제품 | G상담신청(O/X)
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

def append_row(ws, name: str, phone: str, record_sec, shared: bool, product: str, consult: str):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sec_str = "" if record_sec is None else f"{float(record_sec):.3f}"
    ws.append_row([now_str, name, phone, sec_str, str(bool(shared)), product, consult])

# =========================================================
# 5) UI Style (큰틀 유지 + 배경/카드 그라데이션)
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2.5rem; max-width: 720px; }
body { background: linear-gradient(180deg, rgba(245,245,255,0.60), rgba(255,255,255,1.0)); }
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
.bigbtn > button {
  border-radius: 999px !important;
  font-weight: 900 !important;
  padding: 0.75rem 1.2rem !important;
}
.result-bg {
  background: linear-gradient(180deg, rgba(161,140,209,0.20), rgba(142,197,252,0.14));
  border-radius: 18px;
  padding: 10px 10px;
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
.gamebox {
  background: linear-gradient(180deg, rgba(255,140,80,0.10), rgba(161,140,209,0.08));
  border-radius: 18px;
  padding: 16px;
  margin: 12px 0;
  border: 1px solid rgba(140,120,200,0.18);
  box-shadow: 0 10px 28px rgba(0,0,0,0.06);
}
.small-note { font-size: 0.92rem; opacity: 0.88; text-align:center; margin-top: 8px; }
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
.tarot-wrap { text-align:center; }
</style>
""", unsafe_allow_html=True)

inject_seo()

# =========================================================
# 6) Core Data
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
    "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠"
}
def calc_zodiac_key(year: int) -> str:
    idx = (year - 4) % 12
    return ZODIAC_ORDER[idx]

MBTI_DESC = {
    "INTJ":"전략가 · 목표지향","INTP":"아이디어 · 분석가","ENTJ":"리더 · 추진력","ENTP":"토론가 · 발상가",
    "INFJ":"통찰 · 조언자","INFP":"가치 · 감성","ENFJ":"조율 · 리더","ENFP":"열정 · 아이디어",
    "ISTJ":"원칙 · 책임","ISFJ":"배려 · 헌신","ESTJ":"관리자 · 현실","ESFJ":"분위기 · 케어",
    "ISTP":"장인 · 문제해결","ISFP":"감성 · 힐러","ESTP":"모험 · 실행","ESFP":"사교 · 즐거움",
}
MBTI_LIST = sorted(MBTI_DESC.keys())

# 12문항 + 16문항(추가 4문항)
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
    for axis, pick_left in answers:
        counts[axis] += 1
        if pick_left:
            scores[axis] += 1

    def decide(axis, left, right):
        return left if scores[axis] >= (counts[axis] / 2) else right

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_DESC else "ENFP"

# =========================================================
# 7) Share Buttons (native + URL copy)
# =========================================================
def share_and_copy_buttons():
    st.components.v1.html(
        """
<div style="display:flex; gap:10px; margin: 6px 0 0 0;">
  <button id="shareBtn" style="flex:1; border:none; border-radius:999px; padding:12px 14px; font-weight:900;
    background:#6b4fd6; color:white; cursor:pointer;">친구에게 공유하기</button>
  <button id="copyBtn" style="flex:1; border:none; border-radius:999px; padding:12px 14px; font-weight:900;
    background:#ffffff; color:#6b4fd6; border:2px solid rgba(107,79,214,0.35); cursor:pointer;">URL 복사</button>
</div>
<script>
(function(){
  const url = window.location.href.split('#')[0];
  const shareBtn = document.getElementById("shareBtn");
  const copyBtn = document.getElementById("copyBtn");

  async function copyUrl() {
    try {
      await navigator.clipboard.writeText(url);
      alert("URL을 복사했어요!");
    } catch(e) {
      window.prompt("복사해서 보내기", url);
    }
  }

  shareBtn.addEventListener("click", async () => {
    if (!navigator.share) {
      await copyUrl();
      return;
    }
    try {
      await navigator.share({ title: "2026 운세", text: url, url });
      const u = new URL(window.location.href);
      u.searchParams.set("shared", "1");
      window.location.href = u.toString();
    } catch(e) {
      await copyUrl();
    }
  });

  copyBtn.addEventListener("click", copyUrl);
})();
</script>
""",
        height=70
    )

# =========================================================
# 8) Stopwatch (STOP 즉시 판정, 화면 유지, 중복 클릭 방지)
# =========================================================
def stopwatch_component(tries_left: int):
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
  <div style="font-weight:900;font-size:1.10rem;color:#2b2350;margin-bottom:10px;">
    STOPWATCH
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
    STOP을 누르면 시간 정지 + 자동 판정됩니다.
  </div>
</div>

<script>
(function() {
  const disabled = {disabled};
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const display = document.getElementById("display");

  if (disabled) {
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
    return;
  }

  let running = false;
  let startTime = 0;
  let rafId = null;
  let startLocked = false;
  let stopLocked = false;

  function fmt(ms) {
    const total = Math.max(0, ms);
    const m = Math.floor(total / 60000);
    const s = Math.floor((total % 60000) / 1000);
    const mm = Math.floor(total % 1000);
    return String(m).padStart(2,'0') + ":" + String(s).padStart(2,'0') + "." + String(mm).padStart(3,'0');
  }

  function tick() {
    if (!running) return;
    const now = performance.now();
    display.textContent = fmt(now - startTime);
    rafId = requestAnimationFrame(tick);
  }

  startBtn.addEventListener("click", () => {
    if (startLocked) return;
    startLocked = true;
    startBtn.disabled = true;

    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);
  });

  stopBtn.addEventListener("click", () => {
    if (stopLocked) return;
    stopLocked = true;

    if (!running) return;
    running = false;
    if (rafId) cancelAnimationFrame(rafId);

    stopBtn.disabled = true;

    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    const u = new URL(window.location.href);
    u.searchParams.set("t", v);
    window.location.href = u.toString();
  });
})();
</script>
""",
        height=280
    )

# =========================================================
# 9) Result New Tab Launcher
# =========================================================
def open_result_new_tab(params: dict):
    st.components.v1.html(
        f"""
<script>
(function(){
  const url = new URL(window.location.href.split('#')[0]);
  url.searchParams.set("view","result");
  {''.join([f'url.searchParams.set({json.dumps(k)}, {json.dumps(str(v))});' for k,v in params.items()])}
  window.open(url.toString(), "_blank");
})();
</script>
""",
        height=0
    )

# =========================================================
# 10) Tarot (하루 동안 고정값)
# =========================================================
MAJOR_FILES = [
    "00_the_fool.png","01_the_magician.png","02_the_high_priestess.png","03_the_empress.png",
    "04_the_emperor.png","05_the_hierophant.png","06_the_lovers.png","07_the_chariot.png",
    "08_strength.png","09_the_hermit.png","10_wheel_of_fortune.png","11_justice.png",
    "12_the_hanged_man.png","13_death.png","14_temperance.png","15_the_devil.png",
    "16_the_tower.png","17_the_star.png","18_the_moon.png","19_the_sun.png",
    "20_judgement.png","21_the_world.png"
]

def pick_tarot_daily(seed_str: str) -> str:
    r = random.Random(sha_seed(seed_str))
    return MAJOR_FILES[r.randrange(0, len(MAJOR_FILES))]

def tarot_draw_ui(seed_str: str):
    # 카드 뒷면 먼저 보여주고, 버튼 누르면 "뿅" 등장(간단 애니메이션)
    chosen = pick_tarot_daily(seed_str)

    back_exists = os.path.exists(TAROT_BACK)
    front_path = os.path.join(TAROT_MAJORS_DIR, chosen)
    front_exists = os.path.exists(front_path)

    st.markdown("<div class='card tarot-wrap'>", unsafe_allow_html=True)
    st.markdown("### 🃏 오늘의 타로 1장", unsafe_allow_html=True)

    if back_exists:
        st.image(TAROT_BACK, use_column_width=True)
    else:
        st.info("타로 뒷면 이미지가 없습니다: assets/tarot/back.png")

    if st.button("타로 뽑기", use_container_width=True):
        # 애니메이션 + 결과 표시
        st.components.v1.html("""
<style>
@keyframes shake { 0%{transform:translate(0,0) rotate(0deg);} 25%{transform:translate(2px,-2px) rotate(-1deg);}
50%{transform:translate(-2px,2px) rotate(1deg);} 75%{transform:translate(2px,2px) rotate(0deg);} 100%{transform:translate(0,0) rotate(0deg);} }
@keyframes pop { 0%{transform:scale(0.85); opacity:0.0;} 100%{transform:scale(1.0); opacity:1.0;} }
</style>
<div id="tarot_anim" style="animation: shake 0.35s ease-in-out 2;"></div>
""", height=0)

        st.markdown("#### ✨ 뿅!", unsafe_allow_html=True)
        if front_exists:
            st.image(front_path, use_column_width=True)
        else:
            st.warning(f"타로 앞면 이미지가 없습니다: {front_path}")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 11) Session
# =========================================================
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "last_time" not in st.session_state: st.session_state.last_time = None
if "last_outcome" not in st.session_state: st.session_state.last_outcome = None  # "win"/"fail"
if "show_success_form" not in st.session_state: st.session_state.show_success_form = False
if "show_consult_form" not in st.session_state: st.session_state.show_consult_form = False
if "mbti" not in st.session_state: st.session_state.mbti = "ENFP"

qp = get_query_params()

# 공유 보너스 1회만
shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"
if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        st.session_state.max_attempts = 2
        st.toast("공유 확인! 미니게임 1회 추가 지급 🎁")
    clear_param("shared")

# STOP 기록 들어오면 자동 판정
t_val = qp.get("t", None)
if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None
if t_val is not None:
    try:
        sec = float(str(t_val).strip())
        st.session_state.last_time = float(f"{sec:.3f}")
        if st.session_state.attempts_used < st.session_state.max_attempts:
            st.session_state.attempts_used += 1

        if 20.260 <= st.session_state.last_time <= 20.269:
            st.session_state.last_outcome = "win"
            st.session_state.show_success_form = True
            st.session_state.show_consult_form = False
        else:
            st.session_state.last_outcome = "fail"
            st.session_state.show_success_form = False
            st.session_state.show_consult_form = True
    except Exception:
        pass
    clear_param("t")

# =========================================================
# 12) Screens
# =========================================================
view = qp.get("view", "input")
if isinstance(view, list):
    view = view[0] if view else "input"

def render_input():
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 운세 | 띠 + MBTI + 오늘/내일 + 타로</p>
      <p class="hero-sub">완전 무료</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    name = st.text_input("이름 입력 (결과에 표시돼요)", value="")

    st.markdown("<div class='card'><b>생년월일 입력</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    year = c1.number_input("년", 1900, 2030, 2005, 1)
    month = c2.number_input("월", 1, 12, 1, 1)
    day = c3.number_input("일", 1, 31, 1, 1)

    st.markdown("<div class='card'><b>MBTI를 어떻게 할까요?</b></div>", unsafe_allow_html=True)
    mode = st.radio("", ["직접 선택", "간단 테스트 (12문항)", "상세 테스트 (16문항)"], index=0, horizontal=True)

    if mode == "직접 선택":
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=MBTI_LIST.index(st.session_state.mbti) if st.session_state.mbti in MBTI_LIST else 0)
    else:
        is16 = (mode == "상세 테스트 (16문항)")
        questions = MBTI_Q_12 + (MBTI_Q_16_EXTRA if is16 else [])
        answers = []
        st.markdown("<div class='card'><b>각 문항에서 더 가까운 쪽을 선택하세요.</b></div>", unsafe_allow_html=True)
        for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
            choice = st.radio(f"{i}.", [left_txt, right_txt], key=f"q_{mode}_{i}")
            answers.append((axis, choice == left_txt))

        if st.button("제출하고 MBTI 확정", use_container_width=True):
            st.session_state.mbti = compute_mbti(answers)
            st.success(f"MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("운세 보기 (새 창)", use_container_width=True):
        params = {
            "name": name.strip(),
            "y": str(int(year)), "m": str(int(month)), "d": str(int(day)),
            "mbti": st.session_state.mbti
        }
        open_result_new_tab(params)
    st.markdown('</div>', unsafe_allow_html=True)

def render_result():
    name = qp.get("name", "")
    if isinstance(name, list): name = name[0] if name else ""
    y = qp.get("y", "2005"); m = qp.get("m", "1"); d = qp.get("d", "1")
    if isinstance(y, list): y = y[0]
    if isinstance(m, list): m = m[0]
    if isinstance(d, list): d = d[0]
    mbti = qp.get("mbti", st.session_state.mbti)
    if isinstance(mbti, list): mbti = mbti[0] if mbti else st.session_state.mbti

    try:
        year = int(str(y)); month = int(str(m)); day = int(str(d))
        birth = date(year, month, day)
    except Exception:
        hard_stop("생년월일이 올바르지 않습니다. 입력 화면에서 다시 시도해주세요.")

    zodiac_key = calc_zodiac_key(birth.year)
    zodiac_label = ZODIAC_LABEL[zodiac_key]
    mbti_line = MBTI_DESC.get(mbti, "성향 정보")

    display_name = (name.strip() + "님") if name.strip() else ""

    today_dt = date.today()
    tomorrow_dt = today_dt + timedelta(days=1)

    seed_base = birth.strftime("%Y%m%d")
    seed_today = seed_base + "_" + today_dt.strftime("%Y%m%d")
    seed_tomorrow = seed_base + "_" + tomorrow_dt.strftime("%Y%m%d")
    seed_year = seed_base

    pools = DB["pools"]
    today_msg = seeded_pick(pools["today"], seed_today)
    tomorrow_msg = seeded_pick(pools["tomorrow"], seed_tomorrow)
    year_all_msg = seeded_pick(pools["year_all"], seed_year)
    advice_msg = seeded_pick(pools["advice"], seed_today)

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{zodiac_label} · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='result-bg'>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**띠 운세**: {zodiac_label}")
    st.markdown(f"**MBTI 특징**: {mbti_line}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**오늘 운세** ({today_dt.strftime('%m/%d')}): {today_msg}")
    st.markdown(f"**내일 운세** ({tomorrow_dt.strftime('%m/%d')}): {tomorrow_msg}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**2026 전체 운세**: {year_all_msg}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**조언**:\n\n{advice_msg}")
    st.markdown("</div>", unsafe_allow_html=True)

    # 결과창 바로 밑: 공유 버튼
    share_and_copy_buttons()

    # 광고 (복구)
    st.markdown("""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">정수기 렌탈 제휴카드시 월 0원부터</div>
      <div style="margin-top:6px;">설치당일 최대 50만원 + 사은품.</div>
    </div>
    """, unsafe_allow_html=True)

    # 타로 (하루 고정)
    tarot_seed = seed_base + "_" + today_dt.strftime("%Y%m%d")
    tarot_draw_ui(tarot_seed)

    # 구글시트
    ws = get_sheet()
    if ws is None:
        st.warning("구글시트 연동이 안 되어 있습니다. (Secrets/시트 공유/탭 이름 확인)")
    else:
        st.success("구글시트 연동 완료")

    # 미니게임 안내
    st.markdown("<div class='gamebox'>", unsafe_allow_html=True)
    st.markdown("### 🎁 미니게임: 선착순 20명 커피 쿠폰")
    st.markdown("- **20.260 ~ 20.269초** 사이면 성공")
    st.markdown("- 선착순으로 커피 쿠폰 지급되며 조기종료 될 수 있습니다")
    st.markdown("</div>", unsafe_allow_html=True)

    closed = False
    if ws is not None:
        try:
            closed = (count_winners(ws) >= 20)
        except Exception:
            closed = False

    tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    st.markdown(f"<div class='small-note'>남은 시도: <b>{tries_left}</b> / {st.session_state.max_attempts}</div>", unsafe_allow_html=True)

    if closed:
        st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
    else:
        # 게임 컴포넌트
        stopwatch_component(tries_left)

        # STOP 결과 문구
        if st.session_state.last_time is not None and st.session_state.last_outcome is not None:
            if st.session_state.last_outcome == "win":
                st.success("성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.")
            else:
                st.info(
                    f"친구 공유 후 재도전.\n"
                    f"또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.\n\n"
                    f"(당신의 기록: {st.session_state.last_time:.3f}s)"
                )

        # 성공시 입력
        if st.session_state.show_success_form:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🎉 성공! 정보 입력")
            nm = st.text_input("이름", value=name.strip())
            ph = st.text_input("전화번호", value="")
            consent = st.checkbox("개인정보 수집·이용 동의(필수)")
            product = st.selectbox("관심 제품", ["정수기", "안마의자", "기타가전"], index=0)

            if st.button("응모 제출", use_container_width=True):
                if ws is None:
                    st.error("구글시트 연동이 안 되어 있어 저장할 수 없습니다.")
                else:
                    ph_norm = normalize_phone(ph)
                    if not consent:
                        st.warning("동의가 필요합니다.")
                    elif nm.strip() == "" or ph_norm == "":
                        st.warning("이름/전화번호를 정확히 입력해주세요.")
                    elif phone_exists(ws, ph_norm):
                        st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                    elif count_winners(ws) >= 20:
                        st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
                    else:
                        append_row(ws, nm.strip(), ph_norm, st.session_state.last_time, st.session_state.shared, product, "X")
                        st.success("접수 완료!")
                        st.session_state.show_success_form = False
                        st.session_state.show_consult_form = False
            st.markdown("</div>", unsafe_allow_html=True)

        # 실패시 상담신청 O/X
        if st.session_state.show_consult_form:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### ☎️ 상담 신청으로 커피쿠폰 응모하기")
            nm2 = st.text_input("이름", value=name.strip(), key="consult_name")
            ph2 = st.text_input("전화번호", value="", key="consult_phone")
            consent2 = st.checkbox("개인정보처리방침 동의(필수)", key="consult_consent")
            product2 = st.selectbox("관심 제품", ["정수기", "안마의자", "기타가전"], index=0, key="consult_product")
            choice = st.radio("상담 신청", ["O", "X"], horizontal=True)

            if st.button("신청완료", use_container_width=True):
                if choice == "X":
                    st.info("신청을 취소했습니다. (DB 저장 금지)")
                    st.session_state.show_consult_form = False
                else:
                    if ws is None:
                        st.error("구글시트 연동이 안 되어 있어 저장할 수 없습니다.")
                    else:
                        ph_norm2 = normalize_phone(ph2)
                        if not consent2:
                            st.warning("동의가 필요합니다.")
                        elif nm2.strip() == "" or ph_norm2 == "":
                            st.warning("이름/전화번호를 정확히 입력해주세요.")
                        elif phone_exists(ws, ph_norm2):
                            st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                        else:
                            append_row(ws, nm2.strip(), ph_norm2, st.session_state.last_time, st.session_state.shared, product2, "O")
                            st.success("커피쿠폰 응모되었습니다.")
                            st.session_state.show_consult_form = False
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # result-bg end

def router():
    if str(view) == "result":
        render_result()
    else:
        render_input()

router()
