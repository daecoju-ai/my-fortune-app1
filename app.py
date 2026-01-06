import json
import os
import re
import hashlib
from datetime import date, datetime, timedelta

import streamlit as st


# =========================================================
# 0) 고정 설정 (1번만)
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"  # 필요하면 너 주소로 유지/수정
DATA_DIR = "data"

DB_TODAY_PATH = os.path.join(DATA_DIR, "fortunes_ko_today.json")
DB_TOMORROW_PATH = os.path.join(DATA_DIR, "fortunes_ko_tomorrow.json")
DB_YEAR_PATH = os.path.join(DATA_DIR, "fortunes_ko_2026_year.json")

# 키 이름 고정(혼용 금지)
KEY_TODAY = "today"
KEY_TOMORROW = "tomorrow"
KEY_YEAR_ALL = "year_all"

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로",
    page_icon="🔮",
    layout="centered"
)

# =========================================================
# 1) 디자인(사용자가 좋아한 스타일 유지 전제)
#    - 여기선 1번만 구현이 목표라서: 기존 CSS가 이미 있었다면 그대로 붙여넣어도 됨
#    - 현재는 최소한의 카드 스타일만 넣음(크게 바꾸지 않음)
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
  line-height: 1.7;
  font-size: 1.0rem;
}
.bigbtn > button {
  border-radius: 999px !important;
  font-weight: 900 !important;
  padding: 0.75rem 1.2rem !important;
}
hr.soft { border:0; height:1px; background: rgba(120, 90, 210, 0.15); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 2) 1번 핵심: DB 로드 + 안정 해시 seed 선택
# =========================================================
def _read_json_or_fail(path: str) -> dict:
    if not os.path.exists(path):
        st.error(f"DB 파일이 없습니다: `{path}`\n\n- GitHub에 `data/` 폴더 만들고 파일 업로드했는지 확인하세요.")
        st.stop()

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"DB 파일을 JSON으로 읽는 중 오류가 났습니다: `{path}`\n\n오류: {e}")
        st.stop()


def _get_pool(db: dict, pool_key: str, path_for_msg: str) -> list:
    if not isinstance(db, dict):
        st.error(f"DB 구조가 dict가 아닙니다: `{path_for_msg}`")
        st.stop()

    pools = db.get("pools")
    if not isinstance(pools, dict):
        st.error(f"DB에 `pools`가 없습니다 또는 dict가 아닙니다: `{path_for_msg}`")
        st.stop()

    arr = pools.get(pool_key)
    if not isinstance(arr, list) or len(arr) == 0:
        st.error(
            f"DB에 `pools.{pool_key}` 리스트가 비어있거나 없습니다.\n\n"
            f"- 파일: `{path_for_msg}`\n"
            f"- 필요한 키: `pools.{pool_key}`"
        )
        st.stop()

    # 각 항목은 문자열이길 권장 (텍스트)
    bad = [i for i, x in enumerate(arr[:50]) if not isinstance(x, str)]
    if bad:
        st.error(
            f"`pools.{pool_key}` 안에 문자열이 아닌 항목이 있습니다(예: index {bad[:5]}).\n\n"
            f"- 파일: `{path_for_msg}`"
        )
        st.stop()

    return arr


def stable_index(seed: str, n: int) -> int:
    # 파이썬 내장 hash() 금지 → sha256 안정 해시 사용
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    # 앞 16 hex만으로도 충분히 균등
    v = int(h[:16], 16)
    return v % n


def pick_seeded(pool: list, seed: str) -> str:
    idx = stable_index(seed, len(pool))
    return pool[idx]


def normalize_birth(y: int, m: int, d: int) -> str:
    # YYYY-MM-DD 고정
    try:
        dt = date(int(y), int(m), int(d))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        st.error("생년월일이 올바르지 않습니다. 다시 확인해주세요.")
        st.stop()


def yyyyMMdd(dt: date) -> str:
    return dt.strftime("%Y%m%d")


