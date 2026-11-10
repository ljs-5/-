import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. 웹 페이지 타이틀 설정
st.title("📈 미국 주식 실전 단타 및 리스크 진단 시스템")
st.write("실시간 시세, RSI 모멘텀, 볼린저 밴드 변동성, 그리고 자동 익절/손절선을 진단합니다.")

# 2. 사용자 입력 인터페이스 구성
col_in1, col_in2 = st.columns(2)
with col_in1:
    종목코드 = st.text_input("미국 주식 종목 코드 입력 (예: TSLA, AAPL, NVDA):", "NVDA")
    목표익절가 = st.number_input("희망 목표 익절가 ($):", min_value=0.0, value=140.0, step=1.0)
with col_in2:
    손절기준가 = st.number_input("긴급 청산 / 손절가 ($):", min_value=0.0, value=115.0, step=1.0)

# 3. 분석 실행 버튼
if st.button("실전 단타 지표 분석 시작"):
    try:
        # 지표 계산을 위해 최근 1개월 데이터 수집 (RSI, 볼린저밴드 연산용)
        stock = yf.Ticker(종목코드.upper())
        주가데이터 = stock.history(period="1mo")
        
        # 유효한 종목 코드인지 검증
        if 주가데이터.empty or len(주가데이터) < 15:
            st.error("데이터가 부족하거나 존재하지 않는 종목 코드입니다. 정확한 티커를 입력해 주세요.")
        else:
            # 주요 가격 지표 추출
            현재가 = 주가데이터['Close'].iloc[-1]
            당일고가 = 주가데이터['High'].iloc[-1]
            당일저가 = 주가데이터['Low'].iloc[-1]
            거래량 = 주가데이터['Volume'].iloc[-1]
            전일종가 = 주가데이터['Close'].iloc[-2]
            등락률 = ((현재가 - 전일종가) / 전일종가) * 100
            
            # --- [단타 심화 지표 계산] ---
            # 1. RSI (14일 기준 상대강도지수) 계산
            delta = 주가데이터['Close'].diff()
            상승분 = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            하락분 = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            RS = 상승분 / 하락분
            RSI지표 = 100 - (100 / (1 + RS))
            현재RSI = RSI지표.iloc[-1]
            
            # 2. 볼린저 밴드 (20일 기준) 계산
            중간선 = 주가데이터['Close'].rolling(window=20).mean()
            표준편차 = 주가데이터['Close'].rolling(window=20).std()
            상단선 = 중간선 + (표준편차 * 2)
            하단선 = 중간선 - (표준편차 * 2)
            현재상단 = 상단선.iloc[-1]
            현재하단 = 하단선.iloc[-1]
            
            # --- 화면 시각화 (메트릭 카드) ---
            st.success(f"[{종목코드.upper()}] 실전 단타 분석 리포트")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("현재가", f"${현재가:.2f}", f"{등락률:+.2f}%")
            m2.metric("당일 고가", f"${당일고가:.2f}")
            m3.metric("당일 저가", f"${당일저가:.2f}")
            m4.metric("RSI (14일)", f"{현재RSI:.1f}점")
            
            st.info(f"📊 당일 거래량: **{거래량:,} 주** | 📈 볼린저 밴드 상단: **${현재상단:.2f}** / 하단: **${현재하단:.2f}**")
            
            # --- [실전 단타 매매 신호 및 리스크 경고 진단] ---
            
            # ① 손절 및 긴급 청산 진단
            if 현재가 <= 손절기준가:
                st.error(f"🚨 [긴급 청산 경고] 현재가(${현재가:.2f})가 설정한 손절선(${손절기준가})을 이탈했습니다! 즉시 손실을 끊으세요.")
            
            # ② 목표 익절가 도달 진단
            if 현재가 >= 목표익절가:
                st.balloons()
                st.success(f"🎯 [익절 달성] 현재가(${현재가:.2f})가 목표 익절가(${목표익절가})에 도달했습니다! 수익을 실현하세요.")
            
            # ③ RSI 모멘텀 과열/침체 진단
            if 현재RSI >= 70:
                st.warning(f"🔥 [RSI 과매수 경고] RSI가 {현재RSI:.1f}점으로 70을 초과했습니다. 단기 고점일 수 있으니 추격 매수를 조심하세요.")
            elif 현재RSI <= 30:
                st.info(f"💡 [RSI 과매도 포착] RSI가 {현재RSI:.1f}점으로 30 이하입니다. 과도한 하락에 따른 기술적 반등 가능성이 있습니다.")
            
            # ④ 볼린저 밴드 돌파 진단
            if 현재가 >= 현재상단:
                st.warning(f"⚡ [볼린저 밴드 상단 돌파] 주가가 상단 밴드(${현재상단:.2f})를 상향 돌파했습니다. 강한 모멘텀이 발생 중입니다.")
            elif 현재가 <= 현재하단:
                st.warning(f"⚠️ [볼린저 밴드 하단 이탈] 주가가 하단 밴드(${현재하단:.2f})를 이탈했습니다. 추가 하락에 유의하세요.")
                
    except Exception as 오류내용:
        st.error(f"데이터 분석 중 시스템 오류가 발생했습니다: {오류내용}")
