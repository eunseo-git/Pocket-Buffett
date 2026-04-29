import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import base64
import re
import requests 
import yfinance as yf
import os

# ⚙️ 전역 설정 (Global Configuration)
API_BASE_URL = "https://api.pocketbuffett.com/v1"


# 💡 [백엔드 연동 대비] 상단 헤더용 overview API 호출
def fetch_company_data(ticker):
    ticker = ticker.upper()
    try:
        response = requests.get(f"{API_BASE_URL}/company/{ticker}/overview", timeout=5)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"⚠️ 백엔드 API 호출 실패 (더미 데이터 모드 전환): {e}")
        time.sleep(0.5)

        # 💡 [핵심 해결] AAPL일 때 기본 경쟁사(peer_data) 정보도 같이 내려주도록 수정했습니다!
        if ticker == "AAPL":
            return {
                "status": "success",
                "ticker": "AAPL",
                "company_name": "Apple",
                "current_price": 238.56,
                "ai_fair_value": 255.0,
                "peer_data": {
                    "기업명": ["Microsoft (MSFT)", "Alphabet (GOOGL)", "Meta (META)"],
                    "현재주가": ["$415.30", "$142.60", "$485.10"],
                    "시가총액": ["$3.0T", "$1.8T", "$1.2T"],
                    "시장점유율": ["18.5%", "15.2%", "9.8%"],
                    "영업이익률": ["42.5%", "28.4%", "34.2%"],
                    "PER": ["35.2", "24.5", "31.8"]
                }
            }
        else:
            # 💡 [보너스 해결] AAPL이 아닌 다른 종목을 검색했을 때도 에러가 나지 않게 임시 데이터를 넣어줍니다.
            return {
                "status": "success",
                "ticker": ticker,
                "company_name": f"{ticker} Corp",
                "current_price": 150.00,
                "ai_fair_value": 180.00,
                "peer_data": {
                    "기업명": [f"Competitor A (COMA)", f"Competitor B (COMB)"],
                    "현재주가": ["$120.00", "$90.00"],
                    "시가총액": ["$1.2T", "$800.0B"],
                    "시장점유율": ["12.0%", "8.5%"],
                    "영업이익률": ["25.0%", "15.0%"],
                    "PER": ["20.5", "18.2"]
                }
            }


# 💡 [백엔드 연동 대비] 탭1&탭2 전용 API (AI 공시 분석 & 시그널 데이터 수집)
# ==========================================
@st.cache_data(ttl=3600)  # AI 분석 결과는 자주 안 변하므로 1시간 캐싱
def fetch_analysis_data(ticker):
    try:
        # 실제 연동 시 주석 해제할 부분
        # response = requests.get(f"{API_BASE_URL}/company/{ticker}/analysis", timeout=15)
        # response.raise_for_status()
        # return response.json()
        raise Exception("API 미구현")
    except:
        time.sleep(2)
        data = {
            "status": "success",
            "ticker": ticker,
            "report_year": 2026,
            "report_quarter": 1,
            "report_type": "10-Q",
            "briefing_summary": "Apple은 제품 및 서비스의 혁신적인 개발을 통해 경쟁력을 유지하며, 2025년 총 매출의 60%가 간접 유통 채널을 통해 발생했습니다. 최근 분기에서는 $257억 상당의 자사주를 매입했으며, "
            "이는 자본 구조 개선에 긍정적인 영향을 미칠 것입니다. 또한, 최근 주주총회에서는 \"China Entanglement Audit\"주주 제안이 부결되었으나, Apple Inc. 비상임 이사 주식 플랜의 수정 및 개정이 승인되었습니다.",
            "business_model_10k": [
                "회사는 직접 판매와 간접 유통 채널을 통한 제품 판매를 병행하고 있습니다. 이는 다양한 소비자층에 제품을 제공하며 시장 점유율을 확대하는 전략입니다.",
                "회사는 스마트폰, 개인용 컴퓨터, 태블릿, 웨어러블 및 액세서리, 클라우드 서비스 등 다양한 제품과 서비스를 제공합니다. Apple의 성공 요인은 지속적인 혁신과 강력한 기술 생태계 구축에 있습니다.",
                "Apple은 디지털 콘텐츠와 결제 서비스를 통해 소비자 경험을 향상시키며, 지역별로 사업을 관리하여 각 지역의 특수한 시장 동향에 대응하고 있습니다."
            ],
            "recent_update_10q": [
                "회사는 내년 말까지 최대 $1000억 규모의 자사주 매입 프로그램을 발표했으며, 이는 주주가치 제고에 기여할 것입니다.",
                "재무 담당 수석 부사장인 Kevan Parekh은 2026년 중순까지 주식 매도를 위한 10b5-1(c) 조건을 충족하는 거래 계획을 체결했습니다."
            ],
            "emergency_8k": {
                "has_issue": True, "title": "Apple Inc. 비상임 이사 주식 플랜 수정 및 개정 승인","issue_date": "2026-04-17",
                "description": "Apple Inc. 비상임 이사 주식 플랜의 수정 및 개정이 주주총회에서 승인되었습니다. 해당 수정안은 2026년 2월 24일을 기점으로 효력을 발휘합니다."
            },
            "positive_signals": [
                "회사는 자사주 매입을 통해 주주 가치를 제고하고 있습니다.",
                "제품 및 서비스 혁신을 통한 시장 경쟁력 유지가 예상됩니다."
            ],
            "negative_signals": [
                "경쟁적인 시장 환경으로 인해 가격 압박과 마진 감소의 위험이 존재합니다.",
                "글로벌 경제 불확실성이 소비자 신뢰와 수요에 부정적인 영향을 미칠 수 있습니다."
            ]
        }

    # 💡 [API누락 방어용]
    data['report_year'] = data.get('report_year', 2025)
    data['report_quarter'] = data.get('report_quarter', 3)
    data['report_type'] = data.get('report_type', '10-Q')

    return data


# 💡 [백엔드 연동 대비] DCF탭 전용 API
@st.cache_data(ttl=3600)
def fetch_dcf_data(ticker, current_price):
    try:
        # 실제 연동 시 주석 해제
        # response = requests.get(f"{API_BASE_URL}/company/{ticker}/dcf", timeout=10)
        # response.raise_for_status()
        # return response.json()
        raise Exception("API 미구현")
    except:
        months = 30 * 12
        temp_prices = 100 + np.cumsum(np.random.normal(0.5, 2.5, months))
        dummy_historical = (temp_prices + (current_price - temp_prices[-1])).tolist()
        return {
            "status": "success", "ticker": ticker,
            "dcf_base_growth": 1.6, "dcf_base_margin": 28,
            "wacc": 8.5, "terminal_growth": 2.5,
            "historical_prices": dummy_historical
        }

