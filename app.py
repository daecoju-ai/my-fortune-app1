import streamlit as st
from datetime import datetime
import json, re, hashlib
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

DB_PATH = "data/fortunes_ko.json"
st.set_page_config(
    page_title="2026 운세 | 띠+MBTI+사주+오늘/내일",
    page_icon="🔮",
    layout="centered"
)

# =========================================================
# 1) Helpers
# =========================================================
def normalize_phone(phone: str) -> str:
    return re.sub(r"[^0-9]", "", phone or "")

def stable_seed_int(*parts) -> int:
    """문자열 조합을 SHA256으로 해시 → 안정적인 int seed 생성"""
    s = "|".join(str(p) for p in parts)
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def pick_from_pool(pool: list, seed_parts: tuple, tag: str) -> str:
    """seed 기반으로 pool에서 항상 같은 항목 선택"""
    if not isinstance(pool, list) or len(pool) == 0:
        return "데이터가 없습니다."
    idx = stable_seed_int(*seed_parts, tag) % len(pool)
    return pool[idx]

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
# 2) SEO Inject (한국어 고정)
# =========================================================
def inject_seo():
    description = "2026년 띠운세 + MBTI + 사주 + 오늘/내일 운세 + 타로까지 무료로!"
    keywords = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, 무료 운세, 타로, 연애운, 재물운, 건강운"
    title = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 운세"
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
# 3) Load DB (JSON)
# =========================================================
@st.cache_data(show_spinner=False)
def load_db(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"DB 파일을 찾을 수 없습니다: {p}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

try:
    DB = load_db(str(DB_PATH))
except Exception as e:
    st.error(f"DB 로딩 실패: {e}")
    st.stop()

ZODIAC_ORDER = DB["zodiac"]["order"]
ZODIAC_LABELS = DB["zodiac"]["labels"]
ZODIAC_BASE = DB["zodiac"]["base_fortune"]
MBTI_DESC = DB["mbti"]["desc"]
POOLS = DB["pools"]
COMBOS = DB.get("combos", {})

MBTI_LIST = sorted(MBTI_DESC.keys())

def calc_zodiac_key(year: int) -> str:
    return ZODIAC_ORDER[(year - 4) % 12]

# =========================================================
# 4) Google Sheet (컬럼 유지 + G열 상담신청)
#  A:시간 | B:이름 | C:전화번호 | D:언어 | E:기록초 | F:공유여부 | G:상담신청(O/X/빈값)
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

def append_entry(ws, name, phone, seconds, shared_bool, consult_flag=""):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([now_str, name, phone, "ko", f"{seconds:.3f}", str(bool(shared_bool)), consult_flag])

# =========================================================
# 5) Share Button (시스템 공유창만)
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
    }} catch (e) {{}}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 6) Stopwatch Component
# =========================================================
def stopwatch_component(note_text: str, tries_left: int):
    disabled = "true" if tries_left <= 0 else "false"
    started_once = "true" if st.session_state.get("attempt_started", False) else "false"
    stopped_once = "true" if st.session_state.get("attempt_stopped", False) else "false"

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
    ">START</button>

    <button id="stopBtn" style="
      flex:1; max-width: 240px;
      border:none; border-radius: 999px;
      padding: 12px 14px;
      font-weight:900;
      background:#ff8c50; color:white;
      cursor:pointer;
    ">STOP</button>
  </div>

  <div style="margin-top:10px; font-size:0.92rem; opacity:0.85;">
    {note_text}
  </div>
</div>

