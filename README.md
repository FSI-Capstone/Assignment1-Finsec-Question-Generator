# 금융보안 문제 생성 시스템

금융보안 관련 문제를 자동으로 생성하는 Streamlit 기반 웹 애플리케이션입니다.

## 기능

- 다양한 유형의 금융보안 문제 생성
- 도메인별 문제 생성 (금융보안 일반 지식, IT, 법률, 동향)
- 난이도 조절 가능
- 다양한 출력 형식 지원
- 해설 포함 옵션

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd [repository-name]
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
- `.env.example` 파일을 `.env`로 복사
- OpenAI API 키 설정

## 실행 방법

```bash
streamlit run app/main.py
```

## 사용 방법

1. 사이드바에서 원하는 설정 선택
   - 문제 유형
   - 도메인
   - 출제 기준
   - 문제 수
   - 난이도
   - 출력 형식
   - 해설 포함 여부

2. "문제 생성" 버튼 클릭

3. 생성된 문제 확인 