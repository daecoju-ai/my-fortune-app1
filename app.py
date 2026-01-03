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

DATA_DIR = "data"
FORTUNE_DB_PATHS = [
    os.path.join(DATA_DIR, "fortune_db.json"),
    os.path.join(DATA_DIR, "fortune-db.json"),
    os.path.join(DATA_DIR, "fortune_db_v1.json"),
]

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

def inject_seo_ko_only():
    description = "2026년 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로까지 무료로! (한국어 미니게임 이벤트 포함)"
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

def safe_text(s):
    """결과 텍스트에서 태그가 보이는 문제를 막기 위해,
    HTML로 렌더링되는 곳(unsafe_allow_html)에는 절대 데이터 본문을 넣지 않는다.
    """
    if s is None:
        return ""
    return str(s)

# =========================================================
# 2) Text (한국어 고정)
# =========================================================
T = {
    "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
    "subtitle": "완전 무료",
    "name": "이름 입력 (결과에 표시돼요)",
    "birth": "생년월일 입력",
    "year": "년", "month": "월", "day": "일",
    "mbti_mode": "MBTI를 어떻게 할까요?",
    "mbti_direct": "MBTI 아는 사람 (직접 선택)",
    "mbti_12": "간단 테스트 (12문항)",
    "mbti_16": "상세 테스트 (16문항)",
    "mbti_submit": "제출하고 MBTI 확정",
    "go_result": "2026년 운세 보기!",
    "reset": "처음부터 다시하기",
    "share_link_btn": "🔗 링크 공유하기",
    "share_link_hint": "버튼을 누르면 ‘링크 공유’ 창이 뜹니다.",
    "share_bonus_done": "공유 확인! 미니게임 1회 추가 지급 🎁",
    "tarot_btn": "오늘의 타로 카드 뽑기",
    "tarot_title": "오늘의 타로 카드",
    "sections": {
        "zodiac": "띠 운세",
        "mbti_trait": "MBTI 특징",
        "mbti_influence": "MBTI 영향",
        "saju": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year_all": "2026 전체 운세",
        "love": "연애운 조언",
        "money": "재물운 조언",
        "work": "직장/일 조언",
        "health": "건강운 조언",
        "lucky": "행운 포인트",
        "action": "오늘의 액션팁",
        "caution": "주의할 점",
    },
    "ad_placeholder": "AD (심사 통과 후 이 위치에 광고가 표시됩니다)",
    "ad_kr_title": "정수기렌탈 대박!",
    "ad_kr_body1": "제휴카드면 월 0원부터!",
    "ad_kr_body2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍",
    "ad_kr_link": "다나눔렌탈.com 바로가기",
    "ad_kr_url": "https://www.다나눔렌탈.com",
    "mini_title": "🎁 미니게임: 선착순 20명 커피쿠폰 도전!",
    "mini_desc": "스톱워치를 **20.16초**에 맞추면 당첨!\n\n- 기본 1회\n- **링크 공유하기**를 누르면 1회 추가\n- 목표 구간: **20.160 ~ 20.169초**",
    "mini_try_left": "남은 시도",
    "mini_closed": "이벤트가 종료되었습니다. (선착순 20명 마감)",
    "mini_dup": "이미 참여한 번호입니다. (중복 참여 불가)",
    "win_title": "🎉 당첨! 정보 입력",
    "win_name": "이름",
    "win_phone": "전화번호",
    "win_consent": "개인정보 수집·이용 동의(필수)",
    "win_consent_text": "이벤트 경품 발송을 위해 이름/전화번호를 수집하며, 목적 달성 후 지체 없이 파기합니다. 동의 거부 시 참여가 제한됩니다.",
    "win_submit": "제출",
    "win_thanks": "접수 완료! 커피쿠폰 발송 대상에 등록되었습니다.",
    "sheet_fail": "구글시트 연결이 필요합니다. (Secrets/requirements/시트 공유/탭 이름 확인)",
    "sheet_ok": "구글시트 연결 완료",
    "faq_title": "🔎 검색/AI 노출용 정보(FAQ)",
    "stopwatch_note": "START 후 STOP을 누르면 자동으로 기록이 확정됩니다. (기록 제출 버튼 없음)",
    "mbti_test_12_title": "MBTI 12문항 (각 축 3문항)",
    "mbti_test_16_title": "MBTI 16문항 (각 축 4문항)",
    "mbti_test_help": "각 문항에서 더 가까운 쪽을 선택하세요.",
    "try_over": "남은 시도가 없습니다.",
    "miss": "아쉽게도 미달/초과! 다음 기회에 🙂",
    "share_not_supported": "이 기기에서는 시스템 공유가 지원되지 않습니다.",
    "no_tries_block": "남은 시도가 0이라 START/STOP이 비활성화됩니다.",
    "db_fail_title": "데이터 로드 실패",
    "db_fail_desc": "fortune_db.json을 읽지 못해 결과를 만들 수 없습니다. (임시 생성 없이 중단)",
}

