import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta
import json
import re
import random
import hashlib
from pathlib import Path

# =========================================================
# 0) 기본 설정
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"
DANANEUM_LANDING_URL = "https://incredible-dusk-20d2b5.netlify.app/"

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로",
    page_icon="🔮",
    layout="centered",
)

DATA_DIR = Path("data")

# =========================================================
# 1) DB 로더 (✅ 네가 준 파일명 8개로 고정)
# =========================================================
def load_json(path: str):
    fp = Path(path)
    if not fp.exists():
        raise FileNotFoundError(f"DB 파일을 찾지 못했습니다: {path}\n(data 폴더/파일명 확인)")
    with open(fp, "r", encoding="utf-8") as f:
        return json.load(f)

def load_all_dbs():
    paths = {
        "year": "data/fortunes_ko_2026.json",
        "today": "data/fortunes_ko_today.json",
        "tomorrow": "data/fortunes_ko_tomorrow.json",
        "lny": "data/lunar_new_year_1920_2026.json",
        "mbti": "data/mbti_traits_ko.json",
        "saju": "data/saju_ko.json",
        "tarot": "data/tarot_db_ko.json",
        "zodiac": "data/zodiac_fortunes_ko_2026.json",
    }

    dbs = {
        "fortunes_year": load_json(paths["year"]),
        "fortunes_today": load_json(paths["today"]),
        "fortunes_tomorrow": load_json(paths["tomorrow"]),
        "lunar_lny": load_json(paths["lny"]),
        "mbti_db": load_json(paths["mbti"]),
        "saju_db": load_json(paths["saju"]),
        "tarot_db": load_json(paths["tarot"]),
        "zodiac_db": load_json(paths["zodiac"]),
        "paths": paths
    }
    return dbs

# =========================================================
# 2) 유틸
# =========================================================
def stable_seed(*parts: str) -> int:
    s = "|".join([str(p) for p in parts])
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def pick_one(pool, seed_int: int):
    if not isinstance(pool, list) or len(pool) == 0:
        return None
    r = random.Random(seed_int)
    return r.choice(pool)

def safe_str(x):
    if x is None:
        return ""
    if isinstance(x, (dict, list)):
        return json.dumps(x, ensure_ascii=False)
    return str(x)

def strip_html_like(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]*>", "", text)
    return text.strip()

# =========================================================
# 3) 설 기준 띠
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL_KO = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
    "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠",
}

def parse_lny_map(lny_json):
    out = {}
    if isinstance(lny_json, dict):
        for y, dstr in lny_json.items():
            try:
                yy = int(str(y))
                parts = str(dstr).split("-")
                out[yy] = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except Exception:
                continue
    return out

def zodiac_key_from_year(gregorian_year: int) -> str:
    idx = (gregorian_year - 4) % 12
    return ZODIAC_ORDER[idx]

def zodiac_by_birth(birth: date, lny_map: dict) -> tuple[str, int]:
    y = birth.year
    lny = lny_map.get(y)
    zodiac_year = y
    if lny and birth < lny:
        zodiac_year = y - 1
    zk = zodiac_key_from_year(zodiac_year)
    return zk, zodiac_year

# =========================================================
# 3-1) 60갑자(사주 키) - 설 기준 연도
# =========================================================
HEAVENLY_STEMS = ["갑","을","병","정","무","기","경","신","임","계"]
EARTHLY_BRANCHES = ["자","축","인","묘","진","사","오","미","신","유","술","해"]

def ganji_from_year(year: int) -> str:
    stem = HEAVENLY_STEMS[(year - 4) % 10]
    branch = EARTHLY_BRANCHES[(year - 4) % 12]
    return f"{stem}{branch}"

# =========================================================
# 4) MBTI
# =========================================================
MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]

