import streamlit as st
from datetime import datetime, date, timedelta
import json
import re
import random
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
DB_PATH = "data/fortunes_ko.json"  # ✅ data 폴더 내부 고정
SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_NAME = "시트1"

st.set_page_config(
    page_title="2026 운세 | 띠+MBTI+사주+오늘/내일+타로",
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

def stable_seed_int(*parts: str) -> int:
    s = "||".join([str(p) for p in parts])
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def pick_seeded(pool: list, seed_value: int):
    if not isinstance(pool, list) or len(pool) == 0:
        return None
    rng = random.Random(seed_value)
    return pool[rng.randrange(0, len(pool))]

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
# 2) SEO Inject (코드에만, 화면엔 안보임)
# =========================================================
def inject_seo():
    description = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘운세, 내일운세, 무료 운세, 타로, 연애운, 재물운, 건강운"
    keywords = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, 무료 운세, 타로, 연애운, 재물운, 건강운, 네이버 운세, 구글 운세, 챗지피티 운세, 제미나이 운세"
    title = "2026 운세 | 띠+MBTI+사주+오늘/내일+타로"

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
# 3) DB Load (DB 없으면 추가 생성 금지)
# =========================================================
def load_db_or_stop():
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        if not isinstance(db, dict) or "pools" not in db:
            st.error("DB 형식이 올바르지 않습니다. data/fortunes_ko.json 구조를 확인해주세요.")
            st.stop()
        return db
    except FileNotFoundError:
        st.error("DB 파일이 없습니다. data/fortunes_ko.json 파일이 GitHub에 업로드되어 있는지 확인해주세요.")
        st.stop()
    except Exception as e:
        st.error(f"DB를 읽는 중 오류가 발생했습니다: {e}")
        st.stop()

# =========================================================
# 4) Google Sheet (컬럼은 기존 + 상담신청(O/X) + 품목을 뒤에 붙이는 방식)
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
        # 기록초가 어디에 있든 float 변환 가능한 값 중 승리구간이면 count (보수적)
        for cell in row:
            try:
                sec = float(cell)
                if 20.260 <= sec <= 20.269:
                    winners += 1
                    break
            except Exception:
                continue
    return winners

def phone_exists(ws, phone_norm: str) -> bool:
    if not phone_norm:
        return False
    values = read_all_rows(ws)
    for row in values[1:] if len(values) > 1 else []:
        for cell in row:
            if normalize_phone(cell) == phone_norm:
                return True
    return False

def append_entry(ws, name, phone, seconds, shared_bool, product_type, consult_ox):
    """
    ✅ 시트에 '뒤에' 붙여 저장하는 방식 (기존 컬럼 구조를 깨지 않도록)
    저장값(추가): 시간 | 이름 | 전화 | 기록초 | 공유여부 | 품목 | 상담신청(O/X)
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([
        now_str,
        name,
        phone,
        f"{float(seconds):.3f}",
        "TRUE" if shared_bool else "FALSE",
        product_type,
        consult_ox
    ])

# =========================================================
# 5) MBTI (직접/12/16 유지)
# =========================================================
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

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

def compute_mbti_from_answers(answers):
    scores = {"EI":0, "SN":0, "TF":0, "JP":0}
    counts = {"EI":0, "SN":0, "TF":0, "JP":0}
    for axis, pick_left in answers:
        counts[axis] += 1
        if pick_left:
            scores[axis] += 1

    def decide(axis, left_char, right_char):
        return left_char if scores[axis] >= (counts[axis] / 2) else right_char

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_LIST else "ENFP"

def render_mbti_test(questions, title, key_prefix):
    st.markdown(f"<div class='card'><b>{title}</b><br><span style='opacity:0.85;'>각 문항에서 더 가까운 쪽을 선택하세요.</span></div>", unsafe_allow_html=True)
    answers = []
    for i, (axis, left_txt, right_txt) in enumerate(questions, start=1):
        choice = st.radio(f"{i}.", options=[left_txt, right_txt], index=0, key=f"{key_prefix}_{i}")
        answers.append((axis, choice == left_txt))
    if st.button("제출하고 MBTI 확정", use_container_width=True, key=f"{key_prefix}_submit"):
        st.session_state.mbti = compute_mbti_from_answers(answers)
        return True
    return False

# =========================================================
# 6) Share Buttons (native share + url copy fallback)
# =========================================================
def share_buttons():
    st.components.v1.html(
        f"""
<div style="display:flex; gap:10px; margin: 10px 0;">
  <button id="btnShare" style="
    flex:1; width:100%;
    border:none;border-radius:999px;
    padding:12px 14px;
    font-weight:900;
    background:#6b4fd6;color:white;
    cursor:pointer;
  ">👥 친구에게 공유하기</button>

  <button id="btnCopy" style="
    flex:1; width:100%;
    border:none;border-radius:999px;
    padding:12px 14px;
    font-weight:900;
    background:#ffffff;color:#6b4fd6;
    border: 2px solid rgba(107,79,214,0.35);
    cursor:pointer;
  ">🔗 URL 복사</button>
</div>

<script>
(function() {{
  const url = {json.dumps(APP_URL, ensure_ascii=False)};

  function markShared() {{
    try {{
      const u = new URL(window.location.href);
      u.searchParams.set("shared","1");
      window.location.href = u.toString();
    }} catch(e) {{
      window.location.href = url + "?shared=1";
    }}
  }}

  const btnShare = document.getElementById("btnShare");
  const btnCopy  = document.getElementById("btnCopy");

  btnShare.addEventListener("click", async () => {{
    if (!navigator.share) {{
      alert("이 앱에서는 시스템 공유가 지원되지 않습니다. 대신 'URL 복사'를 눌러 공유해주세요.");
      return;
    }}
    try {{
      await navigator.share({{ title: "2026 운세", text: url, url }});
      markShared();
    }} catch (e) {{
      alert("카톡/브라우저 정책으로 공유가 막혔을 수 있어요. 'URL 복사'로 공유해주세요.");
    }}
  }});

  btnCopy.addEventListener("click", async () => {{
    try {{
      await navigator.clipboard.writeText(url);
      alert("URL이 복사되었습니다. 카톡 대화창에 붙여넣기 해주세요!");
      markShared(); // ✅ 우회 공유도 보너스 1회 인정
    }} catch(e) {{
      alert("복사 실패: 주소를 길게 눌러 복사해 주세요.\\n" + url);
      markShared();
    }}
  }});
}})();
</script>
""",
        height=80
    )

# =========================================================
# 7) Stopwatch Component (00.000 초만 / STOP 후 정지 유지 / 자동 기록 반영)
#    - START/STOP 한번 누르면 즉시 비활성화 표시
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
    font-size: 56px;
    letter-spacing: 1px;
    padding: 14px 10px;
    border-radius: 14px;
    background: rgba(245,245,255,0.85);
    border: 1px solid rgba(130,95,220,0.20);
    color: #1f1747;
  ">00.000</div>

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
    STOP을 누르면 기록이 자동 반영되고, 화면이 멈춘 상태로 유지됩니다.
  </div>
</div>

<script>
(function() {{
  const disabledAll = {disabled_all};
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const display = document.getElementById("display");

  if (disabledAll) {{
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
    return;
  }}

  let running = false;
  let startTime = 0;
  let rafId = null;

  function fmtSeconds(sec) {{
    const s = Math.max(0, sec);
    return s.toFixed(3).padStart(6,'0'); // 00.000 형식
  }}

  function tick() {{
    if (!running) return;
    const now = performance.now();
    const elapsed = (now - startTime) / 1000.0;
    display.textContent = fmtSeconds(elapsed);
    rafId = requestAnimationFrame(tick);
  }}

  function disableBoth() {{
    startBtn.disabled = true;
    stopBtn.disabled = true;
    startBtn.style.opacity = "0.55";
    stopBtn.style.opacity = "0.55";
    startBtn.style.cursor = "not-allowed";
    stopBtn.style.cursor = "not-allowed";
  }}

  startBtn.addEventListener("click", () => {{
    // ✅ START 한번 누르면 즉시 비활성화(연타 방지)
    startBtn.disabled = true;
    startBtn.style.opacity = "0.55";
    startBtn.style.cursor = "not-allowed";

    stopBtn.disabled = false;
    stopBtn.style.opacity = "1";
    stopBtn.style.cursor = "pointer";

    running = true;
    startTime = performance.now();
    display.textContent = "00.000";
    if (rafId) cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(tick);
  }});

  stopBtn.addEventListener("click", () => {{
    if (!running) return;

    // ✅ STOP 한번 누르면 즉시 비활성화(연타 방지)
    disableBoth();

    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    const now = performance.now();
    const elapsedSec = (now - startTime) / 1000.0;
    display.textContent = fmtSeconds(elapsedSec); // ✅ 멈춘 화면 유지

    const v = elapsedSec.toFixed(3);

    // ✅ t= 기록 + stopped=1 로 리다이렉트 → 파이썬에서 즉시 판정/차감
    try {{
      const u = new URL(window.location.href);
      u.searchParams.set("t", v);
      u.searchParams.set("stopped", "1");
      window.location.href = u.toString();
    }} catch (e) {{
      window.location.href = {json.dumps(APP_URL, ensure_ascii=False)} + "?t=" + v + "&stopped=1";
    }}
  }});
}})();
</script>
""",
        height=290
    )

