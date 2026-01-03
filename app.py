import streamlit as st
from datetime import datetime
import json
import random
import re
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

# 구글시트(미니게임 당첨자 저장)
SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_NAME = "시트1"

# DB 파일(한국어 단일)
DB_PATH = Path(__file__).parent / "data" / "fortunes_ko.json"

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일",
    page_icon="🔮",
    layout="centered"
)

# =========================================================
# 1) Small helpers
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
def inject_seo_ko():
    description = "2026년 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로까지 무료로! (미니게임 이벤트 포함)"
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
# 4) UI Text (한국어만)
# =========================================================
T = {
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
    "share_link_btn": "🔗 링크 공유하기",
    "share_link_hint": "버튼을 누르면 ‘링크 공유’ 창이 뜹니다.",
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
        "love": "연애운",
        "money": "재물운",
        "work": "일/학업운",
        "health": "건강운",
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
    "mini_desc": "스톱워치를 **20.16초**에 맞추면 당첨!\n\n- 기본 1회\n- **링크 공유하기**를 누르면 1회 추가\n- 목표 구간: **20.160 ~ 20.169초**\n\n※ **START → STOP 한 번**으로 자동 판정됩니다. (기록제출 버튼 없음)",
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
    "stopwatch_note": "START 후 STOP을 누르면 기록이 자동으로 판정됩니다.",
    "try_over": "남은 시도가 없습니다.",
    "miss": "아쉽게도 미달/초과! 다음 기회에 도전해보세요 🙂",
    "share_not_supported": "이 기기에서는 시스템 공유가 지원되지 않습니다.",
    "db_missing": "DB 파일을 찾을 수 없습니다: data/fortunes_ko.json",
    "db_invalid": "DB 형식/내용이 올바르지 않습니다. (아래 오류를 확인하세요)",
}

# =========================================================
# 5) Tarot (간단)
# =========================================================
TAROT = {
    "Wheel of Fortune": {"name": "운명의 수레바퀴", "meaning": "변화, 전환점"},
    "The Sun": {"name": "태양", "meaning": "행복, 성공, 긍정 에너지"},
    "Strength": {"name": "힘", "meaning": "용기, 인내"},
    "The World": {"name": "세계", "meaning": "완성, 성취"},
}

def pick_tarot():
    key = random.choice(list(TAROT.keys()))
    return key, TAROT[key]["name"], TAROT[key]["meaning"]

# =========================================================
# 6) Zodiac / MBTI
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL_KO = {
    "rat":"쥐", "ox":"소", "tiger":"호랑이", "rabbit":"토끼",
    "dragon":"용", "snake":"뱀", "horse":"말", "goat":"양",
    "monkey":"원숭이", "rooster":"닭", "dog":"개", "pig":"돼지"
}
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

# =========================================================
# 7) MBTI Test (12/16) — 한국어만
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
        counts[axis] += 1
        if pick_left:
            scores[axis] += 1

    def decide(axis, left_char, right_char):
        if counts[axis] == 0:
            return left_char
        return left_char if scores[axis] >= (counts[axis]/2) else right_char

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_LIST else default

def render_mbti_test(mode: str):
    questions = MBTI_Q_12[:] + (MBTI_Q_16_EXTRA[:] if mode == "16" else [])
    st.markdown(f"<div class='card'><b>{'MBTI 12문항' if mode=='12' else 'MBTI 16문항'}</b><br>"
                f"<span style='opacity:0.85;'>각 문항에서 더 가까운 쪽을 선택하세요.</span></div>", unsafe_allow_html=True)
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}. {axis}", options=[left_txt, right_txt], index=0, key=f"mbtiq_{mode}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button(T["mbti_submit"], use_container_width=True):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 8) Fortune DB Loader (v2 정석 + v1 호환 변환)
#     - 절대 "없으면 생성" 안 함
# =========================================================
ZODIAC_KO_TO_ID = {
    "쥐":"rat", "소":"ox", "호랑이":"tiger", "토끼":"rabbit",
    "용":"dragon", "뱀":"snake", "말":"horse", "양":"goat",
    "원숭이":"monkey", "닭":"rooster", "개":"dog", "돼지":"pig",
}

