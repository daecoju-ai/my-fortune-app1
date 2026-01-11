# app.py
# -*- coding: utf-8 -*-

import json
import random
import hashlib
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# =========================
# 기본 설정
# =========================
APP_TITLE = "2026 띠 + MBTI + 사주 + 오늘/내일 운세"
BUILD_TAG = "BUILD_SAJU_FIX_V3"

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets"
TAROT_DIR = ASSETS_DIR / "tarot"
TAROT_BACK_PATH = TAROT_DIR / "back.png"
TAROT_MAJORS_DIR = TAROT_DIR / "majors"
TAROT_MINORS_DIR = TAROT_DIR / "minors"

# 너가 업로드한 taro db (사용 가능한 경우)
# (개발자 메시지로 마운트된 파일 경로)
MOUNTED_TAROT_DB_KO = Path("/mnt/data/tarot_db_ko.json")

# 광고/링크
RENTAL_LINK = "https://incredible-dusk-20d2b5.netlify.app/"

# =========================
# 유틸
# =========================
def safe_read_json(path: Path) -> dict:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}

def stable_seed(*parts: str) -> int:
    """같은 입력이면 같은 seed를 만들기 위한 안정 seed."""
    raw = "|".join([p for p in parts if p is not None])
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:8], 16)

def today_key() -> str:
    return date.today().isoformat()

def ensure_text(val, fallback: str) -> str:
    """dict/list 같은 게 들어오면 fallback 또는 요약 문자열로 막기."""
    if val is None:
        return fallback
    if isinstance(val, str):
        s = val.strip()
        return s if s else fallback
    # dict/list면 절대 그대로 노출하지 않음
    return fallback

def pick_one(rng: random.Random, items, fallback: str) -> str:
    if not items:
        return fallback
    try:
        return ensure_text(rng.choice(items), fallback)
    except Exception:
        return fallback

def k_st(x: str) -> str:
    return (x or "").strip()

# =========================
# 띠 매핑 (영문키 섞임 정리)
# =========================
# 12지지: 쥐 소 호랑이 토끼 용 뱀 말 양 원숭이 닭 개 돼지
ZODIAC_KO = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]

# 영어 키가 섞여 들어오는 경우를 전부 한국어로 정규화
ZODIAC_EN2KO = {
    "rat": "쥐",
    "ox": "소",
    "tiger": "호랑이",
    "rabbit": "토끼",
    "dragon": "용",
    "snake": "뱀",
    "horse": "말",
    "goat": "양",
    "sheep": "양",
    "monkey": "원숭이",
    "rooster": "닭",
    "chicken": "닭",
    "dog": "개",
    "pig": "돼지",
}

def zodiac_from_year_lunar_like(birth: date) -> tuple[str, int]:
    """
    '설 기준'을 아주 간단히 근사:
    - 1~2월 초(2/4 이전)는 전년도 띠로 처리 (완전한 음력 설 계산은 아님)
    """
    y = birth.year
    if (birth.month, birth.day) < (2, 4):
        y -= 1
    idx = (y - 4) % 12  # 2008 쥐 기준 등 통상식
    return ZODIAC_KO[idx], y

def normalize_zodiac_key(key: str) -> str:
    k = (key or "").strip().lower()
    if not k:
        return ""
    # 이미 한국어면 그대로
    for ko in ZODIAC_KO:
        if ko in key:
            return ko
    # 영어면 매핑
    return ZODIAC_EN2KO.get(k, key)

# =========================
# MBTI (질문지 복구: 간단 8문항)
# =========================
MBTI_TYPES = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]

@dataclass
class MbtiQuestion:
    axis: str  # "EI", "SN", "TF", "JP"
    a: str     # 왼쪽 성향 문장
    b: str     # 오른쪽 성향 문장

MBTI_QUESTIONS = [
    MbtiQuestion("EI", "혼자 정리하며 충전한다", "사람들과 어울리며 충전한다"),
    MbtiQuestion("EI", "말하기 전에 생각이 정리된다", "말하면서 생각이 정리된다"),
    MbtiQuestion("SN", "현재/현실/경험 중심으로 본다", "가능성/아이디어 중심으로 본다"),
    MbtiQuestion("SN", "디테일과 사실이 중요하다", "큰 그림과 의미가 중요하다"),
    MbtiQuestion("TF", "논리·원칙이 우선이다", "사람·관계가 우선이다"),
    MbtiQuestion("TF", "결정은 냉정하게 내리는 편", "결정은 공감과 조화를 고려"),
    MbtiQuestion("JP", "계획대로 가야 마음이 편하다", "유연하게 바꾸는 게 편하다"),
    MbtiQuestion("JP", "마감/정리 선호", "탐색/즉흥 선호"),
]

