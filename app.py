import streamlit as st
from datetime import datetime, timedelta, date
import random

# =========================
# 1) 데이터 (KO 중심 / 화면 PPT 스타일)
# =========================

# 띠/MBTI 이모지 (PPT처럼 시각 강조)
ZODIAC_EMOJI_KO = {
    "쥐띠":"🐭","소띠":"🐮","호랑이띠":"🐯","토끼띠":"🐰","용띠":"🐲","뱀띠":"🐍",
    "말띠":"🐴","양띠":"🐑","원숭이띠":"🐵","닭띠":"🐔","개띠":"🐶","돼지띠":"🐷"
}
MBTI_EMOJI = {
    "INTJ":"♟️","INTP":"🧩","ENTJ":"👑","ENTP":"🧨",
    "INFJ":"🔮","INFP":"🎨","ENFJ":"🤝","ENFP":"✨",
    "ISTJ":"📏","ISFJ":"🫶","ESTJ":"🧱","ESFJ":"🎉",
    "ISTP":"🔧","ISFP":"🌿","ESTP":"🏎️","ESFP":"🎭"
}

ZODIAC_LIST_KO = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]

ZODIACS_KO = {
    "쥐띠": "안정 속 새로운 기회! 민첩한 판단으로 성공 잡아요",
    "소띠": "꾸준함의 결실! 안정된 성장과 행복한 가족운",
    "호랑이띠": "대박 띠! 도전과 성공, 리더십 발휘로 큰 성과",
    "토끼띠": "삼재 주의! 신중함으로 변화 대처, 안정 추구",
    "용띠": "운기 상승! 리더십과 승진 기회 많음",
    "뱀띠": "직감과 실속! 예상치 못한 재물운",
    "말띠": "본띠 해! 추진력 강하지만 균형이 핵심",
    "양띠": "대박 띠! 편안함과 최고 돈운, 가정 행복",
    "원숭이띠": "변화와 재능 발휘! 창의력으로 성공",
    "닭띠": "노력 결실! 인정과 승진 가능성 높음",
    "개띠": "대박 띠! 귀인 도움과 네트워킹으로 상승",
    "돼지띠": "여유와 재물 대박! 즐기는 최고의 해"
}

MBTIS_KO = {
    "INTJ": "냉철 전략가", "INTP": "아이디어 천재", "ENTJ": "보스", "ENTP": "토론왕",
    "INFJ": "마음 마스터", "INFP": "감성 예술가", "ENFJ": "모두 선생님", "ENFP": "인간 비타민",
    "ISTJ": "규칙 지킴이", "ISFJ": "세상 따뜻함", "ESTJ": "리더", "ESFJ": "분위기 메이커",
    "ISTP": "고치는 장인", "ISFP": "감성 힐러", "ESTP": "모험왕", "ESFP": "파티 주인공"
}

SAJU_MSGS_KO = [
    "목(木) 기운 강함 → 성장과 발전의 해!",
    "화(火) 기운 강함 → 열정 폭발!",
    "토(土) 기운 강함 → 안정과 재물운",
    "금(金) 기운 강함 → 결단력 좋음!",
    "수(水) 기운 강함 → 지혜와 흐름",
    "오행 균형 → 행복한 한 해",
    "양기 강함 → 도전 성공",
    "음기 강함 → 내면 성찰"
]

DAILY_MSGS_KO = [
    "재물운 좋음! 작은 투자도 이득 봐요",
    "연애운 최고! 고백하거나 데이트 좋음",
    "건강 주의! 과로 피하고 쉬세요",
    "전체운 대박! 좋은 일만 생길 거예요",
    "인간관계 운 좋음! 귀인 만남 가능",
    "학업/일 운 최고! 집중력 최고",
    "여행운 좋음! 갑자기 떠나도 괜찮아요",
    "기분 좋은 하루! 웃음이 가득할 거예요"
]

OVERALL_FORTUNES_KO = [
    "성장과 재물이 함께하는 최고의 해! 대박 기운 가득",
    "안정과 행복이 넘치는 한 해! 가족과 함께하는 기쁨",
    "도전과 성공의 해! 큰 성과를 이룰 거예요",
    "사랑과 인연이 피어나는 로맨틱한 해",
    "변화와 새로운 시작! 창의력이 빛나는 한 해"
]

