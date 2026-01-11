import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta
import json
import re
import random
import hashlib
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# =========================================================
# 0) 기본 설정 (디자인/구조 임의 변경 금지 기준 준수)
# =========================================================
APP_URL = "https://my-fortune.streamlit.app"  # 필요 시 네 Streamlit 앱 주소로만 수정
DANANEUM_LANDING_URL = "https://incredible-dusk-20d2b5.netlify.app/"

st.set_page_config(
    page_title="2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로",
    page_icon="🔮",
    layout="centered",
)

# =========================================================
# 1) 경로/DB 로더 (data 폴더 기준 + 파일명 후보 방어)
# =========================================================
def _load_json_by_candidates(candidates: List[str]) -> Tuple[Any, str]:
    """
    candidates: ["data/a.json", "data/a", ...]
    존재하는 첫 파일을 로드해서 반환. 없으면 예외(명확하게).
    """
    for p in candidates:
        fp = Path(p)
        if fp.exists() and fp.is_file():
            with open(fp, "r", encoding="utf-8") as f:
                return json.load(f), str(fp)
    raise FileNotFoundError(
        "필수 DB 파일을 찾지 못했습니다.\n"
        + "\n".join([f"- {c}" for c in candidates])
        + "\n\nGitHub에 업로드한 data 폴더 파일명을 다시 확인해주세요."
    )

def load_all_dbs() -> Dict[str, Any]:
    # 사용자가 확정한 DB 목록(확장자 유무 둘 다 대응)
    fortunes_year, path_year = _load_json_by_candidates([
        "data/fortunes_ko_2026.json", "data/fortunes_ko_2026",
        "data/fortunes_ko_2026 (1).json", "data/fortunes_ko_2026 (1)",
    ])
    fortunes_today, path_today = _load_json_by_candidates([
        "data/fortunes_ko_today.json", "data/fortunes_ko_today",
        "data/fortunes_ko_today (1).json", "data/fortunes_ko_today (1)",
        "data/fortunes_ko_today (2).json", "data/fortunes_ko_today (2)",
        "data/fortunes_ko_today (3).json", "data/fortunes_ko_today (3)",
    ])
    fortunes_tomorrow, path_tomorrow = _load_json_by_candidates([
        "data/fortunes_ko_tomorrow.json", "data/fortunes_ko_tomorrow",
        "data/fortunes_ko_tomorrow (1).json", "data/fortunes_ko_tomorrow (1)",
        "data/fortunes_ko_tomorrow (2).json", "data/fortunes_ko_tomorrow (2)",
    ])

    lunar_lny, path_lny = _load_json_by_candidates([
        "data/lunar_new_year_1920_2026.json", "data/lunar_new_year_1920_2026",
    ])

    zodiac_db, path_zodiac = _load_json_by_candidates([
        "data/zodiac_fortunes_ko_2026.json", "data/zodiac_fortunes_ko_2026",
        "data/zodiac_fortunes_ko_2026_FIXED.json", "data/zodiac_fortunes_ko_2026_FIXED",
    ])

    mbti_db, path_mbti = _load_json_by_candidates([
        "data/mbti_traits_ko.json", "data/mbti_traits_ko",
    ])

    saju_db, path_saju = _load_json_by_candidates([
        "data/saju_ko.json", "data/saju_ko",
    ])

    tarot_db, path_tarot = _load_json_by_candidates([
        "data/tarot_db_ko.json", "data/tarot_db_ko",
        "data/tarot_db_ko (1).json", "data/tarot_db_ko (1)",
        "tarot_db_ko.json", "tarot_db_ko",
        "tarot_db_ko (1).json", "tarot_db_ko (1)",
    ])

    return {
        "fortunes_year": fortunes_year,
        "fortunes_today": fortunes_today,
        "fortunes_tomorrow": fortunes_tomorrow,
        "lunar_lny": lunar_lny,
        "zodiac_db": zodiac_db,
        "mbti_db": mbti_db,
        "saju_db": saju_db,
        "tarot_db": tarot_db,
        "paths": {
            "year": path_year,
            "today": path_today,
            "tomorrow": path_tomorrow,
            "lny": path_lny,
            "zodiac": path_zodiac,
            "mbti": path_mbti,
            "saju": path_saju,
            "tarot": path_tarot,
        }
    }

