import streamlit as st
from datetime import datetime
import random
import re
import json
import os

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

# 미니게임 목표 구간
WIN_MIN = 20.260
WIN_MAX = 20.269
MAX_WINNERS = 20

FORTUNE_DB_PATH = os.path.join("data", "fortunes_ko.json")

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

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    description = "2026년 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로까지 무료로! (한국어 미니게임 이벤트 포함)"
    keywords = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, 무료 운세, 타로, 연애운, 재물운, 건강운, 네이버 운세, 구글 운세"
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
t = {
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
    "share_not_supported": "이 기기에서는 시스템 공유가 지원되지 않습니다.",
    "tarot_btn": "오늘의 타로 카드 뽑기",
    "tarot_title": "오늘의 타로 카드",
    "sections": {
        "zodiac": "띠 운세",
        "mbti": "MBTI 특징",
        "mbti_influence": "MBTI가 운세에 미치는 영향",
        "saju": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year_all": "2026 전체 운세",
        "love": "연애운",
        "money": "재물운",
        "work": "일/학업운",
        "health": "건강운",
        "lucky": "행운 포인트",
        "action": "오늘의 실행 팁",
        "caution": "주의할 점",
    },
    "ad_placeholder": "AD (심사 통과 후 이 위치에 광고가 표시됩니다)",
    "ad_kr_title": "정수기렌탈 대박!",
    "ad_kr_body1": "제휴카드면 월 0원부터!",
    "ad_kr_body2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍",
    "ad_kr_link": "다나눔렌탈.com 바로가기",
    "ad_kr_url": "https://www.다나눔렌탈.com",
    "mini_title": "🎁 미니게임: 선착순 20명 커피쿠폰 도전!",
    "mini_desc": f"스톱워치를 **{WIN_MIN:.3f}~{WIN_MAX:.3f}초**에 맞추면 당첨!\n\n- 기본 1회\n- **친구에게 공유하기**를 누르면 1회 추가\n- 목표 구간: **{WIN_MIN:.3f} ~ {WIN_MAX:.3f}초**",
    "mini_try_left": "남은 시도",
    "mini_closed": "이벤트가 종료되었습니다. (선착순 20명 마감)",
    "mini_dup": "이미 참여한 번호입니다. (중복 참여 불가)",
    "sheet_fail": "구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유/탭 이름 확인 필요)",
    "sheet_ok": "구글시트 연결 완료",
    "no_tries_block": "남은 시도가 0이라 START/STOP이 비활성화됩니다.",
    "win_msg": "성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.",
    "lose_msg": "친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.",
    "consult_title": "📩 다나눔렌탈 상담신청 (선택)",
    "consult_q": "상담신청을 하시겠습니까?",
    "consult_o": "O (상담신청하고 커피쿠폰 응모)",
    "consult_x": "X (저장하지 않음)",
    "info_title": "🔎 검색/AI 노출용 정보(FAQ)",
}

# =========================================================
# 5) Tarot (Korean)
# =========================================================
TAROT = [
    ("운명의 수레바퀴", "Wheel of Fortune", "변화, 전환점"),
    ("태양", "The Sun", "행복, 성공, 긍정 에너지"),
    ("힘", "Strength", "용기, 인내"),
    ("세계", "The World", "완성, 성취"),
]

# =========================================================
# 6) Zodiac + MBTI base
# =========================================================
ZODIAC_ORDER = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

def calc_zodiac(year: int) -> str:
    return ZODIAC_ORDER[(year - 4) % 12]

# =========================================================
# 7) MBTI 12/16 Questions (Korean)
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
# 8) Fortune DB Loader (B 방식: fortunes_ko.json)
#    - 없으면 생성하지 않음 (근본원인 제거)
# =========================================================
REQUIRED_TOP_KEYS = [
    "zodiac_fortunes",   # dict: { "쥐띠":[...], ... }
    "mbti_traits",       # dict: { "INTJ":[...], ... }
    "mbti_influences",   # list
    "saju_messages",     # list
    "daily_today",       # list
    "daily_tomorrow",    # list
    "year_2026",         # list
    "love",              # list
    "money",             # list
    "work",              # list
    "health",            # list
    "lucky_colors",      # list
    "lucky_items",       # list
    "lucky_numbers",     # list
    "lucky_directions",  # list
    "action_tips",       # list
    "cautions",          # list
]

