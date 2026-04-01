import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time


# ==========================================
# [백엔드 시뮬레이션] 데이터 수집 함수
# ==========================================
def fetch_company_data(ticker):
    """
    실제 백엔드 서버나 DB에서 티커에 해당하는 데이터를 가져오는 역할을 하는 함수야.
    지금은 프로토타입이므로 AAPL일 때만 하드코딩된 더미 데이터를 반환해.
    """
    # 실제 서버 통신을 하는 것처럼 약간의 딜레이를 줌 (로딩 스피너용)
    time.sleep(1)

    ticker = ticker.upper()

    if ticker == "AAPL":
        return {
            "status": "success",
            "ticker": "AAPL",
            "company_name": "Apple",
            "current_price": 173.50,
            "market_cap": "$2.7T",
            "ai_fair_value": 195.20,
            "ai_diff": "+12.5% (저평가)",
            "briefing_summary": "핵심 비즈니스 모델(10-K)은 견고하게 유지 중이며, 최근 분기(10-Q) 서비스 매출이 예상치를 15% 상회하며 현금흐름이 개선되었습니다.",
            "dcf_base_growth": 1.6,
            "dcf_base_margin": 28,
            "peer_data": {
                # 💡 이 부분이 요청하신 새로운 지표들로 변경되었습니다!
                "기업명": ["Apple (AAPL)", "Microsoft (MSFT)", "Alphabet (GOOGL)", "Meta (META)"],
                "현재주가": ["$173.50", "$415.30", "$142.60", "$485.10"],
                "시가총액": ["$2.7T", "$3.0T", "$1.8T", "$1.2T"],
                "시장점유율": ["21.0%", "18.5%", "15.2%", "9.8%"],
                "영업이익률": ["29.8%", "42.5%", "28.4%", "34.2%"],
                "PER": ["26.5", "35.2", "24.5", "31.8"],
                "영업이익률": ["29.8%", "42.5%", "28.4%", "34.2%"]
            }
        }
    else:
        # AAPL이 아닌 다른 티커를 검색했을 경우 백엔드에서 데이터가 없다고 반환
        return {
            "status": "error",
            "message": "해당 기업의 공시 데이터나 재무 정보가 백엔드 DB에 존재하지 않습니다."
        }


# ==========================================
# 1. 기본 화면 설정 및 모바일 강제 고정 CSS
# ==========================================
st.set_page_config(page_title="Pocket Buffett", layout="centered")

