import pandas as pd

GUIDE_FILES = {
    "금융보안 일반 지식": "guide_general.md",
    "IT": "guide_it.md",
    "법률": "guide_law.md",
    "동향": "guide_trend.md"
}

def load_guide_criteria():
    """guide.md 파일에서 출제 기준을 로드합니다."""
    try:
        # guide.md 파일을 DataFrame으로 읽기
        df = pd.read_table('guide.md', sep='|', skiprows=1)
        
        # 컬럼 이름 정리
        df.columns = ['', '주요항목', '세부항목', '세세항목', '']
        
        # 불필요한 컬럼 제거 및 공백 제거
        df = df[['주요항목', '세부항목', '세세항목']]
        df = df.apply(lambda x: x.str.strip())
        
        # 세세항목 리스트 생성
        criteria_list = []
        for _, row in df.iterrows():
            criteria = f"{row['주요항목']} > {row['세부항목']} > {row['세세항목']}"
            criteria_list.append(criteria)
            
        return criteria_list
    except Exception as e:
        print(f"가이드 파일 로드 중 오류 발생: {e}")
        return []

def get_guide_content(domain):
    """선택된 도메인에 해당하는 가이드 파일의 내용을 포맷팅하여 반환합니다."""
    try:
        # 도메인에 해당하는 가이드 파일 선택
        guide_file = GUIDE_FILES.get(domain)
        if not guide_file:
            return f"Error: {domain}에 대한 가이드 파일을 찾을 수 없습니다."
        
        # guide 파일을 DataFrame으로 읽기
        df = pd.read_table(guide_file, sep='|', skiprows=1)
        
        # 컬럼 이름 정리
        df.columns = ['', '주요항목', '세부항목', '세세항목', '']
        
        # 불필요한 컬럼 제거 및 공백 제거
        df = df[['주요항목', '세부항목', '세세항목']]
        df = df.apply(lambda x: x.str.strip())
        
        # 포맷팅된 문자열 생성
        formatted_content = []
        current_major = ""
        
        for _, row in df.iterrows():
            major = row['주요항목']
            sub = row['세부항목']
            detail = row['세세항목']
            
            # 주요항목이 변경된 경우
            if major != current_major:
                formatted_content.append(f"\n[{major}]")
                current_major = major
            
            # 출제 기준 형식으로 표시
            formatted_content.append(f"  {major} > {sub} > {detail}")
        
        return "\n".join(formatted_content)
    except Exception as e:
        print(f"가이드 파일 로드 중 오류 발생: {e}")
        return f"Error: {domain} 도메인의 가이드 파일을 처리하는 중 오류가 발생했습니다." 