# =========================================================
# 2) 유틸 - 시드 / 문자열 정리
# =========================================================
def stable_seed(*parts: str) -> int:
    s = "|".join([str(p) for p in parts])
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16)

def pick_one(pool: List[str], seed_int: int) -> Optional[str]:
    if not isinstance(pool, list) or len(pool) == 0:
        return None
    r = random.Random(seed_int)
    return r.choice(pool)

def safe_str(x: Any) -> str:
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
# 3) 한국 설(음력 설) 기준 띠 계산
# =========================================================
ZODIAC_ORDER = ["rat","ox","tiger","rabbit","dragon","snake","horse","goat","monkey","rooster","dog","pig"]
ZODIAC_LABEL_KO = {
    "rat":"쥐띠","ox":"소띠","tiger":"호랑이띠","rabbit":"토끼띠","dragon":"용띠","snake":"뱀띠",
    "horse":"말띠","goat":"양띠","monkey":"원숭이띠","rooster":"닭띠","dog":"개띠","pig":"돼지띠",
}
ZODIAC_ANIMAL_KO = {
    "rat":"쥐","ox":"소","tiger":"호랑이","rabbit":"토끼","dragon":"용","snake":"뱀",
    "horse":"말","goat":"양","monkey":"원숭이","rooster":"닭","dog":"개","pig":"돼지",
}

def parse_lny_map(lny_json: Any) -> Dict[int, date]:
    """
    기대 형태:
    { "1920": "1920-02-20", ... }
    """
    out: Dict[int, date] = {}
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

def zodiac_by_birth(birth: date, lny_map: Dict[int, date]) -> Tuple[str, int]:
    y = birth.year
    lny = lny_map.get(y)
    zodiac_year = y
    if lny and birth < lny:
        zodiac_year = y - 1
    zk = zodiac_key_from_year(zodiac_year)
    return zk, zodiac_year

def localize_zodiac_text(text: str) -> str:
    """
    DB 문장에 'rooster띠' 같은 영문 키가 섞이면 한국어로 정리.
    """
    if not text:
        return ""
    out = text
    for k, ko in ZODIAC_LABEL_KO.items():
        out = re.sub(rf"\b{k}\b", ko.replace("띠",""), out, flags=re.IGNORECASE)
        out = out.replace(f"{k}띠", ko)
    # 혹시 'rooster띠' 같은 형태가 이미 위에서 안 잡히면 한번 더
    for k, ko in ZODIAC_LABEL_KO.items():
        out = out.replace(f"{k}띠", ko)
    return out

# =========================================================
# 4) MBTI (직접선택 / 16문항)
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

def compute_mbti_from_answers(answers: List[Tuple[str, bool]]) -> str:
    scores = {"EI":0,"SN":0,"TF":0,"JP":0}
    counts = {"EI":0,"SN":0,"TF":0,"JP":0}
    for axis, pick_left in answers:
        if axis in scores:
            counts[axis] += 1
            if pick_left:
                scores[axis] += 1

    def decide(axis: str, left_char: str, right_char: str) -> str:
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

def get_mbti_trait_text(mbti_db: Any, mbti: str) -> str:
    """
    mbti_traits_ko.json 구조 방어:
    - {"traits": {"ENFP": {...}}}
    - {"ENFP": {...}}
    - {"types": {...}}
    """
    data = mbti_db
    if isinstance(data, dict) and isinstance(data.get("traits"), dict):
        data = data["traits"]
    if isinstance(data, dict) and isinstance(data.get("types"), dict):
        data = data["types"]

    item = data.get(mbti) if isinstance(data, dict) else None
    if not item:
        return ""

    if isinstance(item, str):
        return strip_html_like(item)

    if isinstance(item, dict):
        kws = item.get("keywords") or []
        tips = item.get("tips") or item.get("actions") or []
        # 보기 좋은 출력(태그 깨짐 방지)
        kw_txt = " · ".join([strip_html_like(str(x)) for x in kws][:6]).strip()
        tips_txt = ", ".join([strip_html_like(str(x)) for x in tips][:3]).strip()
        out = ""
        if kw_txt:
            out += f"키워드: {kw_txt} "
        if tips_txt:
            out += f"[{tips_txt}]"
        return out.strip()

    return strip_html_like(safe_str(item))

