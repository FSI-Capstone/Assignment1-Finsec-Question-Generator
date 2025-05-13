import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

# 🌱 환경 변수 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("📘 문제 생성기")

# ✅ 0. 분야 선택
field = st.selectbox("출제 분야를 선택하세요", [
    "IT - 정보보안기사/정보처리기사", 
    "금융보안 관련 일반지식", 
    "법률 - 핵심 법령 및 고시, 가이드라인",
    "동향 - 뉴스, 보도자료 등"
])

# 1. 사용자 입력
uploaded_pdf = st.file_uploader("📄 선택한 분야의 출제기준 PDF 업로드", type="pdf")

problem_type = st.selectbox("문제 유형", [
    "기본 정보 확인", "빈칸 채우기", "사례/시나리오", "일치 여부 판단",
    "원인-결과 연결", "우선순위/절차", "틀린 것 고르기", "비교/구분", "적용 판단"
])

domain = st.text_input("도메인 (예: 시스템 보안, 네트워크 보안 등)")
num_questions = st.number_input("생성할 문제 수", min_value=1, max_value=10, value=1)
difficulty = st.selectbox("난이도", ["쉬움", "보통", "어려움"])
output_format = st.selectbox("출력 형식", ["텍스트", "CSV"])
include_explanation = st.checkbox("해설 포함 여부", value=True)

# 2. 문제 유형별 설명
problem_type_explanations = {
    "기본 정보 확인": "정보 또는 정의를 묻는 정형화된 문제",
    "빈칸 채우기": "내 핵심 개념을 빈칸으로 제시, 알맞은 단어나 개념 선택",
    "사례/시나리오": "상황을 간단히 설명하고, 올바른 대처법이나 판단을 묻는 문제",
    "일치 여부 판단": "설명이 주어진 뒤, 관련 정보 중 올바른 것을 선택하는 문제",
    "원인-결과 연결": "현상의 원인 또는 결과를 묻는 문제",
    "우선순위/절차": "단계가 있는 절차 중, 가장 먼저 혹은 올바른 순서를 묻는 문제",
    "틀린 것 고르기": "보기 중 틀린 정보를 선택하는 문제",
    "비교/구분": "개념이나 기술을 구별하거나 비교하는 문제",
    "적용 판단": "지침/보안 수칙 등을 특정 상황에 적용할 수 있는지 묻는 문제"
}

# 3. PDF 텍스트 추출 함수
def extract_text_from_pdf(file) -> str:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

# 4. GPT 프롬프트 구성
def build_prompt(pdf_text, problem_type, difficulty, domain, num_questions, include_explanation):
    explanation = problem_type_explanations.get(problem_type, "")
    
    # 빈칸 채우기 유형인 경우 추가 지시문 삽입
    extra_instruction = ""
    if problem_type == "빈칸 채우기":
        extra_instruction = (
            "문장 내 중요한 단어나 개념을 빈칸(______)으로 제시하고, 보기 중에서 그 빈칸에 들어갈 가장 적절한 선택지를 고르도록 해주세요.\n"
            "단순 정의형 문제가 아니라 반드시 **빈칸 형태**로 표현해주세요.\n"
        )
    
    return f"""
당신은 '{field}' 분야의 문제를 출제하는 전문가입니다.

아래 출제기준을 기반으로, '{problem_type}' 유형의 문제를 {num_questions}개 생성해주세요.

- 문제 유형 설명: {explanation}
- 도메인: {domain}
- 난이도: {difficulty}
{extra_instruction}

출제기준:
{pdf_text[:5000]}

형식:
문제:
보기:
A.
B.
C.
D.
E.
정답:{' (선택지 중 하나로 명확하게)'}

{"해설:" if include_explanation else ""}
"""

# 5. 문제 생성
if uploaded_pdf and st.button("📌 문제 생성하기"):
    with st.spinner("문제를 생성하는 중입니다..."):
        try:
            pdf_text = extract_text_from_pdf(uploaded_pdf)
            prompt = build_prompt(pdf_text, problem_type, difficulty, domain, num_questions, include_explanation)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            output = response.choices[0].message.content
            st.success("✅ 문제 생성 완료!")
            st.text_area("생성된 문제", value=output, height=500)

            if output_format == "CSV":
                questions = output.split("\n\n")
                data = []
                for q in questions:
                    if "문제:" in q and "정답:" in q:
                        question = q.split("문제:")[1].split("보기:")[0].strip()
                        options = q.split("보기:")[1].split("정답:")[0].strip()
                        answer = q.split("정답:")[1].split("해설:")[0].strip()
                        explanation = q.split("해설:")[1].strip() if "해설:" in q else ""
                        data.append({"문제": question, "보기": options, "정답": answer, "해설": explanation})
                if data:
                    df = pd.DataFrame(data)
                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button("📥 CSV 다운로드", csv, file_name="generated_questions.csv", mime="text/csv")

        except Exception as e:
            st.error(f"⚠️ 오류 발생: {str(e)}")
