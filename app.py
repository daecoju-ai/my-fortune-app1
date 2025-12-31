import streamlit as st
from datetime import datetime, timedelta
import random
from streamlit.components.v1 import html as st_html

# 다국어 사전 (한국어 / English / 中文 / 日本語)
translations = {
    "ko": {
        "title": "🌟 2026 띠 + MBTI + 사주 + 오늘/내일 운세 🌟",
        "caption": "완전 무료 😄",
        "ad_title": "💳 렌탈 궁금할 때?",
        "ad_text": "<b>다나눔렌탈</b> 제휴카드 시 <b>월 0원부터</b> + <b>현금 페이백</b>!",
        "ad_btn": "🔗 보러가기",
        "birth": "### 생년월일 입력",
        "name_placeholder": "이름 입력 (결과에 표시돼요)",
        "mbti_mode": "MBTI 어떻게 할까?",
        "direct": "직접 입력",
        "test": "상세 테스트 (16문제)",
        "test_start": "상세 테스트 시작! 하나씩 답해주세요 😊",
        "energy": "에너지 방향",
        "info": "정보 수집",
        "decision": "결정 방식",
        "life": "생활 방식",
        "result_btn": "결과 보기!",
        "fortune_btn": "🔮 2026년 운세 보기!",
        "reset": "처음부터 다시 하기",
        "share_btn": "친구에게 결과 공유",
        "water_purifier": "정수기는 다나눔렌탈",
        "zodiac_title": "띠 운세",
        "mbti_title": "MBTI 특징",
        "saju_title": "사주 한 마디",
        "today_title": "오늘 운세",
        "tomorrow_title": "내일 운세",
        "combo": "최고 조합!",
        "your_fortune": "님의 2026년 운세",
        "footer": "재미로만 봐주세요 😊",
        "zodiacs": {
            "쥐띠": "🐭 활발한 에너지로 새로운 기회 잡아! 돈운 대박, 투자 주의하며 도전하세요 💰",
            "소띠": "🐮 꾸준한 노력의 결실! 안정된 재물운, 가족과 함께하는 행복한 해 🏡",
            "호랑이띠": "🐯 도전과 성공의 해! 큰 프로젝트 성공, 리더십 발휘 대박 🚀",
            "토끼띠": "🐰 안정과 사랑운 최고! 연애/결혼 운 좋음, 마음 편안한 한 해 ❤️",
            "용띠": "🐲 운기 상승! 리더십으로 주변 끌어당김, 승진/사업 성공 가능성 높음 👑",
            "뱀띠": "🐍 직감과 실속의 해! 예상치 못한 재물운, 조용히 기회 잡으세요 🐍",
            "말띠": "🐴 새 도전과 돈 기회! 이동/여행 운 좋음, 적극적으로 나서보세요 ✈️",
            "양띠": "🐑 편안함과 결혼 운! 가정운 최고, 따뜻한 관계 쌓이는 해 🏠",
            "원숭이띠": "🐵 변화와 재능 발휘! 창의력으로 성공, 새로운 분야 도전 좋음 🎨",
            "닭띠": "🐔 노력의 결실 맺는 해! 인정받고 승진 가능, 꾸준함이 관건 🏆",
            "개띠": "🐶 친구와 돈운 상승! 귀인 도움 많음, 네트워킹 적극적으로 🤝",
            "돼지띠": "🐷 여유와 최고 돈운! 재물 대박, 즐기면서 보내는 최고의 해 🐷"
        },
        "mbtis": {
            "INTJ": "🧠 냉철 전략가", "INTP": "💡 아이디어 천재", "ENTJ": "👑 보스", "ENTP": "⚡ 토론왕",
            "INFJ": "🔮 마음 마스터", "INFP": "🎨 감성 예술가", "ENFJ": "🤗 모두 선생님", "ENFP": "🎉 인간 비타민",
            "ISTJ": "📋 규칙 지킴이", "ISFJ": "🛡️ 세상 따뜻함", "ESTJ": "📢 리더", "ESFJ": "💕 분위기 메이커",
            "ISTP": "🔧 고치는 장인", "ISFP": "🌸 감성 힐러", "ESTP": "🏄 모험왕", "ESFP": "🎭 파티 주인공"
        },
        "saju_msgs": [
            "목(木) 기운 강함 → 성장과 발전의 해! 🌱", "화(火) 기운 강함 → 열정 폭발! ❤️",
            "토(土) 기운 강함 → 안정과 재물운 💰", "금(金) 기운 강함 → 결단력 좋음! 👔",
            "수(水) 기운 강함 → 지혜와 흐름 🌊", "오행 균형 → 행복한 한 해 ✨",
            "양기 강함 → 도전 성공 🚀", "음기 강함 → 내면 성찰 😌"
        ],
        "daily_msgs": [
            "재물운 좋음! 작은 투자도 이득 봐요 💰", "연애운 최고! 고백하거나 데이트 좋음 ❤️",
            "건강 주의! 과로 피하고 쉬세요 😴", "전체운 대박! 좋은 일만 생길 거예요 🌟",
            "인간관계 운 좋음! 귀인 만남 가능 🤝", "학업/일 운 최고! 집중력 최고 📚",
            "여행운 좋음! 갑자기 떠나도 괜찮아요 ✈️", "기분 좋은 하루! 웃음이 가득할 거예요 😄"
        ]
    },
    "en": {
        "title": "🌟 2026 Zodiac + MBTI + Fortune + Today/Tomorrow Luck 🌟",
        "caption": "Completely Free 😄",
        "ad_title": "💳 Curious about rental?",
        "ad_text": "<b>Dananum Rental</b> with partner card: <b>From 0 won/month</b> + <b>Cashback</b>!",
        "ad_btn": "🔗 Check it out",
        "birth": "### Enter Birth Date",
        "name_placeholder": "Enter name (shown in result)",
        "mbti_mode": "How to do MBTI?",
        "direct": "Direct input",
        "test": "Detailed test (16 questions)",
        "test_start": "Detailed test start! Please answer one by one 😊",
        "energy": "Energy Direction",
        "info": "Information Gathering",
        "decision": "Decision Making",
        "life": "Lifestyle",
        "result_btn": "View Result!",
        "fortune_btn": "🔮 View 2026 Fortune!",
        "reset": "Start Over",
        "share_btn": "Share Result with Friends",
        "water_purifier": "Water Purifier is Dananum Rental",
        "zodiac_title": "Zodiac Fortune",
        "mbti_title": "MBTI Traits",
        "saju_title": "Fortune Comment",
        "today_title": "Today's Luck",
        "tomorrow_title": "Tomorrow's Luck",
        "combo": "Best Combo!",
        "your_fortune": "'s 2026 Fortune",
        "footer": "For fun only 😊",
        "zodiacs": {
            "Rat": "🐭 Grab new opportunities with energy! Great money luck 💰",
            "Ox": "🐮 Steady effort pays off! Stable wealth and happy family 🏡",
            "Tiger": "🐯 Challenge and success! Big project success 🚀",
            "Rabbit": "🐰 Stability and love luck best! Great for romance ❤️",
            "Dragon": "🐲 Rising fortune! Leadership shines 👑",
            "Snake": "🐍 Intuition and gain! Unexpected wealth 🐍",
            "Horse": "🐴 New challenges and money chances! Good for travel ✈️",
            "Goat": "🐑 Comfort and marriage luck! Warm relationships 🏠",
            "Monkey": "🐵 Change and talent shine! Creative success 🎨",
            "Rooster": "🐔 Effort rewarded! Recognition and promotion 🏆",
            "Dog": "🐶 Friends and money rise! Helpful people 🤝",
            "Pig": "🐷 Relaxation and best money luck! Wealth jackpot 🐷"
        },
        "mbtis": {
            "INTJ": "🧠 Strategist", "INTP": "💡 Genius Thinker", "ENTJ": "👑 Commander", "ENTP": "⚡ Debater",
            "INFJ": "🔮 Advocate", "INFP": "🎨 Mediator", "ENFJ": "🤗 Protagonist", "ENFP": "🎉 Campaigner",
            "ISTJ": "📋 Logistician", "ISFJ": "🛡️ Defender", "ESTJ": "📢 Executive", "ESFJ": "💕 Consul",
            "ISTP": "🔧 Virtuoso", "ISFP": "🌸 Adventurer", "ESTP": "🏄 Entrepreneur", "ESFP": "🎭 Entertainer"
        },
        "saju_msgs": [
            "Strong Wood → Growth year! 🌱", "Strong Fire → Passion explosion! ❤️",
            "Strong Earth → Stability and wealth 💰", "Strong Metal → Strong determination! 👔",
            "Strong Water → Wisdom and flow 🌊", "Balanced elements → Happy year ✨",
            "Strong Yang → Challenge success 🚀", "Strong Yin → Inner reflection 😌"
        ],
        "daily_msgs": [
            "Good wealth luck! 💰", "Best love luck! ❤️",
            "Health caution 😴", "Overall big luck! 🌟",
            "Good relationships 🤝", "Best for study/work 📚",
            "Good travel luck ✈️", "Happy day full of laughter 😄"
        ]
    },
    "zh": {
        "title": "🌟 2026 生肖 + MBTI + 四柱 + 今日/明日运势 🌟",
        "caption": "完全免费 😄",
        "ad_title": "💳 租赁咨询？",
        "ad_text": "<b>다나눔렌탈</b> 合作信用卡 <b>月租0元起</b> + <b>现金返现</b>!",
        "ad_btn": "🔗 查看详情",
        "birth": "### 输入出生日期",
        "name_placeholder": "输入姓名 (结果中显示)",
        "mbti_mode": "MBTI 如何测试？",
        "direct": "直接输入",
        "test": "详细测试 (16题)",
        "test_start": "详细测试开始！请逐题回答 😊",
        "energy": "能量方向",
        "info": "信息收集",
        "decision": "决策方式",
        "life": "生活方式",
        "result_btn": "查看结果!",
        "fortune_btn": "🔮 查看2026年运势!",
        "reset": "重新开始",
        "share_btn": "分享结果给朋友",
        "water_purifier": "净水器选 다나눔렌탈",
        "zodiac_title": "生肖运势",
        "mbti_title": "MBTI 特点",
        "saju_title": "四柱一句话",
        "today_title": "今日运势",
        "tomorrow_title": "明日运势",
        "combo": "最佳组合!",
        "your_fortune": "的2026年运势",
        "footer": "仅供娱乐 😊",
        "zodiacs": {
            "鼠": "🐭 活力十足抓住新机会！财运大旺，谨慎投资挑战吧 💰",
            "牛": "🐮 努力结出硕果！稳定财运，家庭幸福年 🏡",
            "虎": "🐯 挑战与成功之年！大项目成功，领导力大放光彩 🚀",
            "兔": "🐰 安定与爱情运最佳！恋爱/结婚运佳，心平气和的一年 ❤️",
            "龙": "🐲 运势上升！领导力吸引众人，升职/创业成功可能性高 👑",
            "蛇": "🐍 直觉与实惠之年！意外财运，静待机会 🐍",
            "马": "🐴 新挑战与财运机会！旅行/搬家运好，积极行动 ✈️",
            "羊": "🐑 舒适与结婚运！家庭运最佳，温暖关系年 🏠",
            "猴": "🐵 变化与才能发挥！创意成功，新领域挑战佳 🎨",
            "鸡": "🐔 努力收获之年！获得认可升职可能，坚持是关键 🏆",
            "狗": "🐶 朋友与财运上升！贵人相助，积极人脉 🤝",
            "猪": "🐷 悠闲与最佳财运！财富大旺，享受的一年 🐷"
        },
        "mbtis": {
            "INTJ": "🧠 冷静战略家", "INTP": "💡 创意天才", "ENTJ": "👑 领导者", "ENTP": "⚡ 辩论王",
            "INFJ": "🔮 洞察大师", "INFP": "🎨 感性艺术家", "ENFJ": "🤗 导师型", "ENFP": "🎉 活力传播者",
            "ISTJ": "📋 规则守护者", "ISFJ": "🛡️ 温暖守护者", "ESTJ": "📢 领导者", "ESFJ": "💕 社交达人",
            "ISTP": "🔧 工艺大师", "ISFP": "🌸 感性治愈者", "ESTP": "🏄 冒险家", "ESFP": "🎭 表演者"
        },
        "saju_msgs": [
            "木气旺 → 成长发展之年! 🌱", "火气旺 → 热情爆发! ❤️",
            "土气旺 → 安定与财运 💰", "金气旺 → 决断力强! 👔",
            "水气旺 → 智慧与流动 🌊", "五行平衡 → 幸福一年 ✨",
            "阳气旺 → 挑战成功 🚀", "阴气旺 → 内省之年 😌"
        ],
        "daily_msgs": [
            "财运好！小投资也有收益 💰", "恋爱运最佳！适合告白或约会 ❤️",
            "注意健康！避免过度劳累 😴", "整体大吉！好事连连 🌟",
            "人际运好！可能遇贵人 🤝", "学业/工作运最佳！集中力超强 📚",
            "旅行运好！突然出发也没问题 ✈️", "愉快的一天！笑容满满 😄"
        ]
    },
    "ja": {
        "title": "🌟 2026年 十二支 + MBTI + 四柱推命 + 今日/明日運勢 🌟",
        "caption": "完全無料 😄",
        "ad_title": "💳 レンタル気になる？",
        "ad_text": "<b>다나눔렌탈</b> 提携カードで <b>月額0円から</b> + <b>キャッシュバック</b>!",
        "ad_btn": "🔗 詳細を見る",
        "birth": "### 生年月日を入力",
        "name_placeholder": "名前を入力 (結果に表示されます)",
        "mbti_mode": "MBTIはどうやって診断する？",
        "direct": "直接入力",
        "test": "詳細テスト (16問)",
        "test_start": "詳細テスト開始！1問ずつ答えてください 😊",
        "energy": "エネルギー方向",
        "info": "情報収集",
        "decision": "意思決定方式",
        "life": "生活スタイル",
        "result_btn": "結果を見る!",
        "fortune_btn": "🔮 2026年運勢を見る!",
        "reset": "最初からやり直す",
        "share_btn": "友達に結果を共有",
        "water_purifier": "浄水器は다나눔렌탈",
        "zodiac_title": "十二支運勢",
        "mbti_title": "MBTI特徴",
        "saju_title": "四柱一言",
        "today_title": "今日の運勢",
        "tomorrow_title": "明日の運勢",
        "combo": "最高の組み合わせ!",
        "your_fortune": "さんの2026年運勢",
        "footer": "娯楽目的でお楽しみください 😊",
        "zodiacs": {
            "子": "🐭 エネルギー満タンで新機会を掴む！金運大吉、投資注意し挑戦を 💰",
            "丑": "🐮 努力の実り！安定した財運、家族と幸せな年 🏡",
            "寅": "🐯 挑戦と成功の年！大プロジェクト成功、リーダーシップ発揮 🚀",
            "卯": "🐰 安定と恋愛運最高！恋愛/結婚運良好、心穏やかな年 ❤️",
            "辰": "🐲 運気上昇！リーダーシップで周囲を引きつけ、昇進/起業成功可能性高 👑",
            "巳": "🐍 直感と実益の年！予想外の財運、静かにチャンスを掴む 🐍",
            "午": "🐴 新挑戦と金運チャンス！移動/旅行運良好、積極的に ✈️",
            "未": "🐑 快適さと結婚運！家庭運最高、温かい関係が築ける年 🏠",
            "申": "🐵 変化と才能発揮！創造力で成功、新分野挑戦おすすめ 🎨",
            "酉": "🐔 努力の成果が出る年！認められ昇進可能、継続が鍵 🏆",
            "戌": "🐶 友人関係と金運上昇！貴人助けあり、積極的に人脈を 🤝",
            "亥": "🐷 ゆったりと最高の金運！財運大吉、楽しむ最高の年 🐷"
        },
        "mbtis": {
            "INTJ": "🧠 冷静な戦略家", "INTP": "💡 アイデア天才", "ENTJ": "👑 リーダー", "ENTP": "⚡ 討論王",
            "INFJ": "🔮 洞察マスター", "INFP": "🎨 感性芸術家", "ENFJ": "🤗 みんなの先生", "ENFP": "🎉 人間ビタミン",
            "ISTJ": "📋 ルール守護者", "ISFJ": "🛡️ 世界の温かさ", "ESTJ": "📢 リーダー", "ESFJ": "💕 ムードメーカー",
            "ISTP": "🔧 修理の達人", "ISFP": "🌸 感性ヒーラー", "ESTP": "🏄 冒険王", "ESFP": "🎭 パーティーの主役"
        },
        "saju_msgs": [
            "木の気強い → 成長と発展の年! 🌱", "火の気強い → 情熱爆発! ❤️",
            "土の気強い → 安定と財運 💰", "金の気強い → 決断力抜群! 👔",
            "水の気強い → 知恵と流れ 🌊", "五行バランス → 幸せな年 ✨",
            "陽の気強い → 挑戦成功 🚀", "陰の気強い → 内面省察 😌"
        ],
        "daily_msgs": [
            "財運良好！小さな投資も利益に 💰", "恋愛運最高！告白やデートに最適 ❤️",
            "健康注意！過労を避けて休養を 😴", "全体運大吉！良いことばかり 🌟",
            "人間関係運良好！貴人との出会い可能 🤝", "学業/仕事運最高！集中力抜群 📚",
            "旅行運良好！急な出発もOK ✈️", "笑顔いっぱいの楽しい1日 😄"
        ]
    }
}

