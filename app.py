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

# =========================================================
# 1) 경로/DB 로더
# =========================================================
DATA_DIR = Path("data")


def _load_json_by_candidates(candidates):
    """
    candidates: ["data/a.json", "data/b.json", ...]
    존재하는 첫 파일을 로드해서 반환.
    """
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


# =========================================================
# 2) 띠(설 기준) 계산
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

# 한글 띠 키가 DB에 들어있을 경우 대비(방어)
ZODIAC_KO_TO_KEY = {
    "쥐": "rat",
    "쥐띠": "rat",
    "소": "ox",
    "소띠": "ox",
    "호랑이": "tiger",
    "호랑이띠": "tiger",
    "범": "tiger",
    "토끼": "rabbit",
    "토끼띠": "rabbit",
    "용": "dragon",
    "용띠": "dragon",
    "뱀": "snake",
    "뱀띠": "snake",
    "말": "horse",
    "말띠": "horse",
    "양": "goat",
    "양띠": "goat",
    "원숭이": "monkey",
    "원숭이띠": "monkey",
    "닭": "rooster",
    "닭띠": "rooster",
    "개": "dog",
    "개띠": "dog",
    "돼지": "pig",
    "돼지띠": "pig",
}


def parse_lny_map(lny_json):
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
    """
    DB 문구에 rooster띠 같은 영문키가 섞여 있으면 한글 띠로 교정
    """
    if not text:
        return text
    out = text
    for k in ZODIAC_ORDER:
        out = out.replace(f"{k}띠", ZODIAC_LABEL_KO.get(k, f"{k}띠"))
        out = out.replace(f"{k} 띠", ZODIAC_LABEL_KO.get(k, f"{k} 띠"))
    return out


# =========================================================
# 3) MBTI
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


def compute_mbti_from_answers(answers):
    scores = {"EI":0,"SN":0,"TF":0,"JP":0}
    counts = {"EI":0,"SN":0,"TF":0,"JP":0}
    for axis, pick_left in answers:
        if axis in scores:
            counts[axis] += 1
            if pick_left:
                scores[axis] += 1

    def decide(axis, left_char, right_char):
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


def normalize_mbti_db(mbti_db):
    """
    mbti_traits_ko.json이 키에 공백/소문자 등이 섞여도 항상 매칭되게 정규화
    """
    if not isinstance(mbti_db, dict):
        return mbti_db
    out = {}
    for k, v in mbti_db.items():
        kk = str(k).strip().upper()
        out[kk] = v
    return out


def format_mbti_trait(val) -> str:
    """
    MBTI DB 값이 dict/list/string 어느 형태든 보기 좋게 출력
    """
    if val is None:
        return ""
    if isinstance(val, str):
        return strip_html_like(val)
    if isinstance(val, list):
        items = [strip_html_like(safe_str(x)) for x in val if safe_str(x).strip()]
        return " / ".join(items)
    if isinstance(val, dict):
        # 예: {"keywords":[...], "tips":[...]} 형태를 예쁘게
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
# 4) 공유 버튼
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
# 5) 타로 (하루 고정 + 흔들림 + 이미지)
# =========================================================
def list_tarot_images():
    """
    repo 구조:
      assets/tarot/back.png
      assets/tarot/majors/*.png
      assets/tarot/minors/{cups,pentacles,swords,wands}/*.png
    """
    base = Path("assets/tarot")
    majors = list((base / "majors").glob("*.png"))
    minors = []
    for suit in ["cups", "pentacles", "swords", "wands"]:
        minors.extend(list((base / "minors" / suit).glob("*.png")))
    # png만 우선(네 업로드 캡쳐도 png)
    all_imgs = majors + minors
    # 정렬(결정적)
    all_imgs = sorted(all_imgs, key=lambda p: str(p).lower())
    return all_imgs


def parse_tarot_db(tarot_db):
    """
    tarot_db_ko.json 다양한 형태 방어
    - {"cards":[{...}]}
    - [{...}]
    - {"The Sun": {...}}
    """
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