# =========================================================
# 3) Tarot (한국어만)
# =========================================================
TAROT = [
    ("운명의 수레바퀴", "변화, 전환점"),
    ("태양", "행복, 성공, 긍정 에너지"),
    ("힘", "용기, 인내"),
    ("세계", "완성, 성취"),
]

def pick_tarot():
    return random.choice(TAROT)

# =========================================================
# 4) MBTI 12/16 Questions (한국어 고정)
# =========================================================
MBTI_Q_12 = [
    ("EI", "사람들과 있을 때 에너지가 더 생긴다", "혼자 있을 때 에너지가 더 생긴다"),
    ("SN", "현실적인 정보가 편하다", "가능성/아이디어가 편하다"),
    ("TF", "결정은 논리/원칙이 우선", "결정은 사람/상황 배려가 우선"),
    ("JP", "계획대로 진행해야 마음이 편하다", "유연하게 바뀌어도 괜찮다"),
    ("EI", "말하며 생각이 정리된다", "생각한 뒤 말하는 편이다"),
    ("SN", "경험/사실을 믿는 편", "직감/영감을 믿는 편"),
    ("TF", "피드백은 직설이 낫다", "피드백은 부드럽게가 낫다"),
    ("JP", "마감 전에 미리 끝내는 편", "마감 직전에 몰아서 하는 편"),
    ("EI", "주말엔 약속이 있으면 좋다", "주말엔 혼자 쉬고 싶다"),
    ("SN", "설명은 구체적으로", "설명은 큰그림으로"),
    ("TF", "갈등은 원인/해결이 우선", "갈등은 감정/관계가 우선"),
    ("JP", "정리/정돈이 잘 되어야 편하다", "어수선해도 일단 진행 가능"),
]

MBTI_Q_16_EXTRA = [
    ("EI", "새로운 사람을 만나면 설렌다", "새로운 사람은 적응 시간이 필요"),
    ("SN", "지금 필요한 현실이 중요", "미래 가능성이 더 중요"),
    ("TF", "공정함이 최우선", "조화로움이 최우선"),
    ("JP", "일정이 확정되어야 안심", "상황에 따라 바뀌는 게 자연스러움"),
]

MBTI_DESC_KO = {
    "INTJ":"전략가 · 목표지향","INTP":"아이디어 · 분석가","ENTJ":"리더 · 추진력","ENTP":"토론가 · 발상가",
    "INFJ":"통찰 · 조언자","INFP":"가치 · 감성","ENFJ":"조율 · 리더","ENFP":"열정 · 아이디어",
    "ISTJ":"원칙 · 책임","ISFJ":"배려 · 헌신","ESTJ":"관리자 · 현실","ESFJ":"분위기 · 케어",
    "ISTP":"장인 · 문제해결","ISFP":"감성 · 힐러","ESTP":"모험 · 실행","ESFP":"사교 · 즐거움",
}
MBTI_LIST = sorted(MBTI_DESC_KO.keys())

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
    return mbti if mbti in MBTI_DESC_KO else default