global_css = """
<style>
/* 📱 1. 전체 바깥 배경은 어둡게 */
[data-testid="stAppViewContainer"] { 
    background-color: #f0f2f6; 
}

/* 💡 2. [핵심 수정] 실제 스크롤이 발생하는 '메인 화면' 자체를 폰 모양으로 만들기 */
[data-testid="stMain"] {
    background-color: #ffffff;
    max-width: 430px !important;  /* 모바일 폼팩터 너비 고정 */
    margin: 0 auto !important;    /* 화면 한가운데 정렬 */
    box-shadow: 0px 0px 20px rgba(0,0,0,0.1);
}

/* 📱 3. 안쪽 여백 설정 (너비 제한은 부모에게 맡기고 패딩만 설정) */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 10rem !important; /* 스크롤 맨 밑 여유 공간 */
    max-width: 100% !important; 
    font-family: 'Pretendard', sans-serif;
}

[data-testid="stHeader"], footer { visibility: hidden; }

/* 💬 검색창(selectbox) 안내 멘트(placeholder) 글씨 크기 수정 */
[data-testid="stSelectbox"] input::placeholder {
    font-size: 11px !important;  /* 💡 이 숫자를 원하시는 크기로 조절하세요*/
    color: #999 !important;      
}

/* 🔥 미국 시장 거래량 Top 5 리스트 UI (modern.py 디자인 차용) */
.trend-title { 
    text-align: center; font-size: 16px; font-weight: bold; 
    margin-bottom: 15px; color: #333; 
}
.trend-item {
    display: flex; align-items: center; justify-content: flex-start;
    padding: 14px 30px; border-bottom: 1px solid #f5f5f5;
}
.trend-rank { font-weight: bold; color: #999; width: 35px; font-size: 14px; }
.trend-ticker { font-weight: bold; color: #001f5b; margin-right: 8px; font-size: 15px; }
.trend-name { color: #888; font-size: 13px; }

/* 💡 상단 지표 영역 (5:5 비율) */
.ticker-col {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 90px;
}
.metric-label { font-size: 14px; color: #555; font-weight: bold; margin-bottom: 5px; }
.metric-value { font-size: 32px; font-weight: bold; color: #111; }

/* 🚦 신호등 클릭 팝업 전용 CSS */
.traffic-toggle { display: none; }
.traffic-popup {
    display: none; position: absolute; top: 60px; right: -10px; width: 180px;
    background-color: #fff; border-radius: 10px;
    padding: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.15); z-index: 10000;
    text-align: left;
}
.traffic-toggle:checked ~ .traffic-popup { display: block; animation: fade-in 0.2s; }


/* [수정/반영] ⚡ 우측 하단 플로팅 팝업*/
.fab-wrapper { position: fixed; bottom: 30px; margin-left: 330px; z-index: 9999; }
.alert-toggle { display: none; }
.lightning-fab {
    cursor: pointer; transition: transform 0.2s; font-size: 40px; 
    filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.3)); 
    display: inline-block;
}
.lightning-fab:hover { transform: scale(1.15); }
.fab-label { display: none; } /* CSS로도 한 번 더 숨김 */

/* 8-K 팝업창 (토글) */
.floating-alert {
    display: none; position: absolute; bottom: 60px; right: 0; width: 240px;
    background-color: #fff; border: 2px solid #ff4b4b; border-radius: 10px;
    padding: 15px; box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
}
.alert-toggle:checked ~ .floating-alert { display: block; animation: fade-in 0.2s; }
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.close-btn { position: absolute; top: 10px; right: 12px; font-size: 18px; font-weight: bold; cursor: pointer; color: #999; }
.alert-title { color: #ff4b4b; font-weight: bold; font-size: 15px; margin-bottom: 5px; }

/* 칩 버튼 디자인 */
.peer-chip {
    background-color: #001f5b; color: white; padding: 12px 20px; border-radius: 30px;
    font-weight: bold; font-size: 13px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); cursor: pointer;
    display: inline-block; transition: 0.2s;
}
.peer-chip:hover { transform: translateY(-3px); }
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)

# ==========================================
# 2. 메인 UI
# ===================게======================
logo_col1, logo_col2, logo_col3 = st.columns([1, 6, 1])  # 로고 사이즈를 바꾸고 싶다면 이 코드를 수정하면 됩니다.

with logo_col2:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h3 style='text-align: center; color: #001f5b;'>Pocket Buffett</h3>", unsafe_allow_html=True)

# 검색창과 로고 사이에 살짝 여백 주기
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

company_dict = {
    "AAPL": "AAPL - Apple (애플)",
    "MSFT": "MSFT - Microsoft (마이크로소프트)",
    "GOOGL": "GOOGL - Alphabet (구글/알파벳)",
    "META": "META - Meta (메타/페이스북)",
    "TSLA": "TSLA - Tesla (테슬라)",
    "AMZN": "AMZN - Amazon (아마존)",
    "NVDA": "NVDA - NVIDIA (엔비디아)",
    "NFLX": "NFLX - Netflix (넷플릭스)"
}
# 실제 앱에서는 백엔드에서 전 종목 리스트를 가져와야 함

# --- [수정/반영] 캐릭터 & 검색창 (3:7 비율) ---
col_char, col_search = st.columns([2, 8])

with col_char:
    # 💡 [이미지 삽입 방법] 실제 캐릭터 파일이 준비되면 아래 주석(#)을 풀고 파일명을 맞춰주세요!
    try:
        st.image("buffett.png", use_container_width=True)
    except:
        # 이미지가 없을 때 자리를 잡아주는 임시 더미 박스
        st.markdown(
            "<div style='text-align:center; padding:12px 0; background:#eee; border-radius:50%; color:#999; font-size:11px; font-weight:bold;'>캐릭터<br>이미지</div>",
            unsafe_allow_html=True)

with col_search:
    search_ticker = st.selectbox(
        "🔍 검색",
        options=list(company_dict.keys()),  # 실제 값은 "AAPL", "MSFT" 등 티커만 가짐
        format_func=lambda x: company_dict[x],  # 화면에는 "AAPL - Apple (애플)"로 보여줌
        index=None,
        placeholder="어떤 기업의 내재가치를 분석해볼까요?",  # [수정/반영] 멘트 변경
        label_visibility="collapsed"
    )
# ==========================================
# 3. 초기 홈 화면 (검색 전) 거래량 Top 5 리스트
# ==========================================
if not search_ticker:
    # 검색창과 리스트 사이 여백
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    # 리스트 제목 (컨셉 변경 반영)
    st.markdown("<div class='trend-title'>미국 시장 거래량 Top 5 🔥</div>", unsafe_allow_html=True)

    # 2026년 3월 30일 기준 거래량 최상위 더미 데이터
    st.markdown("""
        <div class='trend-item'><div class='trend-rank'>1</div><div class='trend-ticker'>NVDA</div><div class='trend-name'>엔비디아</div></div>
        <div class='trend-item'><div class='trend-rank'>2</div><div class='trend-ticker'>TSLA</div><div class='trend-name'>테슬라</div></div>
        <div class='trend-item'><div class='trend-rank'>3</div><div class='trend-ticker'>AMD</div><div class='trend-name'>AMD</div></div>
        <div class='trend-item'><div class='trend-rank'>4</div><div class='trend-ticker'>AAPL</div><div class='trend-name'>애플</div></div>
        <div class='trend-item'><div class='trend-rank'>5</div><div class='trend-ticker'>PLTR</div><div class='trend-name'>팔란티어</div></div>
    """, unsafe_allow_html=True)

    # 화면 하단 여유 공간
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    # 💡 [핵심] 검색어가 없을 때는 홈 화면만 그리고 코드를 여기서 정지시킵니다!
    # (이 아래에 붙을 분석 결과 화면이나 탭들이 미리 노출되지 않도록 방어)
    st.stop()

if search_ticker:
    data = fetch_company_data(search_ticker)

    if data["status"] == "success":
        # ==========================================
        # 상단 지표 영역 (5:5 비율)
        # ==========================================
        col1, col2 = st.columns(2)

        # 좌측 (50%): 현재 주가
        with col1:
            st.markdown(f"""
            <div class="ticker-col">
                <div class="metric-label">💰 현재주가</div>
                <div class="metric-value">${data['current_price']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        # 우측 (50%): AI 적정가 (신호등 클릭 팝업)
        with col2:
            is_undervalued = data['ai_fair_value'] > data['current_price']
            diff_pct = abs((data['ai_fair_value'] - data['current_price']) / data['current_price']) * 100

            if is_undervalued:
                traffic_color = "#2ecc71"
                popup_title = "🟢 안전마진 확보"
                popup_msg = f"현재 주가 대비 <b>{diff_pct:.1f}%</b> 더 저렴한 상태입니다."
            else:
                traffic_color = "#e74c3c"
                popup_title = "🔴 투자 주의 구간"
                popup_msg = f"현재 주가 대비 <b>{diff_pct:.1f}%</b> 고평가되어 있습니다."

            # 주의: 마크다운 코드 블록 오류를 막기 위해 HTML 태그의 들여쓰기를 제거했습니다.
            html_str = f"""
<div class="ticker-col" style="position: relative;">
<div class="metric-label">
🚦 AI 적정가
<label for="toggle-traffic" style="background-color: {traffic_color}; display: inline-block; width: 14px; height: 14px; border-radius: 50%; margin-left: 8px; vertical-align: middle; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></label>
</div>
<div class="metric-value">${data['ai_fair_value']:.2f}</div>

<input type="checkbox" id="toggle-traffic" class="traffic-toggle">
<div class="traffic-popup" style="border: 2px solid {traffic_color};">
<label for="toggle-traffic" class="close-btn" style="color: #999; top: 8px; right: 10px;">&times;</label>
<div style="color: {traffic_color}; font-weight: bold; font-size: 13px; margin-bottom: 5px;">{popup_title}</div>
<div style="font-size: 12px; color: #444; line-height: 1.4;">{popup_msg}</div>
</div>
</div>
"""
            st.markdown(html_str, unsafe_allow_html=True)

        st.caption("📅 **데이터 기준:** 2025년 3분기 10-Q 분기보고서 실적 반영 완료")
        st.markdown("<hr style='margin: 5px 0px 5px 0px;'>", unsafe_allow_html=True)

        # ==========================================
        # 3. 탭 구성
        # ==========================================
        st.markdown("""
<style>
div[data-baseweb="tab-list"] { display: flex; width: 100%; }
div[data-baseweb="tab-list"] button { flex: 1; justify-content: center; padding-bottom: -30px; }
</style>
""", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["📑AI 공시 요약", "🔎AI 분석 시그널", "🧮MY DCF", "📊경쟁사 비교"])

        # ------------------------------------------
        # [탭 1] 공시 요약
        # ------------------------------------------
        with tab1:
            st.markdown(
"""<style>.pop-t1{display:none;} #chk-t1:checked + .pop-t1{display:block; animation:fade-in 0.2s;}</style>
<div style="position:relative; margin-bottom:1rem;">
    <div style="display:flex; align-items:center; gap:8px;">
        <h3 style="margin:0; font-size:1.25rem; font-weight:600; color:#31333F;">📑 핵심 비즈니스 모델 요약</h3>
        <label for="chk-t1" style="width:18px; height:18px; border-radius:50%; background:#ddd; color:#555; text-align:center; font-size:12px; font-weight:bold; cursor:pointer; line-height:18px;">i</label>
    </div>
    <input type="checkbox" id="chk-t1" style="display:none;">
    <div class="pop-t1" style="position:absolute; top:35px; left:0; width:280px; background:#fff; border:1px solid #eee; border-radius:8px; padding:15px; box-shadow:0 4px 15px rgba(0,0,0,0.15); z-index:10000; font-size:12px; color:#555; line-height:1.4;">
        <label for="chk-t1" style="position:absolute; top:8px; right:10px; font-size:16px; cursor:pointer; color:#aaa;">&times;</label>
        <b style="color:#001f5b; font-size:13px;">⚖️ 면책 조항 (Disclaimer)</b><br><br>본 자료는 SEC 공시(10-K/Q)의 AI 요약본으로 내용의 축약이나 누락이 있을 수 있습니다. 정확한 사실관계는 반드시 SEC 원문을 대조하여 확인해 주십시오.
    </div>
</div>""", unsafe_allow_html=True)
            st.info("💡 **통합 요약:** 핵심 비즈니스 모델(10-K)은 견고하게 유지 중이며, 최근 분기(10-Q) 서비스 매출이 예상치를 15% 상회하며 현금흐름이 개선되었습니다.")

            with st.expander("▶ 주요 비즈니스 모델 (10-K 기준)"):
                st.write("""
                * **아이폰 (iPhone):** 전체 매출의 절반 이상을 차지하는 핵심 하드웨어
                * **서비스 (Services):** App Store, Apple Music, iCloud 등 고마진 캐시카우
                """)

            with st.expander("▶ 최근 분기 업데이트 (10-Q 기준)"):
                st.write("""
                * **실적 변화:** 서비스 부문 매출 전년 동기 대비 12% 증가
                * **위험 요인 변동:** 중국 시장 하드웨어 판매량 둔화세 진정 국면 진입
                """)

            # 플로팅 버튼 (번개 팝업)
            st.markdown("""
            <div class="fab-wrapper">
                <input type="checkbox" id="toggle-8k" class="alert-toggle">
                <div class="floating-alert">
                    <label for="toggle-8k" class="close-btn">&times;</label>
                    <div class="alert-title">⚡긴급 공시 8-K</div>
                    <div style="font-size: 13px; color: #444;">애플(AAPL), 'OpenAI'와 전략적 파트너십 체결 발표 (방금 전)</div>
                </div>
                <label for="toggle-8k" class="lightning-fab">
                    <div class="fab-label">8-K 팝업</div>
                    <div class="lightning-icon">⚡</div>
                </label>
            </div>
            """, unsafe_allow_html=True)

        # ------------------------------------------
        # [탭 2] AI 분석
        # ------------------------------------------
        with tab2:
            # 💡 [핵심] 제목과 아이콘을 Flexbox(display:flex)로 묶어서 무조건 한 줄에 나오게 고정했습니다.
            st.markdown(
"""<style>.pop-t2{display:none;} #chk-t2:checked + .pop-t2{display:block; animation:fade-in 0.2s;}</style>
<div style="position:relative; margin-bottom:1rem;">
    <div style="display:flex; align-items:center; gap:8px;">
        <h3 style="margin:0; font-size:1.25rem; font-weight:600; color:#31333F;">🔎 AI 분석 시그널</h3>
        <label for="chk-t2" style="width:18px; height:18px; border-radius:50%; background:#ddd; color:#555; text-align:center; font-size:12px; font-weight:bold; cursor:pointer; line-height:18px;">i</label>
    </div>
    <input type="checkbox" id="chk-t2" style="display:none;">
    <div class="pop-t2" style="position:absolute; top:35px; left:0; width:280px; background:#fff; border:1px solid #eee; border-radius:8px; padding:15px; box-shadow:0 4px 15px rgba(0,0,0,0.15); z-index:10000; font-size:12px; color:#555; line-height:1.4;">
        <label for="chk-t2" style="position:absolute; top:8px; right:10px; font-size:16px; cursor:pointer; color:#aaa;">&times;</label>
        <b style="color:#001f5b; font-size:13px;">⚖️ 면책 조항 (Disclaimer)</b><br><br>AI 시그널은 과거 공시 텍스트 기반의 참고용 정보입니다. 예기치 못한 시장 변수를 모두 반영하지 않으며, 특정 종목에 대한 투자 권유를 의미하지 않습니다.
    </div>
</div>""", unsafe_allow_html=True)                

            st.markdown('<style>div[data-testid="stAlert"] { word-break: keep-all; }</style>', unsafe_allow_html=True)

            st.success("""
            **🟢 AI가 찾은 긍정 시그널**
            * [10-Q] 고마진 서비스 부문을 통한 매출 성장세
            * [10-K] 지속적인 자사주 매입
            """)

            st.error("""
            **🚨 AI가 발견한 위기 시그널**
            * [8-K] 반독점 소송 관련 벌금 이슈
            * [10-Q] 스마트폰 교체 주기 장기화
            """)

            # ------------------------------------------
            # [탭 3] MY DCF
            # ------------------------------------------
            with tab3:
                st.markdown(
"""<style>.pop-t3{display:none;} #chk-t3:checked + .pop-t3{display:block; animation:fade-in 0.2s;}</style>
<div style="position:relative; margin-bottom:1rem;">
    <div style="display:flex; align-items:center; gap:8px;">
        <h3 style="margin:0; font-size:1.25rem; font-weight:600; color:#31333F;">📈DCF 시뮬레이션 차트</h3>
        <label for="chk-t3" style="width:18px; height:18px; border-radius:50%; background:#ddd; color:#555; text-align:center; font-size:12px; font-weight:bold; cursor:pointer; line-height:18px;">i</label>
    </div>
    <input type="checkbox" id="chk-t3" style="display:none;">
    <div class="pop-t3" style="position:absolute; top:35px; left:0; width:280px; background:#fff; border:1px solid #eee; border-radius:8px; padding:15px; box-shadow:0 4px 15px rgba(0,0,0,0.15); z-index:10000; font-size:12px; color:#555; line-height:1.4;">
        <label for="chk-t3" style="position:absolute; top:8px; right:10px; font-size:16px; cursor:pointer; color:#aaa;">&times;</label>
        <b style="color:#001f5b; font-size:13px;">⚖️ 면책 조항 (Disclaimer)</b><br><br>시뮬레이터의 결괏값은 DCF 공식에 대입한 이론적 수치입니다. 미래 주가나 실제 가치를 보장하지 않으므로 투자 판단의 보조 지표로만 활용해 주십시오.
    </div>
</div>""", unsafe_allow_html=True)
                st.caption("※ 최신 분기(10-Q)의 잉여현금흐름(FCF) 데이터를 기반으로 기본 파라미터가 보정되었습니다.")

                # 컬럼(st.columns) 구조를 제거하고 위에서 아래로 자연스럽게 배치합니다.
                st.markdown("##### 🔮 나의 투자 시나리오 만들기")

                # --- 1. 매출 성장률 ---
                st.markdown(
                    "<div style='word-break: keep-all; margin-top: 15px;'><b>💡 1. 향후 5년 동안, 이 기업의 매출은 지금보다 몇 배나 더 커질까요?</b></div>",
                    unsafe_allow_html=True)

                growth_multiple = st.slider(
                    "예상 기업 성장 규모 (배수)",
                    min_value=0.5, max_value=3.0, value=1.6, step=0.1,
                    help="🤖 AI 예측: 최근 5년간 이 기업의 매출은 1.4배 커졌습니다. 견고한 하드웨어 생태계와 신규 AI 서비스의 확장을 종합할 때, 5년 뒤에는 현재 대비 약 1.6배(연평균 10%) 수준으로 도약할 전망입니다."
                )

                st.markdown("""
                    <div style='position: relative; font-size: 12px; font-weight: bold; color: #555; margin-top: -15px; height: 25px; white-space: nowrap;'>
                        <span style='position: absolute; left: 0%;'>📉 0.5배</span>
                        <span style='position: absolute; left: 50%; transform: translateX(-50%);'>🚶‍♂️ 1.5배</span>
                        <span style='position: absolute; left: 100%; transform: translateX(-100%);'>🚀 3.0배(Max)</span>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("배수별 의미 보기"):
                    st.caption("""
                        * **📉 0.5배:** 역성장 위기 기업
                        * **🐢 1.0배:** 성숙기 현상 유지 기업
                        * **🚶‍♂️ 1.5배:** 안정형 우량 기업 (AI 예측)
                        * **🚀 3.0배:** 폭발적 성장 주도주
                        """)

                st.markdown("<br>", unsafe_allow_html=True)

                # --- 2. 영업 이익률  ---
                st.markdown(
                    "<div style='word-break: keep-all;'><b>💡 2. 향후 5년 동안, 이 기업은 매출 대비 얼마나 많은 이익을 남길 수 있을까요?</b></div>",
                    unsafe_allow_html=True)

                margin_rate = st.slider(
                    "예상 영업이익률 (%)",
                    min_value=0, max_value=50, value=28, step=1,
                    help="🤖 AI 분석: 동종업계(예: IT 하드웨어) 평균 영업이익률은 20%입니다. 이 기업은 강력한 브랜드 파워를 고려할 때, 업계 평균을 상회하는 25~30% 수준 유지가 합리적입니다."
                )

                st.markdown("""
                    <div style='position: relative; font-size: 12px; font-weight: bold; color: #555; margin-top: -15px; height: 25px; white-space: nowrap;'>
                        <span style='position: absolute; left: 0%;'>📉 평균 이하</span>
                        <span style='position: absolute; left: 50%; transform: translateX(-50%);'>➖ 평균(20%)</span>
                        <span style='position: absolute; left: 100%; transform: translateX(-100%);'>🥇 초과 수익</span>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("이익률별 의미 보기"):
                    st.caption("""
                    * **📉 평균 이하:** 원가 부담으로 동종업계 경쟁사들보다 수익성이 낮을 때
                    * **➖ 업계 평균:** 동종업계 경쟁사들과 비슷한 수준의 표준적인 수익성을 방어할 때
                    * **🥇 초과 수익:** 강력한 경쟁 우위로 경쟁사들보다 월등히 높은 마진을 남길 때
                    """)

                # 시뮬레이션 계산 (데이터 동적 연동)
                base_value = data['ai_fair_value']
                current_price = data['current_price']
                simulated_price = base_value * (growth_multiple / 1.6) * (1 + (margin_rate - 28) / 100)

                st.markdown("---")

                # ==========================================
                # 하단 차트 및 결과부
                # ==========================================
                st.markdown("##### 📉 가치평가 시뮬레이션 결과")

                # 최종 결과값을 차트 위로 올려서 눈에 잘 띄게 배치
                st.metric(
                    label="🎯 나만의 예상 적정주가",
                    value=f"${simulated_price:.2f}",
                    delta=f"현재가(${current_price:.2f}) 대비 {(simulated_price - current_price) / current_price * 100:.1f}%"
                )

                fig = go.Figure()

                # (테스트용 가짜 데이터)
                past_dates = pd.date_range(start="2025-01-01", periods=100, freq='D')
                past_prices = np.linspace(150, current_price, 100) + np.random.normal(0, 3, 100)
                current_date = past_dates[-1]
                future_date = current_date + pd.Timedelta(days=30)

                fig.add_trace(
                    go.Scatter(x=past_dates, y=past_prices, mode='lines', name='과거 주가', line=dict(color='gray')))
                fig.add_hline(y=base_value, line_dash="dash", line_color="green",
                              annotation_text=f"AI 적정가 (${base_value:.2f})")
                fig.add_trace(
                    go.Scatter(x=[current_date, future_date], y=[current_price, simulated_price], mode='lines',
                               name='예상 경로',
                               line=dict(color='black', dash='dash', width=2)))
                fig.add_trace(go.Scatter(x=[current_date], y=[current_price], mode='markers',
                                         name=f'현재가 (${current_price:.2f})',
                                         marker=dict(color='blue', size=10)))
                fig.add_trace(go.Scatter(x=[future_date], y=[simulated_price], mode='markers', name='나만의 예상가',
                                         marker=dict(color='gold', size=14, line=dict(color='black', width=1))))

                # 모바일 화면에 맞춰 차트 마진과 높이 최적화
                fig.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=30, b=10),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)

        # ------------------------------------------
        # [탭 4] 경쟁사
        # ------------------------------------------
        with tab4:
            st.markdown(
"""<style>.pop-t4{display:none;} #chk-t4:checked + .pop-t4{display:block; animation:fade-in 0.2s;}</style>
<div style="position:relative; margin-bottom:1rem;">
    <div style="display:flex; align-items:center; gap:8px;">
        <h3 style="margin:0; font-size:1.25rem; font-weight:600; color:#31333F;">📊 경쟁사 비교분석표</h3>
        <label for="chk-t4" style="width:18px; height:18px; border-radius:50%; background:#ddd; color:#555; text-align:center; font-size:12px; font-weight:bold; cursor:pointer; line-height:18px;">i</label>
    </div>
    <input type="checkbox" id="chk-t4" style="display:none;">
    <div class="pop-t4" style="position:absolute; top:35px; left:0; width:280px; background:#fff; border:1px solid #eee; border-radius:8px; padding:15px; box-shadow:0 4px 15px rgba(0,0,0,0.15); z-index:10000; font-size:12px; color:#555; line-height:1.4;">
        <label for="chk-t4" style="position:absolute; top:8px; right:10px; font-size:16px; cursor:pointer; color:#aaa;">&times;</label>
        <b style="color:#001f5b; font-size:13px;">⚖️ 면책 조항 (Disclaimer)</b><br><br>동종업계 재무 비율은 회계 기준에 따라 오차가 있을 수 있습니다. 모든 투자의 판단과 책임은 본인에게 있습니다.
    </div>
</div>""", unsafe_allow_html=True)

            st.dataframe(pd.DataFrame(data['peer_data']), hide_index=True)

            st.markdown("""
                        <div style="text-align:center; margin-top: 20px;">
                            <a href="/" target="_self" style="text-decoration: none;">
                                <div class="peer-chip">👀 새로운 기업 검색하기 ➔</div>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)