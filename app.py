import json
import hashlib
import random
from datetime import date, datetime, timedelta

import streamlit as st


# =========================================================
# 0) Config
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일",
    page_icon="🔮",
    layout="centered",
)

# =========================================================
# 1) DB Loader (NO fallback)
# =========================================================
def load_json_required(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"필수 DB 파일을 읽을 수 없습니다: `{path}`\n\n에러: {e}")
        st.stop()


LNY_DB = load_json_required("data/lunar_new_year_1920_2026.json")
ZODIAC_DB = load_json_required("data/zodiac_fortunes_ko_2026.json")
TODAY_DB = load_json_required("data/fortunes_ko_today.json")
TOMORROW_DB = load_json_required("data/fortunes_ko_tomorrow.json")
YEAR_DB = load_json_required("data/fortunes_ko_2026_year.json")
MBTI_DB = load_json_required("data/mbti_traits_ko.json")
SAJU_DB = load_json_required("data/saju_ko.json")


# =========================================================
# 2) Seeded random (같은 입력이면 항상 같은 결과)
# =========================================================
def stable_seed(*parts: str) -> int:
    raw = "|".join([p if p is not None else "" for p in parts])
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def seeded_pick(pool: list[str], seed_key: str) -> str:
    if not isinstance(pool, list) or len(pool) == 0:
        st.error("DB 풀(pool)이 비어 있습니다. (JSON 확인 필요)")
        st.stop()
    r = random.Random(stable_seed(seed_key))
    return r.choice(pool)


# =========================================================
# 3) 음력 설(한국설) 기준 띠 계산
# =========================================================
ZODIAC_KEYS = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL_KO = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠",
    "dragon":"용띠","snake":"뱀띠","horse":"말띠","goat":"양띠",
    "monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠",
}

def parse_yyyy_mm_dd(s: str) -> date:
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))

def lunar_zodiac_key_for_birth(birth: date) -> tuple[str, int]:
    y = birth.year
    y_str = str(y)
    if y_str not in LNY_DB:
        st.error(f"음력설 DB에 {y}년 데이터가 없습니다. (지원 범위 밖)")
        st.stop()

    lny = parse_yyyy_mm_dd(LNY_DB[y_str])  # 그 해 음력설(한국설)
    zodiac_year = y - 1 if birth < lny else y
    idx = (zodiac_year - 4) % 12
    return ZODIAC_KEYS[idx], zodiac_year


# =========================================================
# 4) MBTI (직접 선택 + 12문항 + 16문항)
# =========================================================
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"
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
    ("JP","일정이 확정되어야 안심","상황에 따라 바뀌는 게 자연스럽다"),
]

def compute_mbti(answers: list[tuple[str, bool]]) -> str:
    scores = {"EI":0, "SN":0, "TF":0, "JP":0}
    counts = {"EI":0, "SN":0, "TF":0, "JP":0}
    for axis, left in answers:
        if axis in scores:
            counts[axis] += 1
            if left:
                scores[axis] += 1

    def decide(axis: str, left_char: str, right_char: str) -> str:
        if counts[axis] == 0:
            return left_char
        return left_char if scores[axis] >= (counts[axis]/2) else right_char

    mbti = f"{decide('EI','E','I')}{decide('SN','S','N')}{decide('TF','T','F')}{decide('JP','J','P')}"
    return mbti if mbti in MBTI_LIST else "ENFP"


# =========================================================
# 5) Style (큰틀 유지)
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
  display:inline-block; padding: 4px 10px; border-radius: 999px; font-size: 0.85rem;
  background: rgba(255,255,255,0.20); border: 1px solid rgba(255,255,255,0.25); margin-top: 10px;
}
.card { border-radius: 18px; padding: 18px 16px; box-shadow: 0 10px 28px rgba(0,0,0,0.10);
  border: 1px solid rgba(140,120,200,0.18); margin: 12px 0; }
.bg-zodiac { background: rgba(250,245,255,0.92); }
.bg-mbti   { background: rgba(245,255,250,0.92); }
.bg-saju   { background: rgba(245,250,255,0.92); }
.bg-today  { background: rgba(255,255,255,0.96); }
.bg-tom    { background: rgba(255,248,245,0.92); }
.bg-year   { background: rgba(255,252,240,0.92); }