<script>
(function() {{
  const disabled = {disabled};
  const alreadyStarted = {started_once};
  const alreadyStopped = {stopped_once};

  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const display = document.getElementById("display");

  const freezeScroll = () => {{
    try {{
      const y = window.scrollY;
      requestAnimationFrame(() => window.scrollTo(0, y));
    }} catch(e) {{}}
  }};

  if (disabled || alreadyStopped) {{
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.opacity = "0.45";
    stopBtn.style.opacity = "0.45";
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
    return;
  }}

  let running = false;
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

  startBtn.addEventListener("click", (e) => {{
    e.preventDefault();
    freezeScroll();
    if (disabled || alreadyStarted) return;

    running = true;
    startTime = performance.now();
    display.textContent = "00:00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);

    const u = new URL(window.location.href);
    u.searchParams.set("started", "1");
    window.location.href = u.toString();
  }});

  stopBtn.addEventListener("click", (e) => {{
    e.preventDefault();
    freezeScroll();
    if (!running) return;

    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    const v = elapsedSec.toFixed(3);

    const u = new URL(window.location.href);
    u.searchParams.set("t", v);
    u.searchParams.set("stopped", "1");
    window.location.href = u.toString();
  }});
}})();
</script>
""",
        height=285
    )

# =========================================================
# 7) UI Text (한국어 고정)
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
    "share_btn": "🔗 링크 공유하기",
    "share_hint": "버튼을 누르면 갤러리/카톡 등으로 공유할 수 있는 시스템 공유창이 뜹니다.",
    "tarot_btn": "오늘의 타로 카드 뽑기",
    "sections": {
        "zodiac": "띠 운세",
        "mbti": "MBTI 특징",
        "saju": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year_all": "2026 전체 운세",
        "love": "연애운 조언",
        "money": "재물운 조언",
        "work": "일/학업운 조언",
        "health": "건강운 조언",
        "action": "오늘의 액션팁",
        "combo": "조합 한마디",
        "combo_advice": "MBTI가 운세에 미치는 영향",
    },
    "ad_placeholder": "AD (심사 통과 후 이 위치에 광고가 표시됩니다)",
    "ad_title": "정수기렌탈 대박!",
    "ad_body1": "제휴카드면 월 0원부터!",
    "ad_body2": "설치 당일 최대 50만원 지원 + 사은품 듬뿍",
    "ad_link": "다나눔렌탈.com 바로가기",
    "ad_url": "https://www.다나눔렌탈.com",
    "mini_title": "🎁 미니게임: 선착순 20명 커피쿠폰 도전!",
    "mini_desc": "스톱워치를 **20.16초**에 맞추면 당첨!\n\n- 기본 1회\n- **링크 공유하기**를 성공하면 1회 추가\n- 목표 구간: **20.160 ~ 20.169초**",
    "mini_try_left": "남은 시도",
    "mini_closed": "이벤트가 종료되었습니다. (선착순 20명 마감)",
    "mini_dup": "이미 참여한 번호입니다. (중복 참여 불가)",
    "stopwatch_note": "START 후 STOP을 누르면 기록이 자동 확정됩니다.",
    "win_msg": "성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.",
    "lose_msg": "친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.",
    "consult_q": "상담신청 하시겠어요?",
    "consult_o": "O (상담신청)",
    "consult_x": "X (안함)",
    "privacy_title": "개인정보 동의(필수)",
    "privacy_text": "이벤트 경품 발송을 위해 이름/전화번호를 수집하며, 목적 달성 후 지체 없이 파기합니다. 동의 거부 시 참여가 제한됩니다.",
    "submit": "제출",
    "sheet_fail": "구글시트 연결이 아직 안 되어 있어요. (Secrets/requirements/시트 공유/탭 이름 확인 필요)",
    "sheet_ok": "구글시트 연결 완료",
}

# =========================================================
# 8) MBTI Tests (12/16) - 한국어만
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

def compute_mbti(answers):
    scores = {"EI":0,"SN":0,"TF":0,"JP":0}
    counts = {"EI":0,"SN":0,"TF":0,"JP":0}
    for axis, pick_left in answers:
        counts[axis] += 1
        if pick_left:
            scores[axis] += 1

    def decide(axis, left, right):
        return left if scores[axis] >= (counts[axis]/2) else right

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_DESC else "ENFP"

def render_mbti_test(title, questions, key_prefix):
    # 모바일에서 한 화면에 최대한 많이 보이도록: 2열 그리드 + 가로 라디오
    st.subheader(title)

    answers = []

    # 2개씩 한 줄(2열)
    for row_i in range(0, len(questions), 2):
        cols = st.columns(2, gap="large")
        for col_i in range(2):
            q_i = row_i + col_i
            if q_i >= len(questions):
                continue

            axis, left, right = questions[q_i]
            with cols[col_i]:
                # 축 이름을 한국어로 짧게 표시
                axis_label = {
                    "EI": "에너지",
                    "SN": "정보",
                    "TF": "의사결정",
                    "JP": "생활양식",
                }.get(axis, axis)

                st.markdown(f"**{axis_label}**")
                choice = st.radio(
                    "",
                    [left, right],
                    key=f"{key_prefix}_{q_i}",
                    horizontal=True,
                    label_visibility="collapsed",
                )
                answers.append((axis, choice == left))

    if st.button("결과 보기", key=f"{key_prefix}_submit"):
        st.session_state["mbti_result"] = compute_mbti(answers)
        return True
    return False


def render_result():
    s = T["sections"]
    y, m, d = st.session_state.y, st.session_state.m, st.session_state.d
    mbti = st.session_state.mbti or "ENFP"

    zodiac_key = calc_zodiac_key(y)
    zodiac_label = ZODIAC_LABELS.get(zodiac_key, "띠")
    zodiac_base_pool = ZODIAC_BASE.get(zodiac_key, ["데이터가 없습니다."])

    seed_parts = (y, m, d, mbti)

    zodiac_desc = pick_from_pool(zodiac_base_pool, seed_parts, "zodiac_base")
    mbti_line = MBTI_DESC.get(mbti, mbti)

    saju = pick_from_pool(POOLS.get("saju_one_liner", []), seed_parts, "saju")
    today = pick_from_pool(POOLS.get("today_fortune", []), seed_parts, "today")
    tomorrow = pick_from_pool(POOLS.get("tomorrow_fortune", []), (y, m, d+1, mbti), "tomorrow")
    year_all = pick_from_pool(POOLS.get("year_overall", []), seed_parts, "year")

    love = pick_from_pool(POOLS.get("love_advice", []), seed_parts, "love")
    money = pick_from_pool(POOLS.get("money_advice", []), seed_parts, "money")
    work = pick_from_pool(POOLS.get("work_study_advice", []), seed_parts, "work")
    health = pick_from_pool(POOLS.get("health_advice", []), seed_parts, "health")
    action = pick_from_pool(POOLS.get("action_tip", []), seed_parts, "action")

    combo_key = f"{zodiac_label}_{mbti}"
    combo_obj = COMBOS.get(combo_key)
    if combo_obj:
        combo_one = pick_from_pool(combo_obj.get("combo_one_liner", []), seed_parts, "combo_one")
        combo_advice = pick_from_pool(combo_obj.get("combo_advice", []), seed_parts, "combo_advice")
    else:
        combo_one = "오늘은 강점(성향)을 한 가지로만 밀어보세요."
        combo_advice = "MBTI 성향을 한 문장으로만 요약해, 행동으로 옮기면 운이 붙습니다."

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{zodiac_label} · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['zodiac']}**: {zodiac_desc}")
    st.markdown(f"**{s['mbti']}**: {mbti_line}")
    st.markdown(f"**{s['saju']}**: {saju}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['today']}**: {today}")
    st.markdown(f"**{s['tomorrow']}**: {tomorrow}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['year_all']}**: {year_all}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**{s['combo']}**: {combo_one}")
    st.markdown(f"**{s['combo_advice']}**: {combo_advice}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**{s['love']}**: {love}")
    st.markdown(f"**{s['money']}**: {money}")
    st.markdown(f"**{s['work']}**: {work}")
    st.markdown(f"**{s['health']}**: {health}")
    st.markdown(f"**{s['action']}**: {action}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Tarot ----
    tarot_pool = [
        ("운명의 수레바퀴", "변화, 전환점"),
        ("태양", "행복, 성공, 긍정 에너지"),
        ("힘", "용기, 인내"),
        ("세계", "완성, 성취"),
    ]
    if st.button(T["tarot_btn"], use_container_width=True):
        tarot_name = pick_from_pool([x[0] for x in tarot_pool], seed_parts, "tarot")
        tarot_mean = pick_from_pool([x[1] for x in tarot_pool], seed_parts, "tarot_mean")
        st.markdown(f"""
        <div class="card" style="text-align:center;">
          <div style="font-weight:900;color:#6b4fd6;">오늘의 타로 카드</div>
          <div style="font-size:1.45rem;font-weight:900;margin-top:6px;">{tarot_name}</div>
          <div style="margin-top:10px;" class="soft-box">{tarot_mean}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Share ----
    share_button_native_only(T["share_btn"])
    st.caption(T["share_hint"])

    # ---- 광고(미니게임 바로 위) ----
    st.markdown(f"<div class='adplaceholder'>{T['ad_placeholder']}</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">{T["ad_title"]}</div>
      <div style="margin-top:6px;">{T["ad_body1"]}</div>
      <div>{T["ad_body2"]}</div>
      <div style="margin-top:10px;">
        <a href="{T["ad_url"]}" target="_blank"
           style="display:inline-block;background:#ff8c50;color:white;
           padding:10px 16px;border-radius:999px;font-weight:900;text-decoration:none;">
          {T["ad_link"]}
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
    if ws is None:
        st.warning(T["sheet_fail"])
    else:
        st.success(T["sheet_ok"])

    closed = False
    if ws is not None:
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
        stopwatch_component(T["stopwatch_note"], tries_left)

        if st.session_state.last_elapsed is not None:
            st.markdown(f"<div class='card'><b>기록</b>: {st.session_state.last_elapsed:.3f}s</div>", unsafe_allow_html=True)

        if st.session_state.last_result == "win":
            st.success(T["win_msg"])

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🎉 당첨자 정보 입력")
            nm = st.text_input("이름", value=(st.session_state.name or "").strip(), key="win_name")
            ph = st.text_input("전화번호", value="", key="win_phone")
            consent = st.checkbox(f"{T['privacy_title']}  \n{T['privacy_text']}", value=False, key="win_consent")

            if st.button(T["submit"], use_container_width=True, key="win_submit"):
                if ws is None:
                    st.error(T["sheet_fail"])
                else:
                    ph_norm = normalize_phone(ph)
                    if not consent:
                        st.warning("동의가 필요합니다.")
                    elif nm.strip() == "" or ph_norm == "":
                        st.warning("이름/전화번호를 정확히 입력해주세요.")
                    elif phone_exists(ws, ph_norm):
                        st.warning(T["mini_dup"])
                    elif count_winners(ws) >= 20:
                        st.info(T["mini_closed"])
                    else:
                        try:
                            append_entry(ws, nm.strip(), ph_norm, float(st.session_state.last_elapsed), st.session_state.shared, consult_flag="")
                            st.success("접수 완료! 커피쿠폰 발송 대상에 등록되었습니다.")
                        except Exception as e:
                            st.error(f"저장 중 오류: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

        elif st.session_state.last_result == "lose":
            st.info(T["lose_msg"])

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"### {T['consult_q']}")
            choice = st.radio("", [T["consult_o"], T["consult_x"]], horizontal=True, key="consult_choice")

            if choice == T["consult_o"]:
                nm = st.text_input("이름", value=(st.session_state.name or "").strip(), key="c_name")
                ph = st.text_input("전화번호", value="", key="c_phone")
                consent = st.checkbox(f"{T['privacy_title']}  \n{T['privacy_text']}", value=False, key="c_consent")

                if st.button(T["submit"], use_container_width=True, key="c_submit"):
                    if ws is None:
                        st.error(T["sheet_fail"])
                    else:
                        ph_norm = normalize_phone(ph)
                        if not consent:
                            st.warning("동의가 필요합니다.")
                        elif nm.strip() == "" or ph_norm == "":
                            st.warning("이름/전화번호를 정확히 입력해주세요.")
                        elif phone_exists(ws, ph_norm):
                            st.warning(T["mini_dup"])
                        else:
                            try:
                                append_entry(ws, nm.strip(), ph_norm, float(st.session_state.last_elapsed or 0.0), st.session_state.shared, consult_flag="O")
                                st.success("커피쿠폰 응모되었습니다.")
                            except Exception as e:
                                st.error(f"저장 중 오류: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button(T["reset"], use_container_width=True):
        reset_input_only_keep_minigame()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 13) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
