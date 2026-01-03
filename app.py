import json
import os
import random
import time
from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components

# (Google Sheets)
import gspread
from google.oauth2.service_account import Credentials


# =========================
# 0) 기본 설정
# =========================
st.set_page_config(
    page_title="2026 Fortune | Zodiac + MBTI",
    layout="centered",
)

APP_URL = "https://my-fortune.streamlit.app"  # 너의 실제 배포 URL로 바꿔도 됨

# 스프레드시트 (너가 기억해 달라고 한 ID)
SPREADSHEET_ID = "1WvuKXx2if2WvxmQaxkqzFW-BzDEWWma9hZgCr2jJQYY"
SHEET_NAME = "시트1"  # 사용자 메시지: "시트1"


# =========================
# 1) 언어/문구 번역 (UI 전용)
#    결과 본문은 data/fortunes_{lang}.json 에서 가져옴
# =========================
LANGS = [
    ("ko", "한국어"),
    ("en", "English"),
    ("zh", "中文"),
    ("ja", "日本語"),
    ("ru", "Русский"),
    ("hi", "हिन्दी"),
]

T = {
    "ko": {
        "title": "2026 띠 + MBTI + 사주 + 오늘/내일 운세",
        "subtitle": "완전 무료",
        "lang_label": "언어 선택",
        "name_label": "이름 (선택)",
        "name_ph": "이름 입력 (결과에 표시돼요)",
        "birth_title": "생년월일 입력",
        "year": "년",
        "month": "월",
        "day": "일",
        "mbti_mode": "MBTI 어떻게 할까?",
        "mbti_direct": "직접 입력",
        "mbti_12": "간단 테스트 12문항",
        "mbti_16": "상세 테스트 16문항",
        "mbti_select": "MBTI 선택",
        "go_result": "운세 보기!",
        "reset": "처음부터 다시하기",

        "result_title": "님의 2026년 운세",
        "best_combo": "최고 조합!",
        "zodiac": "띠 운세",
        "mbti": "MBTI 특징",
        "saju": "사주 한 마디",
        "today": "오늘 운세",
        "tomorrow": "내일 운세",
        "year_msg": "2026 전체 운세",
        "love": "연애운 조언",
        "money": "재물운 조언",
        "work": "직장/일 조언",
        "health": "건강 조언",
        "lucky": "럭키 포인트",
        "tip": "오늘의 팁",
        "warn": "주의할 점",

        "mbti_q_title_12": "MBTI – 12 (제출하면 바로 결과로 넘어갑니다.)",
        "mbti_q_title_16": "MBTI – 16 (각 축 4문항씩. 제출하면 결과로 넘어갑니다.)",
        "submit": "제출",
        "share_btn": "친구에게 결과 공유하기",

        # 광고 (한국어만 노출)
        "ad_badge": "광고",
        "ad_title": "정수기렌탈 궁금할 때?",
        "ad_text": "다나눔렌탈 제휴카드 시 월 0원부터 + 설치당일 최대 현금 50만원 페이백!",
        "ad_btn": "다나눔렌탈 바로가기",

        # 미니게임
        "game_title": "🎮 커피쿠폰 미니게임 (선착순 20명)",
        "game_desc": "20.260 ~ 20.269초에 정확히 멈추면 성공!",
        "start": "START",
        "stop": "STOP",
        "try_left": "남은 시도",
        "success": "성공! 응모 시 선착순 20명에게 커피 쿠폰 보내드립니다.",
        "fail": "친구 공유 후 재도전.\n또는 다나눔렌탈 정수기 렌탈 정보 상담신청하고 커피쿠폰 응모.",
        "consult_title": "다나눔렌탈 상담신청(실패자만 가능)",
        "consult_ask": "상담 신청하시겠습니까?",
        "yes": "O (신청)",
        "no": "X (취소)",
        "saved": "저장 완료!",
        "not_saved": "저장하지 않았습니다.",
        "tarot_btn": "오늘의 타로 카드 뽑기",
        "tarot_title": "오늘의 타로 카드",

        # AI 검색 노출 섹션
        "seo_title": "AI 검색 노출 키워드(숨김 섹션)",
    },
    "en": {
        "title": "2026 Zodiac + MBTI + Saju + Today/Tomorrow Fortune",
        "subtitle": "Completely Free",
        "lang_label": "Language",
        "name_label": "Name (optional)",
        "name_ph": "Enter your name (shown in result)",
        "birth_title": "Birth date",
        "year": "Year",
        "month": "Month",
        "day": "Day",
        "mbti_mode": "MBTI mode",
        "mbti_direct": "Direct input",
        "mbti_12": "Quick test (12)",
        "mbti_16": "Detailed test (16)",
        "mbti_select": "Select MBTI",
        "go_result": "Show my fortune!",
        "reset": "Start over",

        "result_title": "'s 2026 Fortune",
        "best_combo": "Best combo!",
        "zodiac": "Zodiac fortune",
        "mbti": "MBTI traits",
        "saju": "Saju one-liner",
        "today": "Today",
        "tomorrow": "Tomorrow",
        "year_msg": "2026 overall",
        "love": "Love advice",
        "money": "Money advice",
        "work": "Work advice",
        "health": "Health advice",
        "lucky": "Lucky point",
        "tip": "Tip",
        "warn": "Caution",

        "mbti_q_title_12": "MBTI – 12 (Submit to see result)",
        "mbti_q_title_16": "MBTI – 16 (4 per axis. Submit to see result)",
        "submit": "Submit",
        "share_btn": "Share with friends",

        "ad_badge": "Ad",
        "ad_title": "Water purifier rental?",
        "ad_text": "Dananum Rental: from 0 won/month + up to 500,000 won cashback!",
        "ad_btn": "Open Dananum Rental",

        "game_title": "🎮 Mini game (First 20 winners)",
        "game_desc": "Stop exactly between 20.260 and 20.269 seconds!",
        "start": "START",
        "stop": "STOP",
        "try_left": "Attempts left",
        "success": "Success! First 20 winners will receive a coffee coupon.",
        "fail": "Share, then retry.\nOr apply for Dananum rental consultation to enter.",
        "consult_title": "Consultation (only after fail)",
        "consult_ask": "Do you want to apply?",
        "yes": "O (Apply)",
        "no": "X (Cancel)",
        "saved": "Saved!",
        "not_saved": "Not saved.",
        "tarot_btn": "Draw today's tarot card",
        "tarot_title": "Today's tarot card",
        "seo_title": "AI search keywords (hidden)",
    },
    "zh": {
        "title": "2026 运势（生肖 + MBTI + 四柱 + 今日/明日）",
        "subtitle": "完全免费",
        "lang_label": "语言",
        "name_label": "姓名（可选）",
        "name_ph": "输入姓名（显示在结果中）",
        "birth_title": "出生日期",
        "year": "年",
        "month": "月",
        "day": "日",
        "mbti_mode": "MBTI 方式",
        "mbti_direct": "直接输入",
        "mbti_12": "简测 12 题",
        "mbti_16": "详测 16 题",
        "mbti_select": "选择 MBTI",
        "go_result": "查看运势！",
        "reset": "重新开始",

        "result_title": "的 2026 运势",
        "best_combo": "最佳组合！",
        "zodiac": "生肖运势",
        "mbti": "MBTI 特点",
        "saju": "四柱一句话",
        "today": "今日运势",
        "tomorrow": "明日运势",
        "year_msg": "2026 整体运势",
        "love": "感情建议",
        "money": "财运建议",
        "work": "工作建议",
        "health": "健康建议",
        "lucky": "幸运点",
        "tip": "小提示",
        "warn": "注意点",

        "mbti_q_title_12": "MBTI – 12（提交后直接出结果）",
        "mbti_q_title_16": "MBTI – 16（每轴4题，提交后出结果）",
        "submit": "提交",
        "share_btn": "分享给朋友",

        "ad_badge": "广告",
        "ad_title": "净水器租赁？",
        "ad_text": "Dananum Rental：月 0 韩元起 + 最高 50 万韩元返现！",
        "ad_btn": "打开 Dananum Rental",

        "game_title": "🎮 小游戏（前20名）",
        "game_desc": "在 20.260 ~ 20.269 秒之间停下即成功！",
        "start": "START",
        "stop": "STOP",
        "try_left": "剩余次数",
        "success": "成功！前20名将收到咖啡券。",
        "fail": "分享后再挑战。\n或申请租赁咨询以参与抽奖。",
        "consult_title": "咨询申请（仅失败者可用）",
        "consult_ask": "是否申请咨询？",
        "yes": "O（申请）",
        "no": "X（取消）",
        "saved": "已保存！",
        "not_saved": "未保存。",
        "tarot_btn": "抽取今日塔罗牌",
        "tarot_title": "今日塔罗牌",
        "seo_title": "AI 搜索关键词（隐藏）",
    },
    "ja": {
        "title": "2026年 運勢（干支＋MBTI＋四柱＋今日/明日）",
        "subtitle": "完全無料",
        "lang_label": "言語",
        "name_label": "名前（任意）",
        "name_ph": "名前を入力（結果に表示）",
        "birth_title": "生年月日",
        "year": "年",
        "month": "月",
        "day": "日",
        "mbti_mode": "MBTIの方法",
        "mbti_direct": "直接入力",
        "mbti_12": "簡単テスト 12問",
        "mbti_16": "詳細テスト 16問",
        "mbti_select": "MBTIを選択",
        "go_result": "運勢を見る！",
        "reset": "最初からやり直す",

        "result_title": "の 2026年運勢",
        "best_combo": "最高の組み合わせ！",
        "zodiac": "干支運勢",
        "mbti": "MBTI特徴",
        "saju": "四柱ひとこと",
        "today": "今日",
        "tomorrow": "明日",
        "year_msg": "2026年 全体運",
        "love": "恋愛アドバイス",
        "money": "金運アドバイス",
        "work": "仕事アドバイス",
        "health": "健康アドバイス",
        "lucky": "ラッキーポイント",
        "tip": "今日のコツ",
        "warn": "注意点",

        "mbti_q_title_12": "MBTI – 12（送信で結果へ）",
        "mbti_q_title_16": "MBTI – 16（各軸4問、送信で結果へ）",
        "submit": "送信",
        "share_btn": "友だちに共有",

        "ad_badge": "広告",
        "ad_title": "浄水器レンタル？",
        "ad_text": "Dananum Rental：月0ウォン〜 + 最大50万ウォンキャッシュバック！",
        "ad_btn": "Dananum Rentalを開く",

        "game_title": "🎮 ミニゲーム（先着20名）",
        "game_desc": "20.260〜20.269秒で止めたら成功！",
        "start": "START",
        "stop": "STOP",
        "try_left": "残り回数",
        "success": "成功！先着20名にコーヒークーポンを送ります。",
        "fail": "共有して再挑戦。\nまたは相談申請で応募。",
        "consult_title": "相談申請（失敗者のみ）",
        "consult_ask": "相談を申し込みますか？",
        "yes": "O（申し込む）",
        "no": "X（キャンセル）",
        "saved": "保存しました！",
        "not_saved": "保存しませんでした。",
        "tarot_btn": "今日のタロットを引く",
        "tarot_title": "今日のタロット",
        "seo_title": "AI検索キーワード（非表示）",
    },
    "ru": {
        "title": "Гороскоп 2026 (Зодиак + MBTI + Саджу + Сегодня/Завтра)",
        "subtitle": "Полностью бесплатно",
        "lang_label": "Язык",
        "name_label": "Имя (необязательно)",
        "name_ph": "Введите имя (покажем в результате)",
        "birth_title": "Дата рождения",
        "year": "Год",
        "month": "Месяц",
        "day": "День",
        "mbti_mode": "Режим MBTI",
        "mbti_direct": "Ввести вручную",
        "mbti_12": "Быстрый тест (12)",
        "mbti_16": "Подробный тест (16)",
        "mbti_select": "Выберите MBTI",
        "go_result": "Показать результат!",
        "reset": "Начать заново",

        "result_title": "— гороскоп 2026",
        "best_combo": "Лучшая комбинация!",
        "zodiac": "Зодиак",
        "mbti": "MBTI",
        "saju": "Саджу (одной строкой)",
        "today": "Сегодня",
        "tomorrow": "Завтра",
        "year_msg": "2026 (в целом)",
        "love": "Любовь",
        "money": "Деньги",
        "work": "Работа",
        "health": "Здоровье",
        "lucky": "Удача",
        "tip": "Совет",
        "warn": "Осторожно",

        "mbti_q_title_12": "MBTI – 12 (Нажмите отправить для результата)",
        "mbti_q_title_16": "MBTI – 16 (4 на ось. Отправьте для результата)",
        "submit": "Отправить",
        "share_btn": "Поделиться",

        "ad_badge": "Реклама",
        "ad_title": "Аренда фильтра воды?",
        "ad_text": "Dananum Rental: от 0 вон/мес + кэшбэк до 500,000 вон!",
        "ad_btn": "Открыть Dananum Rental",

        "game_title": "🎮 Мини-игра (первые 20 победителей)",
        "game_desc": "Остановите между 20.260 и 20.269 сек!",
        "start": "START",
        "stop": "STOP",
        "try_left": "Попыток осталось",
        "success": "Успех! Первые 20 получат купон на кофе.",
        "fail": "Поделитесь и попробуйте снова.\nИли подайте заявку на консультацию.",
        "consult_title": "Консультация (только после провала)",
        "consult_ask": "Подать заявку?",
        "yes": "O (Да)",
        "no": "X (Нет)",
        "saved": "Сохранено!",
        "not_saved": "Не сохранено.",
        "tarot_btn": "Таро на сегодня",
        "tarot_title": "Таро на сегодня",
        "seo_title": "AI keywords (hidden)",
    },
    "hi": {
        "title": "2026 भाग्यफल (Zodiac + MBTI + Saju + आज/कल)",
        "subtitle": "पूरी तरह मुफ्त",
        "lang_label": "भाषा",
        "name_label": "नाम (वैकल्पिक)",
        "name_ph": "नाम लिखें (परिणाम में दिखेगा)",
        "birth_title": "जन्मतिथि",
        "year": "वर्ष",
        "month": "महीना",
        "day": "दिन",
        "mbti_mode": "MBTI मोड",
        "mbti_direct": "सीधा इनपुट",
        "mbti_12": "क्विक टेस्ट (12)",
        "mbti_16": "डिटेल्ड टेस्ट (16)",
        "mbti_select": "MBTI चुनें",
        "go_result": "भाग्य देखें!",
        "reset": "फिर से शुरू करें",

        "result_title": "का 2026 भाग्य",
        "best_combo": "बेस्ट कॉम्बो!",
        "zodiac": "Zodiac",
        "mbti": "MBTI",
        "saju": "Saju एक लाइन",
        "today": "आज",
        "tomorrow": "कल",
        "year_msg": "2026 ओवरऑल",
        "love": "प्रेम सलाह",
        "money": "धन सलाह",
        "work": "काम सलाह",
        "health": "स्वास्थ्य सलाह",
        "lucky": "लकी पॉइंट",
        "tip": "टिप",
        "warn": "सावधानी",

        "mbti_q_title_12": "MBTI – 12 (सबमिट करें)",
        "mbti_q_title_16": "MBTI – 16 (हर अक्ष पर 4 प्रश्न)",
        "submit": "सबमिट",
        "share_btn": "शेयर करें",

        "ad_badge": "विज्ञापन",
        "ad_title": "Water purifier rental?",
        "ad_text": "Dananum Rental: 0 won/month + cashback up to 500,000 won!",
        "ad_btn": "Open Dananum Rental",

        "game_title": "🎮 मिनी गेम (पहले 20 विजेता)",
        "game_desc": "20.260 से 20.269 सेकंड के बीच STOP करें!",
        "start": "START",
        "stop": "STOP",
        "try_left": "बचे हुए प्रयास",
        "success": "सफल! पहले 20 को कॉफी कूपन मिलेगा।",
        "fail": "शेयर करके फिर कोशिश करें।\nया कंसल्टेशन अप्लाई करके एंट्री करें।",
        "consult_title": "Consultation (fail के बाद)",
        "consult_ask": "Apply करना है?",
        "yes": "O (हाँ)",
        "no": "X (नहीं)",
        "saved": "Saved!",
        "not_saved": "Not saved.",
        "tarot_btn": "आज का tarot",
        "tarot_title": "आज का tarot",
        "seo_title": "AI keywords (hidden)",
    },
}


