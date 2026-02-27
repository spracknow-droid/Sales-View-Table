import sqlite3

def create_integrated_sales_view(conn):
    """
    서로 다른 형식의 계획과 실적 테이블을 표준화하여 하나의 통합 View로 생성합니다.
    """
    cursor = conn.cursor()

    # 기존 View 정리
    cursor.execute("DROP VIEW IF EXISTS view_cleaned_plan")
    cursor.execute("DROP VIEW IF EXISTS view_cleaned_actual")
    
    # 통합 View 생성
    cursor.execute("DROP VIEW IF EXISTS view_integrated_sales")
    cursor.execute("""
        CREATE VIEW view_integrated_sales AS
        /* 1. 판매계획 데이터 표준화 */
        SELECT 
            '판매계획' AS 데이터구분,
            strftime('%Y-%m', 계획년월) AS 매출연월,
            매출처명,
            품명 AS 품목명,
            판매수량 AS 수량,
            판매금액 AS 장부금액
        FROM sales_plan_data
        
        UNION ALL
        
        /* 2. 매출실적 데이터 표준화 */
        SELECT 
            '판매실적' AS 데이터구분,
            strftime('%Y-%m', 매출일) AS 매출연월,
            매출처명,
            품목명,
            수량,
            장부금액
        FROM sales_actual_data
    """)

    conn.commit()