def load_fortune_db():
    if not os.path.exists(FORTUNE_DB_PATH):
        st.error(f"데이터 파일이 없습니다: `{FORTUNE_DB_PATH}`\n\n깃허브에 파일을 업로드(커밋)한 뒤 다시 배포하세요.")
        st.stop()

    try:
        with open(FORTUNE_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"데이터 파일을 읽을 수 없습니다: {e}")
        st.stop()

    missing = [k for k in REQUIRED_TOP_KEYS if k not in data]
    if missing:
        st.error("fortunes_ko.json 필수 키가 누락되었습니다.\n\n누락 키:\n- " + "\n- ".join(missing))
        st.stop()

    # zodiac dict에 12띠가 모두 있는지 체크
    z = data["zodiac_fortunes"]
    for zz in ZODIAC_ORDER:
        if zz not in z or not isinstance(z[zz], list) or len(z[zz]) == 0:
            st.error(f"zodiac_fortunes['{zz}'] 가 비어있거나 없습니다.")
            st.stop()

    # mbti dict 체크
    m = data["mbti_traits"]
    for mb in MBTI_LIST:
        if mb not in m or not isinstance(m[mb], list) or len(m[mb]) == 0:
            st.error(f"mbti_traits['{mb}'] 가 비어있거나 없습니다.")
            st.stop()

    return data

FORTUNE_DB = load_fortune_db()

# =========================================================
# 9) Google Sheet (컬럼 고정 + G열 상담신청)
#   A: 시간 | B: 이름 | C: 전화번호 | D: 언어 | E: 기록초 | F: 공유여부 | G: 상담신청(O/X)
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
        if len(row) < 5:
            continue
        try:
            sec = float(row[4])
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

def append_entry(ws, name, phone, lang, seconds, shared_bool, consult_flag):
    ws.append_row([now_str(), name, phone, lang, f"{seconds:.3f}", str(bool(shared_bool)), consult_flag])

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
      await navigator.share({{ title: "2026 운세", text: url, url }});
      // 공유 성공 시 보너스 지급용 파라미터
      const u = new URL(window.location.href);
      u.searchParams.set("shared", "1");
      window.location.href = u.toString();
    }} catch (e) {{
      // 취소 시 아무 것도 안함
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 11) Stopwatch Component
#     - START/STOP 한 번 누르면 해당 시도는 종료
#     - STOP하면 URL에 t, token 넣고 #minigame 해시로 내려오게 함
# =========================================================
def stopwatch_component(tries_left: int):
    disabled = "true" if tries_left <= 0 else "false"

    st.components.v1.html(
        f"""
<div id="minigame_stopwatch" style="
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
    STOP을 누르면 기록이 자동 반영됩니다.
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
  let locked = false; // START/STOP 한 번 쓰면 잠금
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
    if (locked) return;
    locked = true;               // START 누르면 잠금 (같은 시도 내 재시작 방지)
    startBtn.disabled = true;    // START 1회 후 비활성화
    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);
  }});

  stopBtn.addEventListener("click", () => {{
    if (!running) return;
    running = false;
    stopBtn.disabled = true;     // STOP 1회 후 비활성화
    if (rafId) cancelAnimationFrame(rafId);
    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);
    const token = String(Date.now());

    // t/token 저장 + #minigame 로 내려오기
    const u = new URL(window.location.href);
    u.searchParams.set("t", v);
    u.searchParams.set("token", token);
    u.hash = "minigame";
    window.location.href = u.toString();
  }});
}})();
</script>
""",
        height=270
    )

# =========================================================
# 12) Session State
# =========================================================
if "stage" not in st.session_state: st.session_state.stage = "input"

# 입력
if "name" not in st.session_state: st.session_state.name = ""
if "y" not in st.session_state: st.session_state.y = 2005
if "m" not in st.session_state: st.session_state.m = 1
if "d" not in st.session_state: st.session_state.d = 1
if "mbti" not in st.session_state: st.session_state.mbti = None
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"

# 공유/시도 (reset해도 유지)
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0

# 미니게임 결과 상태
if "last_token" not in st.session_state: st.session_state.last_token = None
if "last_time" not in st.session_state: st.session_state.last_time = None
if "game_state" not in st.session_state: st.session_state.game_state = "idle"  # idle/win/lose
if "show_consult" not in st.session_state: st.session_state.show_consult = False
if "consult_choice" not in st.session_state: st.session_state.consult_choice = None

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
# 14) Shared + STOP token 처리
# =========================================================
qp = get_query_params()

# 공유 보너스(shared=1)
shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"

if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        st.session_state.max_attempts = 2
        safe_toast(t["share_bonus_done"])
    clear_param("shared")

# STOP 기록 처리(t + token)
t_val = qp.get("t", None)
token_val = qp.get("token", None)

if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None
if isinstance(token_val, list):
    token_val = token_val[0] if token_val else None

def process_stop_time(elapsed_sec: float, token: str):
    # 중복 처리 방지
    if token and st.session_state.last_token == token:
        return

    st.session_state.last_token = token
    st.session_state.last_time = elapsed_sec

    # 남은 시도 체크
    tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    if tries_left <= 0:
        st.session_state.game_state = "idle"
        return

    # 시도 1회 소모
    st.session_state.attempts_used += 1

    # 승/패 판단
    if WIN_MIN <= elapsed_sec <= WIN_MAX:
        st.session_state.game_state = "win"
        st.session_state.show_consult = False
        st.session_state.consult_choice = None
    else:
        st.session_state.game_state = "lose"
        st.session_state.show_consult = True
        st.session_state.consult_choice = None

# token/t가 있으면 처리
if t_val is not None and token_val is not None:
    try:
        elapsed = float(str(t_val).strip())
        process_stop_time(elapsed, str(token_val))
    except Exception:
        pass
    # 파라미터 제거(새로고침 반복 방지)
    clear_param("t")
    clear_param("token")

# =========================================================
# 15) Fortune Picker (B 방식)
#     - 광범위 데이터에서 seed로 "안정적 랜덤" 선택
# =========================================================
def stable_seed(*parts) -> int:
    s = "|".join([str(p) for p in parts])
    # 파이썬 내장 hash는 런마다 바뀔 수 있어서 고정 해시 사용
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) % 2_000_000_000
    return h

