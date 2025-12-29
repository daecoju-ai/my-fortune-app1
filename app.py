import streamlit as st

Z = {"쥐띠":"🐭 활발·성장, 돈↑","소띠":"🐮 노력 결실","호랑이띠":"🐯 도전 성공, 돈 대박","토끼띠":"🐰 안정·사랑 운","용띠":"🐲 운↑ 리더십","뱀띠":"🐍 실속·직감","말띠":"🐴 새 도전·돈 기회","양띠":"🐑 편안+결혼 운","원숭이띠":"🐵 변화·재능","닭띠":"🐔 노력 결과","개띠":"🐶 친구·돈↑","돼지띠":"🐷 여유·돈 최고"}

M = {"INTJ":"🧠 냉철 전략가","INTP":"💡 아이디어 천재","ENTJ":"👑 보스","ENTP":"⚡ 토론왕","INFJ":"🔮 마음 마스터","INFP":"🎨 감성 예술가","ENFJ":"🤗 모두 선생님","ENFP":"🎉 인간 비타민","ISTJ":"📋 규칙 지킴이","ISFJ":"🛡️ 세상 따뜻함","ESTJ":"📢 리더","ESFJ":"💕 분위기 메이커","ISTP":"🔧 고치는 장인","ISFP":"🌸 감성 힐러","ESTP":"🏄 모험왕","ESFP":"🎭 파티 주인공"}

def get_zodiac(y): 
    z = ["쥐띠","소띠","호랑이띠","토끼띠","용띠","뱀띠","말띠","양띠","원숭이띠","닭띠","개띠","돼지띠"]
    return z[(y-4)%12] if 1900<=y<=2030 else None

st.set_page_config(page_title="띠MBTI 운세", layout="centered")
st.title("🌟 2026 띠+MBTI 초궁합 🌟")
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

year = st.number_input("출생 연도",1900,2030,2005,step=1)

if "mbti" not in st.session_state: 
    st.session_state.mbti = None

if st.session_state.mbti is None:
    c = st.radio("MBTI 어떻게 할까?", ["직접 입력","상세 테스트 (16문제, 정식 스타일)"], key="mode")
    if c == "직접 입력":
        m = st.selectbox("너의 MBTI", sorted(M.keys()), key="direct")
        if st.button("운세 보기", key="direct_go"):
            st.session_state.mbti = m
            st.rerun()
    else:
        st.write("정식 MBTI처럼 16문제! 하나씩 답해주세요 😊")
        
        # 점수 계산 변수
        e_i_score = 0
        s_n_score = 0
        t_f_score = 0
        j_p_score = 0
        
        # E/I 4문제
        st.sub
