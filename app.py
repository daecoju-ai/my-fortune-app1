import streamlit as st

Z = {"쥐띠":"🐭 활발·성장, 돈↑","소띠":"🐮 노력 결실","호랑이띠":"🐯 도전 성공, 돈 대박","토끼띠":"🐰 안정·사랑 운","용띠":"🐲 운↑ 리더십","뱀띠":"🐍 실속·직감","말띠":"🐴 새 도전·돈 기회","양띠":"🐑 편안+결혼 운","원숭이띠":"🐵 변화·재능","닭띠":"🐔 노력 결과","개띠":"🐶 친구·돈↑","돼지띠":"🐷 여유·돈 최고"}

M = {"INTJ":"🧠 냉철 전략가","INTP":"💡 아이디어 천재","ENTJ":"👑 보스","ENTP":"⚡ 토론왕","INFJ":"🔮 마음 마스터","INFP":"🎨 감성 예술가","ENFJ":"🤗 모두 선생님","ENFP":"🎉 인간 비타민","ISTJ":"📋 규칙 지킴이","ISFJ":"🛡️ 세상 따뜻함","ESTJ":"📢 리더","ESFJ":"💕 분위기 메이커","ISTP":"🔧 고치는 장인","ISFP":"🌸 감성 힐러","ESTP":"🏄 모험왕","ESFP":"🎭 파티 주인공"}

def get_zodiac(y): 
    z = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
    return z[(y-4)%12] if 1900<=y<=2030 else None

# 조합별 특별 운세 (업그레이드 핵심!)
special_fortune = {
    "용띠ENFP": "리더십 + 인간 비타민 = 올해 최고 스타! 인기+성공 대박 🌟",
    "호랑이띠ENTP": "도전 정신 + 토론왕 = 대박 기회 잡아! 사업/승진 확정 🚀",
    "토끼띠ISFJ": "안정 + 따뜻함 = 사랑운 최고! 결혼/연애 대박 ❤️",
    "돼지띠ESFP": "여유 + 파티 주인공 = 친구운 최고! 재물운 따라와 💰",
    "쥐띠INTJ": "활발 + 전략가 = 계획대로 대성공! 돈 모이기 좋음 👑",
    "개띠ENFJ": "친구 운 + 모두 선생님 = 인간관계 대박! 귀인 많아 🤝",
    "default": "좋은 조합! 안정적이고 행복한 한 해 될 거야 ✨"
}

def get_special(zodiac, mbti):
    key = zodiac + mbti
    return special_fortune.get(key, special_fortune["default"])

st.set_page_config(page_title="띠MBTI 운세", layout="centered")
st.title("🌟 2026 띠+MBTI 초궁합 🌟")
st.caption("완전 무료 😄")

app_url = "https://my-fortune.streamlit.app"

st.markdown("### 📱 QR 코드 스캔!")
st.image("frame.png", caption="폰으로 찍어보세요")

st.markdown("### 🔗 친구들한테 공유할 링크")
st.code(app_url, language=None)
st.write("위 링크 복사해서 카톡에 붙여넣기!")

st.markdown("""
<div style="background:#ffeb3b;padding:15px;border-radius:15px;text-align:center;margin:20px 0;">
  <h3>💳 렌탈 궁금할 때?</h3>
  <p><b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 페이백</b>!</p>
  <a href="https://www.다나눔렌탈.com" target="_blank">
    <button style="background:#ff5722;color:white;padding:10px 25px;border:none;border-radius:10px;">🔗 보러가기</button>
  </a>
</div>
""", unsafe_allow_html=True)

year = st.number_input("출생 연도",1900,2030,2005,step=1)

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
            special_msg = get_special(zodiac, mbti)
            st.success(f"{Z[zodiac][0]} **{zodiac}** + {M[mbti][0]} **{mbti}** 최고 조합!")
            st.metric("운세 점수", f"{score}점", delta="안정적!")
            st.info(f"**띠 운세**: {Z[zodiac].split(' ',1)[1]}")
            st.info(f"**MBTI 특징**: {M[mbti].split(' ',1)[1]}")
            st.write(f"**특별 메시지**: {special_msg}")
            st.balloons()

            # 공유 텍스트 쉽게 복사
            share_text = f"내 2026년 운세: {zodiac} + {mbti} = {special_msg} 점수 {score}점! 너도 해봐: {app_url}"
            st.text_area("카톡에 붙여넣을 텍스트 (길게 눌러 복사)", share_text, height=100)

    if st.button("처음부터 다시 하기", key="reset"):
        st.session_state.clear()
        st.rerun()

st.caption("재미로만 봐주세요! 친구들이랑 결과 비교해보세요 😊")