# =========================
# 2) MBTI 질문 (12문항 / 16문항) - 6개 언어
#    - 결과는 "E/I, S/N, T/F, J/P" 점수로 계산
# =========================

MBTI12 = {
    "ko": [
        ("주말에 갑자기 ‘놀자!’ 하면?", ("바로 나감 (E)", "집이 최고 (I)")),
        ("모임에서 처음 본 사람들과 대화?", ("재밌다 (E)", "부담된다 (I)")),
        ("새로운 카페에서 먼저 보는 건?", ("메뉴/가격 (S)", "분위기/컨셉 (N)")),
        ("영화/책을 볼 때 더 끌리는 건?", ("스토리 디테일 (S)", "숨은 의미/상징 (N)")),
        ("친구가 늦어서 화날 때?", ("바로 말함 (T)", "부드럽게 말함 (F)")),
        ("갈등 상황에서?", ("누가 맞는지 따짐 (T)", "감정 조율 (F)")),
        ("여행 계획은?", ("계획부터 (J)", "즉흥도 좋아 (P)")),
        ("마감 앞두고?", ("미리 끝냄 (J)", "막판 몰아침 (P)")),
        ("생각이 떠오르면?", ("말로 풀어냄 (E)", "머릿속 정리 (I)")),
        ("쇼핑할 때?", ("필요한 거 바로 (S)", "활용 상상 (N)")),
        ("누가 울면서 상담하면?", ("해결책 제시 (T)", "공감 먼저 (F)")),
        ("선택해야 할 때?", ("빨리 결정 (J)", "더 알아보고 (P)")),
    ],
    "en": [
        ("Friends suddenly say “hang out” this weekend?", ("Go out (E)", "Stay home (I)")),
        ("Talking to strangers at a gathering?", ("Fun (E)", "Tiring (I)")),
        ("In a new cafe, first notice?", ("Menu/prices (S)", "Vibe/concept (N)")),
        ("In movies/books, you prefer?", ("Details (S)", "Symbols/meaning (N)")),
        ("When a friend is late and you’re mad?", ("Say it (T)", "Say gently (F)")),
        ("In conflict?", ("Logic first (T)", "Feelings first (F)")),
        ("Trip planning?", ("Plan first (J)", "Go with flow (P)")),
        ("Before deadline?", ("Finish early (J)", "Last-minute (P)")),
        ("When a thought comes?", ("Say it out (E)", "Think first (I)")),
        ("Shopping style?", ("Buy needed now (S)", "Imagine future use (N)")),
        ("When someone cries?", ("Solutions (T)", "Empathy (F)")),
        ("When choosing?", ("Decide fast (J)", "Explore more (P)")),
    ],
    "zh": [
        ("周末朋友突然约你？", ("立刻去(E)", "更想在家(I)")),
        ("聚会与陌生人聊天？", ("有趣(E)", "有点累(I)")),
        ("新咖啡店先注意？", ("菜单价格(S)", "氛围概念(N)")),
        ("看电影/书更喜欢？", ("细节(S)", "含义象征(N)")),
        ("朋友迟到生气？", ("直接说(T)", "委婉说(F)")),
        ("冲突时？", ("讲道理(T)", "顾感受(F)")),
        ("旅行方式？", ("先规划(J)", "随性(P)")),
        ("截止日前？", ("提前做(J)", "最后赶(P)")),
        ("想法出现时？", ("说出来(E)", "先想(I)")),
        ("购物时？", ("需要就买(S)", "想搭配(N)")),
        ("有人哭着倾诉？", ("给方法(T)", "先共情(F)")),
        ("做选择时？", ("快决定(J)", "多看看(P)")),
    ],
    "ja": [
        ("週末に急に「遊ぼう！」と言われたら？", ("すぐ行く(E)", "家で休む(I)")),
        ("初対面の人と話すのは？", ("楽しい(E)", "疲れる(I)")),
        ("新しいカフェで最初に見るのは？", ("メニュー/価格(S)", "雰囲気/コンセプト(N)")),
        ("映画/本はどっち派？", ("細部(S)", "意味/象徴(N)")),
        ("友達が遅れてイラッとしたら？", ("はっきり言う(T)", "やわらかく言う(F)")),
        ("意見が割れたら？", ("論理(T)", "気持ち(F)")),
        ("旅行の準備は？", ("計画(J)", "即興(P)")),
        ("締切前は？", ("前倒し(J)", "直前(P)")),
        ("思いついたら？", ("口に出す(E)", "頭で整理(I)")),
        ("買い物は？", ("必要な物(S)", "使い道想像(N)")),
        ("泣きながら相談されたら？", ("解決策(T)", "共感(F)")),
        ("選ぶときは？", ("早く決める(J)", "もっと調べる(P)")),
    ],
    "ru": [
        ("Друзья внезапно зовут на выходных?", ("Иду (E)", "Останусь дома (I)")),
        ("Разговор с незнакомцами на встрече?", ("Ок (E)", "Утомляет (I)")),
        ("В новом кафе первым замечаете?", ("Меню/цены (S)", "Атмосферу (N)")),
        ("В фильмах/книгах важнее?", ("Детали (S)", "Смысл/символы (N)")),
        ("Друг опоздал, вы злитесь?", ("Скажу прямо (T)", "Скажу мягко (F)")),
        ("В конфликте вы чаще?", ("Логика (T)", "Чувства (F)")),
        ("Путешествие — вы?", ("Планирую (J)", "Спонтанно (P)")),
        ("Перед дедлайном?", ("Заранее (J)", "В последний момент (P)")),
        ("Когда идея пришла?", ("Озвучить (E)", "Сначала подумать (I)")),
        ("Шопинг?", ("Нужное сразу (S)", "Представляю варианты (N)")),
        ("Кто-то плачет?", ("Решения (T)", "Сочувствие (F)")),
        ("Когда нужно выбрать?", ("Быстро (J)", "Проверю ещё (P)")),
    ],
    "hi": [
        ("वीकेंड पर दोस्त अचानक बुलाएँ?", ("चल पड़ूँ (E)", "घर रहूँ (I)")),
        ("अनजान लोगों से बात?", ("मज़ेदार (E)", "थकाऊ (I)")),
        ("नई कैफ़े में पहले क्या?", ("मेनू/कीमत (S)", "वाइब/कॉन्सेप्ट (N)")),
        ("फ़िल्म/किताब में?", ("डिटेल (S)", "अर्थ/सिंबल (N)")),
        ("दोस्त लेट हो तो?", ("सीधा बोलूँ (T)", "नरमी से (F)")),
        ("कन्फ्लिक्ट में?", ("लॉजिक (T)", "फीलिंग्स (F)")),
        ("ट्रिप प्लान?", ("पहले प्लान (J)", "स्पॉन्टेनियस (P)")),
        ("डेडलाइन से पहले?", ("पहले खत्म (J)", "लास्ट मिनट (P)")),
        ("आईडिया आए तो?", ("बोल दूँ (E)", "पहले सोचूँ (I)")),
        ("शॉपिंग?", ("ज़रूरी चीज़ (S)", "यूज़ कल्पना (N)")),
        ("कोई रो रहा हो?", ("सॉल्यूशन (T)", "एम्पैथी (F)")),
        ("चॉइस करनी हो?", ("फास्ट (J)", "और देखूँ (P)")),
    ],
}

