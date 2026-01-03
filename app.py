import streamlit as st
from datetime import datetime
import random
import re
import json
from pathlib import Path

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

FORTUNE_DB_PATH = Path(__file__).parent / "data" / "fortunes_ko.json"

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

def norm_combo_key(s: str) -> str:
    """
    조합키 비교용 정규화:
    - 공백 제거
    - 하이픈/슬래시 등 구분자 통일
    - 연속 언더스코어 정리
    """
    if s is None:
        return ""
    s = str(s).strip()
    s = s.replace(" ", "")
    s = s.replace("-", "_").replace("/", "_")
    s = re.sub(r"_+", "_", s)
    return s

# =========================================================
# 2) Query params (Streamlit 버전 호환)
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
# 3) SEO Inject (한국어만)
# =========================================================
def inject_seo_korean_only():
    description = "2026년 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로까지 무료로!"
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
# 4) Text (한국어만)
# =========================================================
T = {
    "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
    "subtitle": "완전 무료",
    "name": "이름 입력 (결과에 표시돼요)",
    "birth": "생년월일 입력",
    "year": "년",
    "month": "월",
    "day": "일",
    "mbti_mode": "MBTI를 어떻게 할까요?",
    "mbti_direct": "직접 선택",
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
        "mbti": "MBTI 특징",
        "mbti_inf": "MBTI 영향",
        "saju": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year_all": "2026 전체 운세",
        "love": "연애운 조언",
        "money": "재물운 조언",
        "work": "일/학업운 조언",
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
    "sheet_fail": "구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유/탭 이름 확인 필요)",
    "sheet_ok": "구글시트 연결 완료",
    "faq_title": "🔎 검색/AI 노출용 정보(FAQ)",
    "stopwatch_note": "START 후 STOP을 누르면 즉시 판정됩니다. (추가 제출 버튼 없음)",
    "mbti_test_12_title": "MBTI 12문항 (각 축 3문항)",
    "mbti_test_16_title": "MBTI 16문항 (각 축 4문항)",
    "mbti_test_help": "각 문항에서 더 가까운 쪽을 선택하세요.",
    "try_over": "남은 시도가 없습니다.",
    "miss": "아쉽게도 미달/초과! 다시 도전해보세요 🙂",
    "share_not_supported": "이 기기에서는 시스템 공유가 지원되지 않습니다.",
    "db_file_missing": "운세 DB 파일을 찾지 못했습니다: data/fortunes_ko.json",
    "db_json_invalid": "운세 DB JSON 파싱에 실패했습니다. (형식 오류)",
}

# =========================================================
# 5) Tarot
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
# 6) MBTI
# =========================================================
MBTI_LIST = sorted([
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
])

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

def compute_mbti_from_answers(answers, default="ENFP"):
    scores = {"EI":0, "SN":0, "TF":0, "JP":0}
    counts = {"EI":0, "SN":0, "TF":0, "JP":0}

    for axis, pick_left in answers:
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
    st.markdown(
        f"<div class='card'><b>{title}</b><br>"
        f"<span style='opacity:0.85;'>{T['mbti_test_help']}</span></div>",
        unsafe_allow_html=True
    )
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}. {axis}", options=[left_txt, right_txt], index=0, key=f"{key_prefix}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button(T["mbti_submit"], use_container_width=True):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 7) 띠 계산
# =========================================================
ZODIAC_KO_ORDER = ["쥐","소","호랑이","토끼","용","뱀","말","양","원숭이","닭","개","돼지"]

def calc_zodiac_ko(year: int) -> str:
    idx = (year - 4) % 12
    return ZODIAC_KO_ORDER[idx]

# =========================================================
# 8) fortunes_ko.json 로드 + "조합 테이블" 위치 자동 탐지
#    (근본원인: 파일 구조가 다르면 키가 있어도 못 찾음 → 여기서 해결)
# =========================================================
@st.cache_data(show_spinner=False)
def load_fortune_db_and_combos():
    if not FORTUNE_DB_PATH.exists():
        return None, None, ("missing", T["db_file_missing"])

    try:
        raw = FORTUNE_DB_PATH.read_text(encoding="utf-8")
        db = json.loads(raw)
    except Exception:
        return None, None, ("invalid", T["db_json_invalid"])

    if not isinstance(db, dict):
        return None, None, ("invalid", T["db_json_invalid"])

    # 1) 흔한 구조: fortunes 키 아래에 조합 dict
    candidates = []
    for k in ["fortunes", "records", "data", "db", "items"]:
        v = db.get(k)
        if isinstance(v, dict):
            candidates.append(v)

    # 2) 최상단에 조합키들이 섞여 있는 구조(meta/zodiacs + 조합키)
    #    조합키 패턴: "<띠>_<MBTI>" 형태가 상당수 존재할 것
    top_level_combo_like = {}
    for k, v in db.items():
        if isinstance(k, str) and "_" in k and isinstance(v, dict):
            # 대충 MBTI 형태(4글자, 마지막 4글자) 검사
            parts = k.split("_")
            if len(parts) >= 2 and len(parts[-1]) == 4:
                top_level_combo_like[k] = v

    if candidates:
        # 가장 큰 dict를 조합 테이블로 채택
        combos = max(candidates, key=lambda d: len(d))
    elif len(top_level_combo_like) >= 10:
        combos = top_level_combo_like
    else:
        combos = None

    if not isinstance(combos, dict) or len(combos) == 0:
        return db, None, ("invalid", "fortunes_ko.json에서 조합 데이터(예: 닭_ENFP)를 찾지 못했습니다. 파일 구조를 확인해주세요.")

    # 정규화 인덱스 생성
    norm_index = {norm_combo_key(k): k for k in combos.keys() if isinstance(k, str)}

    return db, (combos, norm_index), None