def mbti_from_answers(ans: list[int]) -> str:
    # ans는 0(왼쪽) / 1(오른쪽)
    score = {"EI":0,"SN":0,"TF":0,"JP":0}
    for i, v in enumerate(ans):
        q = MBTI_QUESTIONS[i]
        score[q.axis] += 1 if v == 1 else 0

    # 각 축에서 2문항 중 1 이상이면 오른쪽 성향
    E = "E" if score["EI"] >= 1 else "I"
    N = "N" if score["SN"] >= 1 else "S"
    F = "F" if score["TF"] >= 1 else "T"
    P = "P" if score["JP"] >= 1 else "J"
    return f"{E}{N}{F}{P}"

# =========================
# DB 로더 (띠/MBTI/사주)
# =========================
def load_dbs() -> dict:
    """
    data 폴더 구성은 환경마다 다를 수 있어도 최대한 흡수:
    - zodiac / 띠 운세
    - mbti_traits / MBTI 특징
    - saju_one / 사주 한 마디(오행)
    - tarot_db (설명 텍스트)
    """
    dbs = {}

    # 후보 파일들(이름이 다를 수 있으니 최대 흡수)
    candidates = {
        "zodiac": [
            DATA_DIR / "zodiac_ko.json",
            DATA_DIR / "zodiac.json",
            DATA_DIR / "zodiac_db.json",
        ],
        "mbti": [
            DATA_DIR / "mbti_traits_ko.json",
            DATA_DIR / "mbti_traits.json",
            DATA_DIR / "mbti.json",
        ],
        "saju": [
            DATA_DIR / "saju_one_ko.json",
            DATA_DIR / "saju_one.json",
            DATA_DIR / "saju_db.json",
        ],
        "tarot": [
            DATA_DIR / "tarot_db_ko.json",
            DATA_DIR / "tarot_db.json",
        ],
    }

    # load
    for k, paths in candidates.items():
        loaded = {}
        for p in paths:
            loaded = safe_read_json(p)
            if loaded:
                break
        dbs[k] = loaded or {}

    # tarot mounted fallback (사용 가능하면 우선)
    if not dbs["tarot"] and MOUNTED_TAROT_DB_KO.exists():
        dbs["tarot"] = safe_read_json(MOUNTED_TAROT_DB_KO) or {}

    return dbs

def get_zodiac_text(zodiac_db: dict, zodiac_ko: str, rng: random.Random) -> str:
    """
    zodiac_db 형태:
    - {"원숭이": {"today":[...], "tomorrow":[...], "year2026":[...]}}
    - 또는 {"monkey": {...}} 같이 영어키
    - 또는 상위가 list인 경우도 흡수
    """
    if not zodiac_db:
        return "띠 운세 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"

    # 키 정규화
    zkey = zodiac_ko
    if zkey in zodiac_db:
        bucket = zodiac_db.get(zkey, {})
    else:
        # 영어키 섞인 경우 탐색
        found = None
        for k in zodiac_db.keys():
            if normalize_zodiac_key(k) == zodiac_ko:
                found = k
                break
        bucket = zodiac_db.get(found, {}) if found else {}

    # bucket이 문자열/리스트일 수도 있음
    if isinstance(bucket, str):
        return ensure_text(bucket, "띠 운세 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)")
    if isinstance(bucket, list):
        return pick_one(rng, bucket, "띠 운세 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)")

    # dict인 정상 케이스
    today_pool = bucket.get("today") or bucket.get("오늘") or bucket.get("daily") or []
    year_pool = bucket.get("year2026") or bucket.get("2026") or bucket.get("year") or []

    # 화면에서는 "오늘" 또는 "2026" 중 하나만 보여주길 원하면 today 우선
    line = pick_one(rng, today_pool, "")
    if not line:
        line = pick_one(rng, year_pool, "띠 운세 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)")
    return line