# =========================================================
# 3) MBTI (직접선택 / 12 / 16 유지)
#    - 1번에서는 “DB 신뢰성”만 목표라서 MBTI는 기존 UI 유지용 최소 구현
# =========================================================
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

# 12문항/16문항 (간단 버전, 기존처럼 유지 원칙)
# axis: EI, SN, TF, JP / left 선택이면 +1
MBTI_Q_12 = [
    ("EI","사람들과 있을 때 에너지가 생긴다","혼자 있을 때 에너지가 생긴다"),
    ("SN","현실적인 정보가 편하다","가능성/아이디어가 편하다"),
    ("TF","결정은 논리/원칙이 우선","결정은 사람/상황 배려가 우선"),
    ("JP","계획대로 진행해야 편하다","유연하게 바뀌어도 괜찮다"),
    ("EI","말하며 생각이 정리된다","생각한 뒤 말하는 편이다"),
    ("SN","경험/사실을 믿는다","직감/영감을 믿는다"),
    ("TF","피드백은 직설이 낫다","피드백은 부드럽게가 낫다"),
    ("JP","마감 전에 미리 끝낸다","마감 직전에 몰아서 한다"),
    ("EI","주말엔 약속이 있으면 좋다","주말엔 혼자 쉬고 싶다"),
    ("SN","설명은 구체적으로","설명은 큰그림으로"),
    ("TF","갈등은 원인/해결이 우선","갈등은 감정/관계가 우선"),
    ("JP","정리/정돈이 잘 되어야 편하다","어수선해도 진행 가능"),
]
MBTI_Q_16_EXTRA = [
    ("EI","새로운 사람을 만나면 설렌다","적응 시간이 필요하다"),
    ("SN","지금 필요한 현실이 중요","미래 가능성이 더 중요"),
    ("TF","공정함이 최우선","조화로움이 최우선"),
    ("JP","일정이 확정되어야 안심","상황에 따라 바뀌는 게 자연스러움"),
]

def compute_mbti(answers):
    scores = {"EI":0,"SN":0,"TF":0,"JP":0}
    counts = {"EI":0,"SN":0,"TF":0,"JP":0}
    for axis, pick_left in answers:
        counts[axis]+=1
        if pick_left:
            scores[axis]+=1

    def decide(axis, left, right):
        return left if scores[axis] >= (counts[axis]/2) else right

    mbti = decide("EI","E","I") + decide("SN","S","N") + decide("TF","T","F") + decide("JP","J","P")
    return mbti if mbti in MBTI_LIST else "ENFP"


# =========================================================
# 4) 상태
# =========================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"

if "mbti_mode" not in st.session_state:
    st.session_state.mbti_mode = "direct"

if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFP"

if "name" not in st.session_state:
    st.session_state.name = ""

if "birth_y" not in st.session_state:
    st.session_state.birth_y = 2005
if "birth_m" not in st.session_state:
    st.session_state.birth_m = 1
if "birth_d" not in st.session_state:
    st.session_state.birth_d = 1


