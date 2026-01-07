# app.py
# 2026 운세 앱 (DB/로직 고정, UI는 기존 스타일 최대 유지)
# - DB는 /data 폴더의 JSON만 사용
# - app.py는 운영/로직/UI만 담당 (문장/고정값은 DB로)
# - DB 구조 변경에 강한 안전한 접근(빈 배열/누락 키 fallback)
#
# Required data files (repo: /data):
#   fortunes_ko_today.json
#   fortunes_ko_tomorrow.json
#   fortunes_ko_2026.json
#   zodiac_fortunes_ko_2026.json
#   mbti_traits_ko.json
#   saju_ko.json
#   lunar_new_year_1920_2026.json
#   tarot_db_ko.json (옵션: 추후)

from __future__ import annotations

import json
import os
import random
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components


# -----------------------------
# 기본 설정 (UI/운영)
# -----------------------------
st.set_page_config(page_title="2026년 운세", page_icon="🔮", layout="centered")

DATA_DIR = Path(__file__).parent / "data"

DB_FILES = {
    "today": DATA_DIR / "fortunes_ko_today.json",
    "tomorrow": DATA_DIR / "fortunes_ko_tomorrow.json",
    "year": DATA_DIR / "fortunes_ko_2026.json",
    "zodiac": DATA_DIR / "zodiac_fortunes_ko_2026.json",
    "mbti": DATA_DIR / "mbti_traits_ko.json",
    "saju": DATA_DIR / "saju_ko.json",
    "lunar": DATA_DIR / "lunar_new_year_1920_2026.json",
    "tarot": DATA_DIR / "tarot_db_ko.json",  # optional
}

# 고정 광고 문구 (요청대로 고정)
RENTAL_AD_COPY = (
    "[광고] 정수기 렌탈 제휴카드 적용시 월 렌탈비 0원, "
    "설치당일 최대 현금50만원 + 사은품 증정"
)

# 구글시트 컬럼 고정 (요청대로)
# A:시간, B:이름, C:전화번호, D:언어, E:기록초, F:공유여부, G:상담신청
SHEET_COLUMNS = ["시간", "이름", "전화번호", "언어", "기록초", "공유여부", "상담신청"]

# ---------------------------------
# 유틸: JSON 로드 / 안전 접근
# ---------------------------------
@st.cache_data(show_spinner=False)
def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"필수 DB 파일이 없습니다: {path.as_posix()}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def safe_list(v: Any) -> List[Any]:
    return v if isinstance(v, list) else []

def safe_dict(v: Any) -> Dict[str, Any]:
    return v if isinstance(v, dict) else {}

def seeded_choice(items: List[str], seed_key: str) -> str:
    """같은 입력이면 같은 문장을 뽑도록 (앱 재실행/새로고침에 흔들리지 않게)."""
    if not items:
        return "표시할 문장이 없습니다. (DB를 확인해주세요)"
    seed = 0
    for ch in seed_key:
        seed = (seed * 131 + ord(ch)) % (2**32)
    rnd = random.Random(seed)
    return rnd.choice(items)

# ---------------------------------
# 띠 매핑 (키/표시명 고정)
# ---------------------------------
ZODIAC_ORDER: List[Tuple[str, str]] = [
    ("rat", "쥐띠"),
    ("ox", "소띠"),
    ("tiger", "호랑이띠"),
    ("rabbit", "토끼띠"),
    ("dragon", "용띠"),
    ("snake", "뱀띠"),
    ("horse", "말띠"),
    ("goat", "양띠"),
    ("monkey", "원숭이띠"),
    ("rooster", "닭띠"),
    ("dog", "개띠"),
    ("pig", "돼지띠"),
]
ZODIAC_KEY_TO_KO = dict(ZODIAC_ORDER)
ZODIAC_KO_TO_KEY = {v: k for k, v in ZODIAC_ORDER}