# =========================================================
# 5) 친구 공유 버튼 (카톡 막힘 대비: URL 복사 버튼 포함)
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
# 6) 타로 (하루 동안 같은 카드 고정 + back 이미지 오류 방어 + 흔들림/뿅)
# =========================================================
PNG_SIG = b"\x89PNG\r\n\x1a\n"
JPG_SIG = b"\xff\xd8\xff"

def _safe_read_image_bytes(path: Path) -> Optional[bytes]:
    """
    이미지 파일이 실제 이미지인지(서명)까지 확인해서 bytes 반환.
    (Git LFS 포인터/텍스트 파일이면 None)
    """
    try:
        if not path.exists() or not path.is_file():
            return None
        b = path.read_bytes()
        if b.startswith(PNG_SIG) or b.startswith(JPG_SIG) or b[:4] == b"RIFF":
            return b
        return None
    except Exception:
        return None

def _b64_data_uri(img_bytes: bytes) -> str:
    mime = "image/png"
    if img_bytes.startswith(JPG_SIG):
        mime = "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(img_bytes).decode('ascii')}"

def _flatten_tarot_cards(tarot_db: Any) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    if isinstance(tarot_db, dict):
        # 예상 구조: {"majors":[...], "minors": {...}} 혹은 {"cards":[...]}
        if isinstance(tarot_db.get("cards"), list):
            for c in tarot_db["cards"]:
                if isinstance(c, dict):
                    cards.append(c)
        if isinstance(tarot_db.get("majors"), list):
            for c in tarot_db["majors"]:
                if isinstance(c, dict):
                    cards.append(c)
        if isinstance(tarot_db.get("minors"), dict):
            for suit, arr in tarot_db["minors"].items():
                if isinstance(arr, list):
                    for c in arr:
                        if isinstance(c, dict):
                            cards.append(c)
    elif isinstance(tarot_db, list):
        for c in tarot_db:
            if isinstance(c, dict):
                cards.append(c)
    return cards

def _pick_tarot_of_day(tarot_db: Any, birth: date, name: str, mbti: str, today: date) -> Optional[Dict[str, Any]]:
    cards = _flatten_tarot_cards(tarot_db)
    cleaned: List[Dict[str, Any]] = []
    for c in cards:
        # tarot_db_ko.json 기준: name_ko/name_en/upright/reversed/image
        name_ko = c.get("name_ko") or c.get("name") or c.get("title")
        name_en = c.get("name_en") or ""
        image = c.get("image") or c.get("img") or ""
        upright = c.get("upright") if isinstance(c.get("upright"), dict) else {}
        reversed_ = c.get("reversed") if isinstance(c.get("reversed"), dict) else {}

        if not name_ko:
            continue
        cleaned.append({
            "name_ko": strip_html_like(str(name_ko)),
            "name_en": strip_html_like(str(name_en)),
            "image": str(image),
            "upright": upright,
            "reversed": reversed_,
            "keywords": c.get("keywords") or [],
        })

    if not cleaned:
        return None

    seed_int = stable_seed(str(today), str(birth), name, mbti, "tarot_of_day")
    r = random.Random(seed_int)
    card = r.choice(cleaned)
    # 방향도 날짜/유저 기준으로 고정
    is_upright = (stable_seed(str(today), str(birth), name, mbti, "tarot_dir") % 2 == 0)
    card["direction"] = "upright" if is_upright else "reversed"
    return card

