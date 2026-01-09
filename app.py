# app.py
# 2026 운세 앱 (UI/광고 문구 고정, DB는 data 폴더 JSON 사용)

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


# =========================================================
# 고정(절대 변경 금지) 영역
# =========================================================

APP_TITLE = "2026년 운세"

# [광고] 문구는 사용자 고정본 그대로 (절대 변경 금지)
RENTAL_AD_COPY = (
    "[광고] 정수기 렌탈 제휴카드 적용시 월 렌탈비 0원, 설치당일 최대 현금50만원 + 사은품 증정\n"
    "-> 이름, 전화번호 작성. 무료 상담하기 -> 구글시트 연동"
)

RENTAL_BRAND_LINE = "다나눔렌탈 1660-2445"


# =========================================================
# 파일 경로(사용자 data 폴더 파일명 기준)
# =========================================================

DATA_DIR = Path(__file__).parent / "data"

DB_FILES = {
    "fortunes_today": "fortunes_ko_today.json",
    "fortunes_tomorrow": "fortunes_ko_tomorrow.json",
    "fortunes_year": "fortunes_ko_2026.json",  # (사용자 요청) fortunes_ko_2026_year.json -> fortunes_ko_2026.json
    "zodiac": "zodiac_fortunes_ko_2026.json",
    "mbti": "mbti_traits_ko.json",
    "saju": "saju_ko.json",
    "lunar_new_year": "lunar_new_year_1920_2026.json",
    "tarot": "tarot_db_ko.json",  # 있어도/없어도 앱은 동작
}

# 그라데이션 배너(사용자 요청: “처음에 그라데이션 들어갔던 이미지”)
BANNER_IMAGE = DATA_DIR / "A_digital_gradient_background_features_a_smooth_an.png"


# =========================================================
# 유틸
# =========================================================

def _safe_read_json(path: Path) -> Tuple[Optional[dict], Optional[str]]:
    """JSON을 읽고, 실패하면 (None, 에러메시지) 반환."""
    try:
        if not path.exists():
            return None, f"파일 없음: {path.as_posix()}"
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None, f"JSON 최상위가 dict가 아닙니다: {path.name}"
        return data, None
    except Exception as e:
        return None, f"JSON 로드 실패({path.name}): {e}"


def _seeded_choice(items: List[str], seed_key: str) -> str:
    """항상 같은 입력이면 같은 문장이 나오도록 시드 선택."""
    if not items:
        return ""
    rnd = random.Random(seed_key)
    return rnd.choice(items)


def _today_seed() -> str:
    return date.today().isoformat()


def _tomorrow_seed() -> str:
    return (date.today().toordinal() + 1).__str__()


def _clean_mbti(s: str) -> str:
    s = (s or "").strip().upper()
    s = re.sub(r"[^A-Z]", "", s)
    if len(s) != 4:
        return ""
    # 간단 검증
    ok = (
        s[0] in "EI" and
        s[1] in "SN" and
        s[2] in "TF" and
        s[3] in "JP"
    )
    return s if ok else ""


# =========================================================
# 띠 매핑
# =========================================================