def zodiac_key_from_birth_year(year_num: int) -> str:
    keys = [k for k, _ in ZODIAC_ORDER]
    # 2020=rat 기준(일반적으로 알려진 기준)
    base_year = 2020
    idx = (year_num - base_year) % 12
    return keys[idx]

# ---------------------------------
# DB 접근 레이어 (구조 고정)
# ---------------------------------
@dataclass
class DB:
    today: Dict[str, Any]
    tomorrow: Dict[str, Any]
    year: Dict[str, Any]
    zodiac: Dict[str, Any]
    mbti: Dict[str, Any]
    saju: Dict[str, Any]
    lunar: Dict[str, Any]
    tarot: Optional[Dict[str, Any]]

@st.cache_data(show_spinner=False)
def load_all_db() -> DB:
    today = load_json(DB_FILES["today"])
    tomorrow = load_json(DB_FILES["tomorrow"])
    year = load_json(DB_FILES["year"])
    zodiac = load_json(DB_FILES["zodiac"])
    mbti = load_json(DB_FILES["mbti"])
    saju = load_json(DB_FILES["saju"])
    lunar = load_json(DB_FILES["lunar"])
    tarot = None
    if DB_FILES["tarot"].exists():
        tarot = load_json(DB_FILES["tarot"])
    return DB(today=today, tomorrow=tomorrow, year=year, zodiac=zodiac, mbti=mbti, saju=saju, lunar=lunar, tarot=tarot)

def get_pool_text(db_obj: Dict[str, Any], pool_name: str) -> List[str]:
    pools = safe_dict(db_obj.get("pools"))
    return safe_list(pools.get(pool_name))

def get_zodiac_texts(zodiac_db: Dict[str, Any], zodiac_key: str, section: str) -> List[str]:
    """zodiac_fortunes_ko_2026.json 구조:
       { "rat": { "today":[...], "tomorrow":[...], "year":[...] }, ... }
    """
    z = safe_dict(zodiac_db.get(zodiac_key))
    return safe_list(z.get(section))

def get_mbti_summary_and_traits(mbti_db: Dict[str, Any], mbti_type: str) -> Tuple[str, List[str]]:
    """mbti_traits_ko.json 구조:
       { "ESTJ": {"summary":"...", "traits":[...]} , ... }
    """
    entry = safe_dict(mbti_db.get(mbti_type))
    summary = entry.get("summary") if isinstance(entry.get("summary"), str) else ""
    traits = safe_list(entry.get("traits"))
    return summary, traits

def get_saju_text(saju_db: Dict[str, Any], born: date) -> str:
    """정밀 사주 계산이 아닌, DB를 '고정 키로 안정적으로' 뽑는 방식(테스트/콘텐츠 용).
       born.toordinal() 기준으로 60갑자 중 하나 선택.
    """
    keys = list(saju_db.keys())
    if not keys:
        return "사주 DB가 비어있습니다."
    keys.sort()
    idx = born.toordinal() % len(keys)
    key = keys[idx]
    val = saju_db.get(key)
    if isinstance(val, str) and val.strip():
        return f"{key}: {val}"
    return f"{key}: (내용 없음)"