COMBO_COMMENTS_KO = [
    "{}의 노력과 {}의 따뜻함으로 모두를 이끄는 리더가 될 거예요!",
    "{}의 리더십과 {}의 창의력이 완벽한 시너지!",
    "{}의 직감과 {}의 논리로 무적 조합!",
    "{}의 안정감과 {}의 열정으로 대박 성공!",
    "{}의 유연함과 {}의 결단력으로 모든 일 해결!"
]

LUCKY_COLORS_KO = ["골드", "레드", "블루", "그린", "퍼플"]
LUCKY_ITEMS_KO = ["황금 액세서리", "빨간 지갑", "파란 목걸이", "초록 식물", "보라색 펜"]
TIPS_KO = [
    "새로운 사람 만나는 기회 많아요. 적극적으로!",
    "작은 투자에 집중하세요. 이득 볼 가능성 높음",
    "건강 관리에 신경 쓰세요. 규칙적인 운동 추천",
    "가족/친구와 시간 보내세요. 행복 충전!",
    "창의적인 취미를 시작해보세요. 재능 발휘될 거예요"
]

TAROT_CARDS = {
    "The Fool": "바보 - 새로운 시작, 모험, 순수한 믿음",
    "The Magician": "마법사 - 창조력, 능력 발휘, 집중",
    "The High Priestess": "여사제 - 직감, 신비, 내면의 목소리",
    "The Empress": "여제 - 풍요, 어머니의 사랑, 창작",
    "The Emperor": "황제 - 안정, 권위, 구조",
    "The Hierophant": "교황 - 전통, 스승, 지도",
    "The Lovers": "연인 - 사랑, 조화, 선택",
    "The Chariot": "전차 - 승리, 의지력, 방향",
    "Strength": "힘 - 용기, 인내, 부드러운 통제",
    "The Hermit": "은둔자 - 내면 탐구, 지혜, 고독",
    "Wheel of Fortune": "운명의 수레바퀴 - 변화, 운, 사이클",
    "Justice": "정의 - 공정, 균형, 진실",
    "The Hanged Man": "매달린 사람 - 희생, 새로운 관점, 기다림",
    "Death": "죽음 - 변화, 끝과 시작, 재생",
    "Temperance": "절제 - 균형, 조화, 인내",
    "The Devil": "악마 - 속박, 유혹, 물질주의",
    "The Tower": "탑 - 갑작스러운 변화, 파괴와 재건",
    "The Star": "별 - 희망, 영감, 치유",
    "The Moon": "달 - 불안, 환상, 직감",
    "The Sun": "태양 - 행복, 성공, 긍정 에너지",
    "Judgement": "심판 - 부활, 깨달음, 용서",
    "The World": "세계 - 완성, 성취, 전체성"
}

# 배포 후 본인 앱 URL로 바꾸기
APP_URL = "https://my-fortune.streamlit.app"
AD_URL = "https://www.다나눔렌탈.com"


# =========================
# 2) 유틸 (결과 고정: seed 설계)
# =========================
def get_zodiac_ko(year: int):
    if not (1900 <= year <= 2030):
        return None
    return ZODIAC_LIST_KO[(year - 4) % 12]

def get_saju_msg(year: int, month: int, day: int):
    total = year + month + day
    return SAJU_MSGS_KO[total % 8]

def daily_fortune(zodiac: str, offset_days: int):
    """오늘/내일 운세: 날짜+띠로 고정 (전역 random 오염 X)"""
    d = datetime.now() + timedelta(days=offset_days)
    seed = int(d.strftime("%Y%m%d")) + ZODIAC_LIST_KO.index(zodiac)
    rng = random.Random(seed)
    return rng.choice(DAILY_MSGS_KO)

def stable_result_rng(name: str, y: int, m: int, d: int, mbti: str):
    """연간/럭키/팁/조합: 사용자 입력으로 고정"""
    user_key = f"ko|{name}|{y:04d}-{m:02d}-{d:02d}|{mbti}"
    seed = abs(hash(user_key)) % (10**9)
    return random.Random(seed)


# =========================
# 3) Streamlit 설정/세션
# =========================
st.set_page_config(page_title="2026년 운세", layout="centered")

