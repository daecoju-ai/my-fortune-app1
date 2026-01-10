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
# 1) 유틸
# =========================================================
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


def stable_seed(*parts: str) -> int:
    s = "|".join([str(p) for p in parts])
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:12], 16)


def pick_one(pool, seed_int: int):
    if not isinstance(pool, list) or len(pool) == 0:
        return None
    r = random.Random(seed_int)
    return r.choice(pool)


def ensure_text(val, label):
    if val and str(val).strip():
        return val
    return f"{label} 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"


# =========================================================
# 2) JSON 로더
# =========================================================
def _load_json_by_candidates(candidates):
    for p in candidates:
        fp = Path(p)
        if fp.exists():
            with open(fp, "r", encoding="utf-8") as f:
                return json.load(f), str(fp)
    raise FileNotFoundError(
        "필수 DB 파일을 찾지 못했습니다.\n"
        + "\n".join([f"- {c}" for c in candidates])
        + "\n\nGitHub에 업로드한 data 폴더 파일명을 다시 확인해주세요."
    )


def unwrap_db(x):
    """
    DB 구조가 {data:{...}} / {items:[...]} / {pools:{...}} 같이 감싸져 있으면
    내부 실제 데이터를 최대한 꺼내서 반환.
    """
    if isinstance(x, dict):
        # 흔한 래퍼 키들
        for k in ["data", "DATA", "result", "results", "payload", "items", "item", "content", "contents", "db"]:
            if k in x and isinstance(x[k], (dict, list)):
                return unwrap_db(x[k])

        # MBTI/띠 관련 흔한 키
        for k in ["mbti_traits", "mbti", "traits", "zodiac", "zodiacs", "fortunes", "fortune", "cards"]:
            if k in x and isinstance(x[k], (dict, list)):
                return unwrap_db(x[k])

        return x
    return x


def normalize_mbti_db(mbti_db):
    """
    mbti db를 dict로 만들고 키를 대문자로 정규화.
    - dict이면 키 정규화
    - list이면 가능한 구조를 dict로 변환
    """
    mbti_db = unwrap_db(mbti_db)

    if isinstance(mbti_db, dict):
        out = {}
        for k, v in mbti_db.items():
            kk = str(k).strip().upper()
            out[kk] = v
        return out

    # 리스트형이면 {type:"ENFP", ...} 같은 걸 dict로 변환 시도
    if isinstance(mbti_db, list):
        out = {}
        for row in mbti_db:
            if isinstance(row, dict):
                t = row.get("type") or row.get("mbti") or row.get("name")
                if t:
                    out[str(t).strip().upper()] = row
        return out if out else mbti_db

    return mbti_db


def normalize_zodiac_db(zodiac_db):
    zodiac_db = unwrap_db(zodiac_db)

    # dict 형태면 그대로
    if isinstance(zodiac_db, dict):
        # 키 trim
        out = {}
        for k, v in zodiac_db.items():
            out[str(k).strip()] = v
        return out

    # list 형태면 {"zodiac":"monkey", "text":"..."} 같은 걸 dict로 변환 시도
    if isinstance(zodiac_db, list):
        out = {}
        for row in zodiac_db:
            if isinstance(row, dict):
                z = row.get("zodiac") or row.get("animal") or row.get("key")
                t = row.get("text") or row.get("fortune") or row.get("desc")
                if z and t:
                    out[str(z).strip()] = [t]  # 풀로 만들기
        return out if out else zodiac_db

    return zodiac_db


def format_mbti_trait(val) -> str:
    if val is None:
        return ""
    if isinstance(val, str):
        return strip_html_like(val)
    if isinstance(val, list):
        items = [strip_html_like(safe_str(x)) for x in val if safe_str(x).strip()]
        return " / ".join(items)
    if isinstance(val, dict):
        keywords = val.get("keywords") or val.get("keyword") or val.get("키워드")
        tips = val.get("tips") or val.get("tip") or val.get("추천") or val.get("advice")
        text = val.get("text") or val.get("desc") or val.get("설명")

        parts = []
        if keywords:
            if isinstance(keywords, list):
                parts.append("키워드: " + " · ".join([strip_html_like(safe_str(x)) for x in keywords]))
            else:
                parts.append("키워드: " + strip_html_like(safe_str(keywords)))
        if tips:
            if isinstance(tips, list):
                parts.append(strip_html_like(safe_str(tips)))
            else:
                parts.append(strip_html_like(safe_str(tips)))
        if text and not parts:
            parts.append(strip_html_like(safe_str(text)))

        return " ".join([p for p in parts if p.strip()]) if parts else strip_html_like(safe_str(val))

    return strip_html_like(safe_str(val))