# 16문항: 축별 4문항씩
MBTI16 = {
    "ko": {
        "EI": [
            ("갑자기 약속이 생기면?", "신나! 나감 (E)", "집이 좋아 (I)"),
            ("사람 많이 만나면?", "에너지 충전 (E)", "에너지 소모 (I)"),
            ("대화할 때?", "말하면서 정리 (E)", "생각 후 말함 (I)"),
            ("파티 분위기?", "재밌다 (E)", "조용히 있고 싶다 (I)"),
        ],
        "SN": [
            ("새 장소에서?", "현실 디테일 (S)", "전체 느낌 (N)"),
            ("설명 들을 때?", "사실/근거 (S)", "가능성/아이디어 (N)"),
            ("콘텐츠 소비?", "스토리 디테일 (S)", "의미/메시지 (N)"),
            ("구매 결정?", "지금 필요 (S)", "나중 활용 (N)"),
        ],
        "TF": [
            ("의견 충돌?", "논리로 (T)", "감정 고려 (F)"),
            ("상담 요청?", "해결책 (T)", "공감 (F)"),
            ("평가할 때?", "기준/데이터 (T)", "관계/배려 (F)"),
            ("피드백?", "직설 (T)", "부드럽게 (F)"),
        ],
        "JP": [
            ("여행 준비?", "계획 (J)", "즉흥 (P)"),
            ("일 처리?", "미리 (J)", "막판 (P)"),
            ("정리 습관?", "깔끔히 (J)", "대충 (P)"),
            ("결정 속도?", "빠르게 (J)", "더 알아봄 (P)"),
        ],
    },
    "en": {
        "EI": [
            ("Sudden plan?", "Excited (E)", "Prefer home (I)"),
            ("After meeting many people?", "Recharged (E)", "Drained (I)"),
            ("When talking?", "Think by speaking (E)", "Think then speak (I)"),
            ("Party vibe?", "Love it (E)", "Need quiet (I)"),
        ],
        "SN": [
            ("New place?", "Details (S)", "Overall vibe (N)"),
            ("When listening?", "Facts (S)", "Possibilities (N)"),
            ("Content?", "Details (S)", "Meaning (N)"),
            ("Buying?", "Need now (S)", "Future use (N)"),
        ],
        "TF": [
            ("Conflict?", "Logic (T)", "Feelings (F)"),
            ("When asked for help?", "Solutions (T)", "Empathy (F)"),
            ("When judging?", "Standards (T)", "Care (F)"),
            ("Feedback style?", "Direct (T)", "Gentle (F)"),
        ],
        "JP": [
            ("Trip?", "Plan (J)", "Spontaneous (P)"),
            ("Work style?", "Early (J)", "Last-minute (P)"),
            ("Organizing?", "Neat (J)", "Loose (P)"),
            ("Decision speed?", "Fast (J)", "Explore (P)"),
        ],
    },
    "zh": {
        "EI": [
            ("突然有约？", "兴奋(E)", "想宅(I)"),
            ("见很多人后？", "充电(E)", "耗能(I)"),
            ("聊天时？", "边说边想(E)", "先想后说(I)"),
            ("派对？", "喜欢(E)", "想安静(I)"),
        ],
        "SN": [
            ("新地方？", "细节(S)", "整体感觉(N)"),
            ("听说明？", "事实(S)", "可能性(N)"),
            ("看内容？", "细节(S)", "意义(N)"),
            ("买东西？", "现在需要(S)", "以后用途(N)"),
        ],
        "TF": [
            ("冲突？", "讲理(T)", "顾感受(F)"),
            ("被求助？", "给方案(T)", "先共情(F)"),
            ("评价？", "标准(T)", "体贴(F)"),
            ("反馈？", "直接(T)", "委婉(F)"),
        ],
        "JP": [
            ("旅行？", "先计划(J)", "随性(P)"),
            ("做事？", "提前(J)", "最后赶(P)"),
            ("整理？", "整齐(J)", "随便(P)"),
            ("决定？", "快(J)", "再看看(P)"),
        ],
    },
    "ja": {
        "EI": [
            ("急な予定は？", "ワクワク(E)", "家がいい(I)"),
            ("人と会いすぎると？", "充電(E)", "消耗(I)"),
            ("会話中は？", "話しながら整理(E)", "考えてから(I)"),
            ("パーティーは？", "好き(E)", "静かがいい(I)"),
        ],
        "SN": [
            ("新しい場所は？", "細部(S)", "全体感(N)"),
            ("説明は？", "事実(S)", "可能性(N)"),
            ("作品は？", "ディテール(S)", "意味(N)"),
            ("買い物は？", "今必要(S)", "将来(N)"),
        ],
        "TF": [
            ("衝突は？", "論理(T)", "気持ち(F)"),
            ("相談は？", "解決(T)", "共感(F)"),
            ("評価は？", "基準(T)", "配慮(F)"),
            ("フィードバックは？", "直球(T)", "やさしく(F)"),
        ],
        "JP": [
            ("旅行は？", "計画(J)", "即興(P)"),
            ("仕事は？", "前倒し(J)", "直前(P)"),
            ("整理は？", "きっちり(J)", "ゆるく(P)"),
            ("決断は？", "早い(J)", "調べる(P)"),
        ],
    },
    "ru": {
        "EI": [
            ("Внезапные планы?", "Круто (E)", "Дом (I)"),
            ("После людей?", "Заряд (E)", "Устал (I)"),
            ("В разговоре?", "Думаю говоря (E)", "Думаю потом (I)"),
            ("Вечеринка?", "Нравится (E)", "Тишина (I)"),
        ],
        "SN": [
            ("Новое место?", "Детали (S)", "Общий вайб (N)"),
            ("Слушая?", "Факты (S)", "Возможности (N)"),
            ("Контент?", "Детали (S)", "Смысл (N)"),
            ("Покупка?", "Нужно сейчас (S)", "Будущее (N)"),
        ],
        "TF": [
            ("Конфликт?", "Логика (T)", "Чувства (F)"),
            ("Помощь?", "Решение (T)", "Эмпатия (F)"),
            ("Оценка?", "Стандарты (T)", "Забота (F)"),
            ("Фидбек?", "Прямо (T)", "Мягко (F)"),
        ],
        "JP": [
            ("Поездка?", "План (J)", "Спонтанно (P)"),
            ("Работа?", "Раньше (J)", "В конце (P)"),
            ("Порядок?", "Чётко (J)", "Свободно (P)"),
            ("Решения?", "Быстро (J)", "Проверю (P)"),
        ],
    },
    "hi": {
        "EI": [
            ("अचानक प्लान?", "एक्साइटेड (E)", "घर (I)"),
            ("लोगों के बाद?", "रीचार्ज (E)", "थकान (I)"),
            ("बात करते समय?", "बोलकर सोच (E)", "सोचकर बोल (I)"),
            ("पार्टी?", "पसंद (E)", "शांत (I)"),
        ],
        "SN": [
            ("नई जगह?", "डिटेल (S)", "वाइब (N)"),
            ("सुनते समय?", "फैक्ट (S)", "पॉसिबिलिटी (N)"),
            ("कंटेंट?", "डिटेल (S)", "मीनिंग (N)"),
            ("खरीद?", "अब ज़रूरत (S)", "फ्यूचर (N)"),
        ],
        "TF": [
            ("कन्फ्लिक्ट?", "लॉजिक (T)", "फीलिंग (F)"),
            ("मदद?", "सॉल्यूशन (T)", "एम्पैथी (F)"),
            ("जज?", "स्टैंडर्ड (T)", "केयर (F)"),
            ("फीडबैक?", "डायरेक्ट (T)", "जेंटल (F)"),
        ],
        "JP": [
            ("ट्रिप?", "प्लान (J)", "स्पॉन्टेनियस (P)"),
            ("काम?", "पहले (J)", "लास्ट मिनट (P)"),
            ("ऑर्गनाइज़?", "नीट (J)", "लूज़ (P)"),
            ("डिसीजन?", "फास्ट (J)", "और देखूँ (P)"),
        ],
    },
}