def pick_from_list(arr, seed_int):
    if not arr:
        return ""
    rng = random.Random(seed_int)
    return rng.choice(arr)

def build_fortune(y, m, d, mbti):
    zodiac = calc_zodiac(y)

    # 날짜(오늘/내일)를 안정적으로 뽑기 위해 오늘 기준 seed에 포함
    today_key = datetime.now().strftime("%Y%m%d")

    db = FORTUNE_DB
    seed_base = stable_seed(y, m, d, mbti, zodiac, today_key)

    zodiac_f = pick_from_list(db["zodiac_fortunes"][zodiac], seed_base + 1)
    mbti_t = pick_from_list(db["mbti_traits"][mbti], seed_base + 2)
    mbti_inf = pick_from_list(db["mbti_influences"], seed_base + 3)
    saju = pick_from_list(db["saju_messages"], seed_base + 4)
    today = pick_from_list(db["daily_today"], seed_base + 5)
    tomorrow = pick_from_list(db["daily_tomorrow"], seed_base + 6)
    year_all = pick_from_list(db["year_2026"], seed_base + 7)
    love = pick_from_list(db["love"], seed_base + 8)
    money = pick_from_list(db["money"], seed_base + 9)
    work = pick_from_list(db["work"], seed_base + 10)
    health = pick_from_list(db["health"], seed_base + 11)

    lucky = {
        "color": pick_from_list(db["lucky_colors"], seed_base + 12),
        "item": pick_from_list(db["lucky_items"], seed_base + 13),
        "number": pick_from_list(db["lucky_numbers"], seed_base + 14),
        "direction": pick_from_list(db["lucky_directions"], seed_base + 15),
    }
    action_tip = pick_from_list(db["action_tips"], seed_base + 16)
    caution = pick_from_list(db["cautions"], seed_base + 17)

    return {
        "zodiac": zodiac,
        "zodiac_fortune": zodiac_f,
        "mbti_trait": mbti_t,
        "mbti_influence": mbti_inf,
        "saju": saju,
        "today": today,
        "tomorrow": tomorrow,
        "year_all": year_all,
        "love": love,
        "money": money,
        "work": work,
        "health": health,
        "lucky": lucky,
        "action_tip": action_tip,
        "caution": caution,
    }