def tarot_ui(tarot_db: Any, birth: date, name: str, mbti: str):
    st.markdown("<div class='card tarot-card'>", unsafe_allow_html=True)
    st.markdown("### 🃏 오늘의 타로카드 <span style='font-size:0.92rem;opacity:0.85;'>(하루 1회 가능)</span>", unsafe_allow_html=True)
    st.markdown(
        "<div class='soft-box'>"
        "뒷면 카드를 보고 <b>뽑기</b>를 누르면 오늘의 카드가 공개됩니다.<br>"
        "오늘 하루 동안은 <b>같은 카드(같은 의미/이미지)</b>로 고정됩니다."
        "</div>",
        unsafe_allow_html=True
    )

    # back.png 경로(사용자 구조 고정)
    back_candidates = [
        Path("assets/tarot/back.png"),
        Path("assets/tarot/back.jpg"),
        Path("assets/tarot/back.webp"),
        Path("assets/tarot/back.jpeg"),
    ]
    back_bytes = None
    for p in back_candidates:
        back_bytes = _safe_read_image_bytes(p)
        if back_bytes:
            break

    if "tarot_revealed" not in st.session_state:
        st.session_state.tarot_revealed = False
    if "tarot_anim" not in st.session_state:
        st.session_state.tarot_anim = False

    # back 이미지(에러 방지: HTML로 렌더)
    if back_bytes:
        uri = _b64_data_uri(back_bytes)
        shake_class = "shake" if st.session_state.tarot_anim else ""
        components.html(f"""
        <style>
          .tarot-wrap {{
            width:100%;
            border-radius:18px;
            overflow:hidden;
            border:1px solid rgba(140,120,200,0.18);
            box-shadow: 0 10px 28px rgba(0,0,0,0.10);
            margin-top: 10px;
          }}
          .tarot-img {{
            width:100%;
            display:block;
            border-radius:18px;
          }}
          .shake {{
            animation: shake 0.35s ease-in-out;
          }}
          @keyframes shake {{
            0% {{ transform: translateX(0); }}
            15% {{ transform: translateX(-6px) rotate(-1deg); }}
            30% {{ transform: translateX(6px) rotate(1deg); }}
            45% {{ transform: translateX(-4px) rotate(-1deg); }}
            60% {{ transform: translateX(4px) rotate(1deg); }}
            75% {{ transform: translateX(-2px); }}
            100% {{ transform: translateX(0); }}
          }}
        </style>
        <div class="tarot-wrap">
          <img class="tarot-img {shake_class}" src="{uri}" />
        </div>
        """, height=260)
    else:
        st.markdown(
            "<div style='height:220px;border-radius:18px;"
            "background:linear-gradient(135deg,#2b2350,#6b4fd6,#fbc2eb);"
            "display:flex;align-items:center;justify-content:center;"
            "color:white;font-weight:900;font-size:1.2rem;'>TAROT BACK</div>",
            unsafe_allow_html=True
        )

    if st.button("타로카드 뽑기", use_container_width=True):
        st.session_state.tarot_revealed = True
        st.session_state.tarot_anim = True
        st.rerun()

    # 애니메이션은 1회만 보여주고 바로 해제
    if st.session_state.tarot_anim:
        st.session_state.tarot_anim = False

    if st.session_state.tarot_revealed:
        card = _pick_tarot_of_day(tarot_db, birth, name, mbti, date.today())
        if not card:
            st.info("타로 DB에서 카드를 불러오지 못했습니다. (tarot_db_ko.json 확인)")
        else:
            direction = card.get("direction", "upright")
            pack = card.get(direction, {}) if isinstance(card.get(direction), dict) else {}
            summary = strip_html_like(str(pack.get("summary", ""))).strip()
            # 한 줄 설명(짧게)
            extra = ""
            for k in ["love","work","money","health"]:
                if pack.get(k):
                    extra = strip_html_like(str(pack.get(k))).strip()
                    break

            # 카드 이미지(있으면 표시, 없으면 의미만)
            img_path = Path(card.get("image") or "")
            img_bytes = _safe_read_image_bytes(img_path) if str(img_path) else None
            if img_bytes:
                uri2 = _b64_data_uri(img_bytes)
                components.html(f"""
                <style>
                  .pop {{
                    animation: pop 0.22s ease-out;
                  }}
                  @keyframes pop {{
                    from {{ transform: scale(0.97); opacity: 0.5; }}
                    to {{ transform: scale(1.0); opacity: 1; }}
                  }}
                </style>
                <div class="tarot-wrap pop" style="margin-top:12px;">
                  <img class="tarot-img" src="{uri2}" />
                </div>
                """, height=340)

            st.markdown(
                f"""
                <div class="reveal">
                  <div class="reveal-title">✨ {card.get('name_ko','')}{' ('+card.get('name_en','')+')' if card.get('name_en') else ''}</div>
                  <div class="reveal-meaning"><b>{'정방향' if direction=='upright' else '역방향'}</b> · {summary}</div>
                  {f"<div class='reveal-meaning' style='margin-top:6px;opacity:0.95;'>• {extra}</div>" if extra else ""}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 7) 다나눔렌탈 광고(문구 고정)
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
# 8) 스타일 (그라데이션 + 카드형 고정)
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
</style>
""", unsafe_allow_html=True)