# =========================================================
# 3) 띠 계산(설 기준)
# =========================================================
ZODIAC_ORDER = ["rat", "ox", "tiger", "rabbit", "dragon", "snake", "horse", "goat", "monkey", "rooster", "dog", "pig"]
ZODIAC_LABEL_KO = {
    "rat": "쥐띠",
    "ox": "소띠",
    "tiger": "호랑이띠",
    "rabbit": "토끼띠",
    "dragon": "용띠",
    "snake": "뱀띠",
    "horse": "말띠",
    "goat": "양띠",
    "monkey": "원숭이띠",
    "rooster": "닭띠",
    "dog": "개띠",
    "pig": "돼지띠",
}


def parse_lny_map(lny_json):
    lny_json = unwrap_db(lny_json)
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


def normalize_zodiac_text(text: str) -> str:
    if not text:
        return text
    out = text
    for k in ZODIAC_ORDER:
        out = out.replace(f"{k}띠", ZODIAC_LABEL_KO.get(k, f"{k}띠"))
        out = out.replace(f"{k} 띠", ZODIAC_LABEL_KO.get(k, f"{k} 띠"))
    return out


# =========================================================
# 4) 타로 - LFS 포인터 방어 + st.image 안전 출력
# =========================================================
def is_git_lfs_pointer(data: bytes) -> bool:
    if not data:
        return False
    head = data[:200]
    return b"version https://git-lfs.github.com/spec" in head


def read_file_bytes(path: Path) -> bytes | None:
    try:
        b = path.read_bytes()
        return b
    except Exception:
        return None


def safe_st_image(data_or_path, use_container_width=True):
    """
    st.image가 실패하면(특히 LFS 포인터/깨진 파일) 예외 대신 대체 UI로 처리
    """
    try:
        st.image(data_or_path, use_container_width=use_container_width)
        return True
    except Exception:
        return False


def render_fallback_back():
    st.markdown(
        "<div style='height:260px;border-radius:18px;"
        "background:linear-gradient(135deg,#2b2350,#6b4fd6,#fbc2eb);"
        "display:flex;align-items:center;justify-content:center;"
        "color:white;font-weight:900;font-size:1.2rem;'>TAROT BACK</div>",
        unsafe_allow_html=True
    )


def list_tarot_images():
    base = Path("assets/tarot")
    majors = list((base / "majors").glob("*.png"))
    minors = []
    for suit in ["cups", "pentacles", "swords", "wands"]:
        minors.extend(list((base / "minors" / suit).glob("*.png")))
    all_imgs = sorted(majors + minors, key=lambda p: str(p).lower())
    return all_imgs


def parse_tarot_db(tarot_db):
    tarot_db = unwrap_db(tarot_db)
    cards = []
    if isinstance(tarot_db, dict):
        if isinstance(tarot_db.get("cards"), list):
            cards = tarot_db["cards"]
        else:
            for k, v in tarot_db.items():
                if isinstance(v, dict):
                    cards.append({"name": k, **v})
    elif isinstance(tarot_db, list):
        cards = tarot_db

    cleaned = []
    for c in cards:
        if not isinstance(c, dict):
            continue
        name = c.get("name") or c.get("title") or c.get("card")
        meaning = c.get("meaning") or c.get("desc") or c.get("text")
        image = c.get("image") or c.get("img") or ""
        if name and meaning:
            cleaned.append({
                "name": strip_html_like(str(name)),
                "meaning": strip_html_like(str(meaning)),
                "image": str(image).strip(),
            })
    return cleaned


def tarot_pick_for_today(tarot_cards: list[dict], name: str, birth: date, mbti: str):
    today = date.today()
    seed_int = stable_seed(str(today), (name or "").strip(), str(birth), (mbti or "").strip().upper(), "tarot")
    r = random.Random(seed_int)
    if not tarot_cards:
        return None
    return r.choice(tarot_cards)