# =========================
# 3) DB 로딩 (data/fortunes_{lang}.json)
# =========================
@st.cache_data(show_spinner=False)
def load_fortune_db(lang: str) -> dict:
    lang = lang if lang in ["ko", "en", "zh", "ja", "ru", "hi"] else "en"
    path = os.path.join("data", f"fortunes_{lang}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 4) 띠 계산 (한국어 기본 key: 쥐/소/호랑이/...)
#    DB 키가 한국어 기준이므로, 내부 key는 항상 한국어로 유지
# =========================
ZODIAC_KO_LIST = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]

def get_zodiac_ko(year: int) -> str:
    # 기준: 2008년 = 쥐(자) 로 맞추는 방식(일반적 매핑). 기존 코드의 (y-4)%12도 많이 씀.
    # 여기서는 기존 코드와 동일하게 (year - 4) % 12 로 유지.
    return ZODIAC_KO_LIST[(year - 4) % 12]


def get_zodiac_display(db: dict, zodiac_ko: str, lang: str) -> str:
    # db["zodiacs"]는 [{"name":"쥐","en":"Rat"}, ...] 구조(한국어 master와 동일)
    # 일부 언어 DB는 zodiacs를 그대로 유지하므로, 표시만 적절히.
    if lang == "ko":
        return f"{zodiac_ko}띠"
    # 영어명 찾기
    en_name = None
    for z in db.get("zodiacs", []):
        if z.get("name") == zodiac_ko:
            en_name = z.get("en")
            break
    if not en_name:
        en_name = zodiac_ko
    # 각 언어별 표시
    if lang == "en":
        return en_name
    if lang == "zh":
        return f"{en_name}"
    if lang == "ja":
        return f"{en_name}"
    if lang == "ru":
        return f"{en_name}"
    if lang == "hi":
        return f"{en_name}"
    return en_name