def render_mbti_test(questions, title: str, key_prefix: str):
    st.markdown(f"<div class='card'><b>{title}</b><br><span style='opacity:0.85;'>{T['mbti_test_help']}</span></div>", unsafe_allow_html=True)
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}. {axis}", options=[left_txt, right_txt], index=0, key=f"{key_prefix}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button(T["mbti_submit"], use_container_width=True):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 5) Zodiac (한국어 고정)
# =========================================================
ZODIAC_ORDER = ["쥐","소","호랑이","토끼","용","뱀","말","양","원숭이","닭","개","돼지"]

def calc_zodiac_ko(year: int) -> str:
    idx = (year - 4) % 12
    return ZODIAC_ORDER[idx]

# =========================================================
# 6) Fortune DB Loader (근본 원인 제거: 생성/대체 없음)
# =========================================================
@st.cache_data(show_spinner=False)
def load_fortune_db():
    path_found = None
    for p in FORTUNE_DB_PATHS:
        if os.path.exists(p):
            path_found = p
            break
    if not path_found:
        raise FileNotFoundError("fortune_db.json 파일이 data/ 폴더에 없습니다.")

    with open(path_found, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 형태 허용:
    # 1) {"records": {...}, "meta": {...}}
    # 2) {...} (records 자체가 루트)
    if isinstance(data, dict) and "records" in data and isinstance(data["records"], dict):
        records = data["records"]
    elif isinstance(data, dict):
        # meta만 있고 records가 없다면 여기서 바로 실패시키는 게 원인 제거에 좋음
        if "meta" in data and "records" not in data:
            raise ValueError("fortune_db.json에 records 키가 없습니다.")
        records = data
    else:
        raise ValueError("fortune_db.json 형식이 dict가 아닙니다.")

    if not isinstance(records, dict) or len(records) == 0:
        raise ValueError("fortune_db.json records가 비어있습니다.")

    return records, path_found

REQUIRED_FIELDS = [
    "zodiac_fortune",
    "mbti_trait",
    "mbti_influence",
    "saju_message",
    "today",
    "tomorrow",
    "year_2026",
    "love",
    "money",
    "work",
    "health",
    "lucky_point",
    "action_tip",
    "caution",
]
REQUIRED_LUCKY_FIELDS = ["color", "item", "number", "direction"]

def get_combo_record(records: dict, zodiac_ko: str, mbti: str):
    combo = f"{zodiac_ko}_{mbti}"
    rec = records.get(combo)
    if rec is None:
        raise KeyError(f"record '{combo}' not found")

    missing = [k for k in REQUIRED_FIELDS if k not in rec]
    if missing:
        raise KeyError(f"record '{combo}' missing keys: {missing}")

    lp = rec.get("lucky_point")
    if not isinstance(lp, dict):
        raise KeyError(f"record '{combo}' lucky_point is not an object")
    missing_lp = [k for k in REQUIRED_LUCKY_FIELDS if k not in lp]
    if missing_lp:
        raise KeyError(f"record '{combo}' lucky_point missing keys: {missing_lp}")

    return combo, rec

# =========================================================
# 7) Google Sheet (컬럼 고정)
#  시간 | 이름 | 전화번호 | 언어 | 기록초 | 공유여부
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

def append_entry(ws, name, phone, seconds, shared_bool):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([now_str, name, phone, "ko", f"{seconds:.3f}", str(bool(shared_bool))])

# =========================================================
# 8) Share Button (시스템 공유창만)
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
      // cancel
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 9) Stopwatch Component
#  - START/STOP 각각 1회
#  - STOP 누르면 바로 기록 확정(제출 버튼 없음)
#  - STOP 후 비활성화
# =========================================================
def stopwatch_component_auto_finalize(note_text: str, locked: bool):
    disabled = "true" if locked else "false"
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
      opacity: { "0.45" if locked else "1" };
    ">START</button>

    <button id="stopBtn" style="
      flex:1; max-width: 240px;
      border:none; border-radius: 999px;
      padding: 12px 14px;
      font-weight:900;
      background:#ff8c50; color:white;
      cursor:pointer;
      opacity: { "0.45" if locked else "1" };
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

  function lockButtons() {{
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
    startBtn.style.opacity = "0.45";
    stopBtn.style.opacity = "0.45";
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
    startBtn.style.cursor = "not-allowed";
    startBtn.style.opacity = "0.45";
  }});

  stopBtn.addEventListener("click", () => {{
    if (!running || stoppedOnce) return;
    stoppedOnce = true;
    running = false;
    if (rafId) cancelAnimationFrame(rafId);

    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    // STOP 누르면 즉시 잠금 + URL에 기록 전달 (자동 확정)
    lockButtons();

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
        height=270
    )

# =========================================================
# 10) Session State
# =========================================================
if "name" not in st.session_state: st.session_state.name = ""
if "y" not in st.session_state: st.session_state.y = 2005
if "m" not in st.session_state: st.session_state.m = 1
if "d" not in st.session_state: st.session_state.d = 1
if "stage" not in st.session_state: st.session_state.stage = "input"
if "mbti" not in st.session_state: st.session_state.mbti = None
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"

# 미니게임 상태(리셋해도 유지)
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "show_win_form" not in st.session_state: st.session_state.show_win_form = False
if "win_seconds" not in st.session_state: st.session_state.win_seconds = None
if "last_try_seconds" not in st.session_state: st.session_state.last_try_seconds = None
if "stop_locked" not in st.session_state: st.session_state.stop_locked = False  # STOP 한번 누르면 잠금

# shared=1 감지(보너스 1회)
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

# =========================================================
# 11) Style (디자인 변경 금지: 그대로 유지)
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

inject_seo_ko_only()

# =========================================================
# 12) Reset (입력/결과만 초기화, 미니게임 상태 유지)
# =========================================================
def reset_input_only_keep_minigame():
    keep_keys = {
        "shared", "max_attempts", "attempts_used",
        "show_win_form", "win_seconds", "last_try_seconds", "stop_locked",
    }
    current = dict(st.session_state)
    st.session_state.clear()
    for k, v in current.items():
        if k in keep_keys:
            st.session_state[k] = v

    # 입력값 초기화
    st.session_state.name = ""
    st.session_state.y = 2005
    st.session_state.m = 1
    st.session_state.d = 1
    st.session_state.stage = "input"
    st.session_state.mbti = None
    st.session_state.mbti_mode = "direct"

# =========================================================
# 13) Screens
# =========================================================
def render_input():
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">🔮 {T["title"]}</p>
      <p class="hero-sub">{T["subtitle"]}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

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
            index=0 if st.session_state.mbti_mode == "direct" else (1 if st.session_state.mbti_mode == "12" else 2),
            horizontal=True
        )
    except TypeError:
        mode = st.radio(
            "",
            [T["mbti_direct"], T["mbti_12"], T["mbti_16"]],
            index=0 if st.session_state.mbti_mode == "direct" else (1 if st.session_state.mbti_mode == "12" else 2),
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
    # --- DB 로드 (없으면 생성하지 않고 중단) ---
    try:
        records, db_path = load_fortune_db()
    except Exception as e:
        st.markdown(f"""
        <div class="header-hero">
          <p class="hero-title">🔮 {T["title"]}</p>
          <p class="hero-sub">{T["subtitle"]}</p>
          <span class="badge">2026</span>
        </div>
        """, unsafe_allow_html=True)
        st.error(T["db_fail_title"])
        st.write(T["db_fail_desc"])
        st.write(f"- 원인: {e}")
        st.write("- 해결: data/fortune_db.json 파일 구조(records 포함)와 커밋 상태를 확인하세요.")
        if st.button(T["reset"], use_container_width=True):
            reset_input_only_keep_minigame()
            st.rerun()
        st.caption(APP_URL)
        return

    y = st.session_state.y
    zodiac_ko = calc_zodiac_ko(y)
    mbti = st.session_state.mbti or "ENFP"
    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    # 조합 record 검증 (missing이면 fallback 금지)
    try:
        combo_key, rec = get_combo_record(records, zodiac_ko, mbti)
    except Exception as e:
        st.markdown(f"""
        <div class="header-hero">
          <p class="hero-title">{display_name} 2026년 운세</p>
          <p class="hero-sub">{zodiac_ko} · {mbti}</p>
          <span class="badge">2026</span>
        </div>
        """, unsafe_allow_html=True)
        st.error("데이터 키 불일치(근본 원인)로 결과를 만들 수 없습니다.")
        st.write(f"- 기대 조합키: {zodiac_ko}_{mbti}")
        st.write(f"- 원인: {e}")
        st.write("※ 임시 생성/대체 없이 중단합니다. fortune_db.json의 키와 필드를 수정해야 합니다.")
        if st.button(T["reset"], use_container_width=True):
            reset_input_only_keep_minigame()
            st.rerun()
        st.caption(APP_URL)
        return

    s = T["sections"]

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{zodiac_ko} · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    # ---- 본문 (데이터는 절대 unsafe_allow_html로 넣지 않음) ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['zodiac']}**: {safe_text(rec['zodiac_fortune'])}")
    st.markdown(f"**{s['mbti_trait']}**: {safe_text(rec['mbti_trait'])}")
    st.markdown(f"**{s['mbti_influence']}**: {safe_text(rec['mbti_influence'])}")
    st.markdown(f"**{s['saju']}**: {safe_text(rec['saju_message'])}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['today']}**: {safe_text(rec['today'])}")
    st.markdown(f"**{s['tomorrow']}**: {safe_text(rec['tomorrow'])}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['year_all']}**: {safe_text(rec['year_2026'])}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['love']}**: {safe_text(rec['love'])}")
    st.markdown(f"**{s['money']}**: {safe_text(rec['money'])}")
    st.markdown(f"**{s['work']}**: {safe_text(rec['work'])}")
    st.markdown(f"**{s['health']}**: {safe_text(rec['health'])}")
    st.markdown("</div>", unsafe_allow_html=True)

    lp = rec["lucky_point"]
    lucky_line = f"color={safe_text(lp['color'])} · item={safe_text(lp['item'])} · number={safe_text(lp['number'])} · direction={safe_text(lp['direction'])}"
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['lucky']}**: {lucky_line}")
    st.markdown(f"**{s['action']}**: {safe_text(rec['action_tip'])}")
    st.markdown(f"**{s['caution']}**: {safe_text(rec['caution'])}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tarot ----
    if st.button(T["tarot_btn"], use_container_width=True):
        local_name, local_meaning = pick_tarot()
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900;color:#6b4fd6;">{T["tarot_title"]}</div>
          <div style="font-size:1.45rem;font-weight:900;margin-top:6px;">{local_name}</div>
          <div style="margin-top:10px;" class="soft-box">{local_meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Share (시스템 공유창만) ----
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

    # =====================================================
    # 미니게임 (한국어만, 제출 버튼 제거, START/STOP 1회)
    # =====================================================
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

    if closed:
        st.info(T["mini_closed"])
    elif tries_left <= 0:
        st.info(T["no_tries_block"])
    else:
        # STOP 기록 t= 감지 → 자동 확정 처리
        qp2 = get_query_params()
        t_val = qp2.get("t", None)
        if isinstance(t_val, list):
            t_val = t_val[0] if t_val else None

        # 잠금 조건: 시도 소진/이미 STOP 확정/시트 미연결/이벤트 종료
        locked = (tries_left <= 0) or st.session_state.stop_locked or (not sheet_ready) or closed

        stopwatch_component_auto_finalize(T["stopwatch_note"], locked=locked)

        # t 파라미터 들어오면 즉시 확정(제출 버튼 없음)
        if t_val is not None and (not st.session_state.stop_locked):
            try:
                elapsed_val = float(str(t_val).strip())
                st.session_state.last_try_seconds = float(f"{elapsed_val:.3f}")
                st.session_state.attempts_used += 1
                st.session_state.stop_locked = True  # STOP 한 번 누르면 비활성화

                # URL 파라미터 정리
                clear_param("t")

                st.markdown(f"<div class='card'><b>기록</b>: {st.session_state.last_try_seconds:.3f}s</div>", unsafe_allow_html=True)

                if 20.160 <= st.session_state.last_try_seconds <= 20.169:
                    st.session_state.show_win_form = True
                    st.session_state.win_seconds = st.session_state.last_try_seconds
                else:
                    st.info(T["miss"])
            except Exception:
                clear_param("t")

        # 결과가 이미 확정된 상태에서(리로드 등) 기록 표시
        if st.session_state.stop_locked and st.session_state.last_try_seconds is not None:
            st.markdown(f"<div class='card'><b>최근 기록</b>: {st.session_state.last_try_seconds:.3f}s</div>", unsafe_allow_html=True)

        # 당첨자 폼: 오직 "당첨 + 시트 연결됨"일 때만
        if st.session_state.show_win_form and st.session_state.win_seconds is not None:
            if not sheet_ready:
                st.error(T["sheet_fail"])
            else:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"### {T['win_title']}")
                st.markdown(f"**기록:** {st.session_state.win_seconds:.3f}s")

                nm = st.text_input(T["win_name"], value=(st.session_state.name or "").strip(), key="win_name_input")
                ph = st.text_input(T["win_phone"], value="", key="win_phone_input")
                ph_norm = normalize_phone(ph)

                consent = st.checkbox(
                    f"{T['win_consent']}  \n{T['win_consent_text']}",
                    value=False,
                    key="consent_chk"
                )

                # 동의 거부 시 저장 없이 종료(원하는 흐름)
                if st.button("동의하지 않고 닫기", use_container_width=True):
                    st.session_state.show_win_form = False
                    st.session_state.win_seconds = None
                    st.info("동의하지 않아 저장하지 않았습니다.")

                if st.button(T["win_submit"], use_container_width=True):
                    if not consent:
                        st.warning("동의가 필요합니다.")
                    elif nm.strip() == "" or ph_norm == "":
                        st.warning("이름/전화번호를 정확히 입력해주세요.")
                    else:
                        try:
                            if phone_exists(ws, ph_norm):
                                st.warning(T["mini_dup"])
                            else:
                                if count_winners(ws) >= 20:
                                    st.info(T["mini_closed"])
                                else:
                                    append_entry(ws, nm.strip(), ph_norm, float(st.session_state.win_seconds), st.session_state.shared)
                                    st.success(T["win_thanks"])
                                    st.session_state.show_win_form = False
                                    st.session_state.win_seconds = None
                        except Exception as e:
                            st.error(f"저장 중 오류: {e}")

                st.markdown("</div>", unsafe_allow_html=True)

    # ---- 검색/AI 노출 섹션 (한국어만) ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {T['faq_title']}")
    st.markdown("- **2026 운세/띠운세/MBTI 운세/사주/오늘운세/내일운세/타로**를 무료로 제공합니다.")
    st.markdown("- MBTI 성향을 반영해 **연애·재물·직장/일·건강** 조언을 제공합니다.")
    st.markdown("- 한국어 화면에는 선착순 이벤트 미니게임(구글시트 저장)이 포함됩니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- reset: 입력/결과만 초기화 (미니게임 상태 유지) ----
    if st.button(T["reset"], use_container_width=True):
        reset_input_only_keep_minigame()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 14) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