# 💡 [백엔드 연동 대비] 사용자가 직접 추가하는 단일 경쟁사 API
def fetch_single_competitor(ticker):
        ticker = ticker.upper()
        try:
            # 실제 연동 시 주석 해제
            # response = requests.get(f"{API_BASE_URL}/company/{ticker}/competitor", timeout=5)
            # return response.json()
            raise Exception("API 미구현")
        except:
            time.sleep(0.5)  # 로딩 연출
            # 테스트용 더미 데이터
            return {
                "status": "success",
                "ticker": ticker,
                "data": {
                    "기업명": f"{ticker} Corp ({ticker})",
                    "현재주가": f"${np.random.randint(50, 500)}.00",
                    "시가총액": f"${np.random.randint(10, 900)}B",
                    "시장점유율": f"{np.random.randint(5, 30)}%",
                    "영업이익률": f"{np.random.randint(5, 40)}%",
                    "PER": f"{np.random.randint(10, 50)}.5"
                }
            }


# [프론트엔드 단독 연동] 미국 전체 시장 실시간 거래량 Top 5 스크래핑
@st.cache_data(ttl=300)
def fetch_realtime_top5_volume():
    try:
        url = "https://finance.yahoo.com/most-active"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # 💡 403(접근 거부) 에러

        df = pd.read_html(response.text)[0]
        data = [{"rank": i + 1, "ticker": row['Symbol'],
                 "name": row['Name'][:15] + "..." if len(str(row['Name'])) > 15 else str(row['Name'])} for i, row in
                df.head(5).iterrows()]

        return data, False  # 🟢 성공: (데이터 리스트, is_fallback=False) 반환

    except Exception as e:
        print(f"⚠️ 야후 파이낸스 스크래핑 에러: {e}")
        data = [{"rank": i + 1, "ticker": t, "name": n} for i, (t, n) in enumerate(
            [("NVDA", "NVIDIA"), ("TSLA", "Tesla"), ("AAPL", "Apple"), ("AMD", "AMD"), ("AMZN", "Amazon")])]

        return data, True  # 🟡 실패: (더미 데이터 리스트, is_fallback=True) 반환