def debug_keys_for_zodiac(combos: dict, zodiac_ko: str, limit: int = 12):
    """DB 안에 해당 띠로 시작하는 키들을 보여주기(근거 제공용)"""
    pref = zodiac_ko + "_"
    out = [k for k in combos.keys() if isinstance(k, str) and k.startswith(pref)]
    out = sorted(out)[:limit]
    return out

def get_combo_record_or_stop(combos_pack, zodiac_ko: str, mbti: str):
    combos, norm_index = combos_pack
    expected = f"{zodiac_ko}_{mbti}"
    expected_norm = norm_combo_key(expected)

    # 1) 정확 일치
    if expected in combos:
        rec = combos[expected]
        if not isinstance(rec, dict):
            st.error(f"DB 레코드 형식 오류: {expected}")
            st.stop()
        return expected, rec

    # 2) 정규화 매칭(공백/하이픈 등)
    if expected_norm in norm_index:
        real_key = norm_index[expected_norm]
        rec = combos.get(real_key)
        if isinstance(rec, dict):
            return real_key, rec

    # 3) 여기까지 오면 '진짜 DB에 없음' → 근거 출력
    st.error(f"데이터에 조합 키가 없습니다: {expected}")

    # DB에 원숭이_* 자체가 있는지 보여줌
    similar = debug_keys_for_zodiac(combos, zodiac_ko, limit=20)
    if similar:
        st.info(f"DB에 '{zodiac_ko}_*'로 시작하는 키 예시(일부):\n\n- " + "\n- ".join(similar))
        st.info("즉, 띠는 있는데 MBTI 조합이 빠진 경우입니다. (예: 원숭이_ENFP만 누락)")
    else:
        # 띠 이름 자체가 DB에서 다르게 쓰였을 가능성
        # DB 전체에서 '원숭' 포함 키 검색
        contains = [k for k in combos.keys() if isinstance(k, str) and ("원숭" in k)]
        contains = sorted(contains)[:20]
        if contains:
            st.warning("DB에 '원숭'이 포함된 키가 있긴 한데, 접두사가 다릅니다. (띠 표기/구분자 확인 필요)")
            st.code("\n".join(contains))
        else:
            st.warning(f"DB에 '{zodiac_ko}' 관련 키가 아예 없습니다. (DB 생성/누락 문제)")

    st.stop()

