import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================
# 1. 기본 화면 설정
# ==========================================
st.set_page_config(page_title="Pocket Buffett", layout="wide")

# ==========================================
# [추가] 8-K 긴급 브리핑 팝업
floating_css = """
<style>
.floating-alert {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: #ff4b4b;
    color: white;
    padding: 15px 20px;
    border-radius: 10px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    z-index: 9999;
    font-family: 'Pretendard', sans-serif;
    cursor: pointer;
    animation: pop-in 0.5s ease-out;
}
.floating-alert:hover {
    background-color: #ff3333;
}
.alert-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 5px;
}
.alert-desc {
    font-size: 13px;
    opacity: 0.9;
}
@keyframes pop-in {
    0% { transform: translateY(50px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}
</style>
<div class="floating-alert" onclick="alert('실제 앱에서는 클릭 시 8-K 상세 요약 모달창이 뜹니다.')">
    <div class="alert-title">⚡긴급 수시 공시 8-K </div>
    <div class="alert-desc">애플(AAPL), 'OpenAI'와 전략적 파트너십 체결 발표 (방금 전)</div>
</div>
"""

# ==========================================
# 2. 검색창 영역
# ==========================================
st.title(" Pocket Buffett (포켓 버핏)")
st.markdown("스마트폰 속에 들어온 AI워런버핏 투자전략")

ticker = st.text_input("분석할 기업의 티커(예: AAPL)를 입력하세요:", "")