MBTI_Q16 = [
    ("EI","사람들과 함께 있을 때 에너지가 올라간다","혼자 있는 시간이 에너지를 채운다"),
    ("EI","처음 보는 사람과도 금방 친해지는 편이다","낯선 사람은 적응 시간이 필요하다"),
    ("EI","생각을 말하면서 정리하는 편이다","생각을 정리한 뒤 말하는 편이다"),
    ("EI","주말엔 약속이 있으면 좋다","주말엔 혼자 쉬고 싶다"),

    ("SN","구체적인 사실/데이터가 편하다","가능성/아이디어가 편하다"),
    ("SN","현재의 현실 문제 해결이 우선이다","미래의 큰 방향이 우선이다"),
    ("SN","경험을 기반으로 판단한다","직감/영감을 믿는 편이다"),
    ("SN","설명은 디테일이 중요하다","설명은 큰 그림이 중요하다"),

    ("TF","결정은 논리/원칙이 우선이다","결정은 사람/상황 배려가 우선이다"),
    ("TF","피드백은 직설이 좋다","피드백은 부드러운 방식이 좋다"),
    ("TF","갈등은 원인-해결이 핵심이다","갈등은 감정-관계가 핵심이다"),
    ("TF","공정함이 최우선이다","조화로움이 최우선이다"),

    ("JP","계획대로 진행해야 마음이 편하다","유연하게 바뀌어도 괜찮다"),
    ("JP","마감 전에 미리 끝내는 편이다","마감 직전에 몰아서 하는 편이다"),
    ("JP","정리/정돈이 되어야 편하다","어수선해도 진행 가능하다"),
    ("JP","일정이 확정되어야 안심된다","상황 따라 바뀌는 게 자연스럽다"),
]

def compute_mbti_from_answers(answers):
    scores = {"EI":0,"SN":0,"TF":0,"JP":0}
    counts = {"EI":0,"SN":0,"TF":0,"JP":0}
    for axis, pick_left in answers:
        if axis in scores:
            counts[axis] += 1
            if pick_left:
                scores[axis] += 1

    def decide(axis, left_char, right_char):
        if counts[axis] == 0:
            return left_char
        return left_char if scores[axis] >= (counts[axis]/2) else right_char

    mbti = (
        decide("EI","E","I") +
        decide("SN","S","N") +
        decide("TF","T","F") +
        decide("JP","J","P")
    )
    return mbti if mbti in MBTI_TYPES else "ENFP"

def normalize_mbti_key(m: str) -> str:
    return (m or "").strip().upper()

def mbti_summary_from_db(mbti_db: dict, mbti_key: str) -> str:
    if not isinstance(mbti_db, dict):
        return ""
    key = normalize_mbti_key(mbti_key)
    v = mbti_db.get(key)

    if not v:
        for k in mbti_db.keys():
            if str(k).strip().upper() == key:
                v = mbti_db.get(k)
                break

    if not v:
        return ""

    if isinstance(v, str):
        return strip_html_like(v)

    if isinstance(v, dict):
        for cand in ["summary", "description", "text"]:
            if isinstance(v.get(cand), str) and v.get(cand).strip():
                return strip_html_like(v.get(cand))
        return strip_html_like(safe_str(v))

    return strip_html_like(safe_str(v))

# =========================================================
# 5) 친구 공유 버튼
# =========================================================
def share_block():
    share_html = f"""
<div style="text-align:center; margin: 12px 0 6px 0;">
  <button id="btnShare" style="
    width:100%;
    border:none;border-radius:999px;
    padding:14px 16px;
    font-weight:900;
    background:#6b4fd6;color:white;
    cursor:pointer;
    box-shadow: 0 10px 26px rgba(0,0,0,0.10);
  ">친구에게 공유하기</button>
</div>

<div style="text-align:center; margin: 10px 0 0 0;">
  <button id="btnCopy" style="
    width:100%;
    border:1px solid rgba(120,90,210,0.25);
    border-radius:999px;
    padding:12px 16px;
    font-weight:900;
    background: rgba(255,255,255,0.85);
    color:#2b2350;
    cursor:pointer;
  ">URL 복사</button>
</div>

<div id="copy_toast" style="
  display:none;
  margin-top: 10px;
  font-weight:900;
  color:#2b2350;
  background: rgba(245,245,255,0.85);
  border: 1px solid rgba(130,95,220,0.20);
  border-radius: 14px;
  padding: 10px 12px;
">복사 완료! 카톡/문자에 붙여넣기 하세요.</div>

<script>
(function() {{
  const url = {json.dumps(APP_URL, ensure_ascii=False)};
  const btnShare = document.getElementById("btnShare");
  const btnCopy = document.getElementById("btnCopy");
  const toast = document.getElementById("copy_toast");

  btnShare.addEventListener("click", async () => {{
    try {{
      if (!navigator.share) {{
        await navigator.clipboard.writeText(url);
        toast.style.display = "block";
        return;
      }}
      await navigator.share({{ title: "2026 운세", text: url, url }});
    }} catch (e) {{
      try {{
        await navigator.clipboard.writeText(url);
        toast.style.display = "block";
      }} catch (e2) {{}}
    }}
  }});

  btnCopy.addEventListener("click", async () => {{
    try {{
      await navigator.clipboard.writeText(url);
      toast.style.display = "block";
    }} catch (e) {{
      const ta = document.createElement("textarea");
      ta.value = url;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      toast.style.display = "block";
    }}
  }});
}})();
</script>
"""
    components.html(share_html, height=170)

