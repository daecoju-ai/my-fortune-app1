import streamlit as st

Z = {"쥐띠":"🐭 활발·성장, 돈↑","소띠":"🐮 노력 결실","호랑이띠":"🐯 도전 성공, 돈 대박","토끼띠":"🐰 안정·사랑 운","용띠":"🐲 운↑ 리더십","뱀띠":"🐍 실속·직감","말띠":"🐴 새 도전·돈 기회","양띠":"🐑 편안+결혼 운","원숭이띠":"🐵 변화·재능","닭띠":"🐔 노력 결과","개띠":"🐶 친구·돈↑","돼지띠":"🐷 여유·돈 최고"}

M = {"INTJ":"🧠 냉철 전략가","INTP":"💡 아이디어 천재","ENTJ":"👑 보스","ENTP":"⚡ 토론왕","INFJ":"🔮 마음 마스터","INFP":"🎨 감성 예술가","ENFJ":"🤗 모두 선생님","ENFP":"🎉 인간 비타민","ISTJ":"📋 규칙 지킴이","ISFJ":"🛡️ 세상 따뜻함","ESTJ":"📢 리더","ESFJ":"💕 분위기 메이커","ISTP":"🔧 고치는 장인","ISFP":"🌸 감성 힐러","ESTP":"🏄 모험왕","ESFP":"🎭 파티 주인공"}

def get_zodiac(y): 
    z = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
    return z[(y-4)%12] if 1900<=y<=2030 else None

# 간단 사주 오행 + 운세 (재미용!)
saju_msg = [
    "목(木) 기운 강함 → 성장과 발전의 해! 새로운 시작 좋음 🌱",
    "화(火) 기운 강함 → 열정 폭발! 연애·창의력 대박 ❤️",
    "토(土) 기운 강함 → 안정과 재물운 최고! 투자 조심히 💰",
    "금(金) 기운 강함 → 결단력 좋음! 커리어 승진운 👔",
    "수(水) 기운 강함 → 지혜와 흐름 타기 좋음! 변화에 유연하게 🌊",
    "오행 균형 → 모든 운세 안정적! 행복한 한 해 ✨",
    "양기 강함 → 적극적 행동이 행운 부름! 도전해봐 🚀",
    "음기 강함 → 내면 성찰의 해! 휴식과 회복 좋음 😌"
]

def get_saju(year, month, day):
    total = year + month + day
    index = total % 8
    return saju_msg[index]

st.set_page_config(page_title="띠MBTI 사주 운세", layout="centered")
st.title("🌟 2026 띠 + MBTI + 사주팔자 운세 🌟")
st.caption("완전 무료 😄")

app_url = "https://my-fortune.streamlit.app"

st.markdown("### 📱 QR 코드 스캔!")
st.image("frame.png", caption="폰으로 찍어보세요")

st.markdown("### 🔗 친구들한테 공유할 링크")
st.code(app_url, language=None)
st.write("위 링크 복사해서 보내주세요!")

st.markdown("""
<div style="background:#ffeb3b;padding:15px;border-radius:15px;text-align:center;margin:20px 0;">
  <h3>💳 렌탈 궁금할 때?</h3>
  <p><b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 페이백</b>!</p>
  <a href="https://www.다나눔렌탈.com" target="_blank">
    <button style="background:#ff5722;color:white;padding:10px 25px;border:none;border-radius:10px;">🔗 보러가기</button>
  </a>
</div>
""", unsafe_allow_html=True)

st.write("### 생년월일 입력 (사주 계산을 위해 정확히!)")
col1, col2, col3 = st.columns(3)
year = col1.number_input("년", 1900, 2030, 2005, step=1)
month = col2.number_input("월", 1, 12, 1, step=1)
day = col3.number_input("일", 1, 31, 1, step=1)

if "mbti" not in st.session_state: 
    st.session_state.mbti = None