# ---------------------------------
# 모바일 공유/복사 버튼 (JS)
# ---------------------------------
def render_share_buttons():
    # Streamlit에서 "친구에게 공유하기 / URL 복사" UI를 유지하면서
    # navigator.share / clipboard API로 실제 동작하도록 구성
    app_url = st.get_option("browser.serverAddress")  # 로컬에서는 None일 수 있음
    # Streamlit Cloud에서는 직접 URL을 알기 어려워서 window.location.href 사용
    html = f"""
    <div style="display:flex; gap:12px; margin-top:6px; margin-bottom:6px;">
      <button id="shareBtn" style="flex:1; padding:12px 14px; border-radius:14px; border:1px solid #ddd; background:#fff; font-size:16px;">
        친구에게 공유하기
      </button>
      <button id="copyBtn" style="flex:1; padding:12px 14px; border-radius:14px; border:1px solid #ddd; background:#fff; font-size:16px;">
        URL 복사
      </button>
    </div>
    <div id="msg" style="font-size:13px; color:#666;"></div>
    <script>
      const msg = document.getElementById("msg");
      const getUrl = () => window.location.href;

      document.getElementById("copyBtn").onclick = async () => {{
        try {{
          await navigator.clipboard.writeText(getUrl());
          msg.innerText = "URL이 복사되었습니다.";
        }} catch(e) {{
          // clipboard 권한이 막힌 환경 대비
          const url = getUrl();
          prompt("복사가 막혀있어요. 아래 URL을 길게 눌러 복사하세요.", url);
          msg.innerText = "복사 안내를 띄웠습니다.";
        }}
      }};

      document.getElementById("shareBtn").onclick = async () => {{
        const url = getUrl();
        try {{
          if (navigator.share) {{
            await navigator.share({{ title: "2026년 운세", text: "2026년 운세 확인하기", url }});
            msg.innerText = "공유 창을 열었습니다.";
          }} else {{
            prompt("공유 기능이 지원되지 않습니다. 아래 URL을 복사해 공유하세요.", url);
            msg.innerText = "공유 미지원: 복사 안내를 띄웠습니다.";
          }}
        }} catch(e) {{
          // 사용자가 공유창을 닫아도 에러가 날 수 있어 조용히 처리
          msg.innerText = "";
        }}
      }};
    </script>
    """
    components.html(html, height=80)

