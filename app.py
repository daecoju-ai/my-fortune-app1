import streamlit as st
from datetime import datetime
import random
import json
import os
import re
from urllib.parse import quote, unquote

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

# 다나눔렌탈 광고 문구 (한국어 전용)
AD_TITLE = "정수기 렌탈 제휴카드시 월 0원부터"
AD_BODY = "설치당일 최대 50만원 + 사은품"
AD_URL = "https://www.다나눔렌탈.com"

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일",
    page_icon="🔮",
    layout="centered",
)

# =========================================================
# 1) Helpers
# =========================================================
def normalize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone or "")

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

def today_seed(y: int, m: int, d: int) -> int:
    # 날짜 기반으로 안정적인 seed
    return int(f"{y:04d}{m:02d}{d:02d}")

# =========================================================
# 2) Query params (신/구 Streamlit 대응)
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
            st.query_params[k] = str(v)
    except Exception:
        st.experimental_set_query_params(**params)

def clear_query_params():
    try:
        st.query_params.clear()
    except Exception:
        st.experimental_set_query_params()

# =========================================================
# 3) SEO Inject (프론트에 안 보이게 head meta만 주입)
# =========================================================
def inject_seo():
    description = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘운세, 내일운세, 타로, 무료 운세"
    keywords = "2026 운세,띠운세,MBTI 운세,사주,오늘 운세,내일 운세,무료 운세,타로,연애운,재물운,건강운"
    title = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일"

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
# 4) Design (지금 마음에 든 디자인 틀 유지)
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
.badge {
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.85rem;
  background: rgba(255,255,255,0.20);
  border: 1px solid rgba(255,255,255,0.25);
  margin-top: 10px;
}

.card {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
}

.result-card {
  border-radius: 22px;
  padding: 18px 16px;
  margin: 12px 0;
  border: 1px solid rgba(255,255,255,0.25);
  box-shadow: 0 14px 34px rgba(0,0,0,0.14);
  background: linear-gradient(135deg, rgba(161,140,209,0.35), rgba(251,194,235,0.28), rgba(142,197,252,0.30));
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

.minibox {
  background: rgba(255,255,255,0.96);
  border-radius: 18px;
  padding: 16px;
  margin: 12px 0;
  border: 2px solid rgba(107, 79, 214, 0.35);
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}

.small-note { font-size: 0.92rem; opacity: 0.88; text-align:center; margin-top: 8px; }
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)

inject_seo()

# =========================================================
# 5) MBTI (직접 / 12문항 / 16문항 유지 — 변화금지)
# =========================================================
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"
]