if "result_shown" not in st.session_state:
    st.session_state.result_shown = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "birthdate" not in st.session_state:
    st.session_state.birthdate = date(2005, 1, 1)
if "mbti" not in st.session_state:
    st.session_state.mbti = "ENFJ"
if "show_share" not in st.session_state:
    st.session_state.show_share = False


# =========================
# 4) PPT 스타일 CSS (최대한 유사)
# =========================
st.markdown("""
<style>
/* 전체 배경 */
.stApp {
  background: #efe9ff;
}

/* 상단 여백 줄이기 */
.block-container { padding-top: 20px; padding-bottom: 40px; max-width: 720px; }

/* 상단 타이틀 */
.ppt-title {
  font-size: 28px;
  font-weight: 800;
  color: #2b2b2b;
  text-align: center;
  margin: 6px 0 10px;
}
.ppt-subtitle {
  font-size: 20px;
  font-weight: 800;
  color: #2b2b2b;
  text-align: center;
  margin: 2px 0 6px;
}
.ppt-combo {
  font-size: 16px;
  font-weight: 700;
  color: #2b2b2b;
  text-align: center;
  margin: 6px 0 14px;
}

/* 메인 카드 */
.card {
  background: rgba(255,255,255,0.75);
  border: 1px solid rgba(140, 120, 200, 0.25);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 10px 22px rgba(0,0,0,0.08);
  margin: 10px 0 16px;
  text-align: left;
}
.card p { margin: 6px 0; line-height: 1.65; font-size: 14.5px; color:#2b2b2b; }
.kv { font-weight: 800; }
.hr { height: 1px; background: rgba(120,100,180,0.18); margin: 12px 0; }

/* 광고 카드 */
.ad {
  background: rgba(255,255,255,0.65);
  border: 1px solid rgba(140, 120, 200, 0.22);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 10px 22px rgba(0,0,0,0.06);
  margin: 10px 0 18px;
}
.ad-title { font-weight: 900; font-size: 15px; }
.ad-link {
  display: inline-block;
  margin-top: 10px;
  padding: 7px 12px;
  border-radius: 10px;
  border: 1px solid rgba(80,80,180,0.25);
  background: rgba(255,255,255,0.7);
  font-weight: 800;
  color: #2b5bd7;
  text-decoration: none;
}

/* 타로 카드 박스 (expander 안) */
.tarot-wrap {
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(140, 120, 200, 0.18);
  border-radius: 16px;
  padding: 14px 16px;
}
.tarot-title { font-weight: 900; color: #7c3aed; margin-bottom: 6px; }
.tarot-cardname { font-weight: 900; font-size: 22px; margin: 0 0 6px; color:#2b2b2b; }
.tarot-meaning { margin: 0; color:#2b2b2b; }

/* 공유 버튼 (보라색 pill) */
div.stButton > button.ppt-share {
  background: #7c3aed !important;
  color: white !important;
  border: none !important;
  border-radius: 999px !important;
  padding: 14px 18px !important;
  font-size: 16px !important;
  font-weight: 900 !important;
  width: 100% !important;
  box-shadow: 0 10px 26px rgba(124, 58, 237, 0.35) !important;
}
div.stButton > button.ppt-share:hover {
  filter: brightness(1.03);
}

/* 다시하기 버튼: 텍스트 크게 */
div.stButton > button.ppt-reset {
  background: transparent !important;
  border: none !important;
  color: #111 !important;
  font-size: 22px !important;
  font-weight: 900 !important;
  padding: 10px 0 !important;
  width: 100% !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# 5) 입력 화면
# =========================
if not st.session_state.result_shown:
    st.markdown("<div class='ppt-title'>⭐ 2026년 운세 ⭐</div>", unsafe_allow_html=True)

    st.session_state.name = st.text_input("이름 입력 (결과에 표시돼요)", value=st.session_state.name)

    st.session_state.birthdate = st.date_input(
        "생년월일 입력",
        value=st.session_state.birthdate,
        min_value=date(1900, 1, 1),
        max_value=date(2030, 12, 31),
    )

    st.session_state.mbti = st.selectbox("MBTI", sorted(MBTIS_KO.keys()), index=sorted(MBTIS_KO.keys()).index(st.session_state.mbti) if st.session_state.mbti in MBTIS_KO else 0)

    # PPT는 바로 결과화면이 나오게 보이는 구조라 버튼 1개만 둠
    if st.button("2026년 운세 보기!", use_container_width=True):
        st.session_state.result_shown = True
        st.session_state.show_share = False
        st.rerun()


# =========================
# 6) 결과 화면 (PPT 순서 최대한 동일)
# =========================
if st.session_state.result_shown:
    y = st.session_state.birthdate.year
    m = st.session_state.birthdate.month
    d = st.session_state.birthdate.day
    name = st.session_state.name.strip()
    mbti = st.session_state.mbti

    zodiac = get_zodiac_ko(y)
    if zodiac is None:
        st.error("생년은 1900~2030년 사이로 입력해주세요!")
        st.session_state.result_shown = False
        st.stop()

    zodiac_emoji = ZODIAC_EMOJI_KO.get(zodiac, "")
    mbti_emoji = MBTI_EMOJI.get(mbti, "")

    # 설명/문구
    zodiac_desc = ZODIACS_KO[zodiac]
    mbti_desc = MBTIS_KO[mbti]
    saju = get_saju_msg(y, m, d)

    today_msg = daily_fortune(zodiac, 0)
    tomorrow_msg = daily_fortune(zodiac, 1)

    rng = stable_result_rng(name, y, m, d, mbti)
    overall = rng.choice(OVERALL_FORTUNES_KO)
    combo_comment = rng.choice(COMBO_COMMENTS_KO).format(zodiac, mbti_desc)
    lucky_color = rng.choice(LUCKY_COLORS_KO)
    lucky_item = rng.choice(LUCKY_ITEMS_KO)
    tip = rng.choice(TIPS_KO)

    # PPT 상단
    st.markdown("<div class='ppt-title'>⭐ 2026년 운세 ⭐</div>", unsafe_allow_html=True)

    # 이름 표기: "닭띠 + ENFJ" 형태에 가깝게
    who = f"{name} · " if name else ""
    st.markdown(
        f"<div class='ppt-subtitle'>🔮 {who}{zodiac_emoji} {zodiac}  {mbti_emoji} {mbti}</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='ppt-combo'>최고 조합!</div>", unsafe_allow_html=True)

    # 메인 카드 (PPT 내용 순서)
    st.markdown(
        f"""
        <div class="card">
          <p>✨ <span class="kv">띠 운세</span>: {zodiac_desc}</p>
          <p>🧠 <span class="kv">MBTI 특징</span>: {mbti_desc}</p>
          <p>🍀 <span class="kv">사주 한 마디</span>: {saju}</p>
          <div class="hr"></div>
          <p>💗 <span class="kv">오늘 운세</span>: {today_msg}</p>
          <p>🌙 <span class="kv">내일 운세</span>: {tomorrow_msg}</p>
          <div class="hr"></div>
          <p>💝 <span class="kv">2026 전체 운세</span>: {overall}</p>
          <p>💬 <span class="kv">조합 한 마디</span>: {combo_comment}</p>
          <p>🎨 <span class="kv">럭키 컬러</span>: {lucky_color} &nbsp;&nbsp; 🧿 <span class="kv">럭키 아이템</span>: {lucky_item}</p>
          <p>✅ <span class="kv">팁</span>: {tip}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 광고 블록 (PPT의 "정수기 렌탈 대박!" 느낌)
    st.markdown(
        f"""
        <div class="ad">
          <div class="ad-title">🔥 정수기 렌탈 대박!</div>
          <div style="margin-top:6px; color:#2b2b2b; font-size:14px; line-height:1.6;">
            제휴카드면 월 0원부터!<br/>
            설치 당일 최대 50만원 지원 + 사은품 듬뿍 ✨
          </div>
          <a class="ad-link" href="{AD_URL}" target="_blank">🔗 다나눔렌탈.com 바로가기</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 타로 (PPT처럼 expander)
    with st.expander("오늘의 타로 카드 보기", expanded=False):
        tarot_rng = random.Random(abs(hash(f"tarot|{datetime.now().strftime('%Y%m%d')}|{name}|{mbti}")) % (10**9))
        tarot_card = tarot_rng.choice(list(TAROT_CARDS.keys()))
        tarot_meaning = TAROT_CARDS[tarot_card]

        st.markdown(
            f"""
            <div class="tarot-wrap">
              <div class="tarot-title">오늘의 타로 카드</div>
              <div class="tarot-cardname">{tarot_card}</div>
              <p class="tarot-meaning">🪄 {tarot_meaning}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 공유 텍스트 (안 깨지게 안정형)
    share_text = f"""⭐ 2026년 운세 ⭐

🔮 {who}{zodiac_emoji} {zodiac}  {mbti_emoji} {mbti}
최고 조합!

💗 오늘 운세: {today_msg}
🌙 내일 운세: {tomorrow_msg}

💝 2026 전체 운세: {overall}
💬 조합 한 마디: {combo_comment}
🎨 럭키 컬러: {lucky_color} | 🧿 럭키 아이템: {lucky_item}
✅ 팁: {tip}

나도 운세 보러 가기: {APP_URL}
"""

    # 공유 버튼(보라 pill) + 눌렀을 때 공유 텍스트 표시
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.markdown("<style>div.stButton>button{}</style>", unsafe_allow_html=True)

    # 버튼에 클래스 적용 (Streamlit 기본 버튼에 클래스 붙이기 위해 꼼수: key 기반 CSS 타겟은 불가 → 전체 버튼 스타일 대신 label별 2개만 쓴다고 가정)
    # 그래서 아래는 버튼 직전에 한번 더 CSS를 덮어씌워 '다음 버튼'을 share 스타일로 보이게 함.
    st.markdown("""
    <style>
    div.stButton > button { }
    </style>
    """, unsafe_allow_html=True)

    share_clicked = st.button("친구에게 결과 공유", use_container_width=True, key="share_btn")
    # share 버튼만 ppt-share처럼 보이게(간단 트릭: 버튼 생성 후 css로 첫 버튼 타겟이 어렵기 때문에 페이지 내 버튼이 2개뿐이게 구성)
    st.markdown("""
    <script>
    </script>
    """, unsafe_allow_html=True)

    # 현실적으로 Streamlit은 버튼별 클래스 지정이 어려워서,
    # 페이지에 버튼이 많아지면 스타일이 함께 먹을 수 있음.
    # 여기선 결과화면에서 버튼을 2개만 유지해 최대한 PPT처럼 고정.
    st.markdown("""
    <style>
    /* 결과 화면의 첫 번째 버튼(공유)을 pill로 보이게 */
    div.stButton:nth-of-type(1) > button {
      background: #7c3aed !important;
      color: white !important;
      border: none !important;
      border-radius: 999px !important;
      padding: 14px 18px !important;
      font-size: 16px !important;
      font-weight: 900 !important;
      width: 100% !important;
      box-shadow: 0 10px 26px rgba(124, 58, 237, 0.35) !important;
    }
    /* 결과 화면의 두 번째 버튼(리셋)을 큰 텍스트로 */
    div.stButton:nth-of-type(2) > button {
      background: transparent !important;
      border: none !important;
      color: #111 !important;
      font-size: 22px !important;
      font-weight: 900 !important;
      padding: 10px 0 !important;
      width: 100% !important;
      box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if share_clicked:
        st.session_state.show_share = True
        st.toast("공유용 텍스트를 아래에서 복사해서 카톡/메시지에 붙여넣기 해주세요 🙂")

    if st.session_state.show_share:
        st.text_area("공유 텍스트(복사해서 보내기)", value=share_text, height=220)
        st.caption("전체 선택(Ctrl+A) → 복사(Ctrl+C) → 카톡/문자에 붙여넣기")

    # URL 표시 (PPT처럼 카드 아래에 노출되는 느낌)
    st.markdown(f"<div style='text-align:center; color:#6b6b6b; font-size:12px; margin-top:10px;'>{APP_URL}</div>", unsafe_allow_html=True)

    # 다시하기(아래 큰 텍스트)
    reset_clicked = st.button("처음부터 다시하기", use_container_width=True, key="reset_btn")
    if reset_clicked:
        st.session_state.result_shown = False
        st.session_state.show_share = False
        st.rerun()