ZODIAC_ORDER = [
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
ZODIAC_KEY_BY_LABEL = {label: key for key, label in ZODIAC_ORDER}
ZODIAC_LABELS = [label for _, label in ZODIAC_ORDER]


# =========================================================
# 사주(간단참고) - 아주 단순한 요소 매핑
# (정교한 사주 계산은 추후 고도화 / 현재는 DB 활용용)
# =========================================================

ELEMENT_CYCLE = ["wood", "fire", "earth", "metal", "water"]
ELEMENT_KO = {
    "wood": "목(木)",
    "fire": "화(火)",
    "earth": "토(土)",
    "metal": "금(金)",
    "water": "수(水)",
}


def _element_from_birth_year(y: int) -> str:
    # 5요소 순환 간단 매핑 (임의 규칙이 아니라 “간단 참고”로만 표기)
    # 기준점은 1924(갑자) 같은 정교 기준이 아니라 단순 분배 목적
    return ELEMENT_CYCLE[y % 5]


def _saju_summary(saju_db: dict, birth: date) -> str:
    el = _element_from_birth_year(birth.year)
    items = saju_db.get("elements", [])
    # saju_db["elements"]는 리스트 구조
    found = None
    for it in items:
        if isinstance(it, dict) and it.get("id") == el:
            found = it
            break
    if not found:
        return "사주(간단 참고): (내용 없음)"
    summary = found.get("summary") or ""
    ko = ELEMENT_KO.get(el, el)
    return f"사주(간단 참고): {ko} - {summary}" if summary else f"사주(간단 참고): {ko} (내용 없음)"


# =========================================================
# DB 로더
# =========================================================

@dataclass
class DB:
    fortunes_today: dict
    fortunes_tomorrow: dict
    fortunes_year: dict
    zodiac: dict
    mbti: dict
    saju: dict
    lunar_new_year: dict
    tarot: dict
    errors: List[str]


@st.cache_data(show_spinner=False)
def load_all_db() -> DB:
    errors: List[str] = []

    def load(name: str) -> dict:
        path = DATA_DIR / DB_FILES[name]
        data, err = _safe_read_json(path)
        if err:
            errors.append(err)
            return {}
        return data or {}

    db = DB(
        fortunes_today=load("fortunes_today"),
        fortunes_tomorrow=load("fortunes_tomorrow"),
        fortunes_year=load("fortunes_year"),
        zodiac=load("zodiac"),
        mbti=load("mbti"),
        saju=load("saju"),
        lunar_new_year=load("lunar_new_year"),
        tarot=load("tarot"),
        errors=errors,
    )
    return db


# =========================================================
# 시트 연동 (Apps Script Webhook)
# =========================================================

def _post_to_sheet(payload: dict) -> Tuple[bool, str]:
    """
    Streamlit Cloud:
      - st.secrets["google"]["sheet_webhook_url"] 또는
      - 환경변수 SHEET_WEBHOOK_URL
    로 설정된 Apps Script Webhook에 POST
    """
    try:
        import requests  # type: ignore
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


# =========================================================
# 공유/URL 복사 UI (친구 공유 불가 이슈 방지: 복사 중심)
# =========================================================

def render_share_buttons() -> None:
    """
    - 모바일에서 ‘친구에게 공유하기’는 navigator.share 지원 여부에 따라 실패할 수 있어
      ‘URL 복사’가 항상 되도록 구성.
    """
    url = st.get_url()

    col1, col2 = st.columns(2)
    with col1:
        st.components.v1.html(
            f"""
            <button style="
                width:100%; padding:12px 14px; border-radius:12px;
                border:1px solid #e5e7eb; background:white; font-size:16px;
            " onclick="
                if (navigator.share) {{
                  navigator.share({{title:'{APP_TITLE}', url:'{url}'}}).catch(()=>{{}});
                }} else {{
                  navigator.clipboard.writeText('{url}').then(()=>{{}});
                }}
            ">친구에게 공유하기</button>
            """,
            height=56,
        )

    with col2:
        st.components.v1.html(
            f"""
            <button style="
                width:100%; padding:12px 14px; border-radius:12px;
                border:1px solid #e5e7eb; background:white; font-size:16px;
            " onclick="
                navigator.clipboard.writeText('{url}').then(()=>{
                  const el = document.getElementById('copy_toast');
                  if(el) el.style.display='block';
                  setTimeout(()=>{{ if(el) el.style.display='none'; }}, 1200);
                });
            ">URL 복사</button>
            <div id="copy_toast" style="
                display:none; margin-top:8px; padding:10px 12px; border-radius:12px;
                background:#111827; color:white; font-size:14px; text-align:center;
            ">클립보드에 복사했어요.</div>
            """,
            height=92,
        )


# =========================================================
# 운세 추출 로직
# =========================================================

def _get_pool(db: dict, pool_key: str) -> List[str]:
    pools = db.get("pools", {})
    pool = pools.get(pool_key, [])
    return pool if isinstance(pool, list) else []


def pick_general_today(today_db: dict) -> str:
    items = _get_pool(today_db, "today")
    return _seeded_choice(items, f"{_today_seed()}|general|today")


def pick_general_tomorrow(tomorrow_db: dict) -> str:
    items = _get_pool(tomorrow_db, "tomorrow")
    return _seeded_choice(items, f"{_today_seed()}|general|tomorrow")


def pick_general_year(year_db: dict, mbti_code: str, zodiac_key: str, birth: date) -> str:
    items = _get_pool(year_db, "year")
    # 입력에 따라 조금씩 달라지도록 시드
    seed = f"{birth.isoformat()}|{mbti_code}|{zodiac_key}|year"
    return _seeded_choice(items, seed)


def pick_zodiac_text(zodiac_db: dict, zodiac_key: str, kind: str) -> str:
    """
    zodiac_db 구조:
      zodiac_key: { "today": [...], "tomorrow": [...], "year_2026": [...] }
    과거 코드에서 year를 찾다가 깨졌던 문제를 방지하기 위해
      - kind == "year": "year_2026" 우선, 없으면 "year"
    """
    node = zodiac_db.get(zodiac_key, {})
    if not isinstance(node, dict):
        return ""

    if kind == "today":
        items = node.get("today", [])
        seed = f"{_today_seed()}|{zodiac_key}|today"
    elif kind == "tomorrow":
        items = node.get("tomorrow", [])
        seed = f"{_today_seed()}|{zodiac_key}|tomorrow"
    else:
        items = node.get("year_2026") or node.get("year") or []
        seed = f"{_today_seed()}|{zodiac_key}|year"

    if not isinstance(items, list):
        return ""
    return _seeded_choice(items, seed)


def pick_mbti_summary(mbti_db: dict, mbti_code: str) -> str:
    traits = mbti_db.get("traits", {})
    if not isinstance(traits, dict):
        return ""
    item = traits.get(mbti_code, {})
    if not isinstance(item, dict):
        return ""
    return (item.get("summary") or "").strip()


# =========================================================
# UI (디자인은 기존 형태 유지 + 배너만 복구)
# =========================================================

st.set_page_config(page_title=APP_TITLE, page_icon="✨", layout="centered")

db = load_all_db()

# DB 로드 오류는 상단에만 조용히 표시(앱 자체는 동작)
if db.errors:
    with st.expander("DB 상태(오류 확인)", expanded=False):
        for e in db.errors:
            st.error(e)

# 배너(그라데이션 이미지) - 사용자 요청
if BANNER_IMAGE.exists():
    st.image(str(BANNER_IMAGE), use_container_width=True)

st.title(APP_TITLE)

# 고정 광고 영역 (문구 변경 금지)
st.subheader("다나눔렌탈 상담/이벤트")
st.write(RENTAL_BRAND_LINE)
render_share_buttons()

st.info(RENTAL_AD_COPY)

# 상담 폼 (구글시트 연동) - 컬럼 구조 고정
with st.form("rental_form", clear_on_submit=True):
    name = st.text_input("이름")
    phone = st.text_input("전화번호")
    apply = st.checkbox("무료 상담하기", value=True)
    submitted = st.form_submit_button("제출")

if submitted:
    payload = {
        "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "이름": name.strip(),
        "전화번호": phone.strip(),
        "언어": "ko",
        "기록초": "",
        "공유여부": False,
        "상담신청": "O(정수기)" if apply else "",
    }
    ok, msg = _post_to_sheet(payload)
    if ok:
        st.success(msg)
    else:
        st.warning(msg)

# 메인 탭 (디자인 고정 유지)
tab_today, tab_tomorrow, tab_year = st.tabs(["오늘의 운세", "내일의 운세", "2026년 전체 운세"])

# --- 오늘 ---
with tab_today:
    st.subheader("띠 선택")
    label = st.selectbox(" ", ZODIAC_LABELS, key="zodiac_today")
    zkey = ZODIAC_KEY_BY_LABEL[label]

    general = pick_general_today(db.fortunes_today) if db.fortunes_today else ""
    if general:
        st.write(general)

    ztxt = pick_zodiac_text(db.zodiac, zkey, "today") if db.zodiac else ""
    if ztxt:
        st.write(ztxt)

    if not general and not ztxt:
        st.warning("표시할 문장이 없습니다. (DB를 확인해 주세요)")

# --- 내일 ---
with tab_tomorrow:
    st.subheader("띠 선택")
    label = st.selectbox(" ", ZODIAC_LABELS, key="zodiac_tomorrow")
    zkey = ZODIAC_KEY_BY_LABEL[label]

    general = pick_general_tomorrow(db.fortunes_tomorrow) if db.fortunes_tomorrow else ""
    if general:
        st.write(general)

    ztxt = pick_zodiac_text(db.zodiac, zkey, "tomorrow") if db.zodiac else ""
    if ztxt:
        st.write(ztxt)

    if not general and not ztxt:
        st.warning("표시할 문장이 없습니다. (DB를 확인해 주세요)")

# --- 2026 전체 ---
with tab_year:
    st.subheader("생년월일 / MBTI")
    birth = st.date_input("생년월일", value=date(2000, 1, 1))
    mbti_in = st.text_input("MBTI (예: ENFP)", value="", placeholder="ENFP")
    mbti_code = _clean_mbti(mbti_in)

    st.subheader("띠 선택")
    label = st.selectbox(" ", ZODIAC_LABELS, key="zodiac_year")
    zkey = ZODIAC_KEY_BY_LABEL[label]

    # 2026년 전체 운세(대용량 풀에서 1개)
    year_text = pick_general_year(db.fortunes_year, mbti_code, zkey, birth) if db.fortunes_year else ""
    if year_text:
        st.write(year_text)
    else:
        st.warning("표시할 문장이 없습니다. (DB를 확인해 주세요)")

    st.subheader("조언")

    # MBTI 한줄 요약
    if mbti_code:
        mbti_summary = pick_mbti_summary(db.mbti, mbti_code) if db.mbti else ""
        if mbti_summary:
            st.write(f"MBTI: {mbti_code} - {mbti_summary}")
        else:
            st.write(f"MBTI: {mbti_code} - (내용 없음)")
    else:
        st.write("MBTI: (입력 없음)")

    # 사주(간단참고)
    if db.saju:
        st.write(_saju_summary(db.saju, birth))
    else:
        st.write("사주(간단 참고): (DB 없음)")

    # 띠별 2026년 운세(별도)
    zyear = pick_zodiac_text(db.zodiac, zkey, "year") if db.zodiac else ""
    if zyear:
        st.write(f"{zkey}띠 2026: {zyear}")

