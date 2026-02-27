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

    # 🔥 날짜 변환 제거 (가장 안전한 방식)
    plan_cols = ", ".join([f"{orig} AS {std}" for std, orig, _ in COLUMN_MAP])
    actual_cols = ", ".join([f"{orig} AS {std}" for std, _, orig in COLUMN_MAP])

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
    conn.commit()

def get_view_data(conn):
    import pandas as pd
    return pd.read_sql_query("SELECT * FROM view_integrated_sales", conn)
