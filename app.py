import streamlit as st
import sqlite3
import os
import io
import pandas as pd
from database import create_integrated_sales_view, get_view_data

# ✅ 엑셀 변환 함수 (엔진 자동 선택 + 예외 출력)
def convert_df_to_excel(df):
    output = io.BytesIO()
    try:
        # xlsxwriter 없어도 동작하도록 engine 제거
        with pd.ExcelWriter(output) as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        return output.getvalue()
    except Exception as e:
        return e

def main():
    st.set_page_config(page_title="Sales Data Integrator", layout="wide")
    st.title("판매 데이터 통합 View")

    st.sidebar.header("데이터 업로드")
    uploaded_file = st.sidebar.file_uploader(
        "SQLite DB 파일을 업로드하세요",
        type=["db", "sqlite", "sqlite3"]
    )

    if uploaded_file is not None:

        temp_db_path = "temp_sales_data.db"

        # 기존 파일 삭제 (잠김 방지)
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)

        # 업로드 파일 저장
        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            conn = sqlite3.connect(temp_db_path)

            # 1️⃣ View 생성
            create_integrated_sales_view(conn)
            st.sidebar.success("✅ 통합 View 생성 완료")

            # 2️⃣ 데이터 가져오기
            df = get_view_data(conn)

            st.subheader("📋 판매 분석 View")

            # 🔎 디버그 정보
            st.write("📊 데이터 크기:", df.shape)

            if df.empty:
                st.warning("⚠ 데이터가 없습니다. (df가 비어 있음)")
            else:
                st.success(f"총 {len(df)}건 데이터 로드 완료")

            # ✅ 엑셀 변환
            excel_data = convert_df_to_excel(df)

            # ✅ 버튼은 항상 표시
            if isinstance(excel_data, bytes):
                st.download_button(
                    label="📂 엑셀 다운로드",
                    data=excel_data,
                    file_name="integrated_sales_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error(f"❌ 엑셀 변환 실패: {excel_data}")

            # ✅ 데이터프레임 표시 (비어있어도 표시)
            st.dataframe(df, use_container_width=True)

            conn.close()

        except Exception as e:
            st.error(f"❌ 실행 중 오류 발생: {e}")

    else:
        st.info("사이드바에서 DB 파일을 업로드해주세요.")

if __name__ == "__main__":
    main()
