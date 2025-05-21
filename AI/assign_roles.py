import json
import re

from llm_axe import OllamaChat  # LLM 호출 클래스
from models import Base, Project, Role  # 모델 정의를 불러옵니다.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def generate_roles_for_project(project_id: int, session):
    """
    주어진 프로젝트 ID에 해당하는 프로젝트 정보를 기반으로 LLM에 프롬프트를 전달하여,
    프로젝트의 팀 사이즈에 맞는 역할(role) 목록을 JSON 형식으로 생성하고 데이터베이스에 추가합니다.
    """
    # 프로젝트 조회
    project = session.query(Project).filter_by(project_id=project_id).first()
    if not project:
        print(f"Project with id {project_id} not found.")
        return

    # 팀 사이즈가 없을 경우 기본값 설정 (예: 3)
    num_roles = project.team_size if project.team_size is not None else 3

    # 프로젝트 상세 정보 프롬프트 구성
    prompt = f"""
Project Details:
Name: {project.name}
Description: {project.description}
Category: {project.category}
Team Size: {num_roles}
Core Features: {json.dumps(project.core_features, ensure_ascii=False)}
Tech Stack: {json.dumps(project.tech_stack, ensure_ascii=False)}
Complexity: {project.complexity}
Database: {project.database}
Platform: {project.platform}
Notifications: {project.notifications}
Map Integration: {project.map_integration}
Authentication Required: {project.auth_required}

Based on the above project details, please generate exactly {num_roles} roles for this project.
For each role, provide the following information in JSON format:
- "name": Role title (e.g., "백엔드 개발자", "데이터베이스 관리자", etc.)
- "count": Number of team members for this role
- "description": Detailed explanation of the role responsibilities
- "languages_tools": A list of programming languages and tools required for this role. Include any specific frameworks, libraries, or software tools that are essential for performing the job effectively.

Return your response as a valid JSON array in the following structure:
[
  {{
    "name": "Role Name",
    "count": number,
    "description": "Role responsibilities description",
    "languages": ["Language1", "Language2", ...]
  }},
  {{
    "name": "Role Name2",
    "count": number,
    "description": "Role responsibilities description",
    "languages": ["Language1", "Language2", ...]
  }},
  ...
]
"""

    # ... (이전 코드 동일) ...

    # OllamaChat 인스턴스를 생성할 때 model 파라미터를 반드시 전달합니다.
    llm = OllamaChat(model="llama3:instruct")
    messages = [{"role": "user", "content": prompt}]
    response_text = llm.ask(messages)

    print("LLM response:", repr(response_text))

    # "**Roles:**" 이후의 문자열에서 JSON 배열 추출
    roles_marker = "**Roles:**"
    marker_pos = response_text.find(roles_marker)
    if marker_pos != -1:
        # 마커 이후의 텍스트를 대상으로 추출 시도
        substring = response_text[marker_pos:]
        # 정규표현식으로 객체 배열 형태(여러 객체가 들어있는 배열)를 추출합니다.
        match = re.search(
            r"(\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\])", substring, re.DOTALL
        )

        if match:
            json_str = match.group(1)
        else:
            print("Could not extract a valid JSON array from the roles section.")
            return
    else:
        # 마커를 찾지 못하면 전체 문자열에서 첫번째 JSON 배열 추출 (예외 처리)
        start_idx = response_text.find("[")
        end_idx = response_text.rfind("]")
        if start_idx == -1 or end_idx == -1:
            print("Could not find a valid JSON array in the LLM response.")
            return
        json_str = response_text[start_idx: end_idx + 1]

    try:
        roles_data = json.loads(json_str)
    except Exception as e:
        print("Error parsing extracted JSON:", e)
        return

    roles_created = []
    # LLM 응답으로 받은 각 역할 정보를 기반으로 Role 객체 생성 및 세션에 추가
    for role_info in roles_data:
        new_role = Role(
            project_id=project.project_id,
            name=role_info.get("name"),
            count=role_info.get("count"),
            description=role_info.get("description"),
            languages_tools=role_info.get("languages_tools"),  # 키 이름에 맞게 수정
        )
        session.add(new_role)
        roles_created.append(new_role)

    session.commit()
    print(
        f"Successfully created {
            len(roles_created)} roles for project id {
            project.project_id}.")
    return roles_created


if __name__ == "__main__":
    # 데이터베이스 엔진 및 세션 설정 (여기서는 SQLite 예시)
    engine = create_engine("sqlite:///github.db", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 테이블이 존재하지 않을 경우 생성
    Base.metadata.create_all(engine)

    try:
        project_input_id = int(input("Enter project id: "))
    except ValueError:
        print("올바른 숫자를 입력해 주세요.")
    else:
        generate_roles_for_project(project_input_id, session)
