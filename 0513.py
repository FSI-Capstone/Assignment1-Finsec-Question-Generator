import streamlit as st
import os
from openai import OpenAI
import PyPDF2

# 페이지 설정
st.set_page_config(
    page_title="FSI_A1",
    page_icon="📊",
    layout="wide"
)

# PDF 파일 읽기 함수
@st.cache_data
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"PDF 읽기 오류: {str(e)}")
        return None

# 환경변수에서 OpenAI API 키 가져오기
@st.cache_resource
def get_openai_client():
    # 환경변수에서 API 키 불러오기
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        st.error("OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")
        st.info("사용방법: 터미널에서 `export OPENAI_API_KEY=your_api_key` 실행")
        return None
    
    return OpenAI(api_key=api_key)

# OpenAI 클라이언트 가져오기
client = get_openai_client()

# 메인 페이지
st.title("📊 벤치마크 테스트 문항 생성기")
st.write("환경변수에서 OpenAI API 키를 불러왔습니다.")

if client:
    st.success("✅ OpenAI API 연결 성공!")
else:
    st.error("❌ OpenAI API 연결 실패!")
    st.stop()

# PDF 벤치마크 데이터 업로드 (최상단)
st.header("📋 벤치마크 데이터 업로드")
st.write("문제 출제 기준이 될 PDF 파일을 업로드해주세요:")

# 세션 상태 초기화 (벤치마크 데이터 저장)
if 'benchmark_pdf_data' not in st.session_state:
    st.session_state.benchmark_pdf_data = ""

uploaded_file = st.file_uploader(
    "벤치마크 PDF 파일 업로드", 
    type=['pdf'],
    help="업로드된 PDF 파일의 텍스트가 문제 출제 기준으로 사용됩니다."
)

if uploaded_file is not None:
    with st.spinner("PDF 파일을 읽고 있습니다..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        if extracted_text:
            st.session_state.benchmark_pdf_data = extracted_text
            st.success("✅ PDF 파일이 성공적으로 업로드되고 처리되었습니다!")
            
            # PDF 내용 미리보기
            with st.expander("📖 업로드된 PDF 내용 미리보기"):
                preview_text = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
                st.text(preview_text)
                st.info(f"총 {len(extracted_text)} 문자의 텍스트가 추출되었습니다.")
        else:
            st.error("PDF 파일 처리에 실패했습니다. 다른 파일을 시도해보세요.")

# 사용자 카테고리 선택
st.header("📂 도메인 선택")
st.write("원하시는 분야를 선택해주세요:")

# 버튼 레이아웃 설정
col1, col2, col3, col4 = st.columns(4)

# 세션 상태 초기화 (선택한 카테고리 저장)
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None

# 각 카테고리 버튼
with col1:
    if st.button("📚 일반 지식", use_container_width=True):
        st.session_state.selected_category = "일반 지식"

with col2:
    if st.button("💻 IT", use_container_width=True):
        st.session_state.selected_category = "IT"

with col3:
    if st.button("📊 동향", use_container_width=True):
        st.session_state.selected_category = "동향"

with col4:
    if st.button("⚖️ 법률", use_container_width=True):
        st.session_state.selected_category = "법률"

# 선택된 카테고리 표시
if st.session_state.selected_category:
    st.success(f"선택된 분야: **{st.session_state.selected_category}**")
else:
    st.info("위 버튼 중 하나를 선택해주세요!")

# 문제 수 선택
st.header("📝 문제 개수 선택")
st.write("출제할 문제의 개수를 선택해주세요:")

# 문제 수 버튼 레이아웃
col1, col2, col3, col4 = st.columns(4)

# 세션 상태 초기화 (선택한 문제 수 저장)
if 'selected_count' not in st.session_state:
    st.session_state.selected_count = None

# 각 문제 수 버튼
with col1:
    if st.button("5문제", use_container_width=True):
        st.session_state.selected_count = 5

with col2:
    if st.button("10문제", use_container_width=True):
        st.session_state.selected_count = 10

with col3:
    if st.button("15문제", use_container_width=True):
        st.session_state.selected_count = 15

with col4:
    if st.button("20문제", use_container_width=True):
        st.session_state.selected_count = 20

# 선택된 문제 수 표시
if st.session_state.selected_count:
    st.success(f"선택된 문제 수: **{st.session_state.selected_count}개**")
else:
    st.info("문제 개수를 선택해주세요!")

# 문제 생성 함수
@st.cache_data
def generate_questions(category, count, benchmark_data, _client):
    try:
        prompt = f"""
        다음 벤치마크 데이터를 바탕으로 {category} 분야의 5지선다 문제를 {count}개 생성해주세요.
        
        벤치마크 데이터:
        {benchmark_data[:2000]}...
        
        요구사항:
        1. 각 문제는 다음 형식으로 작성해주세요:
        - 문제: (문제 내용)
        - 보기:
          1) 선택지 1
          2) 선택지 2
          3) 선택지 3
          4) 선택지 4
          5) 선택지 5
        - 정답: (정답 번호)
        - 해설: (상세한 해설)
        
        2. 문제는 벤치마크 데이터와 직접적으로 관련된 내용으로 만들어주세요.
        3. 선택지는 모두 그럴듯하게 작성하되, 정답은 명확히 구분되도록 해주세요.
        4. 해설은 왜 해당 답이 정답인지, 나머지 선택지가 틀린 이유를 포함해주세요.
        5. 각 문제는 "=== 문제 X ===" 로 구분해주세요.
        """
        
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 전문적인 문제 출제자입니다. 주어진 벤치마크 데이터를 정확하게 분석하여 해당 분야의 고품질 문제를 생성합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"문제 생성 중 오류 발생: {str(e)}")
        return None

