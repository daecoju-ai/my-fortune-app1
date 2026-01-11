# =========================================================
# app.py  (v2026.0005)
# =========================================================
# [고정 합의사항]
# - 디자인 임의 변경 금지 (그라데이션 + 카드형)
# - DB fallback / 자동 생성 금지
# - 오늘/내일/타로: 생년월일 기반 + 날짜 seed → 하루 고정
# - 타로: back.png → 5초 흔들림(mystery) → 앞면 reveal
# - reveal 사운드 길이는 기존 유지
# - 전체 코드 단일 파일 / 부분 생략 없음
# =========================================================

import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta
import json
import random
import hashlib
import base64
import re
from pathlib import Path

# =========================================================
# 0. 기본 설정
# =========================================================
APP_VERSION = "v2026.0005"
APP_TITLE = "2026 운세 | 띠 · MBTI · 사주 · 오늘/내일 · 타로"
APP_URL = "https://my-fortune.streamlit.app"
DANANEUM_URL = "https://incredible-dusk-20d2b5.netlify.app/"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🔮",
    layout="centered",
)

# =========================================================
# 1. 공통 유틸
# =========================================================
def stable_seed(*parts) -> int:
    raw = "|".join([str(p) for p in parts])
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def pick_one(pool, seed):
    if not isinstance(pool, list) or len(pool) == 0:
        return None
    r = random.Random(seed)
    return r.choice(pool)

def strip_html(text):
    if not text:
        return ""
    return re.sub(r"<[^>]*>", "", str(text)).strip()

def img_to_b64(path: Path):
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("ascii")

# =========================================================
# 2. DB 로딩 (fallback 금지)
# =========================================================
def load_json(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"DB 파일 없음: {path}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def load_dbs():
    return {
        "year": load_json("data/fortunes_ko_2026.json"),
        "today": load_json("data/fortunes_ko_today.json"),
        "tomorrow": load_json("data/fortunes_ko_tomorrow.json"),
        "zodiac": load_json("data/zodiac_fortunes_ko_2026.json"),
        "mbti": load_json("data/mbti_traits_ko.json"),
        "saju": load_json("data/saju_ko.json"),
        "tarot": load_json("data/tarot_db_ko.json"),
        "lny": load_json("data/lunar_new_year_1920_2026.json"),
    }

# =========================================================
# 3. 띠 계산 (한국 설 기준)
# =========================================================
ZODIAC_ORDER = [
    "rat","ox","tiger","rabbit","dragon","snake",
    "horse","goat","monkey","rooster","dog","pig"
]

ZODIAC_KO = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠",
    "dragon":"용띠","snake":"뱀띠","horse":"말띠","goat":"양띠",
    "monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠",
}

def zodiac_from_birth(birth: date, lny_map: dict):
    year = birth.year
    lny_date = date.fromisoformat(lny_map[str(year)])
    zodiac_year = year - 1 if birth < lny_date else year
    key = ZODIAC_ORDER[(zodiac_year - 4) % 12]
    return key, zodiac_year

# =========================================================
# 4. MBTI
# =========================================================
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]

def mbti_trait_text(mbti_db: dict, mbti: str):
    traits = mbti_db.get("traits", {})
    data = traits.get(mbti)
    if not data:
        return None
    keywords = " · ".join(data.get("keywords", []))
    tips = json.dumps(data.get("tips", []), ensure_ascii=False)
    return f"키워드: {keywords} {tips}"

# =========================================================
# 5. 타로 (하루 고정)
# =========================================================
def tarot_of_day(tarot_db: dict, seed: int):
    cards = tarot_db.get("majors", [])
    if not cards:
        return None
    return pick_one(cards, seed)