def get_financial_metrics(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    market_cap = info.get('marketCap', '-')
    operating_margin_raw = info.get('operatingMargins', None)
    if operating_margin_raw is not None:
        operating_margin = f"{round(operating_margin_raw * 100, 2)}%"
    else:
        operating_margin = "-"

    # PER (Price-to-Earnings Ratio - 보통 Trailing PE를 많이 씁니다.)
    per = info.get('trailingPE', info.get('forwardPE', '-'))
    if per != '-':
        per = round(per, 2)

    # 결과 반환
    return {
        "종목명": info.get('shortName', ticker_symbol),
        "시가총액": market_cap,
        "영업이익률": operating_margin,
        "PER": per
    }

def format_market_cap(value):
    if value is None or value == '-':
        return "-"
    try:
        value = float(value)
        if value >= 1e12:  # 1조 달러 이상 (Trillion)
            return f"${value / 1e12:.2f}T"
        elif value >= 1e9:  # 10억 달러 이상 (Billion)
            return f"${value / 1e9:.2f}B"
        elif value >= 1e6:  # 100만 달러 이상 (Million)
            return f"${value / 1e6:.2f}M"
        else:
            return f"${value:,.0f}"
    except ValueError:
        return "-"


# 💡 [핵심 함수] 탭 4에서 새로운 기업을 추가할 때 실행되는 진짜 API 호출 함수
def fetch_single_competitor(ticker):
    try:
        # 1. 야후 파이낸스에서 실시간 데이터 꾸러미(info) 가져오기
        stock = yf.Ticker(ticker)
        info = stock.info

        # 2. 기업명 (탭 4 표의 정규식 추출을 위해 '기업명 (티커)' 형태로 예쁘게 조립)
        short_name = info.get('shortName', ticker)
        comp_name_formatted = f"{short_name} ({ticker})"

        # 3. 현재 주가
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        price_str = f"${current_price:.2f}" if current_price else "-"

        # 4. 시가총액 (위에서 만든 도우미 함수로 예쁘게 포맷팅)
        market_cap_raw = info.get('marketCap', '-')
        market_cap_str = format_market_cap(market_cap_raw)

        # 5. 영업이익률 (% 단위로 변환)
        margin_raw = info.get('operatingMargins', None)
        margin_str = f"{margin_raw * 100:.2f}%" if margin_raw else "-"

        # 6. PER (주가수익비율)
        per = info.get('trailingPE', info.get('forwardPE', '-'))
        per_str = f"{per:.2f}" if per != '-' else "-"
        market_share_str = "-"

        # 7. 탭 4번 표에 정확히 들어맞는 딕셔너리 형태로 반환
        return {
            'status': 'success',
            'data': {
                '기업명': comp_name_formatted,
                '현재주가': price_str,
                '시가총액': market_cap_str,
                '시장점유율': market_share_str,
                '영업이익률': margin_str,
                'PER': per_str
            }
        }

    except Exception as e:
        print(f"⚠️ {ticker} 데이터 호출 실패: {e}")
        return {'status': 'error'}


def get_top5_peers_by_sector(search_ticker, df_master):
    target_info = df_master[df_master['Ticker'] == search_ticker]
    sector = target_info['Sector'].values[0] if not target_info.empty else "Technology"

    top5_dict = {
        "Technology": ["MSFT", "AAPL", "NVDA", "GOOGL", "AMZN"],
        "Healthcare": ["LLY", "UNH", "JNJ", "MRK", "ABBV"],
        "Financials": ["BRK-B", "JPM", "V", "MA", "BAC"],
        "Consumer Cyclical": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
        "Communication Services": ["GOOGL", "META", "NFLX", "DIS", "CMCSA"],
        "Consumer Defensive": ["WMT", "PG", "COST", "KO", "PEP"],
        "Energy": ["XOM", "CVX", "COP", "EOG", "SLB"],
        "Industrials": ["CAT", "GE", "UNP", "RTX", "HON"],
        "Utilities": ["NEE", "SO", "DUK", "CEG", "SRE"],
        "Real Estate": ["PLD", "AMT", "EQIX", "WELL", "PSA"],
        "Basic Materials": ["LIN", "SHW", "FCX", "ECL", "NEM"]
        # 필요하다면 다른 섹터도 추가 가능!
    }

    top5_tickers = top5_dict.get(sector, ["MSFT", "AAPL", "NVDA", "GOOGL", "AMZN"])

    if search_ticker in top5_tickers:
        top5_tickers.remove(search_ticker)

    return top5_tickers[:5]

# ==========================================
# 1. 기본 화면 설정 및 웹 브라우저 최적화 CSS
# ==========================================
st.set_page_config(page_title="Pocket Buffett", layout="wide")

global_css = """
<style>
/* 📱 1. 전체 바깥 배경은 어둡게 */
[data-testid="stAppViewContainer"] { background-color: #f0f2f6; }
[data-testid="stMain"] { background-color: #ffffff; box-shadow: 0px 0px 20px rgba(0,0,0,0.1); }
.block-container { padding-top: 2rem !important; padding-bottom: 10rem !important; max-width: 100% !important; font-family: 'Pretendard', sans-serif; }
[data-testid="stHeader"], footer { visibility: hidden; }

/* 💬 검색창 멘트 및 글래스모피즘 효과 */
[data-testid="stSelectbox"] input::placeholder { font-size: 11px !important; color: #999 !important; }
[data-baseweb="select"] > div { background-color: rgba(0, 31, 91, 0.03) !important; backdrop-filter: blur(12px) !important; -webkit-backdrop-filter: blur(12px) !important; border: 1px solid rgba(212, 175, 55, 0.5) !important; border-radius: 16px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important; transition: all 0.3s ease; }
[data-baseweb="select"] > div:hover { border-color: #001f5b !important; box-shadow: 0 6px 20px rgba(0, 31, 91, 0.15) !important; }

/* 🔥 미국 시장 거래량 Top 5 리스트 UI */
.glass-panel { max-width: 350px; margin: 0 auto; background: linear-gradient(135deg, #001f5b 0%, #000a1f 100%); border-radius: 24px; padding: 30px; box-shadow: 0 20px 40px rgba(0, 31, 91, 0.25); position: relative; overflow: hidden; }
.glass-panel::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(212,175,55,0.15) 0%, transparent 60%); pointer-events: none; }
.glass-title { text-align: center; font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 25px; letter-spacing: 1px; }
.glass-item { display: flex; align-items: center; justify-content: center; padding: 16px 20px; margin-bottom: 10px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; backdrop-filter: blur(8px); transition: all 0.3s ease; cursor: pointer; }
.glass-item:hover { background: rgba(212, 175, 55, 0.15); border-color: rgba(212, 175, 55, 0.5); transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
.glass-rank { font-weight: 900; color: #D4AF37; width: 30px; font-size: 18px; font-style: italic; text-align: right; margin-right: 15px; }
.glass-ticker { font-weight: 800; color: #ffffff; width: 60px; font-size: 16px; text-align: left; margin-right: 15px; }
.glass-name { color: rgba(255,255,255,0.6); font-size: 14px; font-weight: 500; width: 70px; text-align: left; }

/* 💡 상단 지표 영역 */
.ticker-col { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 90px; }
.metric-label { font-size: 14px; color: #555; font-weight: bold; margin-bottom: 5px; }
.metric-value { font-size: 32px; font-weight: bold; color: #111; }

/* 🚦 신호등 클릭 팝업 */
.traffic-toggle { display: none; }
.traffic-popup { display: none; position: absolute; top: 50%; left: 100%; transform: translateY(-50%); margin-left: 20px; width: 280px; background-color: #fff; border-radius: 12px; padding: 20px; box-shadow: 0px 8px 25px rgba(0,0,0,0.15); z-index: 10000; text-align: left; }
.traffic-toggle:checked ~ .traffic-popup { display: block; animation: fade-in 0.2s; }

/* ⚡ 우측 하단 플로팅 팝업 */
.fab-wrapper { position: fixed; bottom: 40px; right: 40px; z-index: 9999; }
.alert-toggle { display: none; }
.lightning-fab { cursor: pointer; transition: transform 0.2s; font-size: 40px;filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.3)); display: inline-block;}
.lightning-fab:hover { transform: scale(1.15); }
.fab-label { display: none; } /* CSS로도 한 번 더 숨김 */

/*  팝업창 (토글) */
.floating-alert {display: none; position: absolute; bottom: 60px; right: 0; width: 300px;background-color: #fff; border: 2px solid #ff4b4b; border-radius: 10px;padding: 15px; box-shadow: 0px 8px 20px rgba(0,0,0,0.15);}
.alert-toggle:checked ~ .floating-alert { display: block; animation: fade-in 0.2s; }
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.close-btn { position: absolute; top: 10px; right: 12px; font-size: 18px; font-weight: bold; cursor: pointer; color: #999; }
.alert-title { color: #ff4b4b; font-weight: bold; font-size: 15px; margin-bottom: 5px; }
/* 🎯 결과 지표 카드 */
.result { background: linear-gradient(145deg, #ffffff 0%, #fffbf0 100%); border: 1px solid #f0e6d2; border-bottom: 6px solid #D4AF37; border-right: 2px solid #e6d5b8; border-radius: 16px; padding: 20px 25px; box-shadow: 0 10px 20px rgba(212, 175, 55, 0.15), 0 4px 8px rgba(0,0,0,0.05); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.result:hover { transform: translateY(-4px); box-shadow: 0 15px 25px rgba(212, 175, 55, 0.25), 0 6px 12px rgba(0,0,0,0.1); }
.result-label { font-size: 16px; font-weight: bold; color: #665b45; margin-bottom: 5px; }
.result-value { font-size: 42px; font-weight: 900; color: #001f5b; text-shadow: 1px 1px 2px rgba(0,0,0,0.05); line-height: 1.2; }
.result-delta { font-size: 15px; font-weight: bold; margin-top: 5px; }

/* 칩 버튼 디자인 */
.peer-chip { background-color: #001f5b; color: white; padding: 12px 20px; border-radius: 30px; font-weight: bold; font-size: 13px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); cursor: pointer; display: inline-block; transition: 0.2s; }
.peer-chip:hover { transform: translateY(-3px); }
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)

# ==========================================
# 2. 메인 UI
# ==========================================
logo_col1, logo_col2, logo_col3 = st.columns([1, 6, 1])

with logo_col2:
    try:
        with open("logo.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(f"""
        <div style="text-align: center;">
            <a href="/" target="_self">
                <img src="data:image/png;base64,{encoded_string}" style="width: 100%; max-width: 400px; cursor: pointer;">
            </a>
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <a href="/" target="_self" style="text-decoration: none;">
            <h3 style='text-align: center; color: #001f5b; cursor: pointer;'>Pocket Buffett</h3>
        </a>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# 💡 [핵심] Streamlit 캐시를 사용하여 파일을 딱 한 번만 읽고 메모리에 저장 (속도 최적화)
@st.cache_data(show_spinner=False)
def load_company_data():
    """
    직접 구축한 매핑 CSV 파일을 읽어와서 검색창용 딕셔너리와 섹터 데이터프레임으로 변환합니다.
    """
    try:
        # 💡 [핵심 해결] 현재 파이썬 파일(main.py)이 있는 정확한 폴더 위치를 추적합니다!
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "nasdaq_nyse_list_with_sectors.csv")

        # 이름만 적는 대신, 방금 만든 정확한 'file_path'를 사용해 파일을 엽니다.
        df = pd.read_csv(file_path, encoding='utf-8-sig')

        # 결측치(NaN)가 있으면 빈 문자열로 처리
        df = df.fillna("")

        mapping_dict = {}
        for _, row in df.iterrows():
            ticker = str(row['Ticker']).strip().upper()
            eng_name = str(row['EnglishName']).strip()
            kor_name = str(row['KoreanName']).strip()

            # "AAPL - Apple (애플)" 형태로 예쁘게 조합
            if kor_name and kor_name != eng_name:
                mapping_dict[ticker] = f"{ticker} - {eng_name} ({kor_name})"
            else:
                mapping_dict[ticker] = f"{ticker} - {eng_name}"

        return mapping_dict, df

    except FileNotFoundError:
        st.error("🚨 매핑 데이터 파일('nasdaq_nyse_list_with_sectors.csv')을 찾을 수 없습니다.")
        # 에러 발생 시 앱이 터지지 않도록 임시 데이터 반환
        temp_df = pd.DataFrame([{"Ticker": "AAPL", "EnglishName": "Apple", "KoreanName": "애플", "Sector": "Technology"}])
        return {"AAPL": "AAPL - Apple (애플)"}, temp_df
    except Exception as e:
        st.error(f"🚨 데이터 로드 중 알 수 없는 오류 발생: {e}")
        return {}, pd.DataFrame()