def get_mbti_traits(mbti_db: dict, mbti: str) -> tuple[str, list[str]]:
    """
    기대 형태:
    - {"ENFP": {"keywords":["..."], "tips":["...","..."]}}
    - 또는 {"enfp": {...}}
    """
    if not mbti_db:
        return ("MBTI 특징 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)", [])

    key = mbti.upper()
    bucket = mbti_db.get(key) or mbti_db.get(key.lower()) or mbti_db.get(key.title())
    if not bucket:
        return ("MBTI 특징 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)", [])

    # bucket이 문자열인 경우
    if isinstance(bucket, str):
        return (ensure_text(bucket, "MBTI 특징 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"), [])

    # dict
    keywords = bucket.get("keywords") or bucket.get("키워드") or []
    tips = bucket.get("tips") or bucket.get("advice") or bucket.get("팁") or []
    if isinstance(keywords, str):
        keywords = [keywords]
    if isinstance(tips, str):
        tips = [tips]
    keywords = [k_st(x) for x in keywords if k_st(x)]
    tips = [k_st(x) for x in tips if k_st(x)]

    if not keywords and not tips:
        return ("MBTI 특징 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)", [])

    kw_text = " · ".join(keywords) if keywords else ""
    if kw_text:
        return (f"키워드: {kw_text}", tips[:3])
    return ("MBTI 특징", tips[:3])

def get_saju_one_liner(saju_db: dict, seed_rng: random.Random) -> str:
    """
    saju_db 기대 형태:
    - {"wood": {"name":"목", "pools":{"overall":[...]}} , ...}
    - 또는 {"elements":[{...},{...}]}
    - 또는 {"목": [...]} 등 다양할 수 있어 방어
    """
    if not saju_db:
        return "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"

    # elements 리스트 형태 흡수
    if isinstance(saju_db, dict) and "elements" in saju_db and isinstance(saju_db["elements"], list):
        elements = saju_db["elements"]
        if elements:
            el = seed_rng.choice(elements)
            if isinstance(el, dict):
                pools = (el.get("pools") or {}).get("overall") or el.get("overall") or []
                return pick_one(seed_rng, pools, "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)")
            if isinstance(el, str):
                return ensure_text(el, "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)")
        return "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"

    # dict key들 중 하나를 랜덤 선택 (wood/water/metal...)
    if isinstance(saju_db, dict):
        keys = list(saju_db.keys())
        keys = [k for k in keys if k not in ("meta",)]
        if not keys:
            return "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"
        k = seed_rng.choice(keys)
        bucket = saju_db.get(k)

        # bucket이 list면 거기서 뽑기
        if isinstance(bucket, list):
            return pick_one(seed_rng, bucket, "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)")

        # bucket이 dict면 pools.overall에서 뽑기
        if isinstance(bucket, dict):
            pools = (bucket.get("pools") or {}).get("overall") or bucket.get("overall") or []
            return pick_one(seed_rng, pools, "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)")

        # bucket이 str
        if isinstance(bucket, str):
            return ensure_text(bucket, "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)")

    return "사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"

# =========================
# 타로: 이미지 목록/선택
# =========================
def list_tarot_images() -> list[Path]:
    """
    폴더 구조(너 캡처 기준):
    assets/tarot/
      back.png
      majors/*.png
      minors/
        cups/*.png
        pentacles/*.png
        swords/*.png
        wands/*.png
    """
    imgs = []

    if TAROT_MAJORS_DIR.exists():
        imgs += sorted([p for p in TAROT_MAJORS_DIR.glob("*.png")])

    if TAROT_MINORS_DIR.exists():
        for sub in ["cups", "pentacles", "swords", "wands"]:
            d = TAROT_MINORS_DIR / sub
            if d.exists():
                imgs += sorted([p for p in d.glob("*.png")])

    return imgs

def safe_read_bytes(path: Path) -> bytes | None:
    try:
        if path and path.exists():
            return path.read_bytes()
    except Exception:
        return None
    return None

def shake_animation_html(duration_ms: int = 650) -> str:
    # 카드 흔들림 CSS (Streamlit 내 HTML)
    return f"""
    <style>
    @keyframes shake {{
      0% {{ transform: translate(0px, 0px) rotate(0deg) scale(1); }}
      10% {{ transform: translate(-2px, 1px) rotate(-1.2deg) scale(1.01); }}
      20% {{ transform: translate(2px, -1px) rotate(1.2deg) scale(1.01); }}
      30% {{ transform: translate(-3px, 0px) rotate(-1.8deg) scale(1.01); }}
      40% {{ transform: translate(3px, 0px) rotate(1.8deg) scale(1.01); }}
      50% {{ transform: translate(-2px, 1px) rotate(-1.2deg) scale(1.01); }}
      60% {{ transform: translate(2px, -1px) rotate(1.2deg) scale(1.01); }}
      70% {{ transform: translate(-1px, 0px) rotate(-0.8deg) scale(1.01); }}
      80% {{ transform: translate(1px, 0px) rotate(0.8deg) scale(1.01); }}
      90% {{ transform: translate(-1px, 0px) rotate(-0.6deg) scale(1.005); }}
      100% {{ transform: translate(0px, 0px) rotate(0deg) scale(1); }}
    }}
    .shake {{
      animation: shake {duration_ms}ms ease-in-out 1;
      transform-origin: center center;
    }}
    </style>
    """