# =========================
# 5) Google Sheets 연결/저장
#    - 컬럼은 기존(A~F) 유지 가정 + 상담신청만 G열에 'O'
# =========================
def get_gspread_client():
    if "gcp_service_account" not in st.secrets:
        return None

    info = dict(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds)

def append_row_base(
    name: str,
    phone: str,
    lang: str,
    zodiac_ko: str,
    mbti: str,
    game_time: float,
    success: bool,
):
    """
    ⚠️ '저장컬럼 바꾸지 말아줘' 때문에:
    - A~F는 기존 구조를 유지한다고 가정해서, 기본 6개 컬럼만 append
    - G열 상담신청은 별도 업데이트로 처리
    """
    client = get_gspread_client()
    if not client:
        raise RuntimeError("No Google service account in secrets.")

    sh = client.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(SHEET_NAME)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # ✅ A~F: (예시) timestamp, name, phone, lang, zodiac, mbti  + (game_time, success)는 기존이 다를 수 있음
    # 너가 '저장컬럼 유지'를 강하게 말해서, 여기서는 최소한만 저장하도록 구성:
    # A: timestamp
    # B: name
    # C: phone
    # D: lang
    # E: zodiac
    # F: mbti
    # (게임 기록/성공 여부를 기존에 저장하던 컬럼이 있었다면, 캡쳐 보내주면 1:1로 맞춰 변경해줄게.)
    row = [ts, name, phone, lang, zodiac_ko, mbti]
    ws.append_row(row, value_input_option="USER_ENTERED")
    # 방금 추가된 행 번호를 찾아서 반환(간단히: 마지막 행)
    return ws.row_count

def update_consult_flag(row_index: int, flag: str):
    client = get_gspread_client()
    sh = client.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    # G열 = 7
    ws.update_cell(row_index, 7, flag)