MBTI_12 = [
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

MBTI_16_EXTRA = [
    ("EI","새로운 사람을 만나면 설렌다","새로운 사람은 적응 시간이 필요"),
    ("SN","지금 필요한 현실이 중요","미래 가능성이 더 중요"),
    ("TF","공정함이 최우선","조화로움이 최우선"),
    ("JP","일정이 확정되어야 안심","상황에 따라 바뀌는 게 자연스러움"),
]

def compute_mbti(answers):
    # answers: list[(axis, pick_left_bool)]
    scores = {"EI":0,"SN":0,"TF":0,"JP":0}
    counts = {"EI":0,"SN":0,"TF":0,"JP":0}
    for axis, pick_left in answers:
        counts[axis]+=1
        if pick_left:
            scores[axis]+=1

    def decide(axis, left_char, right_char):
        if counts[axis] == 0:
            return left_char
        return left_char if scores[axis] >= (counts[axis]/2) else right_char

    return f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"

# =========================================================
# 6) fortunes_ko.json 로딩 (근본원인 제거: 경로 2군데 시도 + 에러표시)
# =========================================================
def load_fortune_db():
    candidates = [
        os.path.join(os.getcwd(), "fortunes_ko.json"),
        os.path.join(os.getcwd(), "data", "fortunes_ko.json"),
        os.path.join(os.getcwd(), "data", "fortunes_ko_fixed.json"),
        os.path.join(os.getcwd(), "data", "fortunes_ko_clean.json"),
    ]
    last_err = None
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    return None, f"DB 형식 오류: dict가 아님 ({path})"
                return data, None
            except Exception as e:
                last_err = f"{path} 로딩 실패: {e}"
    return None, last_err or "fortunes_ko.json 파일을 찾을 수 없습니다. (루트 또는 data 폴더 확인)"

FORTUNE_DB, DB_ERR = load_fortune_db()

# =========================================================
# 7) 띠 계산 (12띠)
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL_KO = {
    "rat":"쥐", "ox":"소", "tiger":"호랑이", "rabbit":"토끼", "dragon":"용", "snake":"뱀",
    "horse":"말", "goat":"양", "monkey":"원숭이", "rooster":"닭", "dog":"개", "pig":"돼지"
}
def zodiac_key_from_year(year:int)->str:
    return ZODIAC_ORDER[(year - 4) % 12]

# =========================================================
# 8) DB에서 "띠_MBTI" 키로 결과 뽑기 (생년월일 기반으로 항상 동일)
#    - 같은 생년월일 입력하면 10번 해도 결과 동일
# =========================================================
def deterministic_pick(items, seed:int):
    if not items:
        return None
    r = random.Random(seed)
    return items[r.randrange(0, len(items))]

def get_combo_key(year:int, mbti:str)->str:
    z = ZODIAC_LABEL_KO[zodiac_key_from_year(year)]
    return f"{z}_{mbti}"

def pick_from_db(db:dict, combo_key:str, y:int, m:int, d:int):
    """
    기대 DB 구조 예시(권장):
    db["combos"][combo_key]["today"] -> list[str]
    db["combos"][combo_key]["tomorrow"] -> list[str]
    db["combos"][combo_key]["year"] -> list[str]
    db["combos"][combo_key]["saju"] -> list[str]
    db["combos"][combo_key]["mbti_trait"] -> list[str] or str
    db["combos"][combo_key]["zodiac"] -> list[str] or str
    db["combos"][combo_key]["action_tip"] -> list[str]
    """
    if not db or "combos" not in db or combo_key not in db["combos"]:
        return None, f"DB에 키가 없습니다: {combo_key} (fortunes_ko.json combos 확인)"

    combo = db["combos"][combo_key]
    seed = today_seed(y,m,d) + (hash(mbti) % 10000)

    def pick_list(field, add):
        v = combo.get(field, [])
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return deterministic_pick(v, seed + add) or ""
        return ""

    result = {
        "zodiac": pick_list("zodiac", 11),
        "mbti_trait": pick_list("mbti_trait", 12),
        "saju": pick_list("saju", 13),
        "today": pick_list("today", 1),
        "tomorrow": pick_list("tomorrow", 2),
        "year": pick_list("year", 3),
        "advice": pick_list("advice", 4),
        "action_tip": pick_list("action_tip", 5),
    }
    return result, None

# =========================================================
# 9) Google Sheet (컬럼 구조: 기존 + 확장 대응)
#    ✅ 너가 말한 "기존 컬럼 구조"를 유지하면서
#    필요한 경우 뒤 컬럼에 추가 저장
#
# 추천 헤더(너가 이미 쓰던 형태):
# A 시간 | B 이름 | C 전화번호 | D 상품 | E 기록초 | F 공유여부 | G 상담신청(O/X)
# =========================================================
def get_sheet():
    try:
        if gspread is None or Credentials is None:
            return None, "requirements 또는 라이브러리 로딩 실패"
        if "gcp_service_account" not in st.secrets:
            return None, "st.secrets에 gcp_service_account 없음"

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
        return ws, None
    except Exception as e:
        return None, str(e)

def read_all_rows(ws):
    try:
        return ws.get_all_values()
    except Exception:
        return []

def count_winners(ws) -> int:
    values = read_all_rows(ws)
    winners = 0
    for row in values[1:] if len(values) > 1 else []:
        # E열(기록초) 기준
        if len(row) < 5:
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

def append_row(ws, name, phone, product, seconds, shared_bool, consult_ox):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # A~G
    ws.append_row([now_str, name, phone, product, f"{seconds:.3f}", str(bool(shared_bool)), consult_ox])

# =========================================================
# 10) Share Button (네가 말한 “갤러리 공유창” — 시스템 공유 시트)
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
      // 공유 성공하면 shared=1 주입 (보너스 1회)
      const u = new URL(window.location.href);
      u.searchParams.set("shared", "1");
      window.location.href = u.toString();
    }} catch (e) {{
      // 취소하면 아무것도 안 함
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 11) Stopwatch Component
#    - START/STOP 한 번씩 누르면 비활성화 (요청사항)
#    - STOP하면 정지화면 유지
#    - STOP 순간 기록을 자동으로 쿼리 t= 로 주입하여 파이썬이 받게 함
#    - 기록제출 버튼 제거 (STOP 즉시 결과판정)
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
    START 후 STOP을 누르면 기록이 자동 판정됩니다.
  </div>
</div>

<script>
(function() {{
  const disabled = {disabled_all};
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
  let startTime = 0;
  let rafId = null;
  let startedOnce = false;
  let stoppedOnce = false;

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
    if (startedOnce) return; // START 한번만
    startedOnce = true;
    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    startBtn.disabled = true;     // ✅ START 누르면 비활성화
    startBtn.style.opacity = "0.55";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);
  }});

  stopBtn.addEventListener("click", () => {{
    if (!running) return;
    if (stoppedOnce) return; // STOP 한번만
    stoppedOnce = true;

    running = false;
    if (rafId) cancelAnimationFrame(rafId);

    // STOP 이후 정지 화면 유지 (display는 그대로)
    stopBtn.disabled = true;      // ✅ STOP 누르면 비활성화
    stopBtn.style.opacity = "0.55";

    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    // 쿼리 파라미터 t= 로 전달 → 파이썬이 판정 + 메시지 표시
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
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"  # direct / 12 / 16
if "mbti" not in st.session_state: st.session_state.mbti = "ENFP"

# 미니게임 상태
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "last_time" not in st.session_state: st.session_state.last_time = None
if "game_result" not in st.session_state: st.session_state.game_result = None  # "win"/"fail"/None
if "winner_form_open" not in st.session_state: st.session_state.winner_form_open = False

# 실패 시 상담신청 영역 on/off
if "consult_enabled" not in st.session_state: st.session_state.consult_enabled = False

# 상담신청 폼 입력
if "consult_name" not in st.session_state: st.session_state.consult_name = ""
if "consult_phone" not in st.session_state: st.session_state.consult_phone = ""
if "consult_product" not in st.session_state: st.session_state.consult_product = "정수기"

# =========================================================
# 13) Query param 처리: shared=1 / t=기록 / view=result(새창)
# =========================================================
qp = get_query_params()

# 공유 보너스(1회 추가)
shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"
if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        st.session_state.max_attempts = 2
        safe_toast("공유 확인! 미니게임 1회 추가 지급 🎁")
    # shared 파라미터 제거
    try:
        qp2 = get_query_params()
        qp2.pop("shared", None)
        set_query_params(qp2)
    except Exception:
        pass

# 스톱 시간 수신
t_val = qp.get("t", None)
if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None
if t_val is not None:
    try:
        st.session_state.last_time = float(str(t_val).strip())
    except Exception:
        st.session_state.last_time = None
    # t 파라미터 제거
    try:
        qp2 = get_query_params()
        qp2.pop("t", None)
        set_query_params(qp2)
    except Exception:
        pass

# =========================================================
# 14) 새창 결과 보기: view=result&name=...&y=...&m=...&d=...&mbti=...
# =========================================================
def build_result_url(name, y, m, d, mbti):
    # name은 urlencoding
    params = {
        "view": "result",
        "name": quote(name or ""),
        "y": str(y),
        "m": str(m),
        "d": str(d),
        "mbti": mbti
    }
    # 앱 URL에 쿼리 붙이기
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{APP_URL}?{query}"

def read_result_params():
    qp = get_query_params()
    if qp.get("view") != "result":
        return None
    try:
        name = qp.get("name", "")
        if isinstance(name, list): name = name[0] if name else ""
        name = unquote(name)

        y = qp.get("y", "")
        m = qp.get("m", "")
        d = qp.get("d", "")
        mbti = qp.get("mbti", "ENFP")
        if isinstance(y, list): y = y[0]
        if isinstance(m, list): m = m[0]
        if isinstance(d, list): d = d[0]
        if isinstance(mbti, list): mbti = mbti[0]

        y = int(y); m = int(m); d = int(d)
        if mbti not in MBTI_LIST:
            mbti = "ENFP"
        return {"name": name, "y": y, "m": m, "d": d, "mbti": mbti}
    except Exception:
        return None

# =========================================================
# 15) Tarot (이미지 카드형)
#    - assets/tarot/majors/ 파일이 있으면 랜덤으로 표시
# =========================================================
TAROT_MAJOR_FILES = [
    ("00_the_fool.png", "The Fool"),
    ("01_the_magician.png", "The Magician"),
    ("02_the_high_priestess.png", "The High Priestess"),
    ("03_the_empress.png", "The Empress"),
    ("04_the_emperor.png", "The Emperor"),
    ("05_the_hierophant.png", "The Hierophant"),
    ("06_the_lovers.png", "The Lovers"),
    ("07_the_chariot.png", "The Chariot"),
    ("08_strength.png", "Strength"),
    ("09_the_hermit.png", "The Hermit"),
    ("10_wheel_of_fortune.png", "Wheel of Fortune"),
    ("11_justice.png", "Justice"),
    ("12_death.png", "Death"),
    ("21_the_world.png", "The World"),
    ("19_the_sun.png", "The Sun"),
    ("18_the_moon.png", "The Moon"),
    ("17_the_star.png", "The Star"),
]

TAROT_MEANING_KO = {
    "The Sun": "행복, 성공, 긍정 에너지",
    "The Moon": "불안, 환상, 직감",
    "The Star": "희망, 영감, 치유",
    "Strength": "용기, 인내, 부드러운 통제",
    "The Fool": "새로운 시작, 모험, 순수",
    "The Magician": "집중, 실현, 능력 발휘",
    "The High Priestess": "직감, 내면의 목소리",
    "The Empress": "풍요, 사랑, 창작",
    "The Emperor": "안정, 구조, 권위",
    "The Lovers": "사랑, 조화, 선택",
    "The Chariot": "승리, 의지, 방향",
    "Justice": "공정, 균형, 진실",
    "The Hermit": "내면 탐구, 지혜",
    "Death": "변화, 끝과 시작, 재생",
    "Wheel of Fortune": "변화, 운, 사이클",
    "The World": "완성, 성취",
}

def pick_tarot_card():
    # 파일이 없으면 텍스트만이라도 보여줌
    choice = random.choice(TAROT_MAJOR_FILES)
    fname, eng = choice
    meaning = TAROT_MEANING_KO.get(eng, "오늘의 메시지를 믿고 한 걸음!")
    path = os.path.join("assets", "tarot", "majors", fname)
    return path, eng, meaning

# =========================================================
# 16) 화면 렌더
# =========================================================
def render_input_screen():
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세</p>
      <p class="hero-sub">완전 무료</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    # DB 상태 표시 (초보용: 문제 숨기지 말고 원인 보여주기)
    if DB_ERR:
        st.error(f"DB 로딩 오류: {DB_ERR}")
        st.info("✅ 해결: fortunes_ko.json을 app.py와 같은 위치(루트) 또는 data/ 폴더에 업로드하세요.")
        st.stop()
    else:
        st.caption("DB 로딩 정상 ✅")

    st.session_state.name = st.text_input("이름 입력 (결과에 표시돼요)", value=st.session_state.name)

    st.markdown(f"<div class='card'><b>생년월일 입력</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.y = c1.number_input("년", 1900, 2030, st.session_state.y, 1)
    st.session_state.m = c2.number_input("월", 1, 12, st.session_state.m, 1)
    st.session_state.d = c3.number_input("일", 1, 31, st.session_state.d, 1)

    st.markdown(f"<div class='card'><b>MBTI를 어떻게 할까요?</b></div>", unsafe_allow_html=True)

    mode = st.radio(
        "",
        ["직접 선택", "간단 테스트 (12문항)", "상세 테스트 (16문항)"],
        index=0 if st.session_state.mbti_mode == "direct" else (1 if st.session_state.mbti_mode == "12" else 2),
        horizontal=True
    )
    if mode == "직접 선택":
        st.session_state.mbti_mode = "direct"
    elif mode == "간단 테스트 (12문항)":
        st.session_state.mbti_mode = "12"
    else:
        st.session_state.mbti_mode = "16"

    if st.session_state.mbti_mode == "direct":
        idx = MBTI_LIST.index(st.session_state.mbti) if st.session_state.mbti in MBTI_LIST else MBTI_LIST.index("ENFP")
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=idx)

    else:
        questions = MBTI_12[:] if st.session_state.mbti_mode == "12" else (MBTI_12[:] + MBTI_16_EXTRA[:])
        st.markdown("<div class='card'><b>문항에 답하면 제출 즉시 MBTI가 확정됩니다.</b></div>", unsafe_allow_html=True)

        answers = []
        for i, (axis, left, right) in enumerate(questions, start=1):
            pick = st.radio(f"{i}.", [left, right], key=f"q_{st.session_state.mbti_mode}_{i}")
            answers.append((axis, pick == left))

        if st.button("제출하고 MBTI 확정", use_container_width=True):
            st.session_state.mbti = compute_mbti(answers)
            st.success(f"확정 MBTI: {st.session_state.mbti}")

    # 결과보기 버튼 (새창)
    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("2026년 운세 보기!", use_container_width=True):
        # 입력값을 쿼리로 만들고 새창으로 오픈
        name = (st.session_state.name or "").strip()
        y, m, d = st.session_state.y, st.session_state.m, st.session_state.d
        mbti = st.session_state.mbti or "ENFP"
        url = build_result_url(name, y, m, d, mbti)

        st.components.v1.html(
            f"""
<script>
(function() {{
  const url = {json.dumps(url, ensure_ascii=False)};
  window.open(url, "_blank");
}})();
</script>
""",
            height=0
        )
        st.info("✅ 결과를 새창으로 열었습니다. (팝업 차단이면 팝업 허용 필요)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 전체초기화 버튼은 삭제(요청)
    st.caption(APP_URL)

def render_result_screen(params):
    # params from query: {name,y,m,d,mbti}
    name = (params.get("name") or "").strip()
    y, m, d = int(params["y"]), int(params["m"]), int(params["d"])
    mbti = params.get("mbti", "ENFP")
    if mbti not in MBTI_LIST:
        mbti = "ENFP"

    # 날짜 유효성
    try:
        datetime(y, m, d)
    except Exception:
        st.error("생년월일이 올바르지 않습니다.")
        st.stop()

    if DB_ERR:
        st.error(f"DB 로딩 오류: {DB_ERR}")
        st.stop()

    combo_key = get_combo_key(y, mbti)
    result, err = pick_from_db(FORTUNE_DB, combo_key, y, m, d)
    if err:
        st.error(err)
        st.info("✅ 해결: fortunes_ko.json combos에 해당 키(예: 닭_ENFP)가 있는지 확인")
        st.stop()

    z = ZODIAC_LABEL_KO[zodiac_key_from_year(y)]
    display_name = f"{name}님" if name else ""
    title_line = f"{display_name} 2026년 운세" if display_name else "2026년 운세"

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{title_line}</p>
      <p class="hero-sub">{z}띠 · {mbti}</p>
      <span class="badge">RESULT</span>
    </div>
    """, unsafe_allow_html=True)

    # 결과 카드(가독성+고급 그라데이션)
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown(f"**띠 운세**: {result.get('zodiac','')}")
    st.markdown(f"**MBTI 특징**: {result.get('mbti_trait','')}")
    st.markdown(f"**사주 한 마디**: {result.get('saju','')}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**오늘 운세**: {result.get('today','')}")
    st.markdown(f"**내일 운세**: {result.get('tomorrow','')}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**2026 전체 운세**: {result.get('year','')}")
    st.markdown(f"**조합 조언**: {result.get('advice','')}")
    st.markdown("</div>", unsafe_allow_html=True)

    # 오늘의 액션팁(메모앱 문구 같은거 나오면 DB 수정 대상이었음 → 지금은 DB 기반)
    if result.get("action_tip"):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"**오늘의 액션팁**: {result['action_tip']}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ✅ 결과 카드 바로 밑: 친구에게 공유하기 버튼 (요청)
    share_button_native_only("친구에게 공유하기")
    st.caption("버튼을 누르면 ‘갤러리에서 공유’처럼 시스템 공유창이 뜹니다. 공유 성공 시 미니게임 1회 추가!")

    # ✅ 광고 (미니게임 바로 위 + 한국어 전용)
    st.markdown(f"""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">{AD_TITLE}</div>
      <div style="margin-top:6px;">{AD_BODY}</div>
      <div style="margin-top:10px;">
        <a href="{AD_URL}" target="_blank"
           style="display:inline-block;background:#ff8c50;color:white;
           padding:10px 16px;border-radius:999px;font-weight:900;text-decoration:none;">
          상담신청하기
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================
    # 미니게임 (한국어 전용 / 선착순 20 / 20.260~20.269 성공)
    # 규칙:
    # - 기본 1회
    # - 공유 성공하면 1회 추가 (총 2회)
    # - STOP하면 시간 정지 유지 + 자동 판정
    # - 성공: 이름/전화 입력 폼 → 저장
    # - 실패: "친구 공유 후 재도전" 또는 "상담신청 O 선택 시 응모" / X는 저장 안함
    # =========================================================
    st.markdown("<div class='minibox'>", unsafe_allow_html=True)
    st.markdown("### 🎁 미니게임: 선착순 20명 커피쿠폰 도전!")
    st.markdown(
        "<div class='soft-box'>"
        "스톱워치를 <b>20.26초</b>에 맞추면 당첨!<br>"
        "- 성공 구간: <b>20.260 ~ 20.269초</b><br>"
        "- 기본 1회, <b>친구에게 공유하기</b> 성공 시 1회 추가<br>"
        "- 선착순으로 커피 쿠폰 지급되며 조기종료 될 수 있습니다"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    ws, ws_err = get_sheet()
    if ws is None:
        st.warning(f"구글시트 연동이 아직 안 되어 있어요: {ws_err}")
    else:
        st.success("구글시트 연동 완료 ✅")

    # 마감 체크
    closed = False
    if ws is not None:
        try:
            closed = (count_winners(ws) >= 20)
        except Exception:
            closed = False
    if closed:
        st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
        st.stop()

    tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    st.markdown(f"<div class='small-note'>남은 시도: <b>{tries_left}</b> / {st.session_state.max_attempts}</div>", unsafe_allow_html=True)

    # STOP으로 받은 시간(last_time) 판정
    if st.session_state.last_time is not None:
        # 한 번 STOP하면 1회 소모
        if st.session_state.game_result is None:
            st.session_state.attempts_used += 1

            sec = float(st.session_state.last_time)
            if 20.260 <= sec <= 20.269:
                st.session_state.game_result = "win"
                st.session_state.winner_form_open = True
                st.session_state.consult_enabled = False  # 성공자는 상담 off
            else:
                st.session_state.game_result = "fail"
                st.session_state.consult_enabled = True   # 실패자는 상담 on

    # 게임 UI
    tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    if tries_left <= 0 and st.session_state.game_result is None:
        st.info("남은 시도가 없습니다. 공유 후 1회 추가를 노려보세요.")
    else:
        # 스톱워치 렌더 (tries_left==0이면 자동 비활성화)
        stopwatch_component(tries_left)

    # 결과 메시지
    if st.session_state.game_result == "win":
        st.success("성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.")
    elif st.session_state.game_result == "fail":
        st.info(f"실패! 실제 스톱시간: {st.session_state.last_time:.3f}초")
        st.warning("친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.")

    # --------------------
    # 성공자 입력 폼 (이름/전화 + 중복방지 + 저장)
    # --------------------
    if st.session_state.winner_form_open:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎉 당첨! 정보 입력")
        win_sec = float(st.session_state.last_time or 0.0)
        st.markdown(f"**기록:** {win_sec:.3f}s")

        nm = st.text_input("이름", value=(name or ""), key="win_name")
        ph = st.text_input("연락처", value="", key="win_phone")
        consent = st.checkbox(
            "개인정보처리방침 동의(필수)\n\n이벤트 경품 발송을 위해 이름/전화번호를 수집하며 목적 달성 후 지체 없이 파기합니다. 동의 거부 시 참여가 제한됩니다.",
            value=False,
            key="win_consent"
        )

        if st.button("신청완료", use_container_width=True):
            if ws is None:
                st.error("구글시트 연결이 필요합니다.")
            elif not consent:
                st.warning("동의가 필요합니다.")
            else:
                ph_norm = normalize_phone(ph)
                if nm.strip() == "" or ph_norm == "":
                    st.warning("이름/연락처를 정확히 입력해주세요.")
                else:
                    try:
                        if phone_exists(ws, ph_norm):
                            st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                        else:
                            if count_winners(ws) >= 20:
                                st.info("이벤트가 종료되었습니다. (선착순 20명 마감)")
                            else:
                                append_row(
                                    ws,
                                    nm.strip(),
                                    ph_norm,
                                    "커피쿠폰(게임당첨)",
                                    float(win_sec),
                                    st.session_state.shared,
                                    "X"  # 상담신청 X
                                )
                                st.success("접수 완료! 커피쿠폰 발송 대상에 등록되었습니다.")
                                st.session_state.winner_form_open = False
                    except Exception as e:
                        st.error(f"저장 중 오류: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------
    # 실패자: 상담신청 O/X (O이면 시트에 저장 + 응모 문구, X이면 저장 안 함)
    # --------------------
    if st.session_state.consult_enabled and st.session_state.game_result == "fail":
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📞 다나눔렌탈 상담신청 (실패자 응모 옵션)")
        st.caption("O 선택 후 이름/연락처 입력 + 동의하면 응모 처리됩니다. X 선택 시 저장하지 않습니다.")

        product = st.selectbox("상담 품목", ["정수기", "안마의자", "기타가전"], index=0, key="consult_product")
        c_nm = st.text_input("이름", value=(name or ""), key="consult_name")
        c_ph = st.text_input("연락처", value="", key="consult_phone")
        c_consent = st.checkbox(
            "개인정보처리방침 동의(필수)\n\n상담 진행 및 이벤트 응모 처리를 위해 이름/전화번호를 수집합니다.",
            value=False,
            key="consult_consent"
        )

        ox = st.radio("상담신청 여부", ["O", "X"], horizontal=True, key="consult_ox")

        if st.button("상담신청 완료", use_container_width=True):
            if ox == "X":
                st.info("X 선택: 저장하지 않습니다.")
            else:
                # O
                if ws is None:
                    st.error("구글시트 연결이 필요합니다.")
                elif not c_consent:
                    st.warning("동의가 필요합니다.")
                else:
                    ph_norm = normalize_phone(c_ph)
                    if c_nm.strip() == "" or ph_norm == "":
                        st.warning("이름/연락처를 정확히 입력해주세요.")
                    else:
                        try:
                            # 실패 시에도 중복은 막음
                            if phone_exists(ws, ph_norm):
                                st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                            else:
                                append_row(
                                    ws,
                                    c_nm.strip(),
                                    ph_norm,
                                    product,
                                    float(st.session_state.last_time or 0.0),
                                    st.session_state.shared,
                                    "O"
                                )
                                st.success("커피쿠폰 응모 처리되었습니다.")
                                # 상담 한번 했으면 무한 저장 방지: 더 이상 상담 영역 off
                                st.session_state.consult_enabled = False
                        except Exception as e:
                            st.error(f"저장 중 오류: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # 타로 카드 (이미지 카드형)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if st.button("오늘의 타로 카드 뽑기", use_container_width=True):
        img_path, eng, meaning = pick_tarot_card()
        st.markdown("### 🃏 오늘의 타로 카드")
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        st.markdown(f"**{eng}**")
        st.markdown(f"<div class='soft-box'>{meaning}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 새로고침/재시도 시 last_time 처리로 반복 소모되는 것을 막기 위해:
    # last_time은 화면에서만 쓰고 다음 판정에 영향 없게 종료 시 None으로 초기화
    # (단, 결과 메시지/폼을 위해 화면에 남겨야 하므로 여기서 초기화하면 안 됨)

    st.caption(APP_URL)

# =========================================================
# 17) Router
# =========================================================
result_params = read_result_params()

if result_params is None:
    render_input_screen()
else:
    render_result_screen(result_params)