# =========================================================
# 6) 타로 (majors/minors/upright/reversed 대응)
# =========================================================
def build_tarot_deck(tarot_db):
    cards = []
    if isinstance(tarot_db, dict):
        if isinstance(tarot_db.get("majors"), list):
            cards.extend(tarot_db["majors"])
        if isinstance(tarot_db.get("minors"), list):
            cards.extend(tarot_db["minors"])
        if not cards and isinstance(tarot_db.get("cards"), list):
            cards = tarot_db["cards"]
    elif isinstance(tarot_db, list):
        cards = tarot_db

    cleaned = []
    for c in cards:
        if not isinstance(c, dict):
            continue
        name = c.get("name_ko") or c.get("name") or c.get("title") or c.get("card") or c.get("name_en")
        if not name:
            continue
        upright = c.get("upright") if isinstance(c.get("upright"), dict) else {}
        reversed_ = c.get("reversed") if isinstance(c.get("reversed"), dict) else {}
        cleaned.append({
            "name": strip_html_like(str(name)),
            "name_en": strip_html_like(str(c.get("name_en") or "")),
            "keywords": c.get("keywords") if isinstance(c.get("keywords"), list) else [],
            "upright": upright,
            "reversed": reversed_,
            "fallback": strip_html_like(str(c.get("meaning") or c.get("desc") or c.get("text") or "")),
        })
    return cleaned

def format_tarot_meaning(card: dict, is_reversed: bool) -> str:
    if not card:
        return ""
    if card.get("fallback"):
        return card["fallback"]

    block = card.get("reversed") if is_reversed else card.get("upright")
    if not isinstance(block, dict):
        block = {}

    parts = []
    if card.get("keywords"):
        kw = ", ".join([strip_html_like(str(x)) for x in card["keywords"] if str(x).strip()])
        if kw:
            parts.append(f"키워드: {kw}")

    for k in ["summary", "love", "work", "money"]:
        v = block.get(k)
        if isinstance(v, str) and v.strip():
            if k == "summary":
                parts.append(strip_html_like(v))
            elif k == "love":
                parts.append(f"연애: {strip_html_like(v)}")
            elif k == "work":
                parts.append(f"일/학업: {strip_html_like(v)}")
            elif k == "money":
                parts.append(f"금전: {strip_html_like(v)}")

    return "\n".join(parts).strip()

def get_tarot_of_day(tarot_db: dict, user_seed: int, today: date):
    deck = build_tarot_deck(tarot_db)
    if not deck:
        return None

    seed_int = stable_seed(str(today), str(user_seed), "tarot")
    r = random.Random(seed_int)
    card = r.choice(deck)
    is_reversed = r.choice([False, True])
    meaning = format_tarot_meaning(card, is_reversed) or "해석 문장을 불러오지 못했습니다. (tarot_db_ko.json 확인)"

    title = card.get("name", "")
    if card.get("name_en"):
        title = f"{title} ({card.get('name_en')})"
    if is_reversed:
        title = f"{title} · 역방향"

    return {"title": title, "meaning": meaning}

