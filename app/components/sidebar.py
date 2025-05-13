import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from utils.constants import (
    QUESTION_TYPES,
    DOMAINS,
    DIFFICULTY_LEVELS,
    OUTPUT_FORMATS
)

def render_sidebar():
    """사이드바에 문제 생성 설정을 렌더링하고 설정값을 반환합니다."""
    with st.sidebar:
        st.header("문제 생성 설정")
        
        settings = {
            "question_type": st.selectbox(
                "문제 유형",
                options=QUESTION_TYPES,
                help="생성할 문제의 유형을 선택하세요."
            ),
            
            "domain": st.selectbox(
                "도메인",
                options=DOMAINS,
                help="문제의 도메인을 선택하세요."
            ),
            
            "num_questions": st.number_input(
                "생성할 문제 수",
                min_value=1,
                max_value=10,
                value=5,
                help="생성할 문제의 개수를 선택하세요."
            ),
            
            "difficulty": st.select_slider(
                "난이도",
                options=DIFFICULTY_LEVELS,
                value="중",
                help="문제의 난이도를 선택하세요."
            ),
            
            "output_format": st.selectbox(
                "출력 형식",
                options=OUTPUT_FORMATS,
                help="문제의 출력 형식을 선택하세요."
            ),
            
            "include_explanation": st.checkbox(
                "해설 포함",
                value=True,
                help="문제 해설을 포함할지 선택하세요."
            )
        }
        
        return settings 