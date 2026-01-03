# app.py
import json
import hashlib
from datetime import date
from pathlib import Path

import streamlit as st


# ---------------------------
# Config
# ---------------------------
DB_PATH = Path("data/fortunes_ko.json")  # <-- repo 경로 기준
APP_TITLE = "🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세"
APP_SUBTITLE = "완전 무료"


# ---------------------------
# Helpers
# ---------------------------
def stable_hash_int(s: str) -> int:
    """Stable integer hash (no randomness, same input => same output)."""
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def load_db(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path.as_posix()}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def is_valid_date(y: int, m: int, d: int) -> bool:
    try:
        date(y, m, d)
        return True
    except Exception:
        return False


def zodiac_from_year(year: int, zodiacs: list[dict]) -> str:
    """
    DB의 zodiacs 배열 순서를 그대로 사용합니다.
    일반적으로 [쥐, 소, 호랑이, 토끼, 용, 뱀, 말, 양, 원숭이, 닭, 개, 돼지] 순서.
    2008년이 쥐띠(인덱스 0) 기준으로 계산.
    """
    if not zodiacs:
        raise ValueError("DB의 zodiacs가 비어있습니다.")
    idx = (year - 2008) % 12
    idx = idx % len(zodiacs)
    name = zodiacs[idx].get("name")
    if not name:
        raise ValueError("DB의 zodiacs 항목에 name이 없습니다.")
    return str(name)


def pick_from_list(items: list[str], seed: str) -> str:
    """Pick deterministically from list. If empty, return empty string."""
    if not items:
        return ""
    return items[stable_hash_int(seed) % len(items)]


def build_combo_key(zodiac_name: str, mbti: str) -> str:
    return f"{zodiac_name}_{mbti}"


def find_near_keys(combos: dict, zodiac_name: str) -> list[str]:
    # 같은 띠로 시작하는 키들 우선
    prefix = f"{zodiac_name}_"
    same_zodiac = [k for k in combos.keys() if k.startswith(prefix)]
    # 너무 길면 일부만
    return sorted(same_zodiac)[:12]


# ---------------------------
# Fallback tips (date-variant)
#   - "메모 앱" 같은 특정 앱/행동을 지시하지 않도록 일반 문구로 구성
# ---------------------------
ACTION_TIPS = [
    "오늘은 10분만 정리하면 머리가 맑아져요.",
    "작은 약속을 하나 지키면 흐름이 좋아져요.",
    "서두르기보다 ‘한 번 더 확인’이 도움이 돼요.",
    "가벼운 산책이 집중력 회복에 좋아요.",
    "대화는 길게보다 핵심만 정리해보세요.",
    "할 일을 3개로만 줄이면 속도가 붙어요.",
    "지금 떠오른 아이디어를 한 문장으로 정리해두세요.",
    "먼저 어려운 것 1개만 끝내면 나머지가 쉬워져요.",
    "오늘은 ‘불필요한 지출 1개 줄이기’가 효과적이에요.",
    "휴식 시간을 미리 정해두면 흐트러짐이 줄어요.",
]

CAUTIONS = [
    "충동적인 결정은 하루 미뤄보세요.",
    "말이 빨라지면 오해가 생길 수 있어요.",
    "과로 신호가 오면 잠깐 멈추는 게 좋아요.",
    "약속 시간을 과하게 채우지 마세요.",
    "비교로 기분이 흔들릴 수 있어요.",
    "감정이 올라올 때는 결론부터 내리지 마세요.",
    "지나친 낙관/비관 둘 다 피하는 게 좋아요.",
    "돈은 ‘큰 결제’보다 ‘새는 지출’ 점검이 좋아요.",
    "뒷심이 약해질 수 있으니 페이스 조절하세요.",
    "오늘은 작은 실수가 커질 수 있으니 체크리스트 추천!",
]


# ---------------------------
# UI
# ---------------------------
st.set_page_config(page_title="2026 Fortune", page_icon="🔮", layout="centered")