def find_image_for_card(card_name: str, all_images: list[Path]) -> Path | None:
    """
    파일명 규칙(예시):
      majors: 00_the_fool.png, 19_the_sun.png ...
      minors: cups_01_ace.png ...
    -> 카드명에 맞는 정확 매칭이 어렵기 때문에:
       1) tarot_db에 image가 있으면 그걸 우선
       2) 없으면 카드명 일부를 파일명에 포함하는 후보를 찾음(약하게)
       3) 그래도 없으면 None
    """
    if not card_name:
        return None
    key = re.sub(r"[^a-z0-9]+", "_", card_name.lower()).strip("_")

    # 약한 매칭: key의 일부 토큰이 파일명에 포함되는지
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

    # 너무 약한 매칭이면 버림
    if best_score <= 0:
        return None
    return best


def tarot_pick_for_today(tarot_cards: list[dict], name: str, birth: date, mbti: str):
    """
    하루 동안 같은 카드(의미/이미지) 고정:
    시드 = 오늘날짜 + 이름 + 생일 + MBTI
    """
    today = date.today()
    seed_int = stable_seed(str(today), (name or "").strip(), str(birth), (mbti or "").strip().upper(), "tarot")
    r = random.Random(seed_int)
    if not tarot_cards:
        return None
    return r.choice(tarot_cards)