def find_image_for_card(card_name: str, all_images: list[Path]) -> Path | None:
    if not card_name:
        return None
    key = re.sub(r"[^a-z0-9]+", "_", card_name.lower()).strip("_")
    tokens = [t for t in key.split("_") if len(t) >= 3]
    if not tokens:
        return None

    best = None
    best_score = 0
    for p in all_images:
        fn = p.name.lower()
        score = sum(1 for t in tokens if t in fn)
        if score > best_score:
            best_score = score
            best = p

    if best_score <= 0:
        return None
    return best


def tarot_ui(tarot_db, birth: date, name: str, mbti: str):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🃏 오늘의 타로카드 <span style='font-size:0.95rem; opacity:0.85'>(하루 1회 가능)</span>", unsafe_allow_html=True)
    st.markdown(
        "<div class='soft-box'>뒷면 카드를 보고, <b>뽑기</b>를 누르면 오늘의 카드가 공개됩니다."
        "<br>오늘 하루 동안은 <b>같은 카드(같은 의미/이미지)</b>로 고정됩니다.</div>",
        unsafe_allow_html=True
    )

    if "tarot_revealed" not in st.session_state:
        st.session_state.tarot_revealed = False
    if "tarot_shake" not in st.session_state:
        st.session_state.tarot_shake = False

    shake_class = "shake" if st.session_state.tarot_shake else ""
    st.markdown(f"<div class='tarot-stage {shake_class}'>", unsafe_allow_html=True)

    if not st.session_state.tarot_revealed:
        back_path = Path("assets/tarot/back.png")
        back_bytes = read_file_bytes(back_path) if back_path.exists() else None

        # ✅ LFS 포인터면 이미지로 처리하면 안 됨
        if back_bytes and is_git_lfs_pointer(back_bytes):
            back_bytes = None

        if back_bytes:
            ok = safe_st_image(back_bytes, use_container_width=True)
            if not ok:
                render_fallback_back()
        else:
            render_fallback_back()

    st.markdown("</div>", unsafe_allow_html=True)

    # ✅ "이미 뽑았어요" 멘트 금지: 눌러도 오늘카드를 그냥 공개(고정)
    if st.button("타로카드 뽑기", use_container_width=True):
        st.session_state.tarot_shake = True
        st.session_state.tarot_revealed = True
        st.rerun()

    if st.session_state.tarot_revealed:
        if st.session_state.tarot_shake:
            components.html(
                "<script>setTimeout(()=>{window.parent.postMessage({type:'streamlit:rerun'}, '*');}, 350);</script>",
                height=0
            )
            st.session_state.tarot_shake = False

        tarot_cards = parse_tarot_db(tarot_db)
        picked = tarot_pick_for_today(tarot_cards, name, birth, mbti)

        if not picked:
            st.info("타로 DB에서 카드를 불러오지 못했습니다. (tarot_db_ko.json 확인)")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        all_images = list_tarot_images()

        img_path = None
        img_hint = (picked.get("image") or "").strip()
        if img_hint:
            p = Path(img_hint)
            if p.exists():
                img_path = p
            else:
                p2 = Path("assets/tarot") / img_hint
                if p2.exists():
                    img_path = p2

        if img_path is None:
            img_path = find_image_for_card(picked.get("name", ""), all_images)

        # ✅ 카드 이미지도 LFS 포인터 방어 + 안전 출력
        if img_path and img_path.exists():
            b = read_file_bytes(img_path)
            if b and is_git_lfs_pointer(b):
                b = None
            if b:
                ok = safe_st_image(b, use_container_width=True)
                # 실패하면 이미지 없이 텍스트만 표시

        st.markdown(
            f"""
            <div class="reveal">
              <div class="reveal-title">✨ {strip_html_like(picked.get('name',''))}</div>
              <div class="reveal-meaning">{strip_html_like(picked.get('meaning',''))}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 5) 광고
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
            <a class="ad-btn" href="{DANANEUM_LANDING_URL}" target="_blank" rel="noopener noreferrer">무료 상담하기</a>
          </div>
          <div class="ad-sub">이름/전화번호 작성 · 개인정보처리방침 동의 후 신청완료</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 6) UI 스타일
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
.tarot-stage.shake { animation: shake 0.32s ease-in-out 1; }
@keyframes shake {
  0% { transform: translateX(0px) rotate(0deg); }
  20% { transform: translateX(-6px) rotate(-1deg); }
  40% { transform: translateX(6px) rotate(1deg); }
  60% { transform: translateX(-5px) rotate(-0.8deg); }
  80% { transform: translateX(5px) rotate(0.8deg); }
  100% { transform: translateX(0px) rotate(0deg); }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 7) 공유
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
# 8) DB 로드
# =========================================================
def load_all_dbs():
    fortunes_year, path_year = _load_json_by_candidates(["data/fortunes_ko_2026.json", "data/fortunes_ko_2026"])
    fortunes_today, path_today = _load_json_by_candidates(["data/fortunes_ko_today.json", "data/fortunes_ko_today"])
    fortunes_tomorrow, path_tomorrow = _load_json_by_candidates(["data/fortunes_ko_tomorrow.json", "data/fortunes_ko_tomorrow"])
    lunar_lny, path_lny = _load_json_by_candidates(["data/lunar_new_year_1920_2026.json", "data/lunar_new_year_1920_2026"])
    zodiac_db, path_zodiac = _load_json_by_candidates(["data/zodiac_fortunes_ko_2026.json", "data/zodiac_fortunes_ko_2026"])
    mbti_db, path_mbti = _load_json_by_candidates(["data/mbti_traits_ko.json", "data/mbti_traits_ko"])
    saju_db, path_saju = _load_json_by_candidates(["data/saju_ko.json", "data/saju_ko"])
    tarot_db, path_tarot = _load_json_by_candidates(["data/tarot_db_ko.json", "data/tarot_db_ko", "tarot_db_ko.json"])

    # ✅ 핵심: 구조 언랩/정규화
    zodiac_db = normalize_zodiac_db(zodiac_db)
    mbti_db = normalize_mbti_db(mbti_db)
    saju_db = unwrap_db(saju_db)

    return {
        "fortunes_year": unwrap_db(fortunes_year),
        "fortunes_today": unwrap_db(fortunes_today),
        "fortunes_tomorrow": unwrap_db(fortunes_tomorrow),
        "lunar_lny": unwrap_db(lunar_lny),
        "zodiac_db": zodiac_db,
        "mbti_db": mbti_db,
        "saju_db": saju_db,
        "tarot_db": unwrap_db(tarot_db),
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
# 9) 입력/결과 화면
# =========================================================
MBTI_TYPES = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]


def get_pool_from_fortune_db(fdb, key_name):
    fdb = unwrap_db(fdb)
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


def render_input(dbs):
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로</p>
      <p class="hero-sub">이름 + 생년월일 + MBTI로 결과가 고정 출력됩니다</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름", value=st.session_state.get("name", ""), placeholder="예) 김성흥")
    st.session_state.birth = st.date_input(
        "생년월일",
        value=st.session_state.get("birth", date(2005, 1, 1)),
        min_value=date(1920, 1, 1),
        max_value=date(2026, 12, 31),
    )

    mbti = st.selectbox("MBTI", MBTI_TYPES, index=MBTI_TYPES.index(st.session_state.get("mbti", "ENFP")) if st.session_state.get("mbti", "ENFP") in MBTI_TYPES else 0)
    st.session_state.mbti = mbti

    lny_map = parse_lny_map(dbs["lunar_lny"])
    zk, zy = zodiac_by_birth(st.session_state.birth, lny_map)
    st.markdown(f"<div class='card'><div class='soft-box'>당신의 띠: <b>{ZODIAC_LABEL_KO.get(zk, zk)}</b> (설 기준 띠년도 {zy})</div></div>", unsafe_allow_html=True)

    if st.button("운세 보기", use_container_width=True):
        st.session_state.stage = "result"
        st.rerun()


def render_result(dbs):
    name = (st.session_state.get("name") or "").strip()
    birth = st.session_state.get("birth", date(2005, 1, 1))
    mbti = (st.session_state.get("mbti", "ENFP") or "ENFP").strip().upper()

    lny_map = parse_lny_map(dbs["lunar_lny"])
    zodiac_key, zodiac_year = zodiac_by_birth(birth, lny_map)
    zodiac_label = ZODIAC_LABEL_KO.get(zodiac_key, zodiac_key)

    base_seed = stable_seed(str(birth), name, mbti)

    # ✅ 띠 운세
    zodiac_text = None
    zdb = dbs["zodiac_db"]
    if isinstance(zdb, dict):
        zval = zdb.get(zodiac_key)
        if isinstance(zval, list):
            pool = [strip_html_like(safe_str(x)) for x in zval if safe_str(x).strip()]
            zodiac_text = pick_one(pool, stable_seed(str(base_seed), "zodiac"))
        elif isinstance(zval, dict):
            # {items:[...]} 같은 구조도 방어
            items = zval.get("items") or zval.get("lines") or zval.get("pools") or None
            if isinstance(items, list):
                pool = [strip_html_like(safe_str(x)) for x in items if safe_str(x).strip()]
                zodiac_text = pick_one(pool, stable_seed(str(base_seed), "zodiac"))

    zodiac_text = normalize_zodiac_text(zodiac_text or "")
    zodiac_text = ensure_text(zodiac_text, "띠 운세")

    # ✅ MBTI 특징
    mbti_trait_val = dbs["mbti_db"].get(mbti, None) if isinstance(dbs["mbti_db"], dict) else None
    mbti_trait = format_mbti_trait(mbti_trait_val)
    mbti_trait = ensure_text(mbti_trait, "MBTI 특징")

    # ✅ 사주 한 마디: saju_db 구조가 복잡해도 “문장 pool”만 뽑기
    saju_text = None
    sdb = dbs["saju_db"]
    pool = []
    if isinstance(sdb, dict):
        # pools 안의 문장들을 최대한 모으기
        if isinstance(sdb.get("pools"), dict):
            for _, v in sdb["pools"].items():
                if isinstance(v, list):
                    pool.extend(v)
        # 혹시 최상위가 "pools" 아닌 경우
        for _, v in sdb.items():
            if isinstance(v, list):
                pool.extend(v)
            elif isinstance(v, dict) and isinstance(v.get("pools"), dict):
                for _, vv in v["pools"].items():
                    if isinstance(vv, list):
                        pool.extend(vv)
    elif isinstance(sdb, list):
        pool = sdb

    pool = [strip_html_like(safe_str(x)) for x in pool if safe_str(x).strip()]
    saju_text = pick_one(pool, stable_seed(str(base_seed), "saju"))
    saju_text = ensure_text(saju_text, "사주 한 마디")

    # ✅ 오늘/내일/2026
    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_pool = get_pool_from_fortune_db(dbs["fortunes_today"], "today")
    tomorrow_pool = get_pool_from_fortune_db(dbs["fortunes_tomorrow"], "tomorrow")
    year_pool = get_pool_from_fortune_db(dbs["fortunes_year"], "year_all")

    today_text = ensure_text(pick_one(today_pool, stable_seed(str(base_seed), str(today), "today")), "오늘 운세")
    tomorrow_text = ensure_text(pick_one(tomorrow_pool, stable_seed(str(base_seed), str(tomorrow), "tomorrow")), "내일 운세")
    year_text = ensure_text(pick_one(year_pool, stable_seed(str(base_seed), "year_2026")), "2026 전체 운세")

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
    tarot_ui(dbs["tarot_db"], birth, name, mbti)

    if st.button("입력 화면으로", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

    with st.expander("DB 연결 상태(확인용)"):
        st.write(dbs["paths"])
        # 디버깅용: 실제 구조 확인
        st.write({"zodiac_db_type": str(type(dbs["zodiac_db"])), "mbti_db_type": str(type(dbs["mbti_db"]))})


# =========================================================
# 10) 실행
# =========================================================
if "stage" not in st.session_state:
    st.session_state.stage = "input"

try:
    dbs = load_all_dbs()
except Exception as e:
    st.error(str(e))
    st.stop()

if st.session_state.stage == "input":
    render_input(dbs)
else:
    render_result(dbs)
