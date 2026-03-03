# app.py
import streamlit as st
import os
import sqlite3
from config import TEMP_DB_PATH
from db_manager import create_integrated_sales_view
from data_processor import fetch_integrated_data
from utils import convert_df_to_excel

def main():
    st.set_page_config(page_title="Sales Data Integrator", layout="wide")
    
    uploaded_file = st.sidebar.file_uploader("DB 파일을 업로드하세요 (.db)", type="db")

    if uploaded_file:
        # 파일 저장 로직
        with open(TEMP_DB_PATH, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # 1. 뷰 생성 (DB 매니저 호출)
            with sqlite3.connect(TEMP_DB_PATH) as conn:
                create_integrated_sales_view(conn)
            
            # 2. 데이터 조회 (데이터 프로세서 호출)
            df = fetch_integrated_data(TEMP_DB_PATH)

            # 3. 화면 표시 및 다운로드 (UI 및 유틸리티)
            st.subheader("📊 통합 판매 데이터")
            st.dataframe(df, use_container_width=True)
            
            # ... (생략: 다운로드 버튼 등 UI 요소) ...

        except Exception as e:
            st.error(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
