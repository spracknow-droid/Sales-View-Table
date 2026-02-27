import streamlit as st
import sqlite3
import pandas as pd
import os

def create_sales_views(conn):
    """
    DB 내에 2개의 View를 생성합니다. (기준월 -> 매출연월 반영)
    """
    cursor = conn.cursor()

    # 1. 판매계획 전처리
    cursor.execute("DROP VIEW IF EXISTS view_cleaned_plan")
    cursor.execute("""
        CREATE VIEW view_cleaned_plan AS
        SELECT 
            strftime('%Y-%m', 계획년월) AS 매출연월,
            매출처명,
            품명 AS 품목명,
            판매수량 AS 수량,
            판매금액 AS 장부금액
        FROM sales_plan_data
    """)

    # 2. 매출리스트 전처리
    cursor.execute("DROP VIEW IF EXISTS view_cleaned_actual")
    cursor.execute("""
        CREATE VIEW view_cleaned_actual AS
        SELECT 
            strftime('%Y-%m', 매출일) AS 매출연월,
            매출처명,
            품목명,
            수량,
            장부금액
        FROM sales_actual_data
    """)

    conn.commit()

def main():
    st.set_page_config(page_title="Sales Data View Generator", layout="wide")
    st.title("📊 판매 데이터 DB 자동 전처리")

    # 1. 사이드바에서 DB 파일 업로드
    st.sidebar.header("데이터 업로드")
    uploaded_file = st.sidebar.file_uploader("SQLite DB 파일을 업로드하세요", type=["db", "sqlite", "sqlite3"])

    if uploaded_file is not None:
        # 임시 파일로 저장 (sqlite3 연결용)
        temp_db_path = "temp_sales_data.db"
        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # DB 연결
            conn = sqlite3.connect(temp_db_path)
            
            # [수정] 버튼 없이 파일 업로드 즉시 View 생성 실행
            create_sales_views(conn)
            st.sidebar.success("✅ View 자동 생성/업데이트 완료")

            # 생성된 View 데이터 확인
            st.subheader("📋 실시간 View 데이터 확인")
            
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 1. 판매계획 (view_cleaned_plan)")
                try:
                    df_plan = pd.read_sql_query("SELECT * FROM view_cleaned_plan LIMIT 10", conn)
                    st.dataframe(df_plan, use_container_width=True)
                except Exception:
                    st.warning("판매계획 데이터를 불러올 수 없습니다. 테이블명을 확인해주세요.")

            with col2:
                st.markdown("#### 2. 실적리스트 (view_cleaned_actual)")
                try:
                    df_actual = pd.read_sql_query("SELECT * FROM view_cleaned_actual LIMIT 10", conn)
                    st.dataframe(df_actual, use_container_width=True)
                except Exception:
                    st.warning("실적리스트 데이터를 불러올 수 없습니다. 테이블명을 확인해주세요.")
            
            conn.close()

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    else:
        st.info("왼쪽 사이드바에서 SQLite DB 파일을 업로드하면 자동으로 전처리가 시작됩니다.")

if __name__ == "__main__":
    main()