# =========================================================
# 16) Reset (시도/공유 유지)
# =========================================================
def reset_input_only_keep_game():
    keep = {
        "shared", "max_attempts", "attempts_used",
        "last_token", "last_time",
        "game_state", "show_consult", "consult_choice"
    }
    snap = dict(st.session_state)
    st.session_state.clear()
    for k, v in snap.items():
        if k in keep:
            st.session_state[k] = v

    st.session_state.stage = "input"
    st.session_state.name = ""
    st.session_state.y = 2005
    st.session_state.m = 1
    st.session_state.d = 1
    st.session_state.mbti = None
    st.session_state.mbti_mode = "direct"

# =========================================================
# 17) UI: MBTI Test
# =========================================================
def render_mbti_test(questions, title: str, key_prefix: str):
    st.markdown(f"<div class='card'><b>{title}</b><br><span style='opacity:0.85;'>각 문항에서 더 가까운 쪽을 선택하세요.</span></div>", unsafe_allow_html=True)
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}. ({axis})", options=[left_txt, right_txt], index=0, key=f"{key_prefix}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button(t["mbti_submit"], use_container_width=True):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 18) Screens
# =========================================================
def render_input():
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">🔮 {t["title"]}</p>
      <p class="hero-sub">{t["subtitle"]}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input(t["name"], value=st.session_state.name)

    st.markdown(f"<div class='card'><b>{t['birth']}</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.y = c1.number_input(t["year"], 1900, 2030, st.session_state.y, 1)
    st.session_state.m = c2.number_input(t["month"], 1, 12, st.session_state.m, 1)
    st.session_state.d = c3.number_input(t["day"], 1, 31, st.session_state.d, 1)

    st.markdown(f"<div class='card'><b>{t['mbti_mode']}</b></div>", unsafe_allow_html=True)
    try:
        mode = st.radio(
            "", [t["mbti_direct"], t["mbti_12"], t["mbti_16"]],
            index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
            horizontal=True
        )
    except TypeError:
        mode = st.radio("", [t["mbti_direct"], t["mbti_12"], t["mbti_16"]],
                        index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2))

    if mode == t["mbti_direct"]:
        st.session_state.mbti_mode = "direct"
    elif mode == t["mbti_12"]:
        st.session_state.mbti_mode = "12"
    else:
        st.session_state.mbti_mode = "16"

    if st.session_state.mbti_mode == "direct":
        idx = MBTI_LIST.index(st.session_state.mbti) if st.session_state.mbti in MBTI_LIST else MBTI_LIST.index("ENFP")
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=idx)

    elif st.session_state.mbti_mode == "12":
        done = render_mbti_test(MBTI_Q_12, "MBTI 12문항 (각 축 3문항)", "q12")
        if done:
            st.success(f"MBTI: {st.session_state.mbti}")

    else:
        questions = MBTI_Q_12 + MBTI_Q_16_EXTRA
        done = render_mbti_test(questions, "MBTI 16문항 (각 축 4문항)", "q16")
        if done:
            st.success(f"MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button(t["go_result"], use_container_width=True):
        if not st.session_state.mbti:
            st.session_state.mbti = "ENFP"
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_result():
    s = t["sections"]
    y, m, d = st.session_state.y, st.session_state.m, st.session_state.d
    mbti = st.session_state.mbti or "ENFP"
    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    fortune = build_fortune(y, m, d, mbti)

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{fortune['zodiac']} · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    # 결과 본문 (HTML 태그로 깨져 보이던 문제 → st.markdown 기본 사용)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['zodiac']}**: {fortune['zodiac_fortune']}")
    st.markdown(f"**{s['mbti']}**: {fortune['mbti_trait']}")
    st.markdown(f"**{s['mbti_influence']}**: {fortune['mbti_influence']}")
    st.markdown(f"**{s['saju']}**: {fortune['saju']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['today']}**: {fortune['today']}")
    st.markdown(f"**{s['tomorrow']}**: {fortune['tomorrow']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['year_all']}**: {fortune['year_all']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['love']}**: {fortune['love']}")
    st.markdown(f"**{s['money']}**: {fortune['money']}")
    st.markdown(f"**{s['work']}**: {fortune['work']}")
    st.markdown(f"**{s['health']}**: {fortune['health']}")
    st.markdown("</div>", unsafe_allow_html=True)

    lucky = fortune["lucky"]
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['lucky']}**")
    st.markdown(f"- 컬러: **{lucky['color']}**")
    st.markdown(f"- 아이템: **{lucky['item']}**")
    st.markdown(f"- 숫자: **{lucky['number']}**")
    st.markdown(f"- 방향: **{lucky['direction']}**")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['action']}**: {fortune['action_tip']}")
    st.markdown(f"**{s['caution']}**: {fortune['caution']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tarot ----
    if st.button(t["tarot_btn"], use_container_width=True):
        local, eng, meaning = random.choice(TAROT)
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900;color:#6b4fd6;">{t["tarot_title"]}</div>
          <div style="font-size:1.45rem;font-weight:900;margin-top:6px;">{local}</div>
          <div style="opacity:0.75;margin-top:2px;">{eng}</div>
          <div style="margin-top:10px;" class="soft-box">{meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Share (시스템 공유창만) ----
    share_button_native_only(t["share_link_btn"], t["share_not_supported"])
    st.caption(t["share_link_hint"])

    # ---- 광고 위치: 미니게임 바로 위 ----
    st.markdown(f"<div class='adplaceholder'>{t['ad_placeholder']}</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">{t["ad_kr_title"]}</div>
      <div style="margin-top:6px;">{t["ad_kr_body1"]}</div>
      <div>{t["ad_kr_body2"]}</div>
      <div style="margin-top:10px;">
        <a href="{t["ad_kr_url"]}" target="_blank"
           style="display:inline-block;background:#ff8c50;color:white;
           padding:10px 16px;border-radius:999px;font-weight:900;text-decoration:none;">
          {t["ad_kr_link"]}
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # 미니게임 (한국어만) + 기록제출 버튼 제거
    # =====================================================
    st.markdown(f"<a id='minigame'></a>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='card'><div style='font-weight:900;font-size:1.2rem;'>{t['mini_title']}</div>"
        f"<div style='margin-top:8px;' class='soft-box'>{t['mini_desc']}</div></div>",
        unsafe_allow_html=True
    )

    ws = get_sheet()
    sheet_ready = ws is not None
    if not sheet_ready:
        st.warning(t["sheet_fail"])
    else:
        st.success(t["sheet_ok"])

    closed = False
    if sheet_ready:
        try:
            closed = (count_winners(ws) >= MAX_WINNERS)
        except Exception:
            closed = False

    tries_left = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    st.markdown(
        f"<div class='small-note'>{t['mini_try_left']}: <b>{tries_left}</b> / {st.session_state.max_attempts}</div>",
        unsafe_allow_html=True
    )

    if tries_left <= 0:
        st.info(t["no_tries_block"])

    if closed:
        st.info(t["mini_closed"])
    else:
        # 스톱워치: 남은 시도 0이면 비활성화
        stopwatch_component(tries_left)

        # STOP 기록이 있으면 표시 (자동반영 + 그대로 남음)
        if st.session_state.last_time is not None:
            st.markdown(
                f"<div class='card'><b>기록</b>: {st.session_state.last_time:.3f}s</div>",
                unsafe_allow_html=True
            )

        # 승/패 메시지 + 상담신청 로직
        if st.session_state.game_state == "win":
            st.success(t["win_msg"])
            # 성공 시 상담신청 기능 OFF
            st.session_state.show_consult = False

            # 당첨자는 정보 저장(이름/전화번호)
            if sheet_ready:
                with st.expander("🎉 당첨자 정보 입력 (커피쿠폰 발송용)", expanded=True):
                    nm = st.text_input("이름", value=(st.session_state.name or "").strip(), key="win_nm")
                    ph = st.text_input("전화번호", value="", key="win_ph")
                    ph_norm = normalize_phone(ph)
                    consent = st.checkbox(
                        "개인정보 수집·이용 동의(필수)\n\n이벤트 경품 발송을 위해 이름/전화번호를 수집하며, 목적 달성 후 지체 없이 파기합니다. 동의 거부 시 참여가 제한됩니다.",
                        value=False,
                        key="win_consent"
                    )

                    if st.button("제출", use_container_width=True, key="win_submit_btn"):
                        if not consent:
                            st.warning("동의가 필요합니다.")
                        elif nm.strip() == "" or ph_norm == "":
                            st.warning("이름/전화번호를 정확히 입력해주세요.")
                        else:
                            try:
                                if phone_exists(ws, ph_norm):
                                    st.warning(t["mini_dup"])
                                else:
                                    if count_winners(ws) >= MAX_WINNERS:
                                        st.info(t["mini_closed"])
                                    else:
                                        append_entry(
                                            ws,
                                            nm.strip(),
                                            ph_norm,
                                            "ko",
                                            float(st.session_state.last_time),
                                            st.session_state.shared,
                                            "X"  # 당첨자는 상담신청 X로 고정(요청사항: 성공자는 상담신청 off)
                                        )
                                        st.success("접수 완료! 커피쿠폰 발송 대상에 등록되었습니다.")
                            except Exception as e:
                                st.error(f"저장 중 오류: {e}")

        elif st.session_state.game_state == "lose":
            st.info(t["lose_msg"])

            # 실패한 사람은 상담신청 ON
            st.markdown(f"<div class='card'><b>{t['consult_title']}</b></div>", unsafe_allow_html=True)
            choice = st.radio(
                t["consult_q"],
                [t["consult_o"], t["consult_x"]],
                index=1,
                key="consult_radio"
            )

            if choice == t["consult_o"]:
                # O 선택 시에만 정보 입력 + 저장
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("상담신청(O) 선택 시, 커피쿠폰 응모를 위해 아래 정보를 입력해주세요.")
                nm = st.text_input("이름", value=(st.session_state.name or "").strip(), key="lose_nm")
                ph = st.text_input("전화번호", value="", key="lose_ph")
                ph_norm = normalize_phone(ph)
                consent = st.checkbox(
                    "개인정보 수집·이용 동의(필수)\n\n상담 및 이벤트 안내를 위해 이름/전화번호를 수집하며, 목적 달성 후 지체 없이 파기합니다. 동의 거부 시 저장되지 않습니다.",
                    value=False,
                    key="lose_consent"
                )

                if st.button("상담신청(O) 저장", use_container_width=True, key="lose_save_btn"):
                    if not sheet_ready:
                        st.error(t["sheet_fail"])
                    elif not consent:
                        st.warning("동의가 필요합니다.")
                    elif nm.strip() == "" or ph_norm == "":
                        st.warning("이름/전화번호를 정확히 입력해주세요.")
                    else:
                        try:
                            # 실패자는 중복참여 방지 여부를 엄격 적용할지 애매하지만,
                            # 요청이 '중복 참여 방지'가 있으므로 동일 폰 중복 저장 방지
                            if phone_exists(ws, ph_norm):
                                st.warning(t["mini_dup"])
                            else:
                                append_entry(
                                    ws,
                                    nm.strip(),
                                    ph_norm,
                                    "ko",
                                    float(st.session_state.last_time or 0.0),
                                    st.session_state.shared,
                                    "O"  # G열 상담신청 O
                                )
                                st.success("저장 완료! 상담신청이 접수되었습니다.")
                        except Exception as e:
                            st.error(f"저장 중 오류: {e}")
                st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.caption("X 선택 시 저장하지 않습니다.")

    # ---- 검색/AI 노출 섹션(요청 복구) ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {t['info_title']}")
    st.markdown("- **2026 운세/띠운세/MBTI 운세/사주/오늘운세/내일운세/타로**를 무료로 제공합니다.")
    st.markdown("- MBTI 성향을 반영해 **연애·재물·일/학업·건강** 조언을 제공합니다.")
    st.markdown("- 한국어 화면에는 **선착순 20명 커피쿠폰 미니게임**(구글시트 저장)이 포함됩니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- reset: 입력/결과만 초기화 (시도/공유 유지) ----
    if st.button(t["reset"], use_container_width=True):
        reset_input_only_keep_game()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 19) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