# =========================
# 6) 공유(네가 말한 방식): navigator.share()
# =========================
def render_share_button(label: str, share_text: str):
    # 공유 시트(휴대폰 갤러리 공유 버튼 누를 때 뜨는 화면) = navigator.share
    # 안 되는 환경(PC 등)에서는 클립보드 복사로 fallback
    html = f"""
    <div style="text-align:center; margin:30px 0;">
      <button id="shareBtn"
        style="background:#ffffff; color:#8e44ad; padding:15px 70px; border:none; border-radius:50px;
               font-size:1.2em; font-weight:bold; box-shadow: 0 6px 20px rgba(142,68,173,0.4);
               cursor:pointer;">
        {label}
      </button>
    </div>
    <script>
      const textToShare = {json.dumps(share_text)};
      const btn = document.getElementById("shareBtn");

      async function fallbackCopy() {{
        try {{
          await navigator.clipboard.writeText(textToShare);
          alert("Copied! Paste it anywhere.");
        }} catch (e) {{
          prompt("Copy this text:", textToShare);
        }}
      }}

      btn.addEventListener("click", async () => {{
        if (navigator.share) {{
          try {{
            await navigator.share({{ text: textToShare }});
          }} catch(e) {{
            // user canceled / blocked
          }}
        }} else {{
          await fallbackCopy();
        }}
      }});
    </script>
    """
    components.html(html, height=110)


# =========================
# 7) 세션 상태 초기화
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "ko"
if "result_shown" not in st.session_state:
    st.session_state.result_shown = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "year" not in st.session_state:
    st.session_state.year = 2005
if "month" not in st.session_state:
    st.session_state.month = 1
if "day" not in st.session_state:
    st.session_state.day = 1
if "mbti" not in st.session_state:
    st.session_state.mbti = None

# 미니게임 상태
if "game_running" not in st.session_state:
    st.session_state.game_running = False
if "game_start_ts" not in st.session_state:
    st.session_state.game_start_ts = None
if "game_elapsed" not in st.session_state:
    st.session_state.game_elapsed = 0.0  # STOP하면 이 값이 고정됨
if "game_tries_left" not in st.session_state:
    st.session_state.game_tries_left = 1  # 기본 1회 (공유로 +1 추가 같은 로직은 이후에 확장 가능)
if "game_success" not in st.session_state:
    st.session_state.game_success = False
if "last_saved_row" not in st.session_state:
    st.session_state.last_saved_row = None
if "consult_enabled" not in st.session_state:
    st.session_state.consult_enabled = False
if "consult_done" not in st.session_state:
    st.session_state.consult_done = False


# =========================
# 8) 스타일(디자인 고정)
# =========================
st.markdown("""
<style>
  html, body, [class*="css"] {font-family: 'Noto Sans KR', sans-serif;}
  .gradient-bg {
      background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 50%, #8ec5fc 100%);
      min-height: 100vh;
      padding: 20px 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      text-align: center;
      box-sizing: border-box;
  }
  .main-card, .ad-card, .mini-card {
      background: rgba(255,255,255,0.95);
      border-radius: 25px;
      padding: 26px;
      margin: 14px 0;
      width: 100%;
      max-width: 800px;
      box-shadow: 0 15px 35px rgba(0,0,0,0.25);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(0,0,0,0.06);
  }
  .ad-card {
      border: 2px solid rgba(230, 126, 34, 0.75);
      box-shadow: 0 10px 25px rgba(230,126,34,0.25);
  }
  .title-text {font-size: 2.2em; color: white; text-shadow: 3px 3px 8px rgba(0,0,0,0.7); margin: 22px 0 8px;}
  .combo-text {font-size: 1.8em; color: white; text-shadow: 2px 2px 6px rgba(0,0,0,0.6); margin: 8px 0 10px;}
  .content-text {font-size: 1.15em; line-height: 2.0; color: #111; text-align:left;}
  .center {text-align:center;}
  .badge {display:inline-block; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700;}
  .badge-ad {background:#fff3e0; color:#e67e22; border:1px solid rgba(230,126,34,0.5);}
  .big-num {font-size:3.2em; font-weight:900; letter-spacing:0.02em;}
  .mono {font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;}
  .btnrow {display:flex; gap:10px; justify-content:center; flex-wrap:wrap;}
</style>
""", unsafe_allow_html=True)


# =========================
# 9) 언어 선택 (항상 상단에 보이게)
# =========================
lang_codes = [c for c, _ in LANGS]
lang_labels = [l for _, l in LANGS]
default_idx = lang_codes.index(st.session_state.lang) if st.session_state.lang in lang_codes else 0

sel = st.radio(
    T[st.session_state.lang]["lang_label"],
    options=lang_codes,
    format_func=lambda x: dict(LANGS)[x],
    index=default_idx,
    horizontal=True
)
st.session_state.lang = sel
t = T[st.session_state.lang]

# 해당 언어 DB 로드
db = load_fortune_db(st.session_state.lang)

# =========================
# 10) "SEO(검색 노출)" 숨김 섹션 (AI검색용 키워드)
#     - Streamlit은 head meta를 직접 제어하기 어렵지만,
#       검색엔진이 본문 텍스트를 수집하는 경우를 대비해 숨김 키워드 블록 제공
# =========================
components.html(f"""
<div style="position:absolute; left:-9999px; top:-9999px; height:1px; width:1px; overflow:hidden;">
  2026 fortune mbti zodiac saju today tomorrow test 12 questions 16 questions
  운세 MBTI 띠 사주 오늘운세 내일운세 무료운세
  {APP_URL}
</div>
""", height=0)


