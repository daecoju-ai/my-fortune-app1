import json
import os
import re
import random
import hashlib
from datetime import datetime

import streamlit as st
from PIL import Image

# =========================================================
# 0) App Config
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로",
    page_icon="🔮",
    layout="centered",
)

# =========================================================
# 1) Paths
# =========================================================
ROOT = os.path.dirname(os.path.abspath(__file__))

FORTUNE_DB_PATH = os.path.join(ROOT, "fortunes_ko.json")              # 광범위 운세 DB (너가 만든 것)
TAROT_DB_PATH   = os.path.join(ROOT, "data", "tarot_db_ko.json")      # 타로 텍스트 DB (78장)
TAROT_ASSET_DIR = os.path.join(ROOT, "assets", "tarot")               # 이미지 폴더
TAROT_BACK_IMG  = os.path.join(TAROT_ASSET_DIR, "back.png")
TAROT_MAJORS_DIR = os.path.join(TAROT_ASSET_DIR, "majors")
TAROT_MINORS_DIR = os.path.join(TAROT_ASSET_DIR, "minors")

# =========================================================
# 2) Utils
# =========================================================
def normalize_text(s: str) -> str:
    return (s or "").strip()

def safe_int(s, default=0):
    try:
        return int(s)
    except Exception:
        return default

def safe_float(s, default=None):
    try:
        return float(s)
    except Exception:
        return default