def tarot_desc_from_db(tarot_db: dict, filename: str) -> str:
    """
    tarot_db 구조가 다양할 수 있어 최대한 흡수:
    - {"majors":{"00_the_fool":{"desc":"..."}} ...}
    - {"cards":[{"file":"00_the_fool.png","desc":"..."}]}
    - {"00_the_fool.png":"..."}
    """
    if not tarot_db:
        return ""

    # 1) direct key
    if filename in tarot_db and isinstance(tarot_db[filename], str):
        return tarot_db[filename].strip()

    # 2) cards list
    if isinstance(tarot_db, dict) and isinstance(tarot_db.get("cards"), list):
        for c in tarot_db["cards"]:
            if isinstance(c, dict) and (c.get("file") == filename or c.get("filename") == filename):
                d = c.get("desc") or c.get("description") or ""
                return ensure_text(d, "")

    # 3) nested majors/minors
    base = filename.replace(".png", "")
    for top in ["majors", "minors", "major", "minor"]:
        node = tarot_db.get(top)
        if isinstance(node, dict):
            if base in node and isinstance(node[base], dict):
                d = node[base].get("desc") or node[base].get("description") or ""
                return ensure_text(d, "")
            if filename in node and isinstance(node[filename], dict):
                d = node[filename].get("desc") or node[filename].get("description") or ""
                return ensure_text(d, "")

    return ""