# 문제 파싱 함수
def parse_questions(questions_text):
    questions = []
    if not questions_text:
        return questions
    
    # 문제별로 분리
    question_blocks = questions_text.split("=== 문제")[1:]
    
    for i, block in enumerate(question_blocks, 1):
        try:
            lines = block.strip().split('\n')
            
            # 문제 내용 찾기
            question = ""
            options = []
            answer = ""
            explanation = ""
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("문제:"):
                    current_section = "question"
                    question = line.replace("문제:", "").strip()
                elif line.startswith("보기:"):
                    current_section = "options"
                elif line.startswith("정답:"):
                    current_section = "answer"
                    answer = line.replace("정답:", "").strip()
                elif line.startswith("해설:"):
                    current_section = "explanation"
                    explanation = line.replace("해설:", "").strip()
                else:
                    if current_section == "question":
                        question += " " + line
                    elif current_section == "options" and line.startswith(('1)', '2)', '3)', '4)', '5)')):
                        options.append(line)
                    elif current_section == "explanation":
                        explanation += " " + line
            
            if question and len(options) == 5 and answer and explanation:
                questions.append({
                    "number": i,
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation
                })
        except Exception as e:
            st.warning(f"문제 {i} 파싱 중 오류: {str(e)}")
            continue
    
    return questions

# 문제 생성 버튼
st.header("🚀 문제 생성")

# 모든 선택사항 확인
if all([
    st.session_state.get('selected_category'),
    st.session_state.get('selected_count'),
    st.session_state.get('benchmark_pdf_data')
]):
    if st.button("문제 생성하기 🎯", type="primary", use_container_width=True):
        with st.spinner("문제를 생성 중입니다... 잠시만 기다려주세요!"):
            # 문제 생성
            questions_text = generate_questions(
                st.session_state.selected_category,
                st.session_state.selected_count,
                st.session_state.benchmark_pdf_data,
                client
            )
            
            if questions_text:
                st.session_state.generated_questions = parse_questions(questions_text)
                if st.session_state.generated_questions:
                    st.success(f"✅ {len(st.session_state.generated_questions)}개의 문제가 생성되었습니다!")
                else:
                    st.error("문제 파싱에 실패했습니다. 다시 시도해주세요.")
            else:
                st.error("문제 생성에 실패했습니다. 다시 시도해주세요.")
else:
    st.warning("모든 항목을 선택/입력해주세요:")
    if not st.session_state.get('selected_category'):
        st.error("❌ 도메인을 선택해주세요")
    if not st.session_state.get('selected_count'):
        st.error("❌ 문제 수를 선택해주세요") 
    if not st.session_state.get('benchmark_pdf_data'):
        st.error("❌ 벤치마크 PDF를 업로드해주세요")

# 생성된 문제 표시
if st.session_state.get('generated_questions'):
    st.header("📝 생성된 문제")
    
    for q in st.session_state.generated_questions:
        st.subheader(f"문제 {q['number']}")
        
        # 문제 내용
        st.write(f"**{q['question']}**")
        
        # 보기
        st.write("**보기:**")
        for option in q['options']:
            st.write(option)
        
        # 정답과 해설 토글
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"정답 보기", key=f"answer_{q['number']}"):
                st.info(f"**정답: {q['answer']}**")
        
        with col2:
            if st.button(f"해설 보기", key=f"explanation_{q['number']}"):
                st.info(f"**해설:** {q['explanation']}")
        
        st.divider()

# 여기에 추가 기능들이 들어갈 예정!