REQUIRED_RECORD_KEYS = [
    "zodiac_fortune","mbti_trait","mbti_influence","saju_message",
    "today","tomorrow","year_2026",
    "love","money","work","health",
    "lucky_point","action_tip","caution"
]
REQUIRED_LUCKY_KEYS = ["color","item","number","direction"]

def _load_json_file(path: Path):
    if not path.exists():
        return None, [T["db_missing"]]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data, []
    except Exception as e:
        return None, [f"JSON 파싱 실패: {e}"]

def _convert_v1_to_v2(db_v1: dict):
    # v1 예상: meta.schema == fortune-db-v1, combos: { "닭_ENFP": {...}, ...}
    combos = db_v1.get("combos")
    if not isinstance(combos, dict):
        return None, ["v1 변환 실패: combos가 없습니다."]

    # v2 기본 뼈대
    v2 = {
        "meta": {
            "schema": "fortune-db-v2",
            "lang": "ko",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "notes": "auto-converted from fortune-db-v1 at runtime (please migrate file to v2)"
        },
        "zodiacs": [{"id": zid, "label": ZODIAC_LABEL_KO[zid]} for zid in ZODIAC_ORDER],
        "mbti": [{"id": m, "label": m} for m in MBTI_LIST],
        "content": {zid: {} for zid in ZODIAC_ORDER}
    }

    errors = []
    for k, rec in combos.items():
        # k 예: "닭_ENFP"
        if not isinstance(k, str) or "_" not in k:
            continue
        zko, mbti = k.split("_", 1)
        zko = zko.strip()
        mbti = mbti.strip().upper()

        zid = ZODIAC_KO_TO_ID.get(zko)
        if zid is None:
            errors.append(f"v1 변환: 알 수 없는 띠 라벨 '{zko}' (키: {k})")
            continue
        if mbti not in MBTI_LIST:
            errors.append(f"v1 변환: 알 수 없는 MBTI '{mbti}' (키: {k})")
            continue
        if not isinstance(rec, dict):
            errors.append(f"v1 변환: 레코드가 dict가 아님 (키: {k})")
            continue

        v2["content"][zid][mbti] = rec

    if errors:
        return None, errors
    return v2, []

def validate_db_v2(db: dict):
    errors = []
    meta = db.get("meta", {})
    if meta.get("schema") != "fortune-db-v2":
        errors.append(f"meta.schema가 fortune-db-v2가 아닙니다. (현재: {meta.get('schema')})")

    content = db.get("content")
    if not isinstance(content, dict):
        errors.append("content가 없습니다(또는 dict가 아님).")
        return errors

    # 12띠 존재
    for zid in ZODIAC_ORDER:
        if zid not in content or not isinstance(content.get(zid), dict):
            errors.append(f"content['{zid}']가 없습니다.")
            continue

        # 16MBTI 전부 필수
        for mbti in MBTI_LIST:
            rec = content[zid].get(mbti)
            if not isinstance(rec, dict):
                errors.append(f"조합 누락: {zid}_{mbti}")
                continue

            missing = [k for k in REQUIRED_RECORD_KEYS if k not in rec]
            if missing:
                errors.append(f"레코드 키 누락: {zid}_{mbti} -> {', '.join(missing)}")
                continue

            lp = rec.get("lucky_point")
            if not isinstance(lp, dict):
                errors.append(f"lucky_point 형식 오류: {zid}_{mbti}")
                continue

            miss_lp = [k for k in REQUIRED_LUCKY_KEYS if k not in lp]
            if miss_lp:
                errors.append(f"lucky_point 키 누락: {zid}_{mbti} -> {', '.join(miss_lp)}")
                continue

    return errors

def load_fortune_db():
    raw, errs = _load_json_file(DB_PATH)
    if errs:
        return None, errs
    if not isinstance(raw, dict):
        return None, ["DB 최상위가 dict가 아닙니다."]

    schema = (raw.get("meta") or {}).get("schema")
    if schema == "fortune-db-v2":
        v2 = raw
    elif schema == "fortune-db-v1" or "combos" in raw:
        v2, conv_errs = _convert_v1_to_v2(raw)
        if conv_errs:
            return None, conv_errs
    else:
        return None, [f"알 수 없는 schema 입니다: {schema}"]

    val_errs = validate_db_v2(v2)
    if val_errs:
        return None, val_errs

    return v2, []