# ---------------------------------
# (옵션) 구글시트 저장: Apps Script Web App 사용
# ---------------------------------
# secrets.toml 또는 Streamlit Cloud secrets에 아래를 넣으면 동작
# [google]
# sheet_webhook_url = "https://script.google.com/macros/s/...../exec"
def send_to_sheet(payload: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        import requests  # Streamlit Cloud에서 보통 사용 가능
    except Exception:
        return False, "requests 모듈을 사용할 수 없습니다."

    url = None
    try:
        url = st.secrets["google"]["sheet_webhook_url"]
    except Exception:
        url = os.environ.get("SHEET_WEBHOOK_URL")

    if not url:
        return False, "시트 연동 URL이 설정되지 않았습니다. (secrets 또는 환경변수)"

    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            return True, "저장 완료"
        return False, f"저장 실패: HTTP {r.status_code}"
    except Exception as e:
        return False, f"저장 실패: {e}"

# -----------------------------
# UI (디자인은 기존 형태 유지)
# -----------------------------
db = load_all_db()

st.title("2026년 운세")

# 고정 광고 영역 (문구 변경 금지)
st.subheader("다나눔렌탈 상담/이벤트")
st.write("다나눔렌탈 1660-2445")
render_share_buttons()

st.info(RENTAL_AD_COPY)

# 상담 폼 (구글시트 연동)
with st.expander("무료 상담하기 (이름/전화번호 작성 → 구글시트 저장)", expanded=False):
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("이름", placeholder="이름")
        phone = st.text_input("전화번호", placeholder="01012345678")
        consult = st.selectbox("상담신청", ["", "O(정수기)", "O(공기청정기)", "O(안마의자)", "O(기타)"])
        submitted = st.form_submit_button("저장하기")
        if submitted:
            if not name.strip() or not phone.strip():
                st.error("이름과 전화번호를 입력해주세요.")
            else:
                payload = {
                    "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "이름": name.strip(),
                    "전화번호": re.sub(r"\s+", "", phone.strip()),
                    "언어": "ko",
                    "기록초": "",
                    "공유여부": False,
                    "상담신청": consult,
                    "columns": SHEET_COLUMNS,
                }
                ok, msg = send_to_sheet(payload)
                if ok:
                    st.success("상담 정보가 저장되었습니다.")
                else:
                    st.warning(f"{msg}\n\n※ 시트 연동 URL(secrets)을 설정하면 자동 저장됩니다.")

st.divider()

tab_today, tab_tomorrow, tab_year = st.tabs(["오늘의 운세", "내일의 운세", "2026년 전체 운세"])

# 공통: 띠 선택 옵션은 무조건 고정 목록을 사용 (pools 같은 잘못된 키가 뜨지 않게)
zodiac_label_list = [ko for _, ko in ZODIAC_ORDER]

def render_zodiac_section(section: str, pool_db: Dict[str, Any]):
    st.subheader("띠 선택")
    zodiac_label = st.selectbox("", zodiac_label_list, key=f"zodiac_{section}")
    zodiac_key = ZODIAC_KO_TO_KEY[zodiac_label]

    # 1순위: 띠별 DB
    texts = get_zodiac_texts(db.zodiac, zodiac_key, section)
    # 2순위: 공용 풀 DB
    if not texts:
        pool_name = "today" if section == "today" else "tomorrow"
        texts = get_pool_text(pool_db, pool_name)

    seed_key = f"{section}:{zodiac_key}:{date.today().isoformat()}"
    text = seeded_choice([t for t in texts if isinstance(t, str) and t.strip()], seed_key)
    st.write(text)

with tab_today:
    render_zodiac_section("today", db.today)

with tab_tomorrow:
    render_zodiac_section("tomorrow", db.tomorrow)

with tab_year:
    # 년운은 입력(생년월일/MBTI) + 띠별 년운 조합
    st.subheader("생년월일 / MBTI")
    born = st.date_input("생년월일", value=date(2000, 1, 1), min_value=date(1920, 1, 1), max_value=date(2030, 12, 31))
    mbti_input = st.text_input("MBTI (예: ENFP)", value="", placeholder="ENFP").strip().upper()

    st.subheader("띠 선택")
    zodiac_label = st.selectbox("", zodiac_label_list, key="zodiac_year")
    zodiac_key = ZODIAC_KO_TO_KEY[zodiac_label]

    # (A) 2026 전체 흐름(공용 년운 풀)
    year_texts = get_pool_text(db.year, "year")
    year_text = seeded_choice([t for t in year_texts if isinstance(t, str) and t.strip()], f"year:all:{born.isoformat()}")

    st.write(year_text)

    # (B) 조언(사주/MBTI/띠별 년운을 섞어서 보여주되, 없는 데이터는 조용히 스킵)
    st.subheader("조언")

    advice_parts: List[str] = []

    # 띠별 년운 (우선)
    z_year = get_zodiac_texts(db.zodiac, zodiac_key, "year")
    if z_year:
        advice_parts.append(seeded_choice([t for t in z_year if isinstance(t, str) and t.strip()], f"year:zodiac:{zodiac_key}:{born.isoformat()}"))

    # MBTI 요약/특징
    if mbti_input:
        summary, traits = get_mbti_summary_and_traits(db.mbti, mbti_input)
        if summary:
            advice_parts.append(f"MBTI({mbti_input}) 요약: {summary}")
        if traits:
            # 너무 길면 2~3개만
            pick = traits[:]
            # 입력이 같으면 같은 조합
            rnd = random.Random(sum(map(ord, mbti_input)))
            rnd.shuffle(pick)
            pick = pick[:3]
            advice_parts.append("MBTI 포인트: " + " / ".join(pick))

    # 사주(간단)
    saju_text = get_saju_text(db.saju, born)
    if saju_text:
        advice_parts.append(f"사주(간단 참고): {saju_text}")

    if advice_parts:
        for p in advice_parts:
            st.write(p)
    else:
        st.write("조언 데이터가 아직 준비되지 않았습니다. (DB를 확인해주세요)")

# -----------------------------
# 디버그(숨김): DB 버전 확인
# -----------------------------
with st.expander("DB 상태 확인(관리용)", expanded=False):
    for key, path in DB_FILES.items():
        exists = "✅" if path.exists() else "❌"
        st.write(f"{exists} {path.name}")