# =========================================================
# 8) Tarot (하루 고정 랜덤 + 카드 뒷면→뽑기 애니메이션)
# =========================================================
TAROT_CARDS = [
    {"key":"the_sun","name":"The Sun","meaning":"성공·활력·긍정 에너지"},
    {"key":"the_moon","name":"The Moon","meaning":"직감·무의식·감정의 파도"},
    {"key":"the_star","name":"The Star","meaning":"희망·회복·치유"},
    {"key":"strength","name":"Strength","meaning":"용기·인내·내면의 힘"},
    {"key":"the_fool","name":"The Fool","meaning":"새 출발·자유·모험"},
    {"key":"the_magician","name":"The Magician","meaning":"집중·실현·가능성"},
    {"key":"justice","name":"Justice","meaning":"균형·판단·정의"},
    {"key":"the_world","name":"The World","meaning":"완성·성취·조화"},
]

def pick_daily_tarot(bday: date, mbti: str):
    today = date.today().isoformat()
    seed = stable_seed_int(str(bday), mbti, today, "tarot")
    idx = seed % len(TAROT_CARDS)
    return TAROT_CARDS[idx]

def tarot_ui(bday: date, mbti: str):
    card = pick_daily_tarot(bday, mbti)
    # 이미지 파일은 사용자가 assets에 올렸다는 전제(없으면 텍스트 카드로만 노출)
    back_path = "assets/tarot/back.png"
    front_path = f"assets/tarot/majors/{card['key']}.png"  # 필요시 파일명 맞춰 변경

    st.markdown("<div class='tarot-wrap'>", unsafe_allow_html=True)

    st.components.v1.html(
        f"""
<div style="display:flex; flex-direction:column; align-items:center; gap:10px;">
  <div id="tarotCard" style="
    width: 240px; height: 240px;
    border-radius: 16px;
    overflow:hidden;
    box-shadow: 0 14px 30px rgba(0,0,0,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    background: rgba(0,0,0,0.15);
    display:flex; align-items:center; justify-content:center;
  ">
    <img id="tarotImg" src="{back_path}" style="width:100%; height:100%; object-fit:cover;" />
  </div>

  <button id="drawBtn" style="
    width: 100%;
    max-width: 420px;
    border:none; border-radius: 999px;
    padding: 12px 14px;
    font-weight:900;
    background:#6b4fd6; color:white;
    cursor:pointer;
  ">🃏 타로 뽑기</button>

  <div id="tarotText" style="
    width:100%;
    max-width: 520px;
    display:none;
    margin-top: 6px;
    background: rgba(245,245,255,0.78);
    border: 1px solid rgba(130,95,220,0.18);
    padding: 12px 12px;
    border-radius: 14px;
    line-height: 1.65;
    text-align:center;
    font-weight:800;
    color:#2b2350;
  "></div>
</div>

<script>
(function() {{
  const drawBtn = document.getElementById("drawBtn");
  const tarotImg = document.getElementById("tarotImg");
  const tarotCard = document.getElementById("tarotCard");
  const tarotText = document.getElementById("tarotText");

  const front = {json.dumps(front_path, ensure_ascii=False)};
  const name = {json.dumps(card["name"], ensure_ascii=False)};
  const meaning = {json.dumps(card["meaning"], ensure_ascii=False)};

  let drawn = false;

  drawBtn.addEventListener("click", () => {{
    if (drawn) return;
    drawn = true;

    // 흔들림 애니메이션
    tarotCard.animate([
      {{ transform: "rotate(0deg) scale(1.00)" }},
      {{ transform: "rotate(-3deg) scale(1.02)" }},
      {{ transform: "rotate(3deg) scale(1.02)" }},
      {{ transform: "rotate(-2deg) scale(1.01)" }},
      {{ transform: "rotate(2deg) scale(1.01)" }},
      {{ transform: "rotate(0deg) scale(1.00)" }},
    ], {{ duration: 520, iterations: 1 }});

    setTimeout(() => {{
      tarotImg.src = front;

      // 뿅 느낌
      tarotCard.animate([
        {{ transform: "scale(0.96)" }},
        {{ transform: "scale(1.05)" }},
        {{ transform: "scale(1.00)" }},
      ], {{ duration: 340, iterations: 1 }});

      tarotText.style.display = "block";
      tarotText.innerHTML = "✨ <span style='font-size:1.05rem;'>" + name + "</span><br><span style='opacity:0.85;'>" + meaning + "</span>";
    }}, 420);
  }});
}})();
</script>
""",
        height=360
    )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 9) UI Style (디자인 큰틀 유지)
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
.result-card {
  border-radius: 18px;
  padding: 18px 16px;
  margin: 12px 0;
  color: #1d163f;
  border: 1px solid rgba(140,120,200,0.18);
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  background: linear-gradient(180deg, rgba(255,255,255,0.94) 0%, rgba(244,241,255,0.88) 100%);
}
.adbox {
  background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(255,242,235,0.92) 100%);
  border-radius: 18px;
  padding: 16px;
  margin: 12px 0;
  border: 2px solid rgba(255, 140, 80, 0.55);
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
  text-align:center;
}
.minibox {
  background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(240,248,255,0.92) 100%);
  border-radius: 18px;
  padding: 16px;
  margin: 12px 0;
  border: 1px solid rgba(140,120,200,0.18);
  box-shadow: 0 10px 28px rgba(0,0,0,0.08);
}
.small-note { font-size: 0.92rem; opacity: 0.88; text-align:center; margin-top: 8px; }
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 10) Session State
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "input"