# =========================================================
# 9) Google Sheet (미니게임 당첨자 저장)
#  컬럼: 시간 | 이름 | 전화번호 | 기록초 | 공유여부
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
            sec = float(row[3])
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
    ws.append_row([now_str, name, phone, f"{seconds:.3f}", str(bool(shared_bool))])

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
      // 공유 완료 시 보너스
      const u = new URL(window.location.href);
      u.searchParams.set("shared", "1");
      window.location.href = u.toString();
    }} catch (e) {{
      // user cancelled → do nothing
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 11) Stopwatch Component
#  - STOP 시 ?t=초 로 리다이렉트
#  - tries_left == 0 이면 START/STOP 비활성
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
    // START 한번 누르면 START 비활성 (원하는 UX)
    startBtn.disabled = true;
    startBtn.style.opacity = "0.6";
    startBtn.style.cursor = "not-allowed";

    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);
  }});

  stopBtn.addEventListener("click", () => {{
    // STOP 한번 누르면 둘 다 비활성 (원하는 UX)
    stopBtn.disabled = true;
    stopBtn.style.opacity = "0.6";
    stopBtn.style.cursor = "not-allowed";
    startBtn.disabled = true;
    startBtn.style.opacity = "0.6";
    startBtn.style.cursor = "not-allowed";

    if (!running) return;
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

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
# 12) Style (디자인 유지)
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

# =========================================================
# 13) Session State
# =========================================================
if "name" not in st.session_state: st.session_state.name = ""
if "y" not in st.session_state: st.session_state.y = 2005
if "m" not in st.session_state: st.session_state.m = 1
if "d" not in st.session_state: st.session_state.d = 1
if "stage" not in st.session_state: st.session_state.stage = "input"
if "mbti" not in st.session_state: st.session_state.mbti = "ENFP"
if "mbti_mode" not in st.session_state: st.session_state.mbti_mode = "direct"

# 미니게임 상태(리셋에서 유지)
if "shared" not in st.session_state: st.session_state.shared = False
if "max_attempts" not in st.session_state: st.session_state.max_attempts = 1
if "attempts_used" not in st.session_state: st.session_state.attempts_used = 0
if "show_win_form" not in st.session_state: st.session_state.show_win_form = False
if "win_seconds" not in st.session_state: st.session_state.win_seconds = None
if "last_attempt_seconds" not in st.session_state: st.session_state.last_attempt_seconds = None
if "last_attempt_ok" not in st.session_state: st.session_state.last_attempt_ok = None

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

# ---- STOP 기록 t= 감지 → 자동 판정 ----
t_val = qp.get("t", None)
if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None

if t_val is not None:
    clear_param("t")
    tries_left_now = max(0, st.session_state.max_attempts - st.session_state.attempts_used)
    if tries_left_now > 0:
        try:
            elapsed = float(str(t_val).strip())
            st.session_state.attempts_used += 1
            st.session_state.last_attempt_seconds = elapsed
            ok = (20.160 <= elapsed <= 20.169)
            st.session_state.last_attempt_ok = ok
            if ok:
                st.session_state.show_win_form = True
                st.session_state.win_seconds = elapsed
            else:
                st.session_state.show_win_form = False
                st.session_state.win_seconds = None
        except Exception:
            pass

# =========================================================
# 14) Core logic
# =========================================================
def calc_zodiac_id(year: int) -> str:
    idx = (year - 4) % 12
    return ZODIAC_ORDER[idx]

# =========================================================
# 15) Reset (미니게임 시도/공유 유지)
# =========================================================
def reset_input_only_keep_minigame():
    keep_keys = {
        "shared", "max_attempts", "attempts_used",
        "show_win_form", "win_seconds",
        "last_attempt_seconds", "last_attempt_ok",
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
    else:
        done = render_mbti_test("12" if st.session_state.mbti_mode == "12" else "16")
        if done:
            st.success(f"MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button(T["go_result"], use_container_width=True):
        if not st.session_state.mbti:
            st.session_state.mbti = "ENFP"
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_db_error(errors: list[str]):
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">⚠️ {T["db_invalid"]}</p>
      <p class="hero-sub">DB를 먼저 정상화해야 합니다.</p>
      <span class="badge">DB</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("아래는 앱이 발견한 정확한 오류 목록입니다. (이대로 DB를 고치면 해결됩니다)")
    for e in errors[:200]:
        st.write(f"- {e}")
    if len(errors) > 200:
        st.write(f"... (총 {len(errors)}개 중 일부만 표시)")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(T["reset"], use_container_width=True):
        reset_input_only_keep_minigame()
        st.rerun()

def render_result():
    # DB 로드 + 검증(실패 시 즉시 원인 출력)
    db, db_errors = load_fortune_db()
    if db_errors:
        render_db_error(db_errors)
        return

    s = T["sections"]

    y = st.session_state.y
    zodiac_id = calc_zodiac_id(y)
    zodiac_label = ZODIAC_LABEL_KO.get(zodiac_id, zodiac_id)

    mbti = (st.session_state.mbti or "ENFP").upper()
    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    # v2: content[zodiac_id][mbti]
    rec = db["content"][zodiac_id][mbti]

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{zodiac_label}띠 · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    # ---- 본문 카드(텍스트는 st.write로: 태그 노출 방지) ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write(f"**{s['zodiac']}**")
    st.write(rec["zodiac_fortune"])

    st.write(f"**{s['mbti']}**")
    st.write(rec["mbti_trait"])
    st.write(rec["mbti_influence"])

    st.write(f"**{s['saju']}**")
    st.write(rec["saju_message"])

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.write(f"**{s['today']}**")
    st.write(rec["today"])
    st.write(f"**{s['tomorrow']}**")
    st.write(rec["tomorrow"])

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.write(f"**{s['year_all']}**")
    st.write(rec["year_2026"])

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.write(f"**{s['love']}**")
    st.write(rec["love"])
    st.write(f"**{s['money']}**")
    st.write(rec["money"])
    st.write(f"**{s['work']}**")
    st.write(rec["work"])
    st.write(f"**{s['health']}**")
    st.write(rec["health"])

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    lp = rec["lucky_point"]
    st.write(f"**{s['lucky']}**")
    st.write(f"색: {lp['color']} · 아이템: {lp['item']} · 숫자: {lp['number']} · 방향: {lp['direction']}")

    st.write(f"**{s['action']}**")
    st.write(rec["action_tip"])
    st.write(f"**{s['caution']}**")
    st.write(rec["caution"])
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tarot ----
    if st.button(T["tarot_btn"], use_container_width=True):
        eng_key, local_name, local_meaning = pick_tarot()
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900;color:#6b4fd6;">{T["tarot_title"]}</div>
          <div style="font-size:1.45rem;font-weight:900;margin-top:6px;">{local_name}</div>
          <div style="opacity:0.75;margin-top:2px;">{eng_key}</div>
          <div style="margin-top:10px;" class="soft-box">{local_meaning}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Share (시스템 공유창만) ----
    share_button_native_only(T["share_link_btn"], T["share_not_supported"])
    st.caption(T["share_link_hint"])

    # ---- 광고 위치 ----
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

    # ---- 미니게임 ----
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
        if tries_left <= 0:
            st.info(T["try_over"])

        # 최근 시도 결과(자동 판정 결과 표시)
        if st.session_state.last_attempt_seconds is not None:
            sec = float(st.session_state.last_attempt_seconds)
            ok = bool(st.session_state.last_attempt_ok)
            if ok:
                st.success(f"기록: {sec:.3f}s ✅ (당첨 범위)")
            else:
                st.info(f"기록: {sec:.3f}s ❌ {T['miss']}")

        # 스톱워치(START/STOP 한번씩)
        stopwatch_component_auto_fill(T["stopwatch_note"], tries_left)

        # 당첨 폼
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

    # ---- FAQ ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### {T['faq_title']}")
    st.write("- **2026 운세/띠운세/MBTI 운세/사주/오늘운세/내일운세/타로**를 무료로 제공합니다.")
    st.write("- MBTI 성향을 반영해 **연애·재물·일/학업·건강** 조언을 제공합니다.")
    st.write("- 한국어 화면에는 선착순 이벤트 미니게임(구글시트 저장)이 포함됩니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- reset ----
    if st.button(T["reset"], use_container_width=True):
        reset_input_only_keep_minigame()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 17) Router
# =========================================================
inject_seo_ko()

if st.session_state.stage == "input":
    render_input()
else:
    render_result()