# =========================================================
# 9) 세션 상태
# =========================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"  # input / result

if "name" not in st.session_state:
    st.session_state.name = ""

if "birth" not in st.session_state:
    st.session_state.birth = date(2005, 1, 1)

if "mbti_mode" not in st.session_state:
    st.session_state.mbti_mode = "direct"  # direct / q16

if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFP"

# =========================================================
# 10) 입력 화면
# =========================================================
def render_input(dbs: Dict[str, Any]):
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로</p>
      <p class="hero-sub">이름 + 생년월일 + MBTI로 결과가 고정 출력됩니다</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름", value=st.session_state.name, placeholder="예) 홍길동")

    # ✅ 달력형 생년월일
    st.session_state.birth = st.date_input(
        "생년월일",
        value=st.session_state.birth,
        min_value=date(1920, 1, 1),
        max_value=date(2026, 12, 31),
    )

    # ✅ 음력 설 기준 띠 자동 결정
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
        st.session_state.mbti = st.selectbox("MBTI 직접 선택", MBTI_TYPES, index=MBTI_TYPES.index(st.session_state.mbti))
        trait_txt = get_mbti_trait_text(dbs["mbti_db"], st.session_state.mbti)
        if trait_txt:
            st.markdown(f"<div class='soft-box'><b>{st.session_state.mbti}</b> · {trait_txt}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='soft-box'>각 문항에서 더 가까운 쪽을 선택하세요. 제출하면 MBTI가 확정됩니다.</div>", unsafe_allow_html=True)
        answers: List[Tuple[str, bool]] = []
        for i, (axis, left, right) in enumerate(MBTI_Q16, start=1):
            choice = st.radio(
                f"{i}.",
                [left, right],
                key=f"mbti16_{i}"
            )
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
# 11) 결과 화면(띠/MBTI/사주/오늘/내일/연간/타로/광고/공유)
# =========================================================
def _get_pool_from_fortune_db(fdb: Any, key_name: str) -> List[str]:
    pool: List[Any] = []
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

def _get_year_2026_pool(ydb: Any) -> List[str]:
    if isinstance(ydb, dict):
        if isinstance(ydb.get("pools"), dict) and isinstance(ydb["pools"].get("year_all"), list):
            return [strip_html_like(safe_str(x)) for x in ydb["pools"]["year_all"] if safe_str(x).strip()]
        if isinstance(ydb.get("year_all"), list):
            return [strip_html_like(safe_str(x)) for x in ydb["year_all"] if safe_str(x).strip()]
        if isinstance(ydb.get("lines"), list):
            return [strip_html_like(safe_str(x)) for x in ydb["lines"] if safe_str(x).strip()]
    if isinstance(ydb, list):
        return [strip_html_like(safe_str(x)) for x in ydb if safe_str(x).strip()]
    return []

def _get_zodiac_year_pool(zdb: Any, zodiac_key: str) -> List[str]:
    """
    zodiac_fortunes_ko_2026.json 구조 방어:
    - { "monkey": { "year_2026": [...], "today": [...], ... } }
    - { "monkey": [ ... ] }
    - { "zodiacs": {...} }
    """
    data = zdb
    if isinstance(data, dict) and isinstance(data.get("zodiacs"), dict):
        data = data["zodiacs"]

    v = data.get(zodiac_key) if isinstance(data, dict) else None
    if isinstance(v, list):
        return [strip_html_like(safe_str(x)) for x in v if safe_str(x).strip()]
    if isinstance(v, dict):
        # 연간을 우선 사용
        for cand in ["year_2026", "year", "year_all", "overall", "lines", "items"]:
            if isinstance(v.get(cand), list):
                return [strip_html_like(safe_str(x)) for x in v[cand] if safe_str(x).strip()]
    return []