if "name" not in st.session_state:
    st.session_state.name = ""

if "bday" not in st.session_state:
    st.session_state.bday = date(2005, 1, 1)

if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFP"

if "mbti_mode" not in st.session_state:
    st.session_state.mbti_mode = "direct"  # direct / 12 / 16

# 미니게임 상태(리셋해도 유지)
if "shared" not in st.session_state:
    st.session_state.shared = False

if "attempts_used" not in st.session_state:
    st.session_state.attempts_used = 0

if "last_stop_time" not in st.session_state:
    st.session_state.last_stop_time = None

if "last_stop_processed" not in st.session_state:
    st.session_state.last_stop_processed = None  # 중복 처리 방지용

if "game_result" not in st.session_state:
    st.session_state.game_result = None  # "win" / "lose" / None

# =========================================================
# 11) Shared param 처리 (보너스 1회)
# =========================================================
qp = get_query_params()
shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"

if str(shared_val) == "1":
    if not st.session_state.shared:
        st.session_state.shared = True
        safe_toast("공유 확인! 미니게임 1회 추가 지급 🎁")
    clear_param("shared")

# =========================================================
# 12) STOP param 처리 (자동기록/차감/판정)
# =========================================================
t_val = qp.get("t", None)
stopped_val = qp.get("stopped", None)