if ticker:
    # 8-K 플로팅 알림 렌더링 (검색 후에만 띄움)
    st.markdown(floating_css, unsafe_allow_html=True)

    # 10-K 및 10-Q 데이터 통합 수집 완료 메시지
    st.success(f"[{ticker.upper()}] 기업의 10-K(연간) 및 최신 10-Q(분기) 데이터를 기반으로 분석을 완료했습니다.")
    st.markdown("---")

    # ==========================================
    # 공통 상단 영역 (데이터 기준일 캡션 추가)
    # ==========================================
    col1, col2, col3 = st.columns(3)
    col1.metric("💵 현재 주가", "$173.50")
    col2.metric("💰 시가총액", "$2.7T")
    col3.metric("🚦 AI 적정가", "$195.20", "+12.5% (저평가)")
    
    st.caption("📅 **데이터 기준:** 2025년 3분기 10-Q 분기보고서 실적 반영 완료")
    st.markdown("---")

    # ==========================================
    # 3. 4페이지 탭 구조
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs(["📑 공시 브리핑(10-K/Q)", "🔎 AI 종목 프로파일링", "🧮 DCF 시뮬레이터", "📊 경쟁자 스캔"])

    # ------------------------------------------
    # [페이지 1] 공시 브리핑
    # ------------------------------------------
    with tab1:
        st.subheader("⏱️ 핵심 비즈니스 브리핑")
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

    # ------------------------------------------
    # [페이지 2] AI 종목 프로파일링
    # ------------------------------------------
    with tab2:
        st.subheader("🔎 AI 종목 프로파일링 (시그널 분석)")
        sig_col1, sig_col2 = st.columns(2)
        
        with sig_col1:
            st.success("""
            **🟢 AI가 찾은 긍정 시그널**
            * [10-Q] 고마진 서비스 부문의 두 자릿수 매출 성장세 확인
            * [10-K] 막대한 현금흐름을 바탕으로 한 지속적인 자사주 매입
            """)
            
        with sig_col2:
            st.error("""
            **🚨 AI가 발견한 위기 시그널**
            * [8-K] 최근 글로벌 앱스토어 수수료 관련 반독점 소송 벌금 부과
            * [10-Q] 스마트폰 교체 주기 장기화 여파 지속
            """)

    # ------------------------------------------
    # [페이지 3] DCF 시뮬레이터

    st.subheader("📈 DIY 적정주가 계산기")
    st.caption("※ 최신 분기(10-Q)의 잉여현금흐름(FCF) 데이터를 기반으로 기본 파라미터가 보정되었습니다.")

    calc_col1, calc_col2 = st.columns([1.5, 2]) 

    # ==========================================
    with calc_col1:
        st.markdown("##### 🔮 나의 투자 시나리오 만들기")
        
        # --- 1. 매출 성장률 ---
        st.markdown("<div style='word-break: keep-all;'><b>💡 1. 향후 5년 동안, 이 기업의 매출 지금보다 몇 배나 더 커질까요?</b></div>", unsafe_allow_html=True)
        
        growth_multiple = st.slider(
            "예상 기업 성장 규모 (배수)", 
            min_value=0.5, max_value=3.0, value=1.6, step=0.1, 
            help="🤖 AI 예측: 최근 5년간 이 기업의 매출은 1.4배 커졌습니다. 견고한 하드웨어 생태계와 신규 AI 서비스의 확장을 종합할 때, 5년 뒤에는 현재 대비 약 1.6배(연평균 10%) 수준으로 도약할 전망입니다."
        )
        
        st.markdown("""
        <div style='position: relative; font-size: 13px; font-weight: bold; color: #555; margin-top: -15px; height: 25px; white-space: nowrap;'>
            <span style='position: absolute; left: 0%;'>📉 0.5배</span>
            <span style='position: absolute; left: 20%; transform: translateX(-50%);'>🐢 1.0배</span>
            <span style='position: absolute; left: 40%; transform: translateX(-50%);'>🚶‍♂️ 1.5배</span>
            <span style='position: absolute; left: 60%; transform: translateX(-50%);'>🏃‍♂️ 2.0배</span>
            <span style='position: absolute; left: 100%; transform: translateX(-100%);'>🚀 3.0배(Max)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("""
        * **📉 0.5배 (쇠퇴):** 경쟁력 상실로 매출이 반토막 나는 역성장 위기 기업
        * **🐢 1.0배 (현상 유지):** 성장은 멈췄지만 꾸준히 이익을 내는 성숙기 가치주
        * **🚶‍♂️ 1.0~1.5배 (안정적 성장):** 물가 상승과 함께 꾸준하게 파이를 키우는 안정형 기업
        * **🏃‍♂️ 1.5~2.0배 (우량 성장주):** 시장을 선도하며 확실한 이익 성장을 보여주는 우량주
        * **🚀 2.0배 이상 (폭발적 성장):** 새로운 산업 패러다임을 주도하며 급성장하는 주도주 (최대 3.0배)
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- 2. 영업 이익률  ---
        st.markdown("<div style='word-break: keep-all;'><b>💡 2. 향후 5년 동안, 이 기업은 매출 대비 얼마나 많은 이익을 남길 수 있을까요?</b></div>", unsafe_allow_html=True)
        
        margin_rate = st.slider(
            "예상 영업이익률 (%)", 
            min_value=0, max_value=50, value=28, step=1, 
            help="🤖 AI 분석: 동종업계(예: IT 하드웨어) 평균 영업이익률은 20%입니다. 이 기업은 강력한 브랜드 파워를 고려할 때, 업계 평균을 상회하는 25~30% 수준 유지가 합리적입니다."
        )

        st.markdown("""
        <div style='position: relative; font-size: 13px; font-weight: bold; color: #555; margin-top: -15px; height: 25px; white-space: nowrap;'>
            <span style='position: absolute; left: 0%;'>📉 평균 이하</span>
            <span style='position: absolute; left: 40%; transform: translateX(-50%);'>➖ 업계 평균(20%)</span>
            <span style='position: absolute; left: 100%; transform: translateX(-100%);'>🥇 초과 수익</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("""
        * **📉 평균 이하:** 치열한 경쟁이나 원가 부담으로 동종업계 경쟁사들보다 수익성이 낮을 때
        * **➖ 업계 평균:** 동종업계 경쟁사들과 비슷한 수준의 표준적인 수익성을 방어할 때
        * **🥇 초과 수익:** 강력한 해자(브랜드, 기술력)를 바탕으로 경쟁사들보다 월등히 높은 마진을 남길 때
        """)

        # 백엔드 계산용 숨김 변수 및 적정가 도출 수식 유지
        wacc = 8.5  
        terminal_growth = 2.5 
        base_value = 195.20
        simulated_price = base_value * (growth_multiple / 1.6) * (1 + (margin_rate - 28) / 100)

    # ==========================================
    # 우측 결과부 
    with calc_col2:
        st.markdown("##### 📉 가치평가 시뮬레이션 차트")
        fig = go.Figure()
        
        # ... (차트 데이터 설정 코드 생략  ...
        # (테스트용 가짜 데이터)
        past_dates = pd.date_range(start="2025-01-01", periods=100, freq='D')
        past_prices = np.linspace(150, 173.50, 100) + np.random.normal(0, 3, 100)
        current_date = past_dates[-1]
        future_date = current_date + pd.Timedelta(days=30)
        fig.add_trace(go.Scatter(x=past_dates, y=past_prices, mode='lines', name='과거 주가', line=dict(color='gray')))
        fig.add_hline(y=195.20, line_dash="dash", line_color="green", annotation_text="AI 적정가 ($195.20)")
        fig.add_trace(go.Scatter(x=[current_date, future_date], y=[173.50, simulated_price], mode='lines', name='예상 경로', line=dict(color='black', dash='dash', width=2)))
        fig.add_trace(go.Scatter(x=[current_date], y=[173.50], mode='markers', name='현재가 ($173.50)', marker=dict(color='blue', size=12)))
        fig.add_trace(go.Scatter(x=[future_date], y=[simulated_price], mode='markers', name='나만의 예상가', marker=dict(color='gold', size=14, line=dict(color='black', width=1))))
        
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), showlegend=True)
        st.plotly_chart(fig, use_container_width=True) 
        
        st.markdown("---")
        st.metric(
            label="🎯 나만의 예상 적정주가", 
            value=f"${simulated_price:.2f}", 
            delta=f"현재가($173.50) 대비 {(simulated_price-173.50)/173.50 * 100:.1f}%"
        )

    # ------------------------------------------
    # [페이지 4] 경쟁자 스캔
    # ------------------------------------------
    with tab4:
        st.subheader("📊 경쟁자 스캔 (Peer Group Comparison)")
        peer_data = {
            "기업명": ["Apple (AAPL)", "Microsoft (MSFT)", "Alphabet (GOOGL)", "Meta (META)"],
            "주가(Price)": ["$173.50", "$415.30", "$142.60", "$485.10"],
            "PER": [26.5, 35.2, 24.5, 31.8],
            "PBR": [38.2, 12.1, 6.5, 8.2],
            "ROIC": ["45.2%", "25.1%", "22.3%", "19.5%"],
            "영업이익률": ["29.8%", "42.5%", "28.4%", "34.2%"]
        }
        df_peer = pd.DataFrame(peer_data)
        st.dataframe(df_peer, use_container_width=True, hide_index=True)

else:
    st.info("👈 상단 검색창에 분석하고 싶은 기업의 티커를 입력해 주세요. (예: AAPL, TSLA)")