# 세션 상태 초기화
if "lang" not in st.session_state:
    st.session_state.lang = "ko"

# 언어 선택 라디오 (4개 언어)
st.session_state.lang = st.radio("언어 / Language / 语言 / 言語", ["ko", "en", "zh", "ja"], index=["ko", "en", "zh", "ja"].index(st.session_state.lang), horizontal=True)

t = translations[st.session_state.lang]

Z = t["zodiacs"]
M = t["mbtis"]
saju_msg = t["saju_msgs"]
daily_msgs = t["daily_msgs"]

def get_zodiac(y):
    z_list = list(Z.keys())
    return z_list[(y-4)%12] if 1900<=y<=2030 else None

def get_saju(year, month, day):
    total = year + month + day
    index = total % 8
    return saju_msg[index]

def get_daily_fortune(zodiac, offset=0):
    today = datetime.now() + timedelta(days=offset)
    seed = int(today.strftime("%Y%m%d")) + list(Z.keys()).index(zodiac)
    random.seed(seed)
    return random.choice(daily_msgs)

st.set_page_config(page_title=t["title"], layout="centered")

# 세션 상태 초기화
if "mbti" not in st.session_state: st.session_state.mbti = None
if "result_shown" not in st.session_state: st.session_state.result_shown = False
if "name" not in st.session_state: st.session_state.name = ""
if "year" not in st.session_state: st.session_state.year = 2005
if "month" not in st.session_state: st.session_state.month = 1
if "day" not in st.session_state: st.session_state.day = 1

app_url = "https://my-fortune.streamlit.app"

# 초기 화면 및 결과 카드 (이전 최적화 유지 + 4언어 지원)

# (코드 나머지 부분은 이전과 동일하게 유지, 일본어 번역 추가된 상태)

st.caption(t["footer"])
