# app.py
import json
import random
import time
import hashlib
from pathlib import Path
from datetime import datetime, date

import streamlit as st

# =========================
# Paths
# =========================
ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "fortunes_ko.json"

# Tarot assets (optional)
TAROT_ROOT = ROOT / "assets" / "tarot"
MAJORS_DIR = TAROT_ROOT / "majors"
MINORS_DIR = TAROT_ROOT / "minors"
BACK_IMG = TAROT_ROOT / "back.png"

# =========================
# SEO (Hidden in UI)
# =========================
SEO_KEYWORDS = """
2026 운세 무료, 오늘운세, 내일운세, 띠운세, 사주, MBTI 운세,
2026 띠+MBTI 운세, 다나눔렌탈, 정수기 렌탈, 안마의자 렌탈, 가전 렌탈,
스톱워치 20.26초 게임, 커피쿠폰 이벤트, 운세 카드, 타로카드, 타로 운세
"""

def inject_hidden_seo():
    # front에 안 보이게, 코드에만 삽입
    st.markdown(
        f"""
        <div style="position:absolute; left:-9999px; top:-9999px; height:1px; width:1px; overflow:hidden;">
            {SEO_KEYWORDS}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# Utilities
# =========================
def stable_seed(*parts: str) -> int:
    raw = "|".join([p or "" for p in parts])
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:8], 16)

def pick_from_list(items, seed_int: int, fallback="-"):
    if not isinstance(items, list) or len(items) == 0:
        return fallback
    r = random.Random(seed_int)
    return r.choice(items)

def safe_get(dct, path, default=None):
    cur = dct
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def zodiac_from_birth_year(year: int, db: dict) -> str:
    """
    Returns Korean zodiac label like '말띠', '개띠' etc.
    Uses db['zodiac']['order'] + db['zodiac']['labels'] if present.
    """
    z = safe_get(db, ["zodiac"], {})
    order = z.get("order")
    labels = z.get("labels")

    # fallback: if someone uploaded old schema
    # - 'zodiacs' : list of dicts or list of strings
    if not order or not labels:
        zodiacs = db.get("zodiacs")
        if isinstance(zodiacs, list) and len(zodiacs) >= 12:
            # try map if list of strings
            if isinstance(zodiacs[0], str):
                # assume english order already in list
                # but we need KR label: can't guess, return placeholder
                return "띠"
            # if list of dicts containing label_ko
            if isinstance(zodiacs[0], dict):
                # just pick by index
                idx = (year - 4) % 12
                return zodiacs[idx].get("label_ko", "띠")
        return "띠"

    # standard 12-zodiac index (Rat is base around 4 AD commonly used in many simple calculators)
    idx = (year - 4) % 12
    key = order[idx]
    return labels.get(key, "띠")

def mbti_traits(mbti: str) -> str:
    mbti = (mbti or "").upper().strip()
    if len(mbti) != 4:
        return "-"
    mapping = {
        "E": "외향", "I": "내향",
        "S": "현실", "N": "직관",
        "T": "논리", "F": "감정",
        "J": "계획", "P": "유연",
    }
    return " · ".join([mapping.get(c, c) for c in mbti])

# =========================
# DB Loader (robust)
# =========================
@st.cache_data(show_spinner=False)
def load_db():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")

    data = json.loads(DB_PATH.read_text(encoding="utf-8"))

    # Accept two schemas:
    # A) NEW: { "zodiac": {...}, "mbti": {...}, "pools": {...} }
    # B) OLD: { "zodiacs": [...], "combos": {...}, ... }  -> Not used for full features, but avoid crash
    if "pools" in data and "zodiac" in data and "mbti" in data:
        return data

    # OLD schema fallback (to avoid blank screen): wrap minimal pools
    pools = {
        "today": data.get("work_study_advice", []) + data.get("health_advice", []) + data.get("action_tip", []),
        "tomorrow": data.get("work_study_advice", []) + data.get("health_advice", []),
        "year_2026": data.get("work_study_advice", []) + data.get("health_advice", []),
        "saju_one_liner": data.get("action_tip", []) or ["오늘은 작은 정리가 큰 운을 부릅니다."],
        "zodiac": {},
        "combos": data.get("combos", {}) if isinstance(data.get("combos"), dict) else {},
    }
    data = {
        "meta": data.get("meta", {}),
        "zodiac": data.get("zodiac", {}) if isinstance(data.get("zodiac"), dict) else {},
        "mbti": data.get("mbti", {}) if isinstance(data.get("mbti"), dict) else {},
        "pools": pools,
    }
    return data

# =========================
# UI Styling
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        .wrap { max-width: 860px; margin: 0 auto; }
        .card {
            border-radius: 18px;
            padding: 18px 18px;
            margin: 12px 0;
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        .card-result {
            background: linear-gradient(135deg, rgba(104,68,255,0.28), rgba(0,196,255,0.18));
        }
        .card-ad {
            background: linear-gradient(135deg, rgba(255,150,0,0.16), rgba(255,0,120,0.10));
        }
        .card-game {
            background: linear-gradient(135deg, rgba(0,255,180,0.12), rgba(0,120,255,0.12));
        }
        .pill {
            display:inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 13px;
            border: 1px solid rgba(255,255,255,0.14);
            background: rgba(255,255,255,0.05);
            margin-right: 6px;
        }
        .bigbtn > button {
            width: 100% !important;
            border-radius: 999px !important;
            padding: 14px 18px !important;
            font-size: 18px !important;
        }
        .muted { opacity: 0.85; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================
# MBTI selection / quiz
# (기존 요구: "직접 고르거나 모르면 12/16문항으로 확인" 유지)
# =========================
MBTI_LIST = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]

def render_mbti_picker():
    st.subheader("MBTI 선택")
    mode = st.radio(
        "MBTI를 알고 있나요?",
        ["직접 선택", "모르면 간단 테스트(12문항)", "모르면 간단 테스트(16문항)"],
        horizontal=True,
    )

    if mode == "직접 선택":
        mbti = st.selectbox("MBTI", MBTI_LIST, index=MBTI_LIST.index(st.session_state.get("mbti","ENTJ")) if st.session_state.get("mbti") in MBTI_LIST else 0)
        st.session_state["mbti"] = mbti
        return

    # --- Simple quiz (lightweight) ---
    # 12 or 16 questions; keep structure stable.
    n_q = 12 if "12" in mode else 16

    # (E/I, S/N, T/F, J/P) each scored by simple forced choice
    q_bank = [
        ("사람들과 함께 있을 때 에너지가 충전된다", "혼자 있을 때 에너지가 충전된다", "E", "I"),
        ("세부와 현실이 중요하다", "가능성과 아이디어가 중요하다", "S", "N"),
        ("결정은 논리/원칙이 우선", "결정은 가치/공감이 우선", "T", "F"),
        ("계획대로 하는 게 편하다", "즉흥/유연이 편하다", "J", "P"),
    ]
    # repeat & slightly vary statements to reach n_q (deterministic)
    quiz = []
    for i in range(n_q):
        a,b,p1,p2 = q_bank[i % 4]
        quiz.append((f"Q{i+1}. {a}", f"{b}", p1, p2))

    st.caption("빠른 확인용 간단 테스트입니다. 결과는 참고용으로 사용하세요.")
    score = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}

    for i,(a,b,p1,p2) in enumerate(quiz, start=1):
        choice = st.radio(
            label=f"{a}  vs  {b}",
            options=[a, b],
            key=f"mbti_q_{i}",
            horizontal=False
        )
        if choice == a:
            score[p1] += 1
        else:
            score[p2] += 1

    mbti = ""
    mbti += "E" if score["E"] >= score["I"] else "I"
    mbti += "S" if score["S"] >= score["N"] else "N"
    mbti += "T" if score["T"] >= score["F"] else "F"
    mbti += "J" if score["J"] >= score["P"] else "P"
    st.session_state["mbti"] = mbti
    st.success(f"테스트 결과: {mbti}")

# =========================
# Result page (open as "new tab" style using link)
# =========================
def result_url():
    # Streamlit Cloud: same app URL + ?page=result
    # 버튼 클릭 시 새창(탭)으로 열리게 하기 위해 target=_blank 링크 사용
    return "?page=result"

def open_result_button():
    st.markdown(
        f"""
        <div class="bigbtn">
          <a href="{result_url()}" target="_blank" style="text-decoration:none;">
            <button type="button">결과 보기</button>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# Tarot (optional display)
# =========================
MAJOR_FILES = [
    "00_the_fool.png","01_the_magician.png","02_the_high_priestess.png","03_the_empress.png","04_the_emperor.png","05_the_hierophant.png",
    "06_the_lovers.png","07_the_chariot.png","08_strength.png","09_the_hermit.png","10_wheel_of_fortune.png","11_justice.png",
    "12_the_hanged_man.png","13_death.png","14_temperance.png","15_the_devil.png","16_the_tower.png","17_the_star.png","18_the_moon.png",
    "19_the_sun.png","20_judgement.png","21_the_world.png"
]

def draw_tarot_card(seed_int: int):
    # If majors images exist, draw one deterministic
    r = random.Random(seed_int)
    file_name = r.choice(MAJOR_FILES)
    img_path = MAJORS_DIR / file_name
    if img_path.exists():
        return file_name, img_path
    return None, None

# =========================
# Fortune generation from DB (NEW schema)
# =========================
def build_result(db: dict, zodiac_ko: str, mbti: str, ymd: str):
    pools = db.get("pools", {})
    seed = stable_seed("fortune", ymd, zodiac_ko, mbti)

    saju = pick_from_list(pools.get("saju_one_liner"), seed+1, fallback="-")
    today = pick_from_list(pools.get("today"), seed+2, fallback="-")
    tomorrow = pick_from_list(pools.get("tomorrow"), seed+3, fallback="-")
    year_2026 = pick_from_list(pools.get("year_2026"), seed+4, fallback="-")

    # combos: expected pools["combos"][f"{zodiac_ko}_{mbti}"] or pools["combos"][key]
    combo_key = f"{zodiac_ko}_{mbti}"
    combo_bucket = safe_get(pools, ["combos", combo_key], None)

    combo_one = "-"
    combo_advice = "-"
    if isinstance(combo_bucket, dict):
        combo_one = pick_from_list(combo_bucket.get("combo_one_liner"), seed+5, fallback="-")
        combo_advice = pick_from_list(combo_bucket.get("combo_advice"), seed+6, fallback="-")
    else:
        # fallback: show something instead of '-'
        combo_one = pick_from_list(pools.get("today"), seed+7, fallback="-")
        combo_advice = pick_from_list(pools.get("action_tip"), seed+8, fallback="-") if isinstance(pools.get("action_tip"), list) else "-"

    # if any field becomes empty string, normalize
    def norm(x):
        if not x or (isinstance(x, str) and x.strip() == ""):
            return "-"
        return x

    return {
        "saju": norm(saju),
        "today": norm(today),
        "tomorrow": norm(tomorrow),
        "year_2026": norm(year_2026),
        "combo_one": norm(combo_one),
        "combo_advice": norm(combo_advice),
    }

# =========================
# Share button
# =========================
def render_share_button():
    st.markdown(
        """
        <div class="bigbtn">
            <a href="https://www.dananumrental.com" target="_blank" style="text-decoration:none;">
              <button type="button">친구에게 공유하기</button>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# Main
# =========================
def main():
    st.set_page_config(page_title="2026 띠 + MBTI + 사주 + 오늘/내일 운세", page_icon="🔮", layout="centered")
    inject_css()
    inject_hidden_seo()

    # Keep session defaults
    if "mbti" not in st.session_state:
        st.session_state["mbti"] = "ENTJ"
    if "birth_year" not in st.session_state:
        st.session_state["birth_year"] = 1990

    # Route by query
    page = st.query_params.get("page", "home")

    # Load DB (show message if broken)
    try:
        db = load_db()
    except Exception as e:
        st.error(f"DB 로딩 실패: {e}")
        st.stop()

    # ========== RESULT PAGE ==========
    if page == "result":
        st.title("결과")

        birth_year = int(st.session_state.get("birth_year", 1990))
        zodiac_ko = zodiac_from_birth_year(birth_year, db)
        mbti = st.session_state.get("mbti", "ENTJ")
        ymd = date.today().strftime("%Y-%m-%d")

        res = build_result(db, zodiac_ko, mbti, ymd)

        # Result card (premium)
        st.markdown('<div class="card card-result">', unsafe_allow_html=True)

        st.markdown(f"**띠 운세:** {zodiac_ko}")
        st.markdown(f"**MBTI 특징:** {mbti_traits(mbti)}")
        st.markdown("---")

        st.subheader("사주 한 마디:")
        st.write(res["saju"])

        st.subheader("오늘 운세:")
        st.write(res["today"])

        st.subheader("내일 운세:")
        st.write(res["tomorrow"])

        st.subheader("2026 전체 운세:")
        st.write(res["year_2026"])

        st.subheader("조합 조언:")
        st.write(res["combo_advice"])

        # Tarot (optional)
        seed = stable_seed("tarot", ymd, zodiac_ko, mbti)
        card_name, img_path = draw_tarot_card(seed)
        if img_path:
            st.markdown("---")
            st.caption("오늘의 타로 카드 (이미지)")
            st.image(str(img_path), use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 바로 밑: 공유하기 버튼 (요구사항)
        render_share_button()

        st.markdown(" ")
        if st.button("다시 입력"):
            st.query_params.clear()
            st.rerun()

        return

    # ========== HOME PAGE ==========
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="card card-result">
          <h2 style="margin:0;">🔮 2026 띠 + MBTI + 사주 + 오늘/내일 운세</h2>
          <div class="muted">완전 무료</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Birth year
    st.subheader("생년(년도) 입력")
    st.session_state["birth_year"] = st.number_input("출생년도", min_value=1900, max_value=2100, value=int(st.session_state["birth_year"]), step=1)

    # MBTI block (must keep)
    render_mbti_picker()

    # Ad card (다나눔렌탈)
    st.markdown(
        """
        <div class="card card-ad">
          <div class="pill">광고</div>
          <h3 style="margin:8px 0 6px 0;">다나눔렌탈</h3>
          <div class="muted" style="line-height:1.6;">
            정수기 렌탈 제휴카드시 월 0원부터<br/>
            설치당일 최대 50만원 + 사은품
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 결과보기 (새창)
    open_result_button()

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