company_dict, df_master = load_company_data()


col_char, col_search, col_top5 = st.columns([2, 5, 3])

with col_char:
    try:
        with open("buffett.png", "rb") as image_file:
            encoded_buffett = base64.b64encode(image_file.read()).decode()
        st.markdown(f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{encoded_buffett}" style="width: 70%;">
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown(
            "<div style='text-align:center; background:#eee; color:#999; font-size:11px; font-weight:bold;'>캐릭터</div>",
            unsafe_allow_html=True)

# ==========================================
# 💡 [핵심 해결] URL 명령 처리 (삭제 & 검색)
# 메인 검색창(st.selectbox)이 나오기 전, 위쪽에 배치되어야 합니다!
# ==========================================
if "del_peer" in st.query_params:
    st.session_state["pending_delete"] = st.query_params.get("del_peer")

if "ticker" in st.query_params:
    url_ticker = st.query_params.get("ticker")
    if url_ticker in company_dict:
        st.session_state["search_box_key"] = url_ticker

st.query_params.clear()


with col_search:
    search_ticker = st.selectbox(
        "🔍 검색",
        options=list(company_dict.keys()),
        format_func=lambda x: company_dict[x],
        key="search_box_key",
        index=None,
        placeholder="어떤 기업의 내재가치를 분석해볼까요?",
        label_visibility="collapsed"
    )

if not search_ticker:
    with col_top5:
        top5_data, is_fallback = fetch_realtime_top5_volume()
        status_badge = "<span style='font-size: 11px; font-weight: normal; color: #ff9800; margin-left: 5px;'>🟡 오프라인</span>" if is_fallback else "<span style='font-size: 11px; font-weight: normal; color: #4caf50; margin-left: 5px;'>🟢 실시간</span>"

        html_items = "".join([
                                 f'<div class="glass-item"><div class="glass-rank">{item["rank"]}</div><div class="glass-ticker">{item["ticker"]}</div><div class="glass-name">{item["name"]}</div></div>'
                                 for item in top5_data])

        st.markdown(f"""
        <div class="glass-panel">
            <div class="glass-title">미국 시장 거래량 Top 5 🔥 {status_badge}</div>
            {html_items}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. 분석 결과 화면
# ==========================================
if search_ticker:
    with st.spinner(f"데이터를 불러오는 중입니다..."):
        data = fetch_company_data(search_ticker)

    if data["status"] == "success":
        col1, col2 = st.columns(2)

        with col1:
            main_realtime_data = fetch_single_competitor(search_ticker)
            if main_realtime_data.get('status') == 'success':
                real_price = main_realtime_data['data']['현재주가']
            else:
                real_price = "-"

            # 3. 💡 기존의 예쁜 UI 디자인 안에 진짜 데이터(real_price)  수정 필요
            st.markdown(f"""
            <div class="ticker-col">
                <div class="metric-label">💰 현재주가</div>
                <div class="metric-value">${data['current_price']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

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

            html_str = f"""
<div class="ticker-col" style="flex-direction: row; gap: 20px;">
<div style="display: flex; flex-direction: column; align-items: flex-end;">
<div class="metric-label" style="margin-bottom: 5px;">🚦 AI 적정가</div>
<div class="metric-value">${data['ai_fair_value']:.2f}</div>
</div>

<div style="position: relative; display: flex; align-items: center;">
<label for="toggle-traffic" style="background-color: {traffic_color}; display: block; width: 60px; height: 60px; border-radius: 50%; cursor: pointer; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.3)); transition: transform 0.2s;"></label>
<input type="checkbox" id="toggle-traffic" class="traffic-toggle">

<div class="traffic-popup" style="border: 3px solid {traffic_color};">
<label for="toggle-traffic" class="close-btn" style="color: #999; top: 12px; right: 15px; font-size: 22px;">&times;</label>
<div style="color: {traffic_color}; font-weight: bold; font-size: 16px; margin-bottom: 8px;">{popup_title}</div>
<div style="font-size: 14px; color: #444; line-height: 1.5;">{popup_msg}</div>
</div>
</div>
</div>
"""
            st.markdown(html_str, unsafe_allow_html=True)

        with st.spinner('포켓 버핏 AI가 10-K, 10-Q 공시 원문을 분석하고 있습니다...'):
            analysis_data = fetch_analysis_data(search_ticker)
        r_year = analysis_data['report_year']
        r_quarter = analysis_data['report_quarter']
        r_type = analysis_data['report_type']

        report_name = "분기보고서" if r_type == "10-Q" else "연례보고서"

        st.caption(f"📅 **데이터 기준:** {r_year}년 {r_quarter}분기 {r_type} {report_name} 실적 반영 완료")
        st.markdown("<hr style='margin: 5px 0px 5px 0px;'>", unsafe_allow_html=True)

        st.markdown("""
<style>
div[data-baseweb="tab-list"] { display: flex; width: 100%; gap: 8px; }
div[data-baseweb="tab-list"] button { flex: 1; justify-content: center; padding: 16px 0px; font-size: 17px; font-weight: 700; background-color: #f8f9fa; border: 1px solid #ddd; border-bottom: none; border-radius: 8px 8px 0 0; transition: all 0.2s ease-in-out; }
div[data-baseweb="tab-list"] button[aria-selected="true"] { background-color: #001f5b !important; color: white !important; border-color: #001f5b !important; }
div[data-baseweb="tab-highlight"] { background-color: #FFC107 !important; }                    
</style>
""", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["📑 AI 공시 요약", "🔎 AI 분석 시그널", "🧮 MY DCF", "📊 경쟁사 비교"])

        with tab1:
            st.markdown(
"""<style>.pop-t1{display:none;} #chk-t1:checked + .pop-t1{display:block; animation:fade-in 0.2s;}</style>
<div style="position:relative; margin-bottom:1rem;">
<div style="display:flex; align-items:center; gap:8px;">
<h3 style="margin:0; font-size:1.25rem; font-weight:600; color:#31333F;">📑 핵심 비즈니스 모델 요약</h3>
<label for="chk-t1" style="width:18px; height:18px; border-radius:50%; background:#ddd; color:#555; text-align:center; font-size:12px; font-weight:bold; cursor:pointer; line-height:18px;">i</label>
</div>
<input type="checkbox" id="chk-t1" style="display:none;">
<div class="pop-t1" style="position:absolute; top:35px; left:270px; width:320px; background:#fff; border:1px solid #eee; border-radius:12px; padding:20px; box-shadow:0 8px 25px rgba(0,0,0,0.15); z-index:10000; font-size:13px; color:#555; line-height:1.5;">
<label for="chk-t1" style="position:absolute; top:10px; right:15px; font-size:20px; cursor:pointer; color:#aaa;">&times;</label>
<b style="color:#001f5b; font-size:14px;">⚖️ 면책 조항 (Disclaimer)</b><br><br>본 자료는 SEC 공시(10-K/Q)의 AI 요약본으로 내용의 축약이나 누락이 있을 수 있습니다. 정확한 사실관계는 반드시 SEC 원문을 대조하여 확인해 주십시오.
</div>
</div>""", unsafe_allow_html=True)
            st.info(f"💡 **통합 요약:** {analysis_data['briefing_summary']}")

            with st.expander("▶ 주요 비즈니스 모델 (10-K 기준)"):
                for item in analysis_data['business_model_10k']:
                    st.write(f"* {item}")

            with st.expander("▶ 최근 분기 업데이트 (10-Q 기준)"):
                for item in analysis_data['recent_update_10q']:
                    st.write(f"* {item}")

            # 💡 [핵심] 긴급 공시 8-K 조건부 렌더링
            if analysis_data['emergency_8k']['has_issue']:
                header_text = "⚡ 긴급 공시 8-K"
                main_text = analysis_data['emergency_8k']['title']
                st.markdown(f"""
                <div class="fab-wrapper">
                    <input type="checkbox" id="toggle-8k" class="alert-toggle">
                    <div class="floating-alert">
                        <label for="toggle-8k" class="close-btn">&times;</label>
                        <div class="alert-title">{header_text}</div>
                        <div style="color: #000; font-weight: bold; font-size: 15px; margin-top: 5px; margin-bottom: 10px; line-height: 1.4; word-break: keep-all;">
                            {main_text}
                        </div>
                        <div style="font-size: 13px; color: #444;margin-bottom: 5px;">{analysis_data['emergency_8k']['issue_date']}</div>
                        <div style="font-size: 13px; color: #444; line-height: 1.6;">{analysis_data['emergency_8k']['description']}</div>
                   </div>
                    <label for="toggle-8k" class="lightning-fab">
                        <div class="fab-label">8-K 팝업</div>
                        <div class="lightning-icon">⚡</div>
                    </label>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            st.markdown(
"""<style>.pop-t2{display:none;} #chk-t2:checked + .pop-t2{display:block; animation:fade-in 0.2s;}</style>
<div style="position:relative; margin-bottom:1rem;">
<div style="display:flex; align-items:center; gap:8px;">
<h3 style="margin:0; font-size:1.25rem; font-weight:600; color:#31333F;">🔎 AI 분석 시그널</h3>
<label for="chk-t2" style="width:18px; height:18px; border-radius:50%; background:#ddd; color:#555; text-align:center; font-size:12px; font-weight:bold; cursor:pointer; line-height:18px;">i</label>
</div>
<input type="checkbox" id="chk-t2" style="display:none;">
<div class="pop-t2" style="position:absolute; top:35px; left:190px; width:320px; background:#fff; border:1px solid #eee; border-radius:12px; padding:20px; box-shadow:0 8px 25px rgba(0,0,0,0.15); z-index:10000; font-size:13px; color:#555; line-height:1.5;">
<label for="chk-t2" style="position:absolute; top:10px; right:15px; font-size:20px; cursor:pointer; color:#aaa;">&times;</label>
<b style="color:#001f5b; font-size:14px;">⚖️ 면책 조항 (Disclaimer)</b><br><br>AI 요약은 과거 공시 텍스트 기반의 참고용 정보입니다. 예기치 못한 시장 변수를 모두 반영하지 않으며, 특정 종목에 대한 투자 권유를 의미하지 않습니다.
</div>
</div>""", unsafe_allow_html=True)

            st.markdown('<style>div[data-testid="stAlert"] { word-break: keep-all; }</style>', unsafe_allow_html=True)
            pos_text = "\n".join([f"* {item}" for item in analysis_data['positive_signals']])
            st.success(f"**🟢 AI가 찾은 긍정 시그널**\n{pos_text}")

            neg_text = "\n".join([f"* {item}" for item in analysis_data['negative_signals']])
            st.error(f"**🚨 AI가 발견한 위기 시그널**\n{neg_text}")

        with tab3:
            st.markdown(
"""<style>.pop-t3{display:none;} #chk-t3:checked + .pop-t3{display:block; animation:fade-in 0.2s;}</style>
 <div style="position:relative; margin-bottom:1rem;">
<div style="display:flex; align-items:center; gap:8px;">
<h3 style="margin:0; font-size:1.25rem; font-weight:600; color:#31333F;">📈DCF 시뮬레이션 차트</h3>
<label for="chk-t3" style="width:18px; height:18px; border-radius:50%; background:#ddd; color:#555; text-align:center; font-size:12px; font-weight:bold; cursor:pointer; line-height:18px;">i</label>
</div>
<input type="checkbox" id="chk-t3" style="display:none;">
<div class="pop-t3" style="position:absolute; top:35px; left:250px; width:320px; background:#fff; border:1px solid #eee; border-radius:12px; padding:20px; box-shadow:0 8px 25px rgba(0,0,0,0.15); z-index:10000; font-size:13px; color:#555; line-height:1.5;">
<label for="chk-t3" style="position:absolute; top:10px; right:15px; font-size:20px; cursor:pointer; color:#aaa;">&times;</label>
<b style="color:#001f5b; font-size:14px;">⚖️ 면책 조항 (Disclaimer)</b><br><br>시뮬레이터의 결괏값은 DCF 공식에 대입한 이론적 수치입니다. 미래 주가나 실제 가치를 보장하지 않으므로 투자 판단의 보조 지표로만 활용해 주십시오.
</div>""", unsafe_allow_html=True)
            st.caption("※ 최신 분기(10-Q)의 잉여현금흐름(FCF) 데이터를 기반으로 기본 파라미터가 보정되었습니다.")

            current_price = data['current_price']
            with st.spinner("장기 투자 시나리오 데이터를 불러오는 중입니다..."):
                dcf_data = fetch_dcf_data(search_ticker, current_price)
            base_growth = float(dcf_data['dcf_base_growth'])
            base_margin = int(dcf_data['dcf_base_margin'])

            top_chart_area = st.container()
            st.markdown("<hr style='margin: 15px 0px 15px 0px;'>", unsafe_allow_html=True)

            header_col, period_col = st.columns([7, 3])
            with header_col:
                st.markdown("##### 🔮 나의 투자 시나리오 만들기")
            with period_col:
                invest_period = st.number_input("계획중인 투자기간 (년)", min_value=1, max_value=30, value=5, step=1)

            slider_col1, slider_col2 = st.columns(2)

            with slider_col1:
                st.markdown(
                    f"<div style='word-break: keep-all; margin-top: 15px;'><b>💡 1. 향후 {invest_period}년 동안, 이 기업의 매출은 지금보다 몇 배나 더 커질까요?</b></div>",
                    unsafe_allow_html=True)
                growth_multiple = st.slider("예상 기업 성장 규모", min_value=0.5, max_value=3.0, value=base_growth, step=0.1,
                                            label_visibility="collapsed")
                st.markdown(f"""
                    <div style='position: relative; font-size: 12px; font-weight: bold; color: #555; margin-top: -15px; height: 25px; white-space: nowrap;'>
                        <span style='position: absolute; left: 0%;'>📉 0.5배</span>
                        <span style='position: absolute; left: 20%; transform: translateX(-25%);'>🐢 1.0배</span>
                        <span style='position: absolute; left: 40%; transform: translateX(-50%);'>🚶‍♂️ 1.5배</span>
                        <span style='position: absolute; left: 60%; transform: translateX(-66%);'>🏃‍♂️ 2.0배</span>
                        <span style='position: absolute; left: 100%; transform: translateX(-100%);'>🚀 3.0배(Max)</span>
                    </div>
                    """, unsafe_allow_html=True)
                with st.expander("성장규모 슬라이더 가이드"):
                    st.caption("""
                        🤖 **AI 예측:** 최근 트렌드를 종합할 때 설정된 기간 내 성장을 예측합니다.

                        * **📉 0.5배:** 역성장 위기 기업
                        * **🐢 1.0배:** 성숙기 현상 유지 기업
                        * **🚶‍♂️ 1.0~1.5배:** 안정형 우량 기업        
                        * **🏃‍♂️ 1.5~2.0배:** 우량 성장주
                        * **🚀 2.0배 이상:** 폭발적 성장 주도주
                    """)

            with slider_col2:
                st.markdown(
                    f"<div style='word-break: keep-all; margin-top: 15px;'><b>💡 2. 향후 {invest_period}년 동안, 이 기업은 매출 대비 얼마나 많은 이익을 남길 수 있을까요?</b></div>",
                    unsafe_allow_html=True)
                margin_rate = st.slider("예상 영업이익률 (%)", min_value=0, max_value=50, value=28, step=1,
                                        label_visibility="collapsed")
                st.markdown("""
                    <div style='position: relative; font-size: 12px; font-weight: bold; color: #555; margin-top: -15px; height: 25px; white-space: nowrap;'>
                        <span style='position: absolute; left: 0%;'>📉 평균 이하</span>
                        <span style='position: absolute; left: 50%; transform: translateX(-50%);'>➖ 평균(20%)</span>
                        <span style='position: absolute; left: 100%; transform: translateX(-100%);'>🥇 초과 수익</span>
                    </div>
                    """, unsafe_allow_html=True)
                with st.expander("영업이익률 슬라이더 가이드"):
                    st.caption("""
                    🤖 **AI 예측:** 경쟁 우위를 바탕으로 설정된 기간 동안 유지 가능한 마진율을 예측합니다.
                    * **📉 평균 이하:** 동종업계 경쟁사들보다 수익성이 낮을 때
                    * **➖ 업계 평균:** 표준적인 수익성을 방어할 때
                    * **🥇 초과 수익:** 경쟁사들보다 월등히 높은 마진을 남길 때
                    """)

            base_value = data['ai_fair_value']
            target_ratio = (growth_multiple / base_growth) * (1 + (margin_rate - base_margin) / 100)
            simulated_price = base_value * target_ratio

            implied_cagr = (target_ratio ** (1 / invest_period)) - 1
            if implied_cagr < 0.07:
                difficulty_text = "시장 평균 수준의 평범한 기업도 달성 가능한"
            elif implied_cagr < 0.15:
                difficulty_text = "상위 20% 이내의 탄탄한 우량주들만 해내는"
            else:
                difficulty_text = "최상위 1% 혁신 기업만이 보여주는"

            chart_cagr = (simulated_price / current_price) ** (1 / invest_period) - 1


            def generate_future_curve(start_price, end_price, cagr, years, num_points=50):
                curved_prices = start_price * ((1 + cagr) ** np.linspace(0, years, num_points))
                curved_prices[-1] = end_price
                return curved_prices


            # [UI 렌더링 영역]
            with top_chart_area:
                chart_col, metric_col = st.columns([5, 5])
                all_past_prices = dcf_data['historical_prices']
                months_needed = invest_period * 12
                # [핵심] 파이썬 리스트 슬라이싱: 뒤에서부터 필요한 개수만큼만 잘라냅니다.
                past_prices = all_past_prices[-months_needed:]
                future_prices = generate_future_curve(current_price, simulated_price, chart_cagr, invest_period)
                current_x = 5
                future_x = 10
                past_x = np.linspace(0, current_x, len(past_prices))
                future_x_array = np.linspace(current_x, future_x, len(future_prices))

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=past_x, y=past_prices, mode='lines', name='과거 주가',
                                         line=dict(color='#a0aec0', width=1.5, shape='spline', smoothing=0.5),
                                         opacity=0.8))
                fig.add_hline(y=base_value, line_dash="dash", line_color="green",
                              annotation_text=f"AI 적정가 (${base_value:.2f})")
                fig.add_trace(go.Scatter(x=future_x_array, y=future_prices, mode='lines', name='예상 경로',
                                         line=dict(color='black', dash='dash', width=2, shape='spline', smoothing=0.3)))
                fig.add_trace(
                    go.Scatter(x=[current_x], y=[current_price], mode='markers', name=f'현재가 (${current_price:.2f})',
                               marker=dict(color='blue', size=10)))
                fig.add_trace(go.Scatter(x=[future_x], y=[simulated_price], mode='markers', name='나만의 예상가',
                                         marker=dict(color='gold', size=14, line=dict(color='black', width=1))))

                fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), showlegend=True,
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                  xaxis=dict(tickmode='array', tickvals=[2.5, 5, 10],
                                             ticktext=[f'최근 {invest_period}년 흐름', '현재', f'향후 {invest_period}년'],

                                             showgrid=False, zeroline=False),
                                  yaxis=dict(showgrid=True, gridcolor='#f0f0f0'))

                with chart_col: st.plotly_chart(fig, use_container_width=True)

                with metric_col:
                    st.markdown("<div style='margin-top:-10px;'></div>", unsafe_allow_html=True)
                    _, inner_col = st.columns([1, 9])
                    with inner_col:
                        delta_pct = (simulated_price - current_price) / current_price * 100
                        delta_color, delta_arrow = ("#09ab3b", "↑") if delta_pct >= 0 else ("#ff2b2b", "↓")

                        st.markdown(f"""
                        <div class="result"><div class="result-label">🎯 나만의 예상 적정주가</div><div class="result-value">${simulated_price:.2f}</div><div class="result-delta" style="color: {delta_color}; font-weight: bold;">{delta_arrow} 현재가 대비 {abs(delta_pct):.1f}%</div><div style="font-size: 13px; color: #666; margin-top: 15px; padding-top: 15px; border-top: 1px dashed #e6d5b8; word-break: keep-all; line-height: 1.5;">💡 <b>포켓 버핏 분석:</b> 미국 주식시장 기준, 이 시나리오는 <span style='color: #D4AF37; font-weight: bold;'>{difficulty_text}</span> 난이도의 투자 시나리오입니다.</div></div>
                        """, unsafe_allow_html=True)

            # ------------------------------------------
            # [탭 4] 경쟁사
            # ------------------------------------------
            with tab4:
                st.markdown("""
<style>.pop-t4{display:none;} #chk-t4:checked + .pop-t4{display:block; animation:fade-in 0.2s;}</style>
<div style="position:relative; margin-bottom:1rem;">
<div style="display:flex; align-items:center; gap:8px;">
<h3 style="margin:0; font-size:1.25rem; font-weight:600; color:#31333F;">📊 경쟁사 비교분석표</h3>
<label for="chk-t4" style="width:18px; height:18px; border-radius:50%; background:#ddd; color:#555; text-align:center; font-size:12px; font-weight:bold; cursor:pointer; line-height:18px;">i</label>
</div>
<input type="checkbox" id="chk-t4" style="display:none;">
<div class="pop-t4" style="position:absolute; top:35px; left:230px; width:300px; background:#fff; border:1px solid #eee; border-radius:12px; padding:20px; box-shadow:0 8px 25px rgba(0,0,0,0.15); z-index:10000; font-size:13px; color:#555; line-height:1.5;">
<label for="chk-t4" style="position:absolute; top:10px; right:15px; font-size:20px; cursor:pointer; color:#aaa;">&times;</label>
<b style="color:#001f5b; font-size:14px;">⚖️ 면책 조항 (Disclaimer)</b><br><br>동종업계 재무 비율은 회계 기준에 따라 오차가 있을 수 있습니다. 모든 투자의 판단과 책임은 본인에게 있습니다.
</div>
</div>
                """, unsafe_allow_html=True)

                if 'peer_data' in data:
                    # [로직 1] 최초 검색 시 (또는 종목을 바꿨을 때) 세션 초기화 및 실시간 데이터 로드
                    if "current_search_ticker" not in st.session_state or st.session_state.current_search_ticker != search_ticker:
                        st.session_state.current_search_ticker = search_ticker

                        with st.spinner("📊 동종 섹터 대장주 데이터를 실시간으로 불러오는 중입니다... (약 2~4초 소요)"):
                            # 1. 상위 5개 티커 명단 가져오기
                            peer_tickers = get_top5_peers_by_sector(search_ticker, df_master)

                            # 💡 [핵심 해결] 메인 종목 자기 자신도 실시간 데이터를 가져오도록 명단 맨 앞에 합쳐줍니다!
                            tickers_to_fetch = [search_ticker] + peer_tickers

                            real_peer_data = []
                            # 2. 메인 종목 + 경쟁사들의 진짜 수치를 야후 파이낸스에서 실시간으로 긁어오기
                            for p_ticker in tickers_to_fetch:
                                res = fetch_single_competitor(p_ticker)
                                if res.get('status') == 'success':
                                    real_peer_data.append(res['data'])

                            # 3. 긁어온 진짜 데이터를 Streamlit 메모리에 영구 저장!
                            if real_peer_data:
                                st.session_state.peer_dataframe = pd.DataFrame(real_peer_data)
                            else:
                                st.session_state.peer_dataframe = pd.DataFrame(
                                    columns=["기업명", "현재주가", "시가총액", "시장점유율", "영업이익률", "PER"])

                        # 💡 [신규] 섹터 정보 한글 변환 및 문구 출력
                        target_row = df_master[df_master['Ticker'] == search_ticker]
                        if not target_row.empty:
                            raw_sector = target_row['Sector'].values[0]
                            kor_company_name = target_row['KoreanName'].values[0]

                        # 영문 섹터명 -> 한글 매핑 딕셔너리
                        sector_kor_map = {
                            "Technology": "기술",
                            "Consumer Cyclical": "경기 소비재",
                            "Communication Services": "통신 서비스",
                            "Consumer Defensive": "필수 소비재",
                            "Financial Services": "금융 서비스",
                            "Healthcare": "헬스케어",
                            "Industrials": "산업재",
                            "Real Estate": "부동산",
                            "Basic Materials": "원자재",
                            "Energy": "에너지",
                            "Utilities": "유틸리티"
                        }

                        # 매핑값이 없으면 원문(Unknown 등)을 그대로 표시
                        kor_sector = sector_kor_map.get(raw_sector, raw_sector)

                        st.markdown(f"""
                                           <div style="margin-top: 20px; margin-bottom: 10px; padding: 12px 15px; background-color: #f8f9fa; border-left: 5px solid #001f5b; border-radius: 4px;">
                                               <span style="font-size: 15px; color: #333;">
                                                   🏢 <b>{kor_company_name}</b>은(는) <b style="color: #001f5b;">{kor_sector}</b> 섹터에 해당합니다.
                                               </span>
                                           </div>
                                       """, unsafe_allow_html=True)


                    # [로직 2] 기업 추가 콜백 함수 (화면 깜빡임 없음)
                    def add_competitor_callback():
                        new_ticker = st.session_state.get("tab4_search_box")
                        if new_ticker:
                            new_comp_data = fetch_single_competitor(new_ticker)
                            if new_comp_data.get('status') == 'success':
                                new_row_df = pd.DataFrame([new_comp_data['data']])
                                st.session_state.peer_dataframe = pd.concat(
                                    [st.session_state.peer_dataframe, new_row_df], ignore_index=True)
                                st.session_state.tab4_search_box = None
                            else:
                                st.toast("데이터를 가져오지 못했습니다.", icon="🚨")
                        else:
                            st.toast("추가할 기업을 먼저 검색해 주세요.", icon="⚠️")


                    # 💡 [로직 3 - 신규] 기업 삭제 콜백 함수 (새로고침 없이 메모리에서만 삭제!)
                    def delete_competitor_callback(target_ticker):
                        df = st.session_state.peer_dataframe
                        st.session_state.peer_dataframe = df[
                            ~df['기업명'].str.contains(f"\\({target_ticker}\\)", regex=True, na=False)]


                    # UI: 추가 검색창
                    st.markdown(
                        "<div style='margin-top: 15px; margin-bottom: 5px; font-weight: bold; color: #555; font-size: 14px;'>🔍 추가하고 싶은 경쟁사 티커를 입력하세요.</div>",
                        unsafe_allow_html=True)
                    add_col1, add_col2 = st.columns([7, 3])
                    with add_col1:
                        st.selectbox("경쟁사 검색", options=list(company_dict.keys()),
                                     format_func=lambda x: company_dict[x], key="tab4_search_box", index=None,
                                     placeholder="추가할 기업 검색 (티커, 한글명, 영문명)", label_visibility="collapsed")
                    with add_col2:
                        st.button("➕ 비교 기업 추가", on_click=add_competitor_callback, use_container_width=True)

                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

                    # ==========================================
                    # 💡 [핵심 구현] Streamlit 네이티브 UI로 그리는 모던 데이터 테이블
                    # ==========================================

                    df_temp = st.session_state.peer_dataframe.copy()

                    # 💡 [원인 해결] 표 안에 메인 종목이 아예 없는 경우를 대비해 첫 줄을 직접 만들어줍니다!
                    is_main = df_temp['기업명'].str.contains(f"\\({search_ticker}\\)", regex=True)

                    if not is_main.any():
                        # 데이터프레임에 기준 종목이 없다면 상단(Overview) 데이터를 활용해 강제로 맨 위에 끼워 넣습니다.
                        # (시가총액, PER 등은 overview 데이터에 없다면 임시로 '-' 처리)
                        main_row = pd.DataFrame([{
                            "기업명": f"{data.get('company_name', search_ticker)} ({search_ticker})",
                            "현재주가": f"${data.get('current_price', 0):.2f}",
                            "시가총액": "-",  # 나중에 백엔드 API에 본인 데이터가 추가되면 연동하세요.
                            "시장점유율": "-",
                            "영업이익률": "-",
                            "PER": "-"
                        }])
                        df_display = pd.concat([main_row, df_temp], ignore_index=True)
                    else:
                        # 표 안에 이미 있다면 기존 코드대로 맨 위로 끌어올리기만 합니다.
                        df_main = df_temp[is_main]
                        df_others = df_temp[~is_main]
                        df_display = pd.concat([df_main, df_others], ignore_index=True)

                    # 2. 커스텀 표 헤더 렌더링
                    headers = ["기업명", "현재주가", "시가총액", "시장점유율", "영업이익률", "PER", "삭제"]
                    header_cols = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.8])
                    for i, title in enumerate(headers):
                        header_cols[i].markdown(
                            f"<div style='font-size:13px; font-weight:bold; color:#333; text-align:center; padding-bottom:10px; border-bottom:2px solid #ddd;'>{title}</div>",
                            unsafe_allow_html=True)

                    # 3. 데이터 행(Row) 반복 렌더링
                    for idx, row in df_display.iterrows():
                        cols = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.8])

                        # 티커 파싱
                        comp_name = str(row['기업명'])
                        # 💡 [핵심 해결] 괄호가 여러 개일 경우를 대비해 '모든 괄호'를 찾은 뒤 맨 마지막 것만 가져옵니다!
                        matches = re.findall(r'\((.*?)\)', comp_name)
                        ticker = matches[-1] if matches else ""

                        # 💡 디자인 차별화: 메인 종목은 진하고 굵게, 경쟁사는 회색빛으로 처리
                        font_weight = "900" if ticker == search_ticker else "normal"
                        text_color = "#111" if ticker == search_ticker else "#555"

                        if ticker:
                            display_name = f'<a href="/?ticker={ticker}" target="_self" style="color: #001f5b; font-weight: {font_weight}; text-decoration: underline; font-size:13px;">{comp_name}</a>'
                        else:
                            display_name = f'<span style="font-size:13px; font-weight: {font_weight};">{comp_name}</span>'

                        # 데이터 입력
                        cols[0].markdown(f"<div style='padding-top:12px; text-align:center;'>{display_name}</div>",
                                         unsafe_allow_html=True)
                        cols[1].markdown(
                            f"<div style='padding-top:12px; text-align:center; font-size:13px; font-weight:{font_weight}; color:{text_color};'>{row['현재주가']}</div>",
                            unsafe_allow_html=True)
                        cols[2].markdown(
                            f"<div style='padding-top:12px; text-align:center; font-size:13px; font-weight:{font_weight}; color:{text_color};'>{row['시가총액']}</div>",
                            unsafe_allow_html=True)
                        cols[3].markdown(
                            f"<div style='padding-top:12px; text-align:center; font-size:13px; font-weight:{font_weight}; color:{text_color};'>{row['시장점유율']}</div>",
                            unsafe_allow_html=True)
                        cols[4].markdown(
                            f"<div style='padding-top:12px; text-align:center; font-size:13px; font-weight:{font_weight}; color:{text_color};'>{row['영업이익률']}</div>",
                            unsafe_allow_html=True)
                        cols[5].markdown(
                            f"<div style='padding-top:12px; text-align:center; font-size:13px; font-weight:{font_weight}; color:{text_color};'>{row['PER']}</div>",
                            unsafe_allow_html=True)

                        # 4. 삭제 버튼 (기준 종목 보호)
                        with cols[6]:
                            if ticker != search_ticker:
                                # 💡 키(key) 충돌을 막기 위해 고유한 ticker를 키 이름에 사용했습니다.
                                st.button("✕", key=f"del_{ticker}_btn", on_click=delete_competitor_callback,
                                          args=(ticker,),
                                          help="목록에서 삭제", use_container_width=True)
                            else:
                                st.markdown(
                                    "<div style='padding-top:12px; text-align:center; font-size:13px; color:#ccc; font-weight:bold;'>-</div>",
                                    unsafe_allow_html=True)

                        # 행 구분선
                        st.markdown("<hr style='margin: 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

                    # 스타일 튜닝 (버튼 CSS)
                    st.markdown("""
                                       <style>
                                       div[data-testid="column"] button {
                                           background-color: transparent !important;
                                           border: none !important;
                                           color: #b0b0b0 !important;
                                           font-size: 14px !important;
                                           padding-top: 5px !important;
                                           transition: color 0.2s;
                                       }
                                       div[data-testid="column"] button:hover {
                                           color: #111111 !important;
                                       }
                                       </style>
                                       """, unsafe_allow_html=True)

                else:
                    st.error("기본 경쟁사 데이터를 불러올 수 없습니다.")

                st.markdown("""
                       <div style="text-align:center; margin-top: 25px;">
                           <a href="/" target="_self" style="text-decoration: none;">
                               <div class="peer-chip">👀 새로운 기업 검색하기 ➔</div>
                           </a>
                       </div>
                   """, unsafe_allow_html=True)