# =========================
# UI 구성
# =========================
def render_header():
    st.markdown(
        f"""
        <div style="padding:14px 16px;border-radius:18px;
                    background:linear-gradient(135deg,#f5b7d2,#b9c7ff);
                    color:#fff; text-align:center; margin-bottom:10px;">
          <div style="font-size:28px;font-weight:800;letter-spacing:-0.5px;">{APP_TITLE}</div>
          <div style="opacity:0.9;font-size:14px;margin-top:8px;">{BUILD_TAG}</div>
          <div style="margin-top:10px; display:inline-block; padding:6px 16px;
                      border-radius:999px; background:rgba(255,255,255,0.18);
                      border:1px solid rgba(255,255,255,0.25);">
            2026
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_ad():
    st.markdown("---")
    st.markdown("광고")
    st.markdown(
        f"""
**[광고] 정수기 렌탈**  
제휴카드 적용시 **월 렌탈비 0원**, 설치당일 **최대 현금50만원** + **사은품 증정**  
[무료 상담하기]({RENTAL_LINK})  
이름/전화번호 작성 · 개인정보처리방침 동의 후 신청완료
        """.strip()
    )

def render_input_form():
    st.subheader("입력")

    name = st.text_input("이름", placeholder="예) 김성흥")
    birth_str = st.text_input("생년월일", value="2005/01/01", help="형식: YYYY/MM/DD")
    col1, col2 = st.columns([1, 1])

    with col1:
        mode = st.radio("MBTI 입력 방식", ["직접 선택", "간단 질문지"], horizontal=True)

    mbti_selected = None
    mbti_from_quiz = None

    with col2:
        if mode == "직접 선택":
            mbti_selected = st.selectbox("MBTI", MBTI_TYPES, index=MBTI_TYPES.index("ENFP"))
        else:
            st.caption("간단 질문지(8문항)로 MBTI 추정")
            answers = []
            for i, q in enumerate(MBTI_QUESTIONS):
                v = st.radio(
                    f"Q{i+1}.",
                    [q.a, q.b],
                    index=0,
                    key=f"mbti_q_{i}",
                    horizontal=False
                )
                answers.append(0 if v == q.a else 1)
            mbti_from_quiz = mbti_from_answers(answers)
            st.info(f"추정 MBTI: **{mbti_from_quiz}**")

    mbti = mbti_selected if mbti_selected else mbti_from_quiz

    # birth parse
    birth = None
    try:
        y, m, d = [int(x) for x in birth_str.replace("-", "/").split("/")]
        birth = date(y, m, d)
    except Exception:
        birth = None

    return name, birth, mbti

def render_result(dbs: dict, name: str, birth: date, mbti: str):
    if not name:
        st.warning("이름을 입력해주세요.")
        return
    if not birth:
        st.warning("생년월일 형식이 올바르지 않습니다. (예: 2005/01/01)")
        return
    if not mbti:
        st.warning("MBTI를 선택/완료해주세요.")
        return

    zodiac_ko, lunar_year = zodiac_from_year_lunar_like(birth)
    st.markdown(f"### {name}님의 운세 결과")
    st.caption(f"{zodiac_ko}띠 · {mbti} · (설 기준 띠년도 {lunar_year})")

    # seed (같은 사람 + 같은 날짜는 동일 결과 유지)
    base_seed = stable_seed(name, birth.isoformat(), mbti, today_key())
    rng = random.Random(base_seed)

    # 띠 운세
    zodiac_text = get_zodiac_text(dbs.get("zodiac", {}), zodiac_ko, rng)
    st.markdown(f"**🧧 띠 운세**: {ensure_text(zodiac_text, '띠 운세 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)')}")

    # MBTI 특징
    mbti_title, mbti_tips = get_mbti_traits(dbs.get("mbti", {}), mbti)
    if mbti_tips:
        st.markdown(f"**🧠 MBTI 특징**: {ensure_text(mbti_title, 'MBTI 특징 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)')} {mbti_tips}")
    else:
        st.markdown(f"**🧠 MBTI 특징**: {ensure_text(mbti_title, 'MBTI 특징 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)')}")

    # 사주 한 마디 (절대 dict 출력 금지)
    saju_rng = random.Random(base_seed + 7)
    saju_line = get_saju_one_liner(dbs.get("saju", {}), saju_rng)
    st.markdown(f"**🧾 사주 한 마디**: {ensure_text(saju_line, '사주 한 마디 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)')}")

    # 오늘/내일/2026 (여기서는 간단 생성: 필요하면 DB 연결로 확장 가능)
    today_msg = pick_one(rng, [
        "오늘 하루는 과속이 실수를 만듭니다. 한 박자 늦추면 운이 편이 됩니다.",
        "오늘은 작은 정리가 큰 성과를 만듭니다. 10분만 정리해보세요.",
        "오늘은 말보다 행동이 운을 올립니다. 한 가지를 끝내면 흐름이 좋아집니다."
    ], "오늘 하루는 무리하지 마세요.")

    tomorrow_msg = pick_one(rng, [
        "내일은 가능성만 잡아도 흐름이 좋아집니다. 준비한 만큼 편해지는 날입니다.",
        "내일은 선택지가 많아질 수 있어요. 기준을 1개만 정해두세요.",
        "내일은 가벼운 연락이 기회를 엽니다. 부담 없이 한 번 연결해보세요."
    ], "내일은 한 템포 쉬어가세요.")

    year_msg = pick_one(rng, [
        "2026년에는 휴식에서 강해집니다. 컨디션이 곧 성과입니다.",
        "2026년에는 방향 설정이 핵심입니다. 기준을 세우면 속도가 납니다.",
        "2026년에는 관계/일의 균형이 운을 만듭니다. 한쪽만 무리하지 마세요."
    ], "2026년에는 기회가 들어옵니다.")

    st.markdown(f"**🌞 오늘 운세**: {today_msg}")
    st.markdown(f"**🌙 내일 운세**: {tomorrow_msg}")
    st.markdown(f"**📅 2026 전체 운세**: {year_msg}")

    render_ad()

    tarot_ui(
        tarot_db=dbs.get("tarot", {}),
        name=name,
        birth=birth,
        mbti=mbti
    )

def tarot_ui(tarot_db: dict, name: str, birth: date, mbti: str):
    st.markdown("---")
    st.markdown("### 🃏 오늘의 타로카드  (하루 1회 가능)")
    st.info("뒷면 카드를 보고, **뽑기**를 누르면 오늘의 카드가 공개됩니다.\n오늘 하루 동안은 **같은 카드(같은 의미/이미지)**로 고정됩니다.\n\n(하루 1회 가능)")

    # 세션: 오늘 카드 고정
    tkey = today_key()
    state_key = f"tarot_pick::{name}::{birth.isoformat()}::{mbti}"

    if "tarot_state" not in st.session_state:
        st.session_state["tarot_state"] = {}

    if state_key not in st.session_state["tarot_state"]:
        st.session_state["tarot_state"][state_key] = {
            "date": tkey,
            "picked_path": None,
            "revealed": False
        }
    else:
        # 날짜가 바뀌면 리셋(다음날 새 카드)
        if st.session_state["tarot_state"][state_key]["date"] != tkey:
            st.session_state["tarot_state"][state_key] = {
                "date": tkey,
                "picked_path": None,
                "revealed": False
            }

    tarot_state = st.session_state["tarot_state"][state_key]

    # 카드 뒷면
    back_bytes = safe_read_bytes(TAROT_BACK_PATH)
    if back_bytes:
        st.image(back_bytes, use_container_width=True)
    else:
        st.warning("타로 back.png를 찾지 못했습니다. assets/tarot/back.png 확인")
        st.markdown("**TAROT BACK**")

    # 공개 영역
    card_box = st.empty()

    # 버튼
    c1, c2 = st.columns([1, 1])
    with c1:
        draw = st.button("타로카드 뽑기", use_container_width=True)
    with c2:
        # 디버그용 리셋(원하면 주석)
        debug_reset = st.button("오늘 카드 리셋(테스트)", use_container_width=True)

    if debug_reset:
        tarot_state["picked_path"] = None
        tarot_state["revealed"] = False

    # 뽑기 버튼 누르면:
    # - 이미 뽑은 상태여도 "이미 뽑았어요" 라고 말하지 않고
    # - 그냥 동일 카드가 다시 보여지게 한다.
    if draw:
        # 1) 오늘 카드가 없으면 새로 픽
        if not tarot_state["picked_path"]:
            all_imgs = list_tarot_images()
            if not all_imgs:
                card_box.error("타로 카드 이미지가 없습니다. assets/tarot/majors 및 minors 폴더 확인")
                return

            # 개인+날짜 기반 seed → 오늘은 고정
            seed = stable_seed("tarot", name, birth.isoformat(), mbti, today_key())
            rng = random.Random(seed)
            pick = rng.choice(all_imgs)
            tarot_state["picked_path"] = str(pick)

        # 2) 흔들림 효과(짧게) → 그 다음 카드 공개
        # 흔들림은 back 이미지를 "흔들리는 듯" 보여주기 위한 간단 CSS 애니
        components.html(shake_animation_html(650) + """
            <div class="shake" style="width:100%;height:10px;"></div>
        """, height=0)
        tarot_state["revealed"] = True

    # 렌더 (revealed 상태면 카드 보여주고 설명)
    if tarot_state["revealed"] and tarot_state["picked_path"]:
        p = Path(tarot_state["picked_path"])
        b = safe_read_bytes(p)
        if b:
            card_box.image(b, use_container_width=True)
        else:
            card_box.warning("선택된 타로 이미지를 읽지 못했습니다. 경로 확인 필요")
            card_box.code(str(p))

        desc = tarot_desc_from_db(tarot_db, p.name)
        if desc:
            st.markdown(f"**오늘의 카드 설명**: {desc}")
        else:
            st.caption("카드 설명 DB가 없거나 매칭되지 않았습니다. (tarot_db_ko.json 매칭 키 확인)")

    else:
        # 아직 뽑기 전
        card_box.markdown(
            """
            <div style="border:2px dashed #d7d7e7; border-radius:18px; padding:38px;
                        text-align:center; color:#2d2d45; font-weight:800; font-size:22px;">
                뽑기를 누르면 카드가 공개됩니다
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================
# 앱 실행
# =========================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="centered")

    render_header()

    dbs = load_dbs()

    # 입력 폼
    name, birth, mbti = render_input_form()

    st.markdown("---")
    if st.button("운세 보기", use_container_width=True):
        render_result(dbs, name, birth, mbti)

    # DB 상태 확인용 (접기)
    with st.expander("DB 연결 상태(확인용)"):
        st.write({
            "DATA_DIR": str(DATA_DIR),
            "assets/tarot": str(TAROT_DIR),
            "tarot_back_exists": TAROT_BACK_PATH.exists(),
            "majors_exists": TAROT_MAJORS_DIR.exists(),
            "minors_exists": TAROT_MINORS_DIR.exists(),
            "db_zodiac_loaded": bool(dbs.get("zodiac")),
            "db_mbti_loaded": bool(dbs.get("mbti")),
            "db_saju_loaded": bool(dbs.get("saju")),
            "db_tarot_loaded": bool(dbs.get("tarot")),
        })

if __name__ == "__main__":
    main()