def tarot_ui(tarot_db, birth, name, mbti):
    st.markdown("### 🃏 오늘의 타로카드 (하루 1회 가능)")
    st.markdown("뒷면 카드를 보고 **뽑기**를 누르세요. 하루 동안 같은 카드가 유지됩니다.")

    if "tarot_open" not in st.session_state:
        st.session_state.tarot_open = False

    if st.button("타로카드 뽑기", use_container_width=True):
        st.session_state.tarot_open = True
        st.rerun()

    seed = stable_seed(birth, name, mbti, date.today(), "tarot")
    card = tarot_of_day(tarot_db, seed)

    back_b64 = img_to_b64(Path("assets/tarot/back.png"))
    front_b64 = img_to_b64(Path(card["image"])) if card else None

    if not back_b64:
        st.error("assets/tarot/back.png 파일이 없습니다.")
        return

    revealed = st.session_state.tarot_open

    tarot_html = f"""
    <div class="tarot-wrap">
      <img class="tarot-back {'shake' if revealed else ''}"
           src="data:image/png;base64,{back_b64}">
      {f'<img class="tarot-front" src="data:image/png;base64,{front_b64}">' if revealed and front_b64 else ''}
    </div>

    <style>
    .tarot-wrap {{
      position: relative;
      width: 320px;
      margin: 12px auto;
    }}
    .tarot-wrap img {{
      width: 100%;
      border-radius: 18px;
      box-shadow: 0 14px 32px rgba(0,0,0,0.25);
    }}
    .shake {{
      animation: shake 5s ease-in-out;
    }}
    .tarot-front {{
      position: absolute;
      inset: 0;
      animation: pop 0.4s ease-out forwards;
    }}
    @keyframes shake {{
      0%{{transform:rotate(0)}}
      20%{{transform:rotate(-2deg)}}
      40%{{transform:rotate(2deg)}}
      60%{{transform:rotate(-1deg)}}
      100%{{transform:rotate(0)}}
    }}
    @keyframes pop {{
      from{{opacity:0; transform:scale(0.96)}}
      to{{opacity:1; transform:scale(1)}}
    }}
    </style>
    """
    components.html(tarot_html, height=420)

    if revealed and card:
        st.markdown(f"**{card['name_ko']}**")
        st.markdown(card["upright"]["summary"])

# =========================================================
# 6. 광고
# =========================================================
def ad_block():
    st.markdown(
        f"""
        ---
        **[광고] 정수기 렌탈**  
        제휴카드 적용 시 **월 렌탈비 0원**, 설치당일 **최대 현금 50만원 + 사은품**  
        👉 [무료 상담하기]({DANANEUM_URL})
        """
    )

# =========================================================
# 7. 스타일 (고정)
# =========================================================
st.markdown("""
<style>
.header {
  background: linear-gradient(135deg,#a18cd1,#fbc2eb,#8ec5fc);
  color:white;
  padding:18px;
  border-radius:22px;
  text-align:center;
  margin-bottom:16px;
}
.card {
  background:white;
  padding:16px;
  border-radius:18px;
  box-shadow:0 10px 26px rgba(0,0,0,0.12);
  margin:12px 0;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 8. 세션 상태
# =========================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "name" not in st.session_state:
    st.session_state.name = ""
if "birth" not in st.session_state:
    st.session_state.birth = date(2000, 1, 1)
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFP"

# =========================================================
# 9. 화면
# =========================================================
dbs = load_dbs()

def render_input():
    st.markdown(
        f"""
        <div class="header">
          <h2>🔮 2026 운세</h2>
          <div>{APP_VERSION}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.name = st.text_input("이름", st.session_state.name)
    st.session_state.birth = st.date_input("생년월일", st.session_state.birth)
    st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, MBTI_LIST.index(st.session_state.mbti))

    if st.button("운세 보기", use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()

def render_result():
    name = st.session_state.name
    birth = st.session_state.birth
    mbti = st.session_state.mbti

    zodiac_key, zodiac_year = zodiac_from_birth(birth, dbs["lny"])
    zodiac_label = ZODIAC_KO[zodiac_key]

    base_seed = stable_seed(name, birth, mbti)

    zodiac_text = pick_one(dbs["zodiac"][zodiac_key], base_seed)
    mbti_text = mbti_trait_text(dbs["mbti"], mbti)
    saju_text = pick_one(dbs["saju"]["elements"][0]["pools"]["overall"], base_seed)
    today_text = pick_one(dbs["today"]["pools"]["today"], stable_seed(base_seed, date.today()))
    tomorrow_text = pick_one(dbs["tomorrow"]["pools"]["tomorrow"], stable_seed(base_seed, date.today()+timedelta(days=1)))
    year_text = pick_one(dbs["year"]["pools"]["year_all"], base_seed)

    st.markdown(
        f"""
        <div class="header">
          <h3>{name}님의 운세 결과</h3>
          <div>{zodiac_label} · {mbti} · {zodiac_year}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"**🧧 띠 운세**: {zodiac_text}")
    st.markdown(f"**🧠 MBTI 특징**: {mbti_text}")
    st.markdown(f"**🧾 사주 한 마디**: {saju_text}")
    st.markdown("---")
    st.markdown(f"**🌞 오늘 운세**: {today_text}")
    st.markdown(f"**🌙 내일 운세**: {tomorrow_text}")
    st.markdown(f"**📅 2026 전체 운세**: {year_text}")

    ad_block()
    tarot_ui(dbs["tarot"], birth, name, mbti)

    if st.button("입력 화면으로", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

# =========================================================
# 10. 실행
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
