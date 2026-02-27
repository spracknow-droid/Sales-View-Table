import sqlite3

COLUMN_MAP = [
    ("매출연월", "계획년월", "매출일"),
    ("매출처", "매출처", "매출처"),
    ("매출처명", "매출처명", "매출처명"),
    ("품목", "품목코드", "품목"),
    ("품목명", "품명", "품목명"),
    ("거래통화", "거래통화", "거래통화"),
    ("환율", "환율", "환율"),
    ("판매단가", "판매단가", "판매단가"),
    ("수량", "판매수량", "수량"),
    ("장부금액", "판매금액", "장부금액"),
    ("대분류", "대분류", "대분류"),
    ("중분류", "중분류", "중분류"),
    ("소분류", "소분류", "소분류")
]

def create_integrated_sales_view(conn):
    cursor = conn.cursor()

    # 1. 컬럼 매핑 및 날짜 변환 로직 (STRFTIME 적용)
    plan_cols_list = []
    actual_cols_list = []

    for std, plan_orig, actual_orig in COLUMN_MAP:
        if std == "매출연월":
            plan_cols_list.append(f"STRFTIME('%Y-%m', {plan_orig}) AS {std}")
            actual_cols_list.append(f"STRFTIME('%Y-%m', {actual_orig}) AS {std}")
        else:
            plan_cols_list.append(f"{plan_orig} AS {std}")
            actual_cols_list.append(f"{actual_orig} AS {std}")

    plan_cols = ", ".join(plan_cols_list)
    actual_cols = ", ".join(actual_cols_list)

    # 2. 기존 뷰 삭제 및 재생성
    cursor.execute("DROP VIEW IF EXISTS view_integrated_sales")
    
    sql = f"""
        CREATE VIEW view_integrated_sales AS
        SELECT '판매계획' AS 데이터구분, {plan_cols}
        FROM sales_plan_data
        UNION ALL
        SELECT '판매실적' AS 데이터구분, {actual_cols}
        FROM sales_actual_data
    """

    cursor.execute(sql)
    
    # SQLite에서 스키마 변경을 물리적으로 적용하기 위해 명시적 커밋
    conn.commit()

def get_view_data(conn):
    import pandas as pd
    # 뷰가 정상 생성되었는지 확인하며 조회
    return pd.read_sql_query("SELECT * FROM view_integrated_sales", conn)