def stable_hash_to_int(s: str) -> int:
    """파이썬 hash()는 실행마다 달라질 수 있으니 sha256으로 고정."""
    h = hashlib.sha256((s or "").encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def stable_seed(*parts) -> int:
    """
    같은 입력이면 항상 같은 seed가 나오도록:
    - 생년월일/이름/MBTI/띠/질문타입 등을 합쳐서 sha256 → int
    """
    combined = "||".join([str(p) for p in parts])
    return stable_hash_to_int(combined)

def load_json(path: str, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback

@st.cache_data(show_spinner=False)
def load_fortunes_db():
    return load_json(FORTUNE_DB_PATH, fallback={"meta": {}, "zodiac_mbti": {}, "fallback": {}})

@st.cache_data(show_spinner=False)
def load_tarot_db():
    return load_json(TAROT_DB_PATH, fallback={"meta": {}, "cards": []})

def image_exists(path: str) -> bool:
    try:
        return os.path.exists(path) and os.path.getsize(path) > 0
    except Exception:
        return False

def open_image(path: str):
    try:
        return Image.open(path)
    except Exception:
        return None

def inject_seo_hidden():
    # 프론트에 안보이게 head에만 주입 (height=0)
    desc = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘운세, 내일운세, 타로카드, 무료 운세"
    keywords = "2026 운세, 띠운세, MBTI 운세, 사주, 오늘 운세, 내일 운세, 타로, 연애운, 재물운, 직장운, 건강운, 무료"
    title = "2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로"

    st.components.v1.html(
        f"""
<script>
(function() {{
  try {{
    const metas = [
      ['name','description', {json.dumps(desc, ensure_ascii=False)}],
      ['name','keywords', {json.dumps(keywords, ensure_ascii=False)}],
      ['property','og:title', {json.dumps(title, ensure_ascii=False)}],
      ['property','og:description', {json.dumps(desc, ensure_ascii=False)}],
      ['property','og:type','website'],
      ['property','og:url', {json.dumps(APP_URL, ensure_ascii=False)}],
      ['name','robots','index,follow'],
      ['name','twitter:card','summary']
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

# =========================================================
# 3) UI Style (고급 카드 + 그라데이션 / 큰 틀 유지)
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2.5rem; max-width: 760px; }

.hero {
  border-radius: 22px;
  padding: 18px 16px;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
  color: white;
  text-align: center;
  box-shadow: 0 12px 30px rgba(0,0,0,0.18);
  margin-bottom: 14px;
}
.hero h1 { font-size: 1.55rem; font-weight: 900; margin: 0; }
.hero p { font-size: 0.95rem; opacity: 0.95; margin: 6px 0 0 0; }
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
  padding: 16px 14px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
}

.card-premium {
  border-radius: 20px;
  padding: 16px 14px;
  margin: 12px 0;
  background: linear-gradient(145deg, rgba(20,10,45,0.92), rgba(120,70,200,0.22));
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: 0 14px 40px rgba(0,0,0,0.20);
  color: white;
}

.card-premium .sub {
  opacity: 0.88;
  font-size: 0.95rem;
  line-height: 1.6;
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

hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }

.small-note { font-size: 0.92rem; opacity: 0.88; text-align:center; margin-top: 8px; }

.tarot-grid {
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}
.tarot-item {
  width: 210px;
  max-width: 48%;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  padding: 10px;
}
.tarot-title {
  font-weight: 900;
  margin-top: 8px;
  font-size: 1.05rem;
}
.tarot-meta {
  opacity: 0.85;
  font-size: 0.92rem;
  margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4) MBTI: Direct / 12 / 16 (변화 금지 요구 반영)
# =========================================================
MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

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
    ("JP", "일정이 확정되어야 안심", "상황에 따라 바뀌는 게 자연스럽다"),
]

def compute_mbti_from_answers(answers):
    # answers: list of (axis, pick_left_bool)
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
    return mbti if mbti in MBTI_TYPES else "ENFP"

# =========================================================
# 5) Zodiac
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL_KO = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
    "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠"
}
def calc_zodiac_key(year: int) -> str:
    return ZODIAC_ORDER[(year - 4) % 12]

# =========================================================
# 6) Fortune DB selection (생년월일 기반 "항상 동일" 고정)
# =========================================================
def pick_from_list_deterministic(items, seed_int: int):
    if not items:
        return None
    rng = random.Random(seed_int)
    return items[rng.randrange(0, len(items))]

def get_fortune_bundle(db: dict, zodiac_ko: str, mbti: str, y: int, m: int, d: int, name: str):
    """
    fortunes_ko.json의 구조는 너가 만든 버전 기준으로:
    db["zodiac_mbti"][ "<띠>_<MBTI>" ] 안에 항목들이 있다고 가정.
    fallback도 처리.
    """
    key = f"{zodiac_ko}_{mbti}"
    block = (db.get("zodiac_mbti") or {}).get(key)

    # seed: 생년월일+mbti+띠+이름
    base_seed = stable_seed(y, m, d, zodiac_ko, mbti, name)

    # DB가 없거나 key가 없으면 fallback 사용
    if not isinstance(block, dict):
        block = (db.get("fallback") or {})

    # 여기서는 "항목명"을 최대한 유연하게 뽑음 (DB가 조금 달라도 깨지지 않게)
    def pick(field, salt):
        items = block.get(field)
        if isinstance(items, list):
            return pick_from_list_deterministic(items, base_seed + salt)
        if isinstance(items, str) and items.strip():
            return items.strip()
        return None

    bundle = {
        "zodiac_fortune": pick("zodiac_fortune", 11) or pick("띠운세", 11) or "",
        "mbti_traits":    pick("mbti_traits", 22) or pick("mbti특징", 22) or "",
        "saju_one":       pick("saju_one", 33) or pick("사주한마디", 33) or "",
        "today":          pick("today", 44) or pick("오늘운세", 44) or "",
        "tomorrow":       pick("tomorrow", 55) or pick("내일운세", 55) or "",
        "year_all":       pick("year_all", 66) or pick("2026전체운세", 66) or "",
        "combo_advice":   pick("combo_advice", 77) or pick("조합조언", 77) or "",
        "action_tip":     pick("action_tip", 88) or pick("오늘의액션팁", 88) or "",
    }
    return bundle

# =========================================================
# 7) Tarot (78장) - 이미지 + 텍스트 / 정·역방향 / 질문유형
# =========================================================
def tarot_image_path(card: dict) -> str:
    """
    tarot_db_ko.json 카드 항목에서 파일명을 찾는 방식:
    - card["image"] 가 있으면 그걸 사용
    - 없으면 major/minor 추론해서 생성
    """
    img = card.get("image")
    if isinstance(img, str) and img.strip():
        # image에 "majors/00_the_fool.png" 같은 상대경로가 들어있다고 가정
        cand = os.path.join(TAROT_ASSET_DIR, img)
        return cand

    arcana = card.get("arcana")  # "major" / "minor"
    if arcana == "major":
        num = card.get("number")
        slug = card.get("slug") or ""
        if num is not None and slug:
            fn = f"{int(num):02d}_{slug}.png"
            return os.path.join(TAROT_MAJORS_DIR, fn)

    if arcana == "minor":
        suit = card.get("suit")   # wands/cups/swords/pentacles
        rank = card.get("rank")   # ace,2..10,page,knight,queen,king 등
        # 네가 56장 다 만들었다면 이 규칙대로 저장하는 걸 추천:
        # assets/tarot/minors/wands/ace.png ... /king.png
        if suit and rank:
            return os.path.join(TAROT_MINORS_DIR, suit, f"{rank}.png")

    return TAROT_BACK_IMG

def tarot_draw(db: dict, seed_int: int, n_cards: int = 1):
    cards = db.get("cards") or []
    if not isinstance(cards, list) or len(cards) == 0:
        return []

    rng = random.Random(seed_int)
    picks = []
    used = set()
    tries = 0
    while len(picks) < n_cards and tries < 5000:
        tries += 1
        idx = rng.randrange(0, len(cards))
        if idx in used:
            continue
        used.add(idx)
        c = cards[idx]
        reversed_flag = (rng.random() < 0.35)  # 역방향 확률
        picks.append((c, reversed_flag))
    return picks

def tarot_interpret(card: dict, reversed_flag: bool, topic: str):
    """
    tarot_db_ko.json 카드 구조를 최대한 유연하게 사용:
    - meaning_upright, meaning_reversed
    - topics: {love:..., money:..., work:..., health:...}
    """
    name = card.get("name_ko") or card.get("name") or "카드"
    upright = card.get("meaning_upright") or card.get("upright") or ""
    rev = card.get("meaning_reversed") or card.get("reversed") or ""

    base = rev if reversed_flag else upright
    topic_map = card.get("topics") or {}

    topic_text = ""
    if isinstance(topic_map, dict):
        topic_text = topic_map.get(topic, "")

    # 최종 텍스트 구성
    if topic_text and base:
        return name, base, topic_text
    if base:
        return name, base, ""
    return name, "해석 데이터가 없습니다.", ""

# =========================================================
# 8) Share button (네가 말한 '갤러리 공유 화면' = 시스템 공유시트)
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
      alert("이 기기/브라우저에서는 시스템 공유가 지원되지 않습니다.\\n(모바일 크롬/사파리에서 다시 시도해 주세요)");
      return;
    }}
    try {{
      await navigator.share({{ title: "2026 운세", text: url, url }});
      // 공유 성공 시 (재도전 1회 같은 로직은 여기서 shared=1로 넘겨 처리 가능)
      const u = new URL(window.location.href);
      u.searchParams.set("shared", "1");
      window.location.href = u.toString();
    }} catch (e) {{
      // 사용자가 취소하면 아무것도 안함
    }}
  }});
}})();
</script>
""",
        height=70
    )

# =========================================================
# 9) Session State
# =========================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"

if "name" not in st.session_state:
    st.session_state.name = ""

if "y" not in st.session_state:
    st.session_state.y = 2005
if "m" not in st.session_state:
    st.session_state.m = 1
if "d" not in st.session_state:
    st.session_state.d = 1

if "mbti_mode" not in st.session_state:
    st.session_state.mbti_mode = "direct"  # direct / 12 / 16
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFP"

# tarot state
if "tarot_topic" not in st.session_state:
    st.session_state.tarot_topic = "love"
if "tarot_spread" not in st.session_state:
    st.session_state.tarot_spread = 1
if "tarot_drawn" not in st.session_state:
    st.session_state.tarot_drawn = []  # list of dicts for rendering

# shared bonus example (재도전 1회 같은 구조에 쓰고 싶으면 여기서 저장)
qp = {}
try:
    qp = dict(st.query_params)
except Exception:
    try:
        qp = st.experimental_get_query_params()
    except Exception:
        qp = {}

shared_val = qp.get("shared", "0")
if isinstance(shared_val, list):
    shared_val = shared_val[0] if shared_val else "0"
if str(shared_val) == "1":
    # 지금은 “공유 성공 기록” 정도만 표시 (원하면 미니게임 재도전 로직에 연결하면 됨)
    st.toast("공유가 완료되었습니다 ✅")
    # shared 파라미터 제거
    try:
        st.query_params.pop("shared", None)
    except Exception:
        pass

# =========================================================
# 10) Load DB
# =========================================================
inject_seo_hidden()

fortune_db = load_fortunes_db()
tarot_db = load_tarot_db()

# =========================================================
# 11) Screens
# =========================================================
def render_input():
    st.markdown("""
    <div class="hero">
      <h1>🔮 2026 띠 + MBTI + 사주 + 오늘/내일 + 타로</h1>
      <p>완전 무료 · 같은 생년월일이면 결과가 항상 동일하게 나오도록 설계</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름 입력 (결과에 표시돼요)", value=st.session_state.name)

    st.markdown("<div class='card'><b>생년월일 입력</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.y = c1.number_input("년", min_value=1900, max_value=2030, value=int(st.session_state.y), step=1)
    st.session_state.m = c2.number_input("월", min_value=1, max_value=12, value=int(st.session_state.m), step=1)
    st.session_state.d = c3.number_input("일", min_value=1, max_value=31, value=int(st.session_state.d), step=1)

    st.markdown("<div class='card'><b>MBTI</b> (직접 선택 / 12문항 / 16문항)</div>", unsafe_allow_html=True)

    mode_label = {"direct":"직접 선택", "12":"간단 테스트 (12문항)", "16":"상세 테스트 (16문항)"}
    mode_opts = ["direct","12","16"]
    idx = mode_opts.index(st.session_state.mbti_mode) if st.session_state.mbti_mode in mode_opts else 0

    st.session_state.mbti_mode = mode_opts[
        st.radio("", [mode_label[m] for m in mode_opts], index=idx, horizontal=True).strip() and idx
    ] if False else st.session_state.mbti_mode

    # 위 라디오가 Streamlit 버전마다 가끔 꼬여서, 안정적으로 다시 매핑
    picked_label = st.radio("", [mode_label[m] for m in mode_opts], index=idx, horizontal=True, key="mbti_mode_radio")
    inv = {v:k for k,v in mode_label.items()}
    st.session_state.mbti_mode = inv.get(picked_label, "direct")

    if st.session_state.mbti_mode == "direct":
        mbti_idx = MBTI_TYPES.index(st.session_state.mbti) if st.session_state.mbti in MBTI_TYPES else MBTI_TYPES.index("ENFP")
        st.session_state.mbti = st.selectbox("MBTI 선택", MBTI_TYPES, index=mbti_idx)

    elif st.session_state.mbti_mode == "12":
        st.markdown("<div class='card'><b>MBTI 12문항</b> (각 축 3문항)</div>", unsafe_allow_html=True)
        answers = []
        for i, (axis, left_txt, right_txt) in enumerate(MBTI_Q_12, start=1):
            choice = st.radio(f"{i}. {axis}", [left_txt, right_txt], key=f"mbti12_{i}")
            answers.append((axis, choice == left_txt))
        if st.button("제출하고 MBTI 확정", use_container_width=True):
            st.session_state.mbti = compute_mbti_from_answers(answers)
            st.success(f"MBTI 확정: {st.session_state.mbti}")

    else:
        st.markdown("<div class='card'><b>MBTI 16문항</b> (각 축 4문항)</div>", unsafe_allow_html=True)
        answers = []
        q16 = MBTI_Q_12 + MBTI_Q_16_EXTRA
        for i, (axis, left_txt, right_txt) in enumerate(q16, start=1):
            choice = st.radio(f"{i}. {axis}", [left_txt, right_txt], key=f"mbti16_{i}")
            answers.append((axis, choice == left_txt))
        if st.button("제출하고 MBTI 확정", use_container_width=True):
            st.session_state.mbti = compute_mbti_from_answers(answers)
            st.success(f"MBTI 확정: {st.session_state.mbti}")

    st.markdown("<div class='bigbtn'>", unsafe_allow_html=True)
    if st.button("결과 보기", use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_result():
    name = normalize_text(st.session_state.name)
    y, m, d = int(st.session_state.y), int(st.session_state.m), int(st.session_state.d)
    mbti = st.session_state.mbti or "ENFP"

    zodiac_key = calc_zodiac_key(y)
    zodiac_ko = ZODIAC_LABEL_KO[zodiac_key]

    # ===== 운세: 생년월일 기반 seed 고정 =====
    fortune_bundle = get_fortune_bundle(
        fortune_db, zodiac_ko=zodiac_ko, mbti=mbti, y=y, m=m, d=d, name=name
    )

    display_name = f"{name}님" if name else ""
    st.markdown(f"""
    <div class="hero">
      <h1>{display_name} 2026 운세</h1>
      <p>{zodiac_ko} · {mbti}</p>
      <span class="badge">{y:04d}.{m:02d}.{d:02d}</span>
    </div>
    """, unsafe_allow_html=True)

    # ===== 결과 카드(프리미엄) =====
    st.markdown("<div class='card-premium'>", unsafe_allow_html=True)
    st.markdown(f"### ✨ 핵심 요약", unsafe_allow_html=True)
    st.markdown(f"<div class='sub'>"
                f"• <b>띠 운세</b>: {fortune_bundle.get('zodiac_fortune','')}"
                f"<br>• <b>MBTI 특징</b>: {fortune_bundle.get('mbti_traits','')}"
                f"<br>• <b>사주 한 마디</b>: {fortune_bundle.get('saju_one','')}"
                f"</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📌 오늘/내일", unsafe_allow_html=True)
    st.markdown(f"**오늘 운세**: {fortune_bundle.get('today','')}")
    st.markdown(f"**내일 운세**: {fortune_bundle.get('tomorrow','')}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("### 🧭 2026 전체 운세", unsafe_allow_html=True)
    st.markdown(f"{fortune_bundle.get('year_all','')}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🧩 조합 조언", unsafe_allow_html=True)
    st.markdown(f"{fortune_bundle.get('combo_advice','')}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("### ✅ 오늘의 액션팁", unsafe_allow_html=True)
    st.markdown(f"{fortune_bundle.get('action_tip','')}")
    st.markdown("</div>", unsafe_allow_html=True)

    # ===== 결과 바로 밑: 친구에게 공유하기 버튼(시스템 공유시트) =====
    share_button_native_only("📤 친구에게 공유하기")
    st.caption("버튼을 누르면 휴대폰 ‘공유’ 창(갤러리 공유처럼 뜨는 그 화면)이 열립니다.")

    # ===== 광고(다나눔렌탈) =====
    st.markdown("""
    <div class="adbox">
      <small style="font-weight:900;color:#e74c3c;">광고</small><br>
      <div style="font-size:1.15rem;font-weight:900;margin-top:6px;">
        다나눔렌탈 정수기 렌탈
      </div>
      <div style="margin-top:6px;">제휴카드시 <b>월 0원부터</b></div>
      <div>설치당일 <b>최대 50만원 + 사은품</b></div>
      <div style="margin-top:10px;">
        <a href="https://www.다나눔렌탈.com" target="_blank"
           style="display:inline-block;background:#ff8c50;color:white;
           padding:10px 16px;border-radius:999px;font-weight:900;text-decoration:none;">
          상담 신청하기
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ===== 타로 섹션 (1장/3장 + 질문유형 + 정/역 + 이미지) =====
    st.markdown("<div class='card-premium'>", unsafe_allow_html=True)
    st.markdown("### 🃏 타로카드 (고급 카드형)", unsafe_allow_html=True)
    st.markdown("<div class='sub'>질문 유형과 생년월일 기반으로 ‘같은 입력이면 항상 같은 카드’가 나오도록 고정됩니다.</div>", unsafe_allow_html=True)

    topic_label = {
        "love":"연애/관계",
        "money":"금전/재물",
        "work":"일/학업",
        "health":"건강"
    }
    colA, colB = st.columns(2)
    st.session_state.tarot_topic = colA.selectbox("질문 유형", list(topic_label.keys()),
                                                 format_func=lambda k: topic_label[k],
                                                 index=list(topic_label.keys()).index(st.session_state.tarot_topic)
                                                 if st.session_state.tarot_topic in topic_label else 0)
    st.session_state.tarot_spread = colB.selectbox("뽑는 장수", [1,3], index=0 if st.session_state.tarot_spread == 1 else 1)

    # draw button
    if st.button("타로 뽑기", use_container_width=True):
        # seed를 질문유형/뽑는장수까지 포함해서 고정
        seed_int = stable_seed("tarot", y, m, d, name, mbti, zodiac_ko, st.session_state.tarot_topic, st.session_state.tarot_spread)
        picks = tarot_draw(tarot_db, seed_int, n_cards=int(st.session_state.tarot_spread))

        drawn = []
        for card, revflag in picks:
            title, base_meaning, topic_meaning = tarot_interpret(card, revflag, st.session_state.tarot_topic)
            img_path = tarot_image_path(card)
            if not image_exists(img_path):
                img_path = TAROT_BACK_IMG

            drawn.append({
                "title": title,
                "reversed": bool(revflag),
                "base": base_meaning,
                "topic": topic_meaning,
                "img_path": img_path,
            })
        st.session_state.tarot_drawn = drawn
        st.rerun()

    # render drawn cards
    if st.session_state.tarot_drawn:
        st.markdown("<div class='tarot-grid'>", unsafe_allow_html=True)
        for item in st.session_state.tarot_drawn:
            st.markdown("<div class='tarot-item'>", unsafe_allow_html=True)
            img = open_image(item["img_path"])
            if img is not None:
                # 역방향이면 이미지를 회전
                if item["reversed"]:
                    img = img.rotate(180, expand=True)
                st.image(img, use_container_width=True)
            else:
                st.image(TAROT_BACK_IMG, use_container_width=True)

            st.markdown(f"<div class='tarot-title'>{item['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='tarot-meta'>{'역방향' if item['reversed'] else '정방향'} · {topic_label.get(st.session_state.tarot_topic,'')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='soft-box' style='margin-top:8px;'>{item['base']}</div>", unsafe_allow_html=True)
            if item["topic"]:
                st.markdown(f"<div class='soft-box' style='margin-top:8px;'><b>질문유형 해석</b><br>{item['topic']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ===== 다시하기 =====
    if st.button("처음부터 다시하기", use_container_width=True):
        # 전체 초기화(타로/운세 포함)
        keys_to_keep = []
        cur = dict(st.session_state)
        st.session_state.clear()
        for k in keys_to_keep:
            if k in cur:
                st.session_state[k] = cur[k]
        st.session_state.stage = "input"
        st.session_state.name = ""
        st.session_state.y, st.session_state.m, st.session_state.d = 2005, 1, 1
        st.session_state.mbti_mode = "direct"
        st.session_state.mbti = "ENFP"
        st.session_state.tarot_topic = "love"
        st.session_state.tarot_spread = 1
        st.session_state.tarot_drawn = []
        st.rerun()

    st.caption(APP_URL)

# =========================================================
# 12) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