.soft-box {
  background: rgba(245,245,255,0.78);
  border: 1px solid rgba(130,95,220,0.18);
  padding: 12px 12px;
  border-radius: 14px;
  line-height: 1.65;
  font-size: 1.0rem;
}
.bigbtn > button { border-radius: 999px !important; font-weight: 900 !important; padding: 0.75rem 1.2rem !important; }
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 6) Session
# =========================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFP"


# =========================================================
# 7) Input
# =========================================================
def render_input():
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 운세 | 띠 + MBTI + 사주 + 오늘/내일</p>
      <p class="hero-sub">음력 설(한국설) 기준 띠 적용</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름(선택)", value=st.session_state.get("name",""))

    st.session_state.birth = st.date_input(
        "생년월일",
        value=st.session_state.get("birth", date(2005,1,1)),
        min_value=date(1920,1,1),
        max_value=date(2026,12,31),
    )

    st.markdown("<div class='card'><b>MBTI를 어떻게 할까요?</b></div>", unsafe_allow_html=True)
    mode = st.radio(
        "",
        ["직접 선택", "간단 테스트(12문항)", "상세 테스트(16문항)"],
        index=st.session_state.get("mbti_mode_idx", 0),
        horizontal=True
    )
    st.session_state.mbti_mode_idx = ["직접 선택","간단 테스트(12문항)","상세 테스트(16문항)"].index(mode)

    if mode == "직접 선택":
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=MBTI_LIST.index(st.session_state.mbti))
    else:
        questions = MBTI_Q_12[:] + (MBTI_Q_16_EXTRA[:] if mode == "상세 테스트(16문항)" else [])
        answers = []
        st.markdown("<div class='card'><b>문항에 더 가까운 쪽을 선택하세요.</b></div>", unsafe_allow_html=True)
        for i, (axis, left, right) in enumerate(questions, start=1):
            pick = st.radio(f"{i}. {axis}", [left, right], index=0, key=f"mbti_{mode}_{i}")
            answers.append((axis, pick == left))
        if st.button("제출하고 MBTI 확정", use_container_width=True):
            st.session_state.mbti = compute_mbti(answers)
            st.success(f"확정 MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("2026년 운세 보기!", use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# 8) Result (띠/MBTI/사주/오늘/내일/2026전체 전부 DB)
# =========================================================
def require_pool(db: dict, path_hint: str, *keys: str) -> list[str]:
    cur = db
    for k in keys:
        cur = cur.get(k, None) if isinstance(cur, dict) else None
    if not isinstance(cur, list) or len(cur) == 0:
        st.error(f"DB 내용이 비어 있습니다: {path_hint} ({'.'.join(keys)})")
        st.stop()
    return cur

def render_result():
    birth: date = st.session_state.birth
    mbti: str = st.session_state.mbti
    name = (st.session_state.get("name","") or "").strip()

    zodiac_key, zodiac_year = lunar_zodiac_key_for_birth(birth)
    zodiac_label = ZODIAC_LABEL_KO.get(zodiac_key, zodiac_key)

    birth_key = birth.strftime("%Y-%m-%d")
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # ===== Pools (NO fallback) =====
    pool_today = require_pool(TODAY_DB, "data/fortunes_ko_today.json", "pools", "today")
    pool_tom = require_pool(TOMORROW_DB, "data/fortunes_ko_tomorrow.json", "pools", "tomorrow")
    pool_year = require_pool(YEAR_DB, "data/fortunes_ko_2026_year.json", "pools", "year_all")

    z = ZODIAC_DB.get(zodiac_key)
    if not isinstance(z, dict):
        st.error(f"띠 DB 키 없음: {zodiac_key} (data/zodiac_fortunes_ko_2026.json 확인)")
        st.stop()

    z_today_pool = z.get("today", [])
    z_tom_pool = z.get("tomorrow", [])
    z_year_pool = z.get("year_2026", [])
    z_advice_pool = z.get("advice", [])
    if not all(isinstance(p, list) and len(p) > 0 for p in [z_today_pool, z_tom_pool, z_year_pool, z_advice_pool]):
        st.error(f"띠 DB 풀 비어있음: {zodiac_key} (today/tomorrow/year_2026/advice 확인)")
        st.stop()

    mbti_obj = MBTI_DB.get(mbti)
    if not isinstance(mbti_obj, dict):
        st.error(f"MBTI DB 키 없음: {mbti} (data/mbti_traits_ko.json 확인)")
        st.stop()

    mbti_title = mbti_obj.get("title")
    mbti_traits = mbti_obj.get("traits")
    mbti_cautions = mbti_obj.get("cautions")
    mbti_action = mbti_obj.get("action_tips")
    if not (isinstance(mbti_title, str) and isinstance(mbti_traits, list) and isinstance(mbti_cautions, list) and isinstance(mbti_action, list)):
        st.error(f"MBTI DB 형식 오류: {mbti} (title/traits/cautions/action_tips 확인)")
        st.stop()

    saju_pool = require_pool(SAJU_DB, "data/saju_ko.json", "pools", "saju")

    # ===== Seeded picks =====
    msg_today = seeded_pick(pool_today, f"today|{birth_key}|{today.isoformat()}|{mbti}")
    msg_tom = seeded_pick(pool_tom, f"tomorrow|{birth_key}|{tomorrow.isoformat()}|{mbti}")
    msg_year = seeded_pick(pool_year, f"year2026|{birth_key}|{mbti}")

    z_msg_today = seeded_pick(z_today_pool, f"z_today|{birth_key}|{today.isoformat()}|{zodiac_key}")
    z_msg_tom = seeded_pick(z_tom_pool, f"z_tom|{birth_key}|{tomorrow.isoformat()}|{zodiac_key}")
    z_msg_year = seeded_pick(z_year_pool, f"z_year|{birth_key}|{zodiac_key}")
    z_advice = seeded_pick(z_advice_pool, f"z_adv|{birth_key}|{zodiac_key}|{mbti}")

    saju_msg = seeded_pick(saju_pool, f"saju|{birth_key}")

    # MBTI도 “고정 출력 + 액션팁은 seed로 1개만”
    mbti_action_one = seeded_pick(mbti_action, f"mbti_action|{birth_key}|{mbti}|{today.isoformat()}")

    title_name = f"{name}님 " if name else ""
    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{title_name}2026년 운세</p>
      <p class="hero-sub">{zodiac_label} (음력설 기준: {zodiac_year}년 띠) · {mbti}</p>
      <span class="badge">{birth_key}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card bg-zodiac'>", unsafe_allow_html=True)
    st.markdown(f"**🧧 띠 운세(오늘)**: {z_msg_today}")
    st.markdown(f"**🧧 띠 운세(내일)**: {z_msg_tom}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**🧧 2026 띠 전체 운세**: {z_msg_year}")
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**🧧 조언**: {z_advice}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card bg-mbti'>", unsafe_allow_html=True)
    st.markdown(f"**🧠 MBTI 특징 — {mbti_title}**")
    st.markdown("- " + "\n- ".join(mbti_traits))
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown("**⚠️ 주의 포인트**")
    st.markdown("- " + "\n- ".join(mbti_cautions))
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.markdown(f"**✅ 오늘의 액션팁(고정)**: {mbti_action_one}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card bg-saju'>", unsafe_allow_html=True)
    st.markdown(f"**🔎 사주 한 마디(고정)**: {saju_msg}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card bg-today'>", unsafe_allow_html=True)
    st.markdown(f"**☀️ 오늘 운세(고정)**: {msg_today}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card bg-tom'>", unsafe_allow_html=True)
    st.markdown(f"**🌙 내일 운세(고정)**: {msg_tom}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card bg-year'>", unsafe_allow_html=True)
    st.markdown(f"**📌 2026 전체 운세(고정)**: {msg_year}")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("입력 화면으로", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

    st.caption(APP_URL)


# =========================================================
# 9) Router
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