def tarot_ui(tarot_db: dict, birth: date):
    st.markdown("<div class='card tarot-card'>", unsafe_allow_html=True)
    st.markdown("### 🃏 오늘의 타로카드", unsafe_allow_html=True)
    st.markdown("<div class='soft-box'>뒷면 카드를 보고, <b>뽑기</b>를 누르면 오늘의 카드가 공개됩니다. (하루 동안 고정)</div>", unsafe_allow_html=True)

    # 뒷면 이미지가 없으면 기존 그라데이션 박스
    back_path_candidates = [
        "assets/tarot/back.png",
        "assets/tarot/back.jpg",
        "assets/tarot/back.webp",
        "assets/tarot/back.jpeg",
    ]
    back_found = None
    for p in back_path_candidates:
        if Path(p).exists():
            back_found = p
            break

    if back_found:
        st.image(back_found, use_container_width=True)
    else:
        st.markdown(
            "<div style='height:220px;border-radius:18px;"
            "background:linear-gradient(135deg,#2b2350,#6b4fd6,#fbc2eb);"
            "display:flex;align-items:center;justify-content:center;"
            "color:white;font-weight:900;font-size:1.2rem;'>TAROT BACK</div>",
            unsafe_allow_html=True
        )

    if "tarot_revealed" not in st.session_state:
        st.session_state.tarot_revealed = False

    if st.button("타로카드 뽑기", use_container_width=True):
        st.session_state.tarot_revealed = True

    if st.session_state.tarot_revealed:
        user_seed = stable_seed(str(birth), "user")
        card = get_tarot_of_day(tarot_db, user_seed, date.today())
        if not card:
            st.info("타로 DB에서 카드를 불러오지 못했습니다. (tarot_db_ko.json 확인)")
        else:
            st.markdown(
                f"""
                <div class="reveal">
                  <div class="reveal-title">✨ {strip_html_like(card['title'])}</div>
                  <div class="reveal-meaning">{strip_html_like(card['meaning']).replace("\n","<br>")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 7) 다나눔렌탈 광고
# =========================================================
def dananeum_ad_block():
    st.markdown(
        f"""
        <div class="adbox">
          <div class="ad-badge">광고</div>
          <div class="ad-title">[광고] 정수기 렌탈</div>
          <div class="ad-body">
            제휴카드 적용시 <b>월 렌탈비 0원</b>, 설치당일 <b>최대 현금50만원</b> + <b>사은품 증정</b>
          </div>
          <div style="margin-top:12px;">
            <a class="ad-btn" href="{DANANEUM_LANDING_URL}" target="_blank">무료 상담하기</a>
          </div>
          <div class="ad-sub">이름/전화번호 작성 · 개인정보처리방침 동의 후 신청완료</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# 8) 스타일 (✅ 수정 금지: 너가 고정하자고 한 UI 그대로)
# =========================================================
st.markdown("""
<style>
.block-container { padding-top: 1.0rem; padding-bottom: 2.2rem; max-width: 720px; }

.header-hero {
  border-radius: 22px;
  padding: 18px 16px;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 45%, #8ec5fc 100%);
  color: white;
  text-align: center;
  box-shadow: 0 12px 30px rgba(0,0,0,0.18);
  margin-bottom: 14px;
}
.hero-title { font-size: 1.55rem; font-weight: 900; margin: 0; }
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
  background: linear-gradient(135deg, rgba(245,245,255,0.96), rgba(255,255,255,0.96));
  border-radius: 18px;
  padding: 18px 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18);
  margin: 12px 0;
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
  padding: 0.78rem 1.15rem !important;
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
.ad-badge{
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 900;
  background: rgba(255,140,80,0.18);
  border: 1px solid rgba(255,140,80,0.35);
  color:#c0392b;
}
.ad-title{
  margin-top: 8px;
  font-weight: 900;
  font-size: 1.15rem;
  color:#2b2350;
}
.ad-body{
  margin-top: 8px;
  font-size: 0.98rem;
  color:#2b2350;
  line-height:1.6;
}
.ad-btn{
  display:inline-block;
  background:#ff8c50;
  color:white;
  padding:10px 18px;
  border-radius:999px;
  font-weight:900;
  text-decoration:none;
  box-shadow: 0 10px 26px rgba(0,0,0,0.10);
}
.ad-sub{
  margin-top: 10px;
  font-size: 0.86rem;
  opacity: 0.85;
}

.reveal{
  margin-top: 12px;
  border-radius: 18px;
  padding: 14px 14px;
  background: rgba(245,245,255,0.85);
  border: 1px solid rgba(130,95,220,0.18);
  animation: pop 0.25s ease-out;
}
.reveal-title{
  font-weight: 900;
  font-size: 1.2rem;
  color:#2b2350;
}
.reveal-meaning{
  margin-top: 8px;
  line-height: 1.7;
  color:#1f1747;
}
@keyframes pop{
  from { transform: scale(0.97); opacity: 0.5; }
  to { transform: scale(1.0); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 9) 세션 상태
# =========================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "name" not in st.session_state:
    st.session_state.name = ""
if "birth" not in st.session_state:
    st.session_state.birth = date(2005, 1, 1)
if "mbti_mode" not in st.session_state:
    st.session_state.mbti_mode = "direct"
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFP"

# =========================================================
# 10) 입력 화면
# =========================================================
def render_input(dbs):
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로</p>
      <p class="hero-sub">이름 + 생년월일 + MBTI로 결과가 고정 출력됩니다</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름", value=st.session_state.name, placeholder="예) 홍길동")

    st.session_state.birth = st.date_input(
        "생년월일",
        value=st.session_state.birth,
        min_value=date(1920, 1, 1),
        max_value=date(2026, 12, 31),
    )

    lny_map = parse_lny_map(dbs["lunar_lny"])
    zk, zy = zodiac_by_birth(st.session_state.birth, lny_map)

    st.markdown(
        f"<div class='card'><b>자동 띠 결정(한국 설 기준)</b><br>"
        f"<div class='soft-box'>당신의 띠: <b>{ZODIAC_LABEL_KO.get(zk, zk)}</b> (기준년도: {zy}년)</div></div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='card'><b>MBTI</b></div>", unsafe_allow_html=True)

    mode = st.radio(
        "MBTI를 어떻게 할까요?",
        ["직접 선택", "16문항 테스트"],
        index=0 if st.session_state.mbti_mode == "direct" else 1,
        horizontal=True
    )
    st.session_state.mbti_mode = "direct" if mode == "직접 선택" else "q16"

    if st.session_state.mbti_mode == "direct":
        cur = normalize_mbti_key(st.session_state.mbti)
        if cur not in MBTI_TYPES:
            cur = "ENFP"
        st.session_state.mbti = st.selectbox("MBTI 직접 선택", MBTI_TYPES, index=MBTI_TYPES.index(cur))

        preview = mbti_summary_from_db(dbs["mbti_db"], st.session_state.mbti)
        if preview:
            st.markdown(f"<div class='soft-box'><b>{st.session_state.mbti}</b> · {preview}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='soft-box'>각 문항에서 더 가까운 쪽을 선택하세요. 제출하면 MBTI가 확정됩니다.</div>", unsafe_allow_html=True)
        answers = []
        for i, (axis, left, right) in enumerate(MBTI_Q16, start=1):
            choice = st.radio(f"{i}.", [left, right], key=f"mbti16_{i}")
            answers.append((axis, choice == left))

        if st.button("제출하고 MBTI 확정", use_container_width=True):
            st.session_state.mbti = compute_mbti_from_answers(answers)
            st.success(f"확정된 MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("운세 보기", use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 11) 결과 화면 (띠/MBTI/사주 + 타로 오류만 해결)
# =========================================================
def render_result(dbs):
    name = (st.session_state.name or "").strip()
    birth = st.session_state.birth
    mbti = normalize_mbti_key(st.session_state.mbti) or "ENFP"
    if mbti not in MBTI_TYPES:
        mbti = "ENFP"

    lny_map = parse_lny_map(dbs["lunar_lny"])
    zodiac_key, zodiac_year = zodiac_by_birth(birth, lny_map)
    zodiac_label = ZODIAC_LABEL_KO.get(zodiac_key, zodiac_key)

    base_seed = stable_seed(str(birth), name, mbti)

    # ✅ 1) 띠 운세: zodiac_fortunes_ko_2026 구조 대응
    zodiac_text = None
    zdb = dbs["zodiac_db"]
    if isinstance(zdb, dict):
        animal = zdb.get(zodiac_key)
        if isinstance(animal, dict):
            for k in ["year_2026", "advice", "today", "tomorrow"]:
                arr = animal.get(k)
                if isinstance(arr, list) and arr:
                    pool = [strip_html_like(safe_str(x)) for x in arr if safe_str(x).strip()]
                    zodiac_text = pick_one(pool, stable_seed(str(base_seed), "zodiac", k))
                    if zodiac_text:
                        break

    # ✅ 2) MBTI 특징
    mbti_trait = mbti_summary_from_db(dbs["mbti_db"], mbti)

    # ✅ 3) 사주 한마디: saju_ko 구조(60갑자키) 대응
    saju_text = None
    sdb = dbs["saju_db"]
    if isinstance(sdb, dict):
        g = ganji_from_year(zodiac_year)  # 설 기준 연도로 갑자 계산
        v = sdb.get(g)
        if isinstance(v, dict):
            if isinstance(v.get("one_liner"), str) and v.get("one_liner").strip():
                saju_text = strip_html_like(v.get("one_liner"))
            else:
                for cand in ["summary", "description", "text"]:
                    if isinstance(v.get(cand), str) and v.get(cand).strip():
                        saju_text = strip_html_like(v.get(cand))
                        break

    # 오늘/내일
    today = date.today()
    tomorrow = today + timedelta(days=1)

    def get_pool_from_fortune_db(fdb, key_name):
        pool = []
        if isinstance(fdb, dict):
            if isinstance(fdb.get("pools"), dict) and isinstance(fdb["pools"].get(key_name), list):
                pool = fdb["pools"][key_name]
            elif isinstance(fdb.get(key_name), list):
                pool = fdb[key_name]
            elif isinstance(fdb.get("lines"), list):
                pool = fdb["lines"]
        elif isinstance(fdb, list):
            pool = fdb
        return [strip_html_like(safe_str(x)) for x in pool if safe_str(x).strip()]

    today_pool = get_pool_from_fortune_db(dbs["fortunes_today"], "today")
    tomorrow_pool = get_pool_from_fortune_db(dbs["fortunes_tomorrow"], "tomorrow")

    today_text = pick_one(today_pool, stable_seed(str(base_seed), str(today), "today"))
    tomorrow_text = pick_one(tomorrow_pool, stable_seed(str(base_seed), str(tomorrow), "tomorrow"))

    # 2026 전체 운세
    year_pool = []
    ydb = dbs["fortunes_year"]
    if isinstance(ydb, dict):
        if isinstance(ydb.get("pools"), dict) and isinstance(ydb["pools"].get("year_all"), list):
            year_pool = ydb["pools"]["year_all"]
        elif isinstance(ydb.get("year_all"), list):
            year_pool = ydb["year_all"]
        elif isinstance(ydb.get("lines"), list):
            year_pool = ydb["lines"]
    elif isinstance(ydb, list):
        year_pool = ydb

    year_pool = [strip_html_like(safe_str(x)) for x in year_pool if safe_str(x).strip()]
    year_text = pick_one(year_pool, stable_seed(str(base_seed), "year_2026"))

    def ensure_text(val, label):
        if val and str(val).strip():
            return val
        return f"{label} 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"

    zodiac_text = ensure_text(zodiac_text, "띠 운세")
    mbti_trait = ensure_text(mbti_trait, "MBTI 특징")
    saju_text = ensure_text(saju_text, "사주 한 마디")
    today_text = ensure_text(today_text, "오늘 운세")
    tomorrow_text = ensure_text(tomorrow_text, "내일 운세")
    year_text = ensure_text(year_text, "2026 전체 운세")

    display_name = f"{name}님" if name else "당신"
    st.markdown(
        f"""
        <div class="header-hero">
          <p class="hero-title">{display_name}의 운세 결과</p>
          <p class="hero-sub">{zodiac_label} · {mbti} · (설 기준 띠년도 {zodiac_year})</p>
          <span class="badge">2026</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.markdown(f"**🧧 띠 운세**: {zodiac_text}")
    st.markdown(f"**🧠 MBTI 특징**: {mbti_trait}")
    st.markdown(f"**🧾 사주 한 마디**: {saju_text}")
    st.markdown("---")
    st.markdown(f"**🌞 오늘 운세**: {today_text}")
    st.markdown(f"**🌙 내일 운세**: {tomorrow_text}")
    st.markdown("---")
    st.markdown(f"**📅 2026 전체 운세**: {year_text}")
    st.markdown("</div>", unsafe_allow_html=True)

    share_block()
    dananeum_ad_block()
    tarot_ui(dbs["tarot_db"], birth)

    if st.button("입력 화면으로", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

    with st.expander("DB 연결 상태(확인용)"):
        st.write(dbs["paths"])

# =========================================================
# 12) 실행
# =========================================================
try:
    dbs = load_all_dbs()
except Exception as e:
    st.error(str(e))
    st.stop()

if st.session_state.stage == "input":
    render_input(dbs)
else:
    render_result(dbs)