st.markdown(
    f"""
    <div style="padding:18px 18px 12px 18px;border-radius:18px;
                background: linear-gradient(135deg, #c7b6ff 0%, #f3b6d6 50%, #9fd3ff 100%);
                color:#111;">
        <div style="font-size:28px;font-weight:800;letter-spacing:-0.5px;">{APP_TITLE}</div>
        <div style="margin-top:4px;font-size:16px;font-weight:600;opacity:0.9;">{APP_SUBTITLE}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# Load DB
try:
    db = load_db(DB_PATH)
except Exception as e:
    st.error(f"DB 로드 오류: {e}")
    st.caption(f"경로: {DB_PATH.as_posix()}")
    st.stop()

meta = db.get("meta", {})
zodiacs = db.get("zodiacs", [])
mbti_list = db.get("mbti_list", [])
combos = db.get("combos", {})
tarot_cards = db.get("tarot_cards", [])

if not isinstance(combos, dict) or not combos:
    st.error("DB의 combos가 비어있습니다. fortunes_ko.json 구조를 확인해주세요.")
    st.stop()

st.subheader("입력")
name = st.text_input("이름 (결과에 표시돼요)", value="")

col1, col2, col3 = st.columns(3)
with col1:
    year = st.number_input("년", min_value=1900, max_value=2100, value=1982, step=1)
with col2:
    month = st.number_input("월", min_value=1, max_value=12, value=1, step=1)
with col3:
    day = st.number_input("일", min_value=1, max_value=31, value=1, step=1)

# Q1: MBTI 직접 선택 (사용자 결정)
if not mbti_list or not isinstance(mbti_list, list):
    mbti_list = [
        "ISTJ","ISFJ","INFJ","INTJ",
        "ISTP","ISFP","INFP","INTP",
        "ESTP","ESFP","ENFP","ENTP",
        "ESTJ","ESFJ","ENFJ","ENTJ"
    ]

mbti = st.selectbox("MBTI 선택", options=mbti_list, index=mbti_list.index("ENFP") if "ENFP" in mbti_list else 0)

# Q3: 오늘/내일 문구 약간 변형 (날짜 기준)
variant_today = st.toggle("오늘/내일 문구를 날짜에 따라 약간 바꾸기", value=True)

submitted = st.button("결과 보기", type="primary")

if not submitted:
    st.stop()

# Validate date
if not is_valid_date(int(year), int(month), int(day)):
    st.warning("생년월일이 올바르지 않아요. (월/일 확인)")
    st.stop()

# Resolve key
zodiac_name = zodiac_from_year(int(year), zodiacs)
combo_key = build_combo_key(zodiac_name, mbti)

record = combos.get(combo_key)

# Q2: 없으면 자동 생성하지 않고 오류로 안내
if record is None:
    st.error(f"데이터에 조합 키가 없습니다: {combo_key}")
    near = find_near_keys(combos, zodiac_name)
    if near:
        st.info("같은 띠로 시작하는 키 예시(일부):\n\n- " + "\n- ".join(near))
    st.stop()

# Render
st.write("")
title_name = name.strip() if name.strip() else "당신"
st.header(f"{title_name}님의 결과")

# Core
st.markdown(f"**띠 운세:** {record.get('zodiac_fortune','')}")
st.markdown(f"**MBTI 특징:** {record.get('mbti_trait','')}")
st.markdown(f"**사주 한 마디:** {record.get('saju_message','')}")

st.divider()

# Daily
today_txt = record.get("today", "")
tomorrow_txt = record.get("tomorrow", "")

# Optional slight variation (deterministic per date + birth + combo)
seed_base = f"{combo_key}|{int(year)}-{int(month):02d}-{int(day):02d}|{date.today().isoformat()}"
extra_tip = ""
extra_caution = ""
if variant_today:
    extra_tip = pick_from_list(ACTION_TIPS, seed_base + "|tip")
    extra_caution = pick_from_list(CAUTIONS, seed_base + "|caution")

st.subheader("오늘 운세")
st.write(today_txt if today_txt else "—")
if extra_tip:
    st.caption(f"오늘의 한 줄 팁: {extra_tip}")

st.subheader("내일 운세")
st.write(tomorrow_txt if tomorrow_txt else "—")
if extra_caution:
    st.caption(f"주의 포인트: {extra_caution}")

st.divider()

# Year
st.subheader("2026 전체 운세")
st.write(record.get("year_2026", "—"))

st.divider()

# Love/Money/Work/Health
st.subheader("조합 조언")
st.markdown(f"**연애운:** {record.get('love','—')}")
st.markdown(f"**재물운:** {record.get('money','—')}")
st.markdown(f"**일/학업운:** {record.get('work','—')}")
st.markdown(f"**건강운:** {record.get('health','—')}")

st.write("")

# Lucky point
lp = record.get("lucky_point", {}) if isinstance(record.get("lucky_point", {}), dict) else {}
st.subheader("행운 포인트")
lp_color = lp.get("color", "—")
lp_item = lp.get("item", "—")
lp_number = lp.get("number", "—")
lp_direction = lp.get("direction", "—")
st.write(f"색: {lp_color} · 아이템: {lp_item} · 숫자: {lp_number} · 방향: {lp_direction}")

# DB 기반 action_tip / caution (존재하면 보여주되, 앱/특정 지시 문구가 싫으면 DB에서 수정하세요)
db_action_tip = record.get("action_tip", "")
db_caution = record.get("caution", "")

if db_action_tip or db_caution:
    st.write("")
    st.subheader("DB 추천 문구")
    if db_action_tip:
        st.markdown(f"**액션팁:** {db_action_tip}")
    if db_caution:
        st.markdown(f"**주의할 점:** {db_caution}")

# Tarot
if tarot_cards and isinstance(tarot_cards, list):
    st.write("")
    st.subheader("오늘의 타로 카드 뽑기")
    if st.button("타로 카드 1장 뽑기"):
        card = tarot_cards[stable_hash_int(seed_base + "|tarot") % len(tarot_cards)]
        # 카드 구조는 DB에 따라 다를 수 있어 안전하게 출력
        if isinstance(card, dict):
            st.success(f"**{card.get('name','타로 카드')}**")
            meaning = card.get("meaning") or card.get("desc") or card.get("description") or ""
            if meaning:
                st.write(meaning)
        else:
            st.success(str(card))