# =========================
# 11) 입력 화면
# =========================
if not st.session_state.result_shown:
    st.markdown('<div class="gradient-bg">', unsafe_allow_html=True)

    st.markdown(f"<h1 class='title-text'>{t['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#fff; text-shadow:1px 1px 3px rgba(0,0,0,0.6); margin-top:0;'>{t['subtitle']}</p>",
                unsafe_allow_html=True)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.session_state.name = st.text_input(t["name_ph"], value=st.session_state.name, label_visibility="collapsed")

    st.markdown(f"<h3 class='center'>{t['birth_title']}</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    st.session_state.year = c1.number_input(t["year"], min_value=1900, max_value=2030, value=int(st.session_state.year), step=1)
    st.session_state.month = c2.number_input(t["month"], min_value=1, max_value=12, value=int(st.session_state.month), step=1)
    st.session_state.day = c3.number_input(t["day"], min_value=1, max_value=31, value=int(st.session_state.day), step=1)

    mbti_mode = st.radio(
        t["mbti_mode"],
        [t["mbti_direct"], t["mbti_12"], t["mbti_16"]],
        horizontal=True
    )

    mbti_value = None

    if mbti_mode == t["mbti_direct"]:
        mbti_value = st.selectbox(t["mbti_select"], sorted(db.get("mbti_list", [])))

        if st.button(t["go_result"], use_container_width=True):
            st.session_state.mbti = mbti_value
            st.session_state.result_shown = True
            st.rerun()

    elif mbti_mode == t["mbti_12"]:
        st.markdown(f"<div class='mini-card'><b>{t['mbti_q_title_12']}</b></div>", unsafe_allow_html=True)

        score = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        questions = MBTI12[st.session_state.lang]

        for idx, (q, (a1, a2)) in enumerate(questions):
            ans = st.radio(q, [a1, a2], key=f"mbti12_{st.session_state.lang}_{idx}")
            # 라벨 끝 글자를 기준으로 축 판단 (안전하게 괄호 안 글자)
            if "(E)" in a1 and ans == a1: score["E"] += 1
            if "(I)" in a2 and ans == a2: score["I"] += 1
            if "(S)" in a1 and ans == a1: score["S"] += 1
            if "(N)" in a2 and ans == a2: score["N"] += 1
            if "(T)" in a1 and ans == a1: score["T"] += 1
            if "(F)" in a2 and ans == a2: score["F"] += 1
            if "(J)" in a1 and ans == a1: score["J"] += 1
            if "(P)" in a2 and ans == a2: score["P"] += 1

        if st.button(t["submit"], use_container_width=True):
            ei = "E" if score["E"] >= score["I"] else "I"
            sn = "S" if score["S"] >= score["N"] else "N"
            tf = "T" if score["T"] >= score["F"] else "F"
            jp = "J" if score["J"] >= score["P"] else "P"
            st.session_state.mbti = ei + sn + tf + jp
            st.session_state.result_shown = True
            st.rerun()

    else:  # 16
        st.markdown(f"<div class='mini-card'><b>{t['mbti_q_title_16']}</b></div>", unsafe_allow_html=True)
        qset = MBTI16[st.session_state.lang]
        score = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

        def ask_axis(axis_key, prefix):
            qs = qset[axis_key]
            for i, (q, a1, a2) in enumerate(qs):
                ans = st.radio(q, [a1, a2], key=f"{prefix}_{st.session_state.lang}_{axis_key}_{i}")
                # axis_key 기준으로 가산
                if axis_key == "EI":
                    if "(E)" in a1 and ans == a1: score["E"] += 1
                    if "(I)" in a2 and ans == a2: score["I"] += 1
                if axis_key == "SN":
                    if "(S)" in a1 and ans == a1: score["S"] += 1
                    if "(N)" in a2 and ans == a2: score["N"] += 1
                if axis_key == "TF":
                    if "(T)" in a1 and ans == a1: score["T"] += 1
                    if "(F)" in a2 and ans == a2: score["F"] += 1
                if axis_key == "JP":
                    if "(J)" in a1 and ans == a1: score["J"] += 1
                    if "(P)" in a2 and ans == a2: score["P"] += 1

        ask_axis("EI", "mbti16")
        ask_axis("SN", "mbti16")
        ask_axis("TF", "mbti16")
        ask_axis("JP", "mbti16")

        if st.button(t["submit"], use_container_width=True):
            ei = "E" if score["E"] >= score["I"] else "I"
            sn = "S" if score["S"] >= score["N"] else "N"
            tf = "T" if score["T"] >= score["F"] else "F"
            jp = "J" if score["J"] >= score["P"] else "P"
            st.session_state.mbti = ei + sn + tf + jp
            st.session_state.result_shown = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # main-card

    st.markdown("</div>", unsafe_allow_html=True)  # gradient-bg


# =========================
# 12) 결과 화면
# =========================
if st.session_state.result_shown:
    mbti = st.session_state.mbti
    if not mbti:
        st.session_state.result_shown = False
        st.rerun()

    # 날짜 유효성 간단 체크 (월/일)
    try:
        datetime(int(st.session_state.year), int(st.session_state.month), int(st.session_state.day))
    except Exception:
        st.error("Invalid date.")
        if st.button(t["reset"], use_container_width=True):
            # 결과만 초기화 (게임/시도 횟수는 유지 요구가 있었음)
            st.session_state.result_shown = False
            st.session_state.mbti = None
            st.rerun()
        st.stop()

    zodiac_ko = get_zodiac_ko(int(st.session_state.year))
    zodiac_display = get_zodiac_display(db, zodiac_ko, st.session_state.lang)

    combo_key = f"{zodiac_ko}_{mbti}"
    combo = db.get("combos", {}).get(combo_key)

    if not combo:
        st.error("DB missing combo key: " + combo_key)
        if st.button(t["reset"], use_container_width=True):
            st.session_state.result_shown = False
            st.session_state.mbti = None
            st.rerun()
        st.stop()

    # 표시용 이름
    name_display = st.session_state.name.strip()
    if st.session_state.lang == "ko":
        name_title = f"{name_display}님의" if name_display else ""
    else:
        name_title = f"{name_display}" if name_display else ""

    # 타로
    tarot_cards = db.get("tarot_cards", {})
    tarot_card = random.choice(list(tarot_cards.keys())) if tarot_cards else None

    st.markdown('<div class="gradient-bg">', unsafe_allow_html=True)

    # 헤더
    st.markdown(
        f"<h1 class='title-text'>{name_title} 2026{'년' if st.session_state.lang=='ko' else ''} </h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h2 style='font-size:2.4em; color:white; text-shadow:3px 3px 8px rgba(0,0,0,0.7); margin:0;'>"
        f"{zodiac_display} + {mbti}</h2>",
        unsafe_allow_html=True
    )
    st.markdown(f"<h3 class='combo-text'>{t['best_combo']}</h3>", unsafe_allow_html=True)

    # 본문 카드
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="content-text">
      <b>{t['zodiac']}</b><br>{combo.get('zodiac_fortune','')}<br><br>

      <b>{t['mbti']}</b><br>{combo.get('mbti_trait','')}<br>
      <span style="color:#444;">{combo.get('mbti_influence','')}</span><br><br>

      <b>{t['saju']}</b><br>{combo.get('saju_message','')}<br><br>

      <b>{t['today']}</b><br>{combo.get('today_message','')}<br><br>
      <b>{t['tomorrow']}</b><br>{combo.get('tomorrow_message','')}<br><br>

      <b>{t['year_msg']}</b><br>{combo.get('year_message','')}<br><br>

      <b>{t['love']}</b><br>{combo.get('love_advice','')}<br><br>
      <b>{t['money']}</b><br>{combo.get('money_advice','')}<br><br>
      <b>{t['work']}</b><br>{combo.get('work_advice','')}<br><br>
      <b>{t['health']}</b><br>{combo.get('health_advice','')}<br><br>

      <b>{t['lucky']}</b><br>{combo.get('lucky_point','')}<br><br>
      <b>{t['tip']}</b>: {combo.get('tip','')}<br>
      <b>{t['warn']}</b>: {combo.get('warn','')}<br><br>

      <b>MBTI × Fortune Advice</b><br>{combo.get('combo_advice','')}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # 공유 버튼 (네가 말한 방식 그대로)
    # =========================
    share_text = (
        f"{name_display + ('님의' if st.session_state.lang=='ko' else '')} 2026 Fortune\n\n"
        f"{zodiac_display} + {mbti}\n"
        f"{combo.get('today_message','')}\n"
        f"{combo.get('tomorrow_message','')}\n\n"
        f"{APP_URL}"
    )
    render_share_button(t["share_btn"], share_text)

    # =========================
    # 타로 (정상 작동 유지)
    # =========================
    if st.button(t["tarot_btn"], use_container_width=True):
        tarot_card = random.choice(list(tarot_cards.keys())) if tarot_cards else None
        tarot_meaning = tarot_cards.get(tarot_card, "") if tarot_card else ""
        st.markdown(f"""
        <div class="mini-card">
          <h3 style="color:#9b59b6; font-size:1.3em; margin-top:0;">{t['tarot_title']}</h3>
          <h2 style="font-size:2em; color:#333; margin:10px 0;">{tarot_card}</h2>
          <p style="font-size:1.2em; color:#111; line-height:1.7; margin:0;">{tarot_meaning}</p>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # 광고: 한국어만 + 미니게임 바로 위
    # =========================
    if st.session_state.lang == "ko":
        st.markdown('<div class="ad-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="center">
          <span class="badge badge-ad">{t['ad_badge']}</span><br><br>
          <b style="font-size:1.25em;">{t['ad_title']}</b><br>
          <span style="color:#333;">{t['ad_text']}</span><br><br>
          <a href="https://www.다나눔렌탈.com" target="_blank"
             style="display:inline-block; background:#e67e22; color:white; padding:12px 22px;
                    border-radius:14px; text-decoration:none; font-weight:800;">
            {t['ad_btn']}
          </a>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # 미니게임
    # 요구사항:
    # - Start 누르면 계속되는 문제 방지(이미 running이면 Start 비활성)
    # - Stop하면 시간 고정(이전 버전처럼 그 상태로 남게)
    # - 기록 입력/제출 제거
    # - 성공 범위 20.260~20.269
    # - 성공 시: 성공 문구 + 상담신청 OFF
    # - 실패 시: 실패 문구 + 상담신청 ON(본인이 O/X)
    # - X 선택 시 DB 저장하지 않음(삭제)
    # - O 선택 시: G열에 'O' 기록
    # =========================
    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='margin:0;'>{t['game_title']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='margin:8px 0 14px; color:#333;'><b>{t['game_desc']}</b></p>", unsafe_allow_html=True)

    # 실시간 표시용 elapsed 계산
    def current_elapsed():
        if st.session_state.game_running and st.session_state.game_start_ts is not None:
            return time.time() - st.session_state.game_start_ts
        return st.session_state.game_elapsed

    elapsed_now = current_elapsed()

    # 스톱워치 표시
    st.markdown(
        f"<div class='center mono big-num'>{elapsed_now:0.3f}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='center' style='color:#333; font-weight:700;'>{t['try_left']}: {st.session_state.game_tries_left}</div>",
        unsafe_allow_html=True
    )

    b1, b2 = st.columns(2)

    # START: 이미 running이면 막기 / tries_left <=0이면 막기
    start_disabled = st.session_state.game_running or st.session_state.game_tries_left <= 0 or st.session_state.game_success
    if b1.button(t["start"], use_container_width=True, disabled=start_disabled):
        st.session_state.game_running = True
        st.session_state.game_start_ts = time.time()
        # start 시점에는 elapsed를 0으로 리셋
        st.session_state.game_elapsed = 0.0
        st.session_state.consult_enabled = False
        st.session_state.consult_done = False
        st.rerun()

    # STOP: running일 때만 가능
    stop_disabled = (not st.session_state.game_running) or st.session_state.game_success
    if b2.button(t["stop"], use_container_width=True, disabled=stop_disabled):
        # STOP 누른 순간의 기록을 고정
        st.session_state.game_elapsed = time.time() - st.session_state.game_start_ts
        st.session_state.game_running = False
        st.session_state.game_start_ts = None

        # 시도 차감 (성공/실패 무조건 1회 소모)
        if st.session_state.game_tries_left > 0:
            st.session_state.game_tries_left -= 1

        # 성공 판정
        gt = st.session_state.game_elapsed
        if 20.260 <= gt <= 20.269:
            st.session_state.game_success = True
            st.session_state.consult_enabled = False
        else:
            st.session_state.game_success = False
            st.session_state.consult_enabled = True

        st.rerun()

    # 실시간 업데이트: running이면 자동 rerun (부드럽게)
    if st.session_state.game_running:
        time.sleep(0.03)
        st.rerun()

    # 결과 문구 + 상담 흐름
    if (not st.session_state.game_running) and st.session_state.game_start_ts is None and st.session_state.game_elapsed > 0:
        gt = st.session_state.game_elapsed

        if st.session_state.game_success and 20.260 <= gt <= 20.269:
            st.success(t["success"])
        else:
            st.warning(t["fail"])

            # 실패자 상담신청(한국어 요구: G열 O/X)
            # 상담은 한국어 버전에서만 운영하는 게 자연스럽지만, 사용자가 "실패한 사람 on"이라고 했으므로
            # 여기서는 모든 언어에서 UI는 제공하되, 실제 상담 문구는 언어별 t 사용.
            if st.session_state.consult_enabled and (not st.session_state.consult_done):
                st.markdown(f"<hr><b>{t['consult_title']}</b><br>{t['consult_ask']}", unsafe_allow_html=True)

                # 이름/전화번호 입력(한국어 이벤트로 수집하려면 여기서)
                # 사용자 요구는 "이름과 전화번호 수집"이었고, 지금은 DB에 기록한다는 흐름이 있으므로 유지
                # (전화번호 수집 문구/동의는 이전 대화에서 별도 제공 예정이었지만 여기선 최소 구현)
                st.session_state.phone = st.text_input("Phone / 전화번호", value=st.session_state.phone)

                c_yes, c_no = st.columns(2)

                # O(신청) -> DB 저장 + G열 O
                if c_yes.button(t["yes"], use_container_width=True):
                    try:
                        row_idx = append_row_base(
                            name=st.session_state.name.strip(),
                            phone=st.session_state.phone.strip(),
                            lang=st.session_state.lang,
                            zodiac_ko=zodiac_ko,
                            mbti=mbti,
                            game_time=gt,
                            success=False,
                        )
                        st.session_state.last_saved_row = row_idx
                        # G열 'O'
                        update_consult_flag(row_idx, "O")

                        st.session_state.consult_done = True
                        st.success(t["saved"])
                        st.info("커피쿠폰 응모 완료!" if st.session_state.lang == "ko" else "Entry completed!")
                    except Exception as e:
                        st.error(f"Sheet error: {e}")

                # X(취소) -> DB 저장하지 않음
                if c_no.button(t["no"], use_container_width=True):
                    st.session_state.consult_done = True
                    st.info(t["not_saved"])

    st.markdown("</div>", unsafe_allow_html=True)  # mini-card

    # =========================
    # 결과 화면 하단: 처음부터 다시하기 (중복 기능 제거 요구 반영)
    # - 여기서는 '입력화면으로' 버튼을 만들지 않음
    # - reset 시도 횟수는 "유지" (요구: reset 후에도 시도 횟수 초기화되면 싫다)
    # =========================
    if st.button(t["reset"], use_container_width=True):
        st.session_state.result_shown = False
        st.session_state.mbti = None
        # ✅ tries_left, game_success 등은 유지 (요구사항 반영)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # gradient-bg