if isinstance(t_val, list):
    t_val = t_val[0] if t_val else None
if isinstance(stopped_val, list):
    stopped_val = stopped_val[0] if stopped_val else None

if (t_val is not None) and (str(stopped_val) == "1"):
    # 중복 처리 방지: 같은 t가 연속으로 들어오면 1번만 처리
    if st.session_state.last_stop_processed != str(t_val):
        try:
            stop_sec = float(str(t_val).strip())
            st.session_state.last_stop_time = float(f"{stop_sec:.3f}")
        except Exception:
            st.session_state.last_stop_time = None

        # ✅ 시도 차감은 STOP 때 즉시
        max_attempts = 1 + (1 if st.session_state.shared else 0)
        if st.session_state.attempts_used < max_attempts:
            st.session_state.attempts_used += 1

        # ✅ 성공/실패 판정
        if st.session_state.last_stop_time is not None and (20.260 <= st.session_state.last_stop_time <= 20.269):
            st.session_state.game_result = "win"
        else:
            st.session_state.game_result = "lose"

        st.session_state.last_stop_processed = str(t_val)

    clear_param("t")
    clear_param("stopped")

# =========================================================
# 13) Fortune compute (DB에서만)
# =========================================================
def compute_result(db: dict, name: str, bday: date, mbti: str) -> dict:
    pools = db.get("pools", {})

    # 필수 풀들 (없으면 “없음”이 아니라, 정확히 오류 메시지로 표시)
    need_keys = ["today", "tomorrow", "year_all", "saju_one_liner", "advice", "action_tip"]
    missing = [k for k in need_keys if k not in pools or not isinstance(pools.get(k), list) or len(pools.get(k)) == 0]
    if missing:
        return {"_db_error": f"DB에 필요한 풀이 비어있습니다: {', '.join(missing)}"}

    today_d = date.today()
    tomorrow_d = today_d + timedelta(days=1)

    base = f"{bday.isoformat()}|{mbti}"

    res = {
        "today": pick_seeded(pools["today"], stable_seed_int(base, today_d.isoformat(), "today")),
        "tomorrow": pick_seeded(pools["tomorrow"], stable_seed_int(base, tomorrow_d.isoformat(), "tomorrow")),
        "year_all": pick_seeded(pools["year_all"], stable_seed_int(base, "2026", "year_all")),
        "saju_one_liner": pick_seeded(pools["saju_one_liner"], stable_seed_int(base, "saju")),
        "advice": pick_seeded(pools["advice"], stable_seed_int(base, today_d.isoformat(), "advice")),
        "action_tip": pick_seeded(pools["action_tip"], stable_seed_int(base, today_d.isoformat(), "action_tip")),
    }
    return res