def _pick_saju_one_line(saju_db: Any, birth: date, base_seed: int) -> str:
    """
    saju_ko.json 구조 방어(현재 파일: {"elements":[{key, pools:{overall, ...}}]})
    - 원소(key)를 유저 기준으로 고정 선택 후 overall/advice에서 1줄 선택
    """
    elements = []
    if isinstance(saju_db, dict) and isinstance(saju_db.get("elements"), list):
        elements = [e for e in saju_db["elements"] if isinstance(e, dict) and e.get("key")]
    elif isinstance(saju_db, list):
        elements = [e for e in saju_db if isinstance(e, dict) and e.get("key")]

    if not elements:
        return ""

    idx = stable_seed(str(birth), str(base_seed), "saju_element") % len(elements)
    elem = elements[idx]
    pools = elem.get("pools") if isinstance(elem.get("pools"), dict) else {}
    # overall 우선
    pool = pools.get("overall") if isinstance(pools.get("overall"), list) else []
    if not pool and isinstance(pools.get("advice"), list):
        pool = pools["advice"]
    clean_pool = [strip_html_like(safe_str(x)) for x in pool if safe_str(x).strip()]
    return pick_one(clean_pool, stable_seed(str(base_seed), "saju_line")) or ""

def ensure_text(val: Optional[str], label: str) -> str:
    if val and str(val).strip():
        return str(val).strip()
    return f"{label} 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"

def render_result(dbs: Dict[str, Any]):
    name = (st.session_state.name or "").strip()
    birth = st.session_state.birth
    mbti = (st.session_state.mbti or "ENFP").strip()

    lny_map = parse_lny_map(dbs["lunar_lny"])
    zodiac_key, zodiac_year = zodiac_by_birth(birth, lny_map)
    zodiac_label = ZODIAC_LABEL_KO.get(zodiac_key, zodiac_key)

    base_seed = stable_seed(str(birth), name, mbti)

    # 1) 띠 운세(연간)
    zodiac_pool = _get_zodiac_year_pool(dbs["zodiac_db"], zodiac_key)
    zodiac_text = pick_one(zodiac_pool, stable_seed(str(base_seed), "zodiac_year"))
    zodiac_text = localize_zodiac_text(zodiac_text or "")

    # 2) MBTI 특징
    mbti_trait = get_mbti_trait_text(dbs["mbti_db"], mbti)

    # 3) 사주 한마디(1줄)
    saju_text = _pick_saju_one_line(dbs["saju_db"], birth, base_seed)

    # 4) 오늘/내일 (날짜 포함 시드)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_pool = _get_pool_from_fortune_db(dbs["fortunes_today"], "today")
    tomorrow_pool = _get_pool_from_fortune_db(dbs["fortunes_tomorrow"], "tomorrow")

    today_text = pick_one(today_pool, stable_seed(str(base_seed), str(today), "today"))
    tomorrow_text = pick_one(tomorrow_pool, stable_seed(str(base_seed), str(tomorrow), "tomorrow"))

    # 5) 2026 전체 운세
    year_pool = _get_year_2026_pool(dbs["fortunes_year"])
    year_text = pick_one(year_pool, stable_seed(str(base_seed), "year_2026"))

    zodiac_text = ensure_text(zodiac_text, "띠 운세")
    mbti_trait = ensure_text(mbti_trait, "MBTI 특징")
    saju_text = ensure_text(saju_text, "사주 한 마디")
    today_text = ensure_text(today_text, "오늘 운세")
    tomorrow_text = ensure_text(tomorrow_text, "내일 운세")
    year_text = ensure_text(year_text, "2026 전체 운세")

    display_name = f"{name}님의" if name else "당신의"
    st.markdown(
        f"""
        <div class="header-hero">
          <p class="hero-title">{display_name} 운세 결과</p>
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

    # 결과창 바로 밑: 공유
    share_block()

    # 광고(고정)
    dananeum_ad_block()

    # 타로
    tarot_ui(dbs["tarot_db"], birth, name, mbti)

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