if st.session_state.mbti is None:
    c = st.radio("MBTI 어떻게 할까?", ["직접 입력","상세 테스트 (16문제)"], key="mode")
    if c == "직접 입력":
        m = st.selectbox("너의 MBTI", sorted(M.keys()), key="direct")
        if st.button("운세 보기", key="direct_go"):
            st.session_state.mbti = m
            st.rerun()
    else:
        st.write("상세 테스트 시작! (총 16문제)")
        
        e_i, s_n, t_f, j_p = 0, 0, 0, 0
        
        st.subheader("에너지 방향")
        if st.radio("1. 사람 많을수록 좋아?", ["네 (E)", "아니 (I)"], key="ei1") == "네 (E)": e_i += 1
        if st.radio("2. 새로운 사람 만나는 거 좋아?", ["좋아 (E)", "부담 (I)"], key="ei2") == "좋아 (E)": e_i += 1
        if st.radio("3. 혼자 시간 필요해?", ["많이 (I)", "가끔 (E)"], key="ei3") == "많이 (I)": e_i += 1
        if st.radio("4. 생각 바로 말해?", ["바로 (E)", "정리 후 (I)"], key="ei4") == "바로 (E)": e_i += 1
        
        st.subheader("정보 수집")
        if st.radio("5. 구체적 사실 중요?", ["네 (S)", "가능성 (N)"], key="sn1") == "네 (S)": s_n += 1
        if st.radio("6. 세부 기억 잘해?", ["잘해 (S)", "큰 그림 (N)"], key="sn2") == "잘해 (S)": s_n += 1
        if st.radio("7. 미래 상상 좋아?", ["좋아 (N)", "현재 집중 (S)"], key="sn3") == "좋아 (N)": s_n += 1
        if st.radio("8. 실제 경험 선호?", ["네 (S)", "추상 (N)"], key="sn4") == "네 (S)": s_n += 1
        
        st.subheader("결정 방식")
        if st.radio("9. 논리 우선?", ["네 (T)", "감정 고려 (F)"], key="tf1") == "네 (T)": t_f += 1
        if st.radio("10. 비판 논리로 받아?", ["네 (T)", "마음 아파 (F)"], key="tf2") == "네 (T)": t_f += 1
        if st.radio("11. 공감 잘 해?", ["공감 먼저 (F)", "조언 위주 (T)"], key="tf3") == "공감 먼저 (F)": t_f += 1
        if st.radio("12. 진실 중요?", ["네 (T)", "상처 주지 않게 (F)"], key="tf4") == "네 (T)": t_f += 1
        
        st.subheader("생활 방식")
        if st.radio("13. 계획 좋아?", ["좋아 (J)", "즉흥 (P)"], key="jp1") == "좋아 (J)": j_p += 1
        if st.radio("14. 미리 끝내?", ["미리 (J)", "마감 때 (P)"], key="jp2") == "미리 (J)": j_p += 1
        if st.radio("15. 빨리 결정?", ["빨리 (J)", "열어두기 (P)"], key="jp3") == "빨리 (J)": j_p += 1
        if st.radio("16. 정리정돈 좋아?", ["좋아 (J)", "괜찮아 (P)"], key="jp4") == "좋아 (J)": j_p += 1
        
        if st.button("결과 보기!", key="test_go"):
            ei = "E" if e_i >= 3 else "I"
            sn = "S" if s_n >= 3 else "N"
            tf = "T" if t_f >= 3 else "F"
            jp = "J" if j_p >= 3 else "P"
            result = ei + sn + tf + jp
            st.session_state.mbti = result
            st.rerun()

if st.session_state.mbti:
    mbti = st.session_state.mbti
    zodiac = get_zodiac(year)
    if zodiac:
        if st.button("🔮 2026년 운세 보기!", use_container_width=True, key="fortune"):
            score = 90
            saju = get_saju(year, month, day)
            st.success(f"{Z[zodiac][0]} **{zodiac}** + {M[mbti][0]} **{mbti}** 최고 조합!")
            st.metric("운세 점수", f"{score}점", delta="안정적!")
            st.info(f"**띠 운세**: {Z[zodiac].split(' ',1)[1]}")
            st.info(f"**MBTI 특징**: {M[mbti].split(' ',1)[1]}")
            st.warning(f"**사주팔자 한 마디**: {saju}")
            st.balloons()

            share_text = f"내 2026년 운세!\n띠: {zodiac}\nMBTI: {mbti}\n사주: {saju}\n점수 {score}점! 너도 해봐: {app_url}"
            st.text_area("카톡에 붙여넣을 텍스트", share_text, height=150)

    if st.button("처음부터 다시 하기", key="reset"):
        st.session_state.clear()
        st.rerun()

st.caption("재미로만 봐주세요! 사주팔자 느낌으로 더 정확한 운세 😊")