# =========================================================
# 14) Pages
# =========================================================
def reset_to_input_only():
    # ✅ 입력만 초기화 (게임 시도/공유는 유지)
    st.session_state.page = "input"
    st.session_state.name = ""
    st.session_state.bday = date(2005, 1, 1)
    st.session_state.mbti = "ENFP"
    st.session_state.mbti_mode = "direct"

def page_input(db: dict):
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 띠 + MBTI + 사주 + 오늘/내일 + 타로</p>
      <p class="hero-sub">완전 무료</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름 입력 (결과에 표시돼요)", value=st.session_state.name)

    st.markdown("<div class='card'><b>생년월일 입력</b></div>", unsafe_allow_html=True)
    st.session_state.bday = st.date_input("생년월일", value=st.session_state.bday, min_value=date(1900,1,1), max_value=date(2030,12,31))

    st.markdown("<div class='card'><b>MBTI를 어떻게 할까요?</b></div>", unsafe_allow_html=True)
    mode = st.radio(
        "",
        ["직접 선택", "간단 테스트 (12문항)", "상세 테스트 (16문항)"],
        index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
        horizontal=True
    )

    if mode == "직접 선택":
        st.session_state.mbti_mode = "direct"
        idx = MBTI_LIST.index(st.session_state.mbti) if st.session_state.mbti in MBTI_LIST else MBTI_LIST.index("ENFP")
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=idx)
    elif mode == "간단 테스트 (12문항)":
        st.session_state.mbti_mode = "12"
        done = render_mbti_test(MBTI_Q_12, "MBTI 12문항 (각 축 3문항)", "q12")
        if done:
            st.success(f"MBTI: {st.session_state.mbti}")
    else:
        st.session_state.mbti_mode = "16"
        questions = MBTI_Q_12 + MBTI_Q_16_EXTRA
        done = render_mbti_test(questions, "MBTI 16문항 (각 축 4문항)", "q16")
        if done:
            st.success(f"MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("2026년 운세 보기!", use_container_width=True):
        st.session_state.page = "result"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def page_result(db: dict):
    inject_seo()

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""

    mbti = st.session_state.mbti or "ENFP"
    bday = st.session_state.bday

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">{bday.isoformat()} · {mbti}</p>
      <span class="badge">🔮 타로 포함</span>
    </div>
    """, unsafe_allow_html=True)

    # 결과 생성
    res = compute_result(db, name, bday, mbti)
    if "_db_error" in res:
        st.error(res["_db_error"])
        st.stop()

    # ✅ 결과 카드(고급 카드 느낌 그라데이션)
    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown("**오늘 운세**")
    st.markdown(f"- {res['today']}")
    st.markdown("")
    st.markdown("**내일 운세**")
    st.markdown(f"- {res['tomorrow']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("**2026 전체 운세**")
    st.markdown(f"- {res['year_all']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown("**사주 한 마디**")
    st.markdown(f"- {res['saju_one_liner']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("**오늘의 액션팁**")
    st.markdown(f"- {res['action_tip']}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("**조언**")
    st.markdown(f"- {res['advice']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ✅ 결과창 바로 밑: 친구에게 공유하기
    share_buttons()
    st.caption("공유가 막히면 ‘URL 복사’로 공유해 주세요. 공유하면 도전 1회가 추가됩니다.")

    # ✅ 광고(다나눔렌탈) 복구
    st.markdown("""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">정수기 렌탈</div>
      <div style="margin-top:6px;">제휴카드시 월 0원부터</div>
      <div>설치당일 최대 50만원 + 사은품</div>
    </div>
    """, unsafe_allow_html=True)

    # 상담 신청 폼 (항상 가능: 게임과 별개)
    ws = get_sheet()
    if ws is None:
        st.warning("구글시트 연결이 아직 안 되어 있어요. (Secrets/시트 공유/탭 이름 확인)")
    else:
        with st.expander("📞 상담신청하기 (이름/연락처 입력)"):
            product_type = st.radio("품목 선택", ["정수기", "안마의자", "기타가전"], horizontal=True)
            c_name = st.text_input("이름", value=(name if name else ""))
            c_phone = st.text_input("연락처", value="")
            consent = st.checkbox("개인정보처리방침 동의(필수): 상담 안내를 위해 이름/연락처를 수집하며 목적 달성 후 지체없이 파기합니다.")
            if st.button("신청완료", use_container_width=True):
                pn = normalize_phone(c_phone)
                if not consent:
                    st.warning("동의가 필요합니다.")
                elif not c_name.strip() or not pn:
                    st.warning("이름/연락처를 정확히 입력해주세요.")
                else:
                    try:
                        append_entry(ws, c_name.strip(), pn, seconds="", shared_bool=st.session_state.shared, product_type=product_type, consult_ox="O")
                        st.success("상담 신청이 완료되었습니다.")
                    except Exception as e:
                        st.error(f"저장 중 오류: {e}")

    # ✅ 타로(하루 고정 랜덤)
    st.markdown("<div class='card'><b>오늘의 타로</b><br><span style='opacity:0.85;'>뒷면 카드에서 ‘타로 뽑기’를 누르면 오늘의 카드가 나옵니다. (하루 동안 고정)</span></div>", unsafe_allow_html=True)
    tarot_ui(bday, mbti)

    # ✅ 미니게임 (스톱워치 버전)
    st.markdown("<div class='minibox'>", unsafe_allow_html=True)
    st.markdown("### 🎁 미니게임: 선착순 커피쿠폰 이벤트")
    st.markdown("**커피쿠폰 선착순 지급 소진시 조기 종료될 수 있습니다.**")
    st.markdown("- 성공 구간: **20.260 ~ 20.269초**")
    st.markdown("- 기본 1회, **공유(또는 URL 복사)** 하면 1회 추가")
    st.markdown("</div>", unsafe_allow_html=True)

    # 조기 종료 체크
    event_closed = False
    if ws is not None:
        try:
            event_closed = (count_winners(ws) >= 20)
        except Exception:
            event_closed = False

    max_attempts = 1 + (1 if st.session_state.shared else 0)
    tries_left = max(0, max_attempts - st.session_state.attempts_used)

    st.markdown(
        f"<div class='small-note'>남은 시도: <b>{tries_left}</b> / {max_attempts}</div>",
        unsafe_allow_html=True
    )

    if event_closed:
        st.info("이벤트가 종료되었습니다. (선착순 마감)")
    else:
        # 스톱워치 표시
        stopwatch_component(tries_left=tries_left)

        # 판정 결과 문구 (STOP 시점 기록 포함)
        if st.session_state.last_stop_time is not None and st.session_state.game_result is not None:
            tsec = float(st.session_state.last_stop_time)
            if st.session_state.game_result == "win":
                st.success(f"성공! {tsec:.3f}초 기록. 쿠폰지급을 위해 이름, 전화번호 입력해주세요")
                # 성공자는 상담신청 기능 OFF (게임 응모 폼에서만 입력)
                if ws is None:
                    st.warning("구글시트 연결이 필요합니다. (Secrets/시트 공유 확인)")
                else:
                    with st.expander("🎉 당첨자 정보 입력", expanded=True):
                        w_name = st.text_input("이름", value=(name if name else ""), key="win_name")
                        w_phone = st.text_input("전화번호", value="", key="win_phone")
                        w_consent = st.checkbox("개인정보 수집·이용 동의(필수): 경품 발송을 위해 이름/전화번호를 수집하며 목적 달성 후 지체없이 파기합니다.", key="win_consent")
                        if st.button("제출", use_container_width=True, key="win_submit"):
                            pn = normalize_phone(w_phone)
                            if not w_consent:
                                st.warning("동의가 필요합니다.")
                            elif not w_name.strip() or not pn:
                                st.warning("이름/전화번호를 정확히 입력해주세요.")
                            else:
                                try:
                                    if phone_exists(ws, pn):
                                        st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                                    elif count_winners(ws) >= 20:
                                        st.info("이벤트가 종료되었습니다. (선착순 마감)")
                                    else:
                                        append_entry(ws, w_name.strip(), pn, seconds=tsec, shared_bool=st.session_state.shared, product_type="(쿠폰당첨)", consult_ox="X")
                                        st.success("접수 완료! 커피쿠폰 발송 대상에 등록되었습니다.")
                                except Exception as e:
                                    st.error(f"저장 중 오류: {e}")

            else:
                st.warning(f"실패! {tsec:.3f}초 기록. 친구공유시 도전기회 1회추가 또는 정수기렌탈 상담신청 후 커피쿠폰 응모")

                # 실패자: 상담신청 O/X 선택 → O면 쿠폰 응모로 저장, X면 저장 금지
                if ws is not None:
                    with st.expander("☕ 커피쿠폰 응모(상담신청) - 실패자만", expanded=True):
                        product_type = st.radio("품목 선택", ["정수기", "안마의자", "기타가전"], horizontal=True, key="lose_product")
                        lose_name = st.text_input("이름", value=(name if name else ""), key="lose_name")
                        lose_phone = st.text_input("전화번호", value="", key="lose_phone")
                        lose_consent = st.checkbox("개인정보 수집·이용 동의(필수): 쿠폰 응모/상담 안내를 위해 이름/전화번호를 수집합니다.", key="lose_consent")

                        ox = st.radio("상담신청", ["O", "X"], horizontal=True, key="lose_ox")

                        if st.button("확인", use_container_width=True, key="lose_submit"):
                            if ox == "X":
                                st.info("상담신청 X 선택 → 저장하지 않습니다.")
                            else:
                                pn = normalize_phone(lose_phone)
                                if not lose_consent:
                                    st.warning("동의가 필요합니다.")
                                elif not lose_name.strip() or not pn:
                                    st.warning("이름/전화번호를 정확히 입력해주세요.")
                                else:
                                    try:
                                        if phone_exists(ws, pn):
                                            st.warning("이미 참여한 번호입니다. (중복 참여 불가)")
                                        else:
                                            append_entry(ws, lose_name.strip(), pn, seconds=tsec, shared_bool=st.session_state.shared, product_type=product_type, consult_ox="O")
                                            st.success("커피쿠폰 응모가 완료되었습니다.")
                                    except Exception as e:
                                        st.error(f"저장 중 오류: {e}")

    # ✅ 입력만 초기화(게임 유지)
    if st.button("처음부터 다시하기(입력만)", use_container_width=True):
        reset_to_input_only()
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 15) Main
# =========================================================
db = load_db_or_stop()

if st.session_state.page == "input":
    page_input(db)
else:
    page_result(db)