# =========================================================
# 9) Google Sheet
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
      window.location.href = url + "?shared=1";
    }} catch (e) {{}}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 11) Stopwatch Component (STOP 시 t= 리다이렉트)
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
    if (running) return;
    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);

    startBtn.disabled = true;
    startBtn.style.cursor = "not-allowed";
    startBtn.style.opacity = "0.65";
  }});

  stopBtn.addEventListener("click", () => {{
    if (!running) return;
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    stopBtn.disabled = true;
    stopBtn.style.cursor = "not-allowed";
    stopBtn.style.opacity = "0.65";

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
        height=285
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

if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "show_win_form" not in st.session_state: st.session_state.show_win_form = False
if "win_seconds" not in st.session_state: st.session_state.win_seconds = None
if "last_elapsed" not in st.session_state: st.session_state.last_elapsed = None

# =========================================================
# 13) Shared=1 감지 + t= 기록 감지
# =========================================================
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

t_val = qp.get("t", None)
if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None

if t_val is not None:
    try:
        elapsed = float(str(t_val).strip())
        elapsed = float(f"{elapsed:.3f}")
    except Exception:
        elapsed = None

    clear_param("t")

    if elapsed is not None:
        tries_left_before = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
        if tries_left_before > 0:
            st.session_state.attempts_used += 1
            st.session_state.last_elapsed = elapsed

            if 20.160 <= elapsed <= 20.169:
                st.session_state.show_win_form = True
                st.session_state.win_seconds = elapsed
            else:
                st.session_state.show_win_form = False
                st.session_state.win_seconds = None

# =========================================================
# 14) Style
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

inject_seo_korean_only()

# =========================================================
# 15) Reset
# =========================================================
def reset_input_only_keep_minigame():
    keep_keys = {
        "shared", "max_attempts", "attempts_used",
        "show_win_form", "win_seconds", "last_elapsed",
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
# 16) Screens
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
            index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
            horizontal=True
        )
    except TypeError:
        mode = st.radio(
            "",
            [T["mbti_direct"], T["mbti_12"], T["mbti_16"]],
            index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
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
    db, combos_pack, err = load_fortune_db_and_combos()
    if err is not None:
        st.error(err[1])
        st.stop()

    y = st.session_state.y
    zodiac_ko = calc_zodiac_ko(y)
    mbti = st.session_state.mbti or "ENFP"

    real_key, record = get_combo_record_or_stop(combos_pack, zodiac_ko, mbti)

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{zodiac_ko}띠 · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    s = T["sections"]

    def req(k: str):
        if k not in record:
            st.error(f"DB 레코드({real_key})에 필수 키가 없습니다: {k}")
            st.stop()
        return record[k]

    zodiac_fortune = req("zodiac_fortune")
    mbti_trait = req("mbti_trait")
    mbti_influence = req("mbti_influence")
    saju_message = req("saju_message")
    today = req("today")
    tomorrow = req("tomorrow")
    year_2026 = req("year_2026")
    love = req("love")
    money = req("money")
    work = req("work")
    health = req("health")
    lucky_point = req("lucky_point")
    action_tip = req("action_tip")
    caution = req("caution")

    if not isinstance(lucky_point, dict):
        st.error(f"DB 레코드({real_key})의 lucky_point 형식이 올바르지 않습니다.")
        st.stop()

    lp_color = lucky_point.get("color", "")
    lp_item = lucky_point.get("item", "")
    lp_number = lucky_point.get("number", "")
    lp_direction = lucky_point.get("direction", "")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['zodiac']}**: {zodiac_fortune}")
    st.markdown(f"**{s['mbti']}**: {mbti_trait}")
    st.markdown(f"**{s['mbti_inf']}**: {mbti_influence}")
    st.markdown(f"**{s['saju']}**: {saju_message}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['today']}**: {today}")
    st.markdown(f"**{s['tomorrow']}**: {tomorrow}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['year_all']}**: {year_2026}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['love']}**: {love}")
    st.markdown(f"**{s['money']}**: {money}")
    st.markdown(f"**{s['work']}**: {work}")
    st.markdown(f"**{s['health']}**: {health}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(
        f"**{s['lucky']}**: 색상 **{lp_color}**, 아이템 **{lp_item}**, 숫자 **{lp_number}**, 방향 **{lp_direction}**"
    )
    st.markdown(f"**{s['action']}**: {action_tip}")
    st.markdown(f"**{s['caution']}**: {caution}")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(T["tarot_btn"], use_container_width=True):
        local_name, local_meaning = pick_tarot()
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900;color:#6b4fd6;">{T["tarot_title"]}</div>
          <div style="font-size:1.45rem;font-weight:900;margin-top:6px;">{local_name}</div>
          <div style="margin-top:10px;" class="soft-box">{local_meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    share_button_native_only(T["share_link_btn"], T["share_not_supported"])
    st.caption(T["share_link_hint"])

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
    else:
        if st.session_state.last_elapsed is not None:
            st.markdown(
                f"<div class='card'><b>방금 기록</b>: {st.session_state.last_elapsed:.3f}s</div>",
                unsafe_allow_html=True
            )
            if st.session_state.show_win_form and st.session_state.win_seconds is not None:
                st.success("🎯 목표 구간 성공! 아래 정보를 입력하면 접수됩니다.")
            else:
                st.info(T["miss"])

        if tries_left > 0:
            stopwatch_component_auto_fill(T["stopwatch_note"], tries_left)
        else:
            st.info(T["try_over"])

        if st.session_state.show_win_form and st.session_state.win_seconds is not None:
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

            if st.button(T["win_submit"], use_container_width=True):
                if not sheet_ready:
                    st.error(T["sheet_fail"])
                elif not consent:
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

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {T['faq_title']}")
    st.markdown("- **2026 운세/띠운세/MBTI 운세/사주/오늘운세/내일운세/타로**를 무료로 제공합니다.")
    st.markdown("- 띠+MBTI 조합으로 **연애·재물·일/학업·건강** 조언을 제공합니다.")
    st.markdown("- 일부 브라우저에서는 자동 번역 기능으로 다른 언어로도 볼 수 있습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(T["reset"], use_container_width=True):
        reset_input_only_keep_minigame()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 17) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