# =========================================================
# 5) 화면
# =========================================================
def render_input():
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세</p>
      <p class="hero-sub">완전 무료</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름 입력 (결과에 표시돼요)", value=st.session_state.name)

    st.markdown("<div class='card'><b>생년월일 입력</b></div>", unsafe_allow_html=True)

    # ✅ 달력 UI(요청했던 “달력 나오는” 버전 느낌)
    # 단, Streamlit date_input은 연도 범위 제한이 애매하므로 안전하게 처리
    # (원하면 여기만 더 정교하게 조정 가능)
    default_dt = date(int(st.session_state.birth_y), int(st.session_state.birth_m), int(st.session_state.birth_d))
    picked = st.date_input("생년월일", value=default_dt, min_value=date(1900,1,1), max_value=date(2030,12,31))
    st.session_state.birth_y = picked.year
    st.session_state.birth_m = picked.month
    st.session_state.birth_d = picked.day

    st.markdown("<div class='card'><b>MBTI를 어떻게 할까요?</b></div>", unsafe_allow_html=True)
    mode = st.radio(
        "",
        ["직접 선택", "간단 테스트 (12문항)", "상세 테스트 (16문항)"],
        index=0 if st.session_state.mbti_mode=="direct" else (1 if st.session_state.mbti_mode=="12" else 2),
        horizontal=True
    )
    st.session_state.mbti_mode = "direct" if mode=="직접 선택" else ("12" if "12" in mode else "16")

    if st.session_state.mbti_mode == "direct":
        st.session_state.mbti = st.selectbox("MBTI", MBTI_LIST, index=MBTI_LIST.index(st.session_state.mbti))
    else:
        qs = MBTI_Q_12 + (MBTI_Q_16_EXTRA if st.session_state.mbti_mode=="16" else [])
        title = "MBTI 12문항 (각 축 3문항)" if st.session_state.mbti_mode=="12" else "MBTI 16문항 (각 축 4문항)"
        st.markdown(f"<div class='card'><b>{title}</b><br><span style='opacity:0.85;'>각 문항에서 더 가까운 쪽을 선택하세요.</span></div>", unsafe_allow_html=True)

        answers = []
        for i, (axis, left, right) in enumerate(qs, start=1):
            choice = st.radio(f"{i}. {axis}", [left, right], index=0, key=f"mbti_q_{st.session_state.mbti_mode}_{i}")
            answers.append((axis, choice == left))

        if st.button("제출하고 MBTI 확정", use_container_width=True):
            st.session_state.mbti = compute_mbti(answers)
            st.success(f"MBTI: {st.session_state.mbti}")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("2026년 운세 보기!", use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_result():
    # ---- DB 로드 (1번 핵심) ----
    db_today = _read_json_or_fail(DB_TODAY_PATH)
    db_tom = _read_json_or_fail(DB_TOMORROW_PATH)
    db_year = _read_json_or_fail(DB_YEAR_PATH)

    pool_today = _get_pool(db_today, KEY_TODAY, DB_TODAY_PATH)
    pool_tomorrow = _get_pool(db_tom, KEY_TOMORROW, DB_TOMORROW_PATH)
    pool_year = _get_pool(db_year, KEY_YEAR_ALL, DB_YEAR_PATH)

    # ---- seed 규칙 (확정) ----
    birth_key = normalize_birth(st.session_state.birth_y, st.session_state.birth_m, st.session_state.birth_d)

    today_dt = date.today()
    tomorrow_dt = today_dt + timedelta(days=1)

    seed_year = f"{birth_key}"
    seed_today = f"{birth_key}|TODAY_{yyyyMMdd(today_dt)}"
    seed_tomorrow = f"{birth_key}|TOM_{yyyyMMdd(tomorrow_dt)}"

    # ---- 선택 (항상 고정) ----
    msg_today = pick_seeded(pool_today, seed_today)
    msg_tomorrow = pick_seeded(pool_tomorrow, seed_tomorrow)
    msg_year = pick_seeded(pool_year, seed_year)

    name = (st.session_state.name or "").strip()
    display_name = f"{name}님" if name else ""
    mbti = st.session_state.mbti or "ENFP"

    st.markdown(f"""
    <div class="header-hero">
      <p class="hero-title">{display_name} 2026년 운세</p>
      <p class="hero-sub">MBTI · {mbti}</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**오늘 운세**")
    st.markdown(f"<div class='soft-box'>{msg_today}</div>", unsafe_allow_html=True)
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    st.markdown("**내일 운세**")
    st.markdown(f"<div class='soft-box'>{msg_tomorrow}</div>", unsafe_allow_html=True)
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    st.markdown("**2026 전체 운세**")
    st.markdown(f"<div class='soft-box'>{msg_year}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("입력 화면으로", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.caption(APP_URL)


# =========================================================
# 6) 라우팅
# =========================================================
if st.session_state.stage == "input":
    render_input()
else:
    render_result()
