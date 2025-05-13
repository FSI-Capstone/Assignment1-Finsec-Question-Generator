import streamlit as st
import pandas as pd
import io
from components.sidebar import render_sidebar
from components.question_generator import generate_questions

def create_csv_download(questions):
    """문제와 해답을 CSV 형식으로 변환하여 다운로드 링크를 생성합니다."""
    # DataFrame 생성을 위한 데이터 준비
    data = []
    for i, (question, answer) in enumerate(questions, 1):
        data.append({
            '번호': i,
            '출제기준': question.split('\n')[0].replace('출제 기준: ', ''),
            '문제': '\n'.join(question.split('\n')[1:]),
            '해답': answer
        })
    
    # DataFrame 생성
    df = pd.DataFrame(data)
    
    # CSV 파일 생성
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    
    # 다운로드 버튼 생성
    st.download_button(
        label="CSV 파일 다운로드",
        data=csv,
        file_name="금융보안_문제.csv",
        mime="text/csv"
    )

def main():
    st.set_page_config(
        page_title="금융보안 문제 생성기",
        page_icon="🔒",
        layout="wide"
    )
    
    st.title("금융보안 문제 생성 시스템")
    
    # 사이드바에서 설정값 가져오기
    settings = render_sidebar()
    
    # 문제 생성 버튼
    if st.button("문제 생성"):
        with st.spinner("문제를 생성하고 있습니다..."):
            questions = generate_questions(settings)
            st.success("문제가 생성되었습니다!")
            
            if settings['output_format'] == 'CSV':
                # CSV 다운로드 제공
                create_csv_download(questions)
                
                # 미리보기 표시
                st.subheader("문제 미리보기")
                for i, (question, answer) in enumerate(questions, 1):
                    with st.expander(f"문제 {i}", expanded=True):
                        st.text(question)
                    with st.expander(f"문제 {i} 해답", expanded=False):
                        st.text(answer)
            else:  # Plain Text
                for i, (question, answer) in enumerate(questions, 1):
                    with st.expander(f"문제 {i}", expanded=True):
                        st.text(question)
                    with st.expander(f"문제 {i} 해답", expanded=False):
                        st.text(answer)

if __name__ == "__main__":
    main() 