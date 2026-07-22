# ========================================================================
# ~/bigdata2026/fastapi/Streamlit/practice2_풀이.py
#   
#   Streamlit 연습문제 2 - CSV 데이터 필터링
# ========================================================================
import streamlit as st
import pandas as pd

st.title('CSV 데이터 필터링 앱')

# 1. 파일 업로더 
file = st.file_uploader('CSV 파일을 업로드하세요', type='csv')

if file is not None:
    df = pd.read_csv(file)

    st.write('업로드된 데이터 미리보기')
    # 데이터프레임(file)이 화면에 보여진다
    st.dataframe(df.head())  # 앞부분 5줄만 미리보기

    st.divider()

    # 2. 보고 싶은 열(컬럼) 선택 (multiselect)
    selected_cols = st.multiselect(
        '확인하고 싶은 열을 선택하세요.',
        options=df.columns.tolist(),
        default=df.columns.tolist()
    )

    # 숫자형 열만 필터 대상으로 선택가능하도록 추출
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    # 3. 점수 범위 필터링 (slider) - 숫자형 열이 있을 때만
    if numeric_cols:
        target_col = st.selectbox('범위로 필터링할 열을 선택하세요.', numeric_cols)

        min_val = int(df[target_col].min())
        max_val = int(df[target_col].max())

        # 슬라이더 위젯
        low, high = st.slider(f'{target_col} 범위 선택',
                              min_value=min_val,
                              max_value=max_val,
                              value=(min_val, max_val))

        # 4. 조건에 맞는 행만 필터링
        filtered_df = df[
            (df[target_col] >= low) & (df[target_col] <= high)
        ]

        st.divider()
        st.write(f'필터링 결과 ({len(filtered_df)}건)')
        st.dataframe(filtered_df[selected_cols])
    else:
        st.warning('범위 필터링에 사용할 숫자형 열이 없습니다')
else:
    st.info('CSV 파일을 업로드 해주세요')