def read_image_bytes(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except Exception:
        return None


def tarot_ui(tarot_db, birth: date, name: str, mbti: str):
    st.markdown("<div class='card tarot-card'>", unsafe_allow_html=True)
    st.markdown("### 🃏 오늘의 타로카드 <span style='font-size:0.95rem; opacity:0.85'>(하루 1회 가능)</span>", unsafe_allow_html=True)
    st.markdown(
        "<div class='soft-box'>뒷면 카드를 보고, <b>뽑기</b>를 누르면 오늘의 카드가 공개됩니다."
        "<br>오늘 하루 동안은 <b>같은 카드(같은 의미/이미지)</b>로 고정됩니다.</div>",
        unsafe_allow_html=True
    )

    # 세션 상태
    if "tarot_revealed" not in st.session_state:
        st.session_state.tarot_revealed = False
    if "tarot_shake" not in st.session_state:
        st.session_state.tarot_shake = False

    # back.png는 bytes로 읽어서 안정적으로 표시
    back_path = Path("assets/tarot/back.png")
    back_bytes = read_image_bytes(back_path) if back_path.exists() else None

    # 표시 영역(흔들림용 래퍼)
    shake_class = "shake" if st.session_state.tarot_shake else ""
    st.markdown(f"<div class='tarot-stage {shake_class}'>", unsafe_allow_html=True)

    if not st.session_state.tarot_revealed:
        if back_bytes:
            st.image(back_bytes, use_container_width=True)
        else:
            st.markdown(
                "<div style='height:260px;border-radius:18px;"
                "background:linear-gradient(135deg,#2b2350,#6b4fd6,#fbc2eb);"
                "display:flex;align-items:center;justify-content:center;"
                "color:white;font-weight:900;font-size:1.2rem;'>TAROT BACK</div>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)

    # 버튼: “이미 뽑음” 멘트 금지 → 눌러도 오늘카드(고정) 그냥 보여주기
    if st.button("타로카드 뽑기", use_container_width=True):
        st.session_state.tarot_shake = True
        st.session_state.tarot_revealed = True
        st.rerun()

    # 공개 상태
    if st.session_state.tarot_revealed:
        # 흔들림은 1회만 보이게 하고 바로 끔
        if st.session_state.tarot_shake:
            components.html("<script>setTimeout(()=>{window.parent.postMessage({type:'streamlit:rerun'}, '*');}, 350);</script>", height=0)
            st.session_state.tarot_shake = False

        tarot_cards = parse_tarot_db(tarot_db)
        picked = tarot_pick_for_today(tarot_cards, name, birth, mbti)

        if not picked:
            st.info("타로 DB에서 카드를 불러오지 못했습니다. (tarot_db_ko.json 확인)")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        # 이미지 결정 우선순위:
        # 1) tarot_db의 image 필드가 "assets/..." 상대경로면 그걸 사용
        # 2) 없으면 폴더 스캔해서 이름 기반 약한 매칭
        # 3) 그래도 없으면 이미지 없이 텍스트만
        all_images = list_tarot_images()

        img_path = None
        img_hint = (picked.get("image") or "").strip()
        if img_hint:
            p = Path(img_hint)
            if p.exists():
                img_path = p
            else:
                # 혹시 "majors/..." 같은 상대값만 있을 수 있어서 base 붙여보기
                p2 = Path("assets/tarot") / img_hint
                if p2.exists():
                    img_path = p2

        if img_path is None:
            img_path = find_image_for_card(picked.get("name", ""), all_images)

        # 이미지 출력(에러 방지: bytes로)
        if img_path and img_path.exists():
            b = read_image_bytes(img_path)
            if b:
                st.image(b, use_container_width=True)
            else:
                # bytes 읽기 실패하면 그냥 텍스트로 진행
                pass

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
# 6) 다나눔렌탈 광고
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
# 7) 스타일
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

/* 타로 흔들림 */
.tarot-stage.shake {
  animation: shake 0.32s ease-in-out 1;
}
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
# 8) DB 로드 + 정규화
# =========================================================
def load_all_dbs():
    fortunes_year, path_year = _load_json_by_candidates([
        "data/fortunes_ko_2026.json",
        "data/fortunes_ko_2026",
    ])

    fortunes_today, path_today = _load_json_by_candidates([
        "data/fortunes_ko_today.json",
        "data/fortunes_ko_today",
    ])
    fortunes_tomorrow, path_tomorrow = _load_json_by_candidates([
        "data/fortunes_ko_tomorrow.json",
        "data/fortunes_ko_tomorrow",
    ])

    lunar_lny, path_lny = _load_json_by_candidates([
        "data/lunar_new_year_1920_2026.json",
        "data/lunar_new_year_1920_2026",
    ])

    zodiac_db, path_zodiac = _load_json_by_candidates([
        "data/zodiac_fortunes_ko_2026.json",
        "data/zodiac_fortunes_ko_2026",
    ])

    mbti_db, path_mbti = _load_json_by_candidates([
        "data/mbti_traits_ko.json",
        "data/mbti_traits_ko",
    ])

    saju_db, path_saju = _load_json_by_candidates([
        "data/saju_ko.json",
        "data/saju_ko",
    ])

    tarot_db, path_tarot = _load_json_by_candidates([
        "data/tarot_db_ko.json",
        "data/tarot_db_ko",
        "tarot_db_ko.json",
    ])

    # ✅ 정규화(여기서 안정화)
    mbti_db = normalize_mbti_db(mbti_db)

    # zodiac db 키가 한글일 가능성 방어(한글키를 영문키로 복제)
    if isinstance(zodiac_db, dict):
        for ko, key in ZODIAC_KO_TO_KEY.items():
            if ko in zodiac_db and key not in zodiac_db:
                zodiac_db[key] = zodiac_db[ko]

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
# 10) 화면 렌더
# =========================================================
def render_input(dbs):
    st.markdown("""
    <div class="header-hero">
      <p class="hero-title">🔮 2026 운세 | 띠 + MBTI + 사주 + 오늘/내일 + 타로</p>
      <p class="hero-sub">이름 + 생년월일 + MBTI로 결과가 고정 출력됩니다</p>
      <span class="badge">2026</span>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름", value=st.session_state.name, placeholder="예) 홍길동")

    st.session_state.birth = st.date_input(
        "생년월일",
        value=st.session_state.birth,
        min_value=date(1920, 1, 1),
        max_value=date(2026, 12, 31),
    )

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
        st.session_state.mbti = st.selectbox(
            "MBTI 직접 선택",
            MBTI_TYPES,
            index=MBTI_TYPES.index(st.session_state.mbti) if st.session_state.mbti in MBTI_TYPES else 0
        )
        trait_val = dbs["mbti_db"].get(st.session_state.mbti, None) if isinstance(dbs["mbti_db"], dict) else None
        trait_txt = format_mbti_trait(trait_val)
        if trait_txt:
            st.markdown(f"<div class='soft-box'><b>{st.session_state.mbti}</b> · {trait_txt}</div>", unsafe_allow_html=True)

    else:
        st.markdown("<div class='soft-box'>각 문항에서 더 가까운 쪽을 선택하세요. 제출하면 MBTI가 확정됩니다.</div>", unsafe_allow_html=True)
        answers = []
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


def get_pool_from_fortune_db(fdb, key_name):
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


def ensure_text(val, label):
    if val and str(val).strip():
        return val
    return f"{label} 데이터를 DB에서 찾지 못했습니다. (data 폴더 JSON 확인)"


def render_result(dbs):
    name = (st.session_state.name or "").strip()
    birth = st.session_state.birth
    mbti = (st.session_state.mbti or "ENFP").strip().upper()

    # 띠
    lny_map = parse_lny_map(dbs["lunar_lny"])
    zodiac_key, zodiac_year = zodiac_by_birth(birth, lny_map)
    zodiac_label = ZODIAC_LABEL_KO.get(zodiac_key, zodiac_key)

    base_seed = stable_seed(str(birth), name, mbti)

    # 1) 띠 운세
    zodiac_pool = []
    zdb = dbs["zodiac_db"]
    if isinstance(zdb, dict):
        val = zdb.get(zodiac_key)
        if isinstance(val, list):
            zodiac_pool = val
        elif isinstance(val, dict):
            if isinstance(val.get("items"), list):
                zodiac_pool = val["items"]
            elif isinstance(val.get("lines"), list):
                zodiac_pool = val["lines"]

    zodiac_text = pick_one(
        [strip_html_like(safe_str(x)) for x in zodiac_pool if safe_str(x).strip()],
        stable_seed(str(base_seed), "zodiac")
    )
    zodiac_text = normalize_zodiac_text(zodiac_text or "")
    zodiac_text = ensure_text(zodiac_text, "띠 운세")

    # 2) MBTI 특징
    mbti_trait_val = dbs["mbti_db"].get(mbti, None) if isinstance(dbs["mbti_db"], dict) else None
    mbti_trait = format_mbti_trait(mbti_trait_val)
    mbti_trait = ensure_text(mbti_trait, "MBTI 특징")

    # 3) 사주 한마디
    saju_pool = []
    sdb = dbs["saju_db"]
    if isinstance(sdb, dict):
        if isinstance(sdb.get("pools"), dict) and isinstance(sdb["pools"].get("saju"), list):
            saju_pool = sdb["pools"]["saju"]
        elif isinstance(sdb.get("saju"), list):
            saju_pool = sdb["saju"]
        elif isinstance(sdb.get("lines"), list):
            saju_pool = sdb["lines"]
        else:
            # dict인데 구조가 다른 경우: 값들 중 문자열/리스트 끌어오기
            for _, v in sdb.items():
                if isinstance(v, list):
                    saju_pool.extend(v)
                elif isinstance(v, str):
                    saju_pool.append(v)
    elif isinstance(sdb, list):
        saju_pool = sdb

    saju_text = pick_one(
        [strip_html_like(safe_str(x)) for x in saju_pool if safe_str(x).strip()],
        stable_seed(str(base_seed), "saju")
    )
    saju_text = ensure_text(saju_text, "사주 한 마디")

    # 4) 오늘/내일
    today = date.today()
    tomorrow = today + timedelta(days=1)

    today_pool = get_pool_from_fortune_db(dbs["fortunes_today"], "today")
    tomorrow_pool = get_pool_from_fortune_db(dbs["fortunes_tomorrow"], "tomorrow")

    today_text = pick_one(today_pool, stable_seed(str(base_seed), str(today), "today"))
    tomorrow_text = pick_one(tomorrow_pool, stable_seed(str(base_seed), str(tomorrow), "tomorrow"))
    today_text = ensure_text(today_text, "오늘 운세")
    tomorrow_text = ensure_text(tomorrow_text, "내일 운세")

    # 5) 2026 전체 운세
    year_pool = []
    ydb = dbs["fortunes_year"]
    if isinstance(ydb, dict):
        if isinstance(ydb.get("pools"), dict) and isinstance(ydb["pools"].get("year_all"), list):
            year_pool = ydb["pools"]["year_all"]
        elif isinstance(ydb.get("year_all"), list):
            year_pool = ydb["year_all"]
        elif isinstance(ydb.get("lines"), list):
            year_pool = ydb["lines"]
    elif isinstance(ydb, list):
        year_pool = ydb

    year_text = pick_one(
        [strip_html_like(safe_str(x)) for x in year_pool if safe_str(x).strip()],
        stable_seed(str(base_seed), "year_2026")
    )
    year_text = ensure_text(year_text, "2026 전체 운세")

    # 헤더
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

    # 결과
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

    # 공유
    share_block()

    # 광고
    dananeum_ad_block()

    # 타로
    tarot_ui(dbs["tarot_db"], birth, name, mbti)

    # 입력으로
    if st.button("입력 화면으로", use_container_width=True):
        st.session_state.stage = "input"
        st.rerun()

    with st.expander("DB 연결 상태(확인용)"):
        st.write(dbs["paths"])


# =========================================================
# 11) 실행
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
