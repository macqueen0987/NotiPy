import json
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_functions import get_user_id, get_project_id  # 이미 정의된 함수들
from models import User, Role, Project
from llm_axe import OllamaChat, Agent  # llm-axe 사용

def assign_users_to_roles():
    # 데이터베이스 엔진 생성 및 세션 설정
    engine = create_engine("sqlite:///github.db", echo=False, future=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. 프로젝트 이름 입력 후 프로젝트 정보 조회
    project_name = input("Enter the project name: ")
    project_id = get_project_id(project_name, session)
    if project_id is None:
        print("Project not found.")
        return None, None, session

    project = session.query(Project).filter(Project.project_id == project_id).first()
    roles = session.query(Role).filter(Role.project_id == project_id).all()
    if not roles:
        print("No roles registered for this project.")
        return None, None, session

    # 각 역할별 사용자 점수 저장을 위한 이차원 리스트 초기화
    role_results = [[] for _ in range(len(roles))]

    # llm-axe 사용: Agent 생성
    llm = OllamaChat(model="llama3:instruct")
    agent = Agent(llm, custom_system_prompt="", stream=False)

    # 2. 팀원 수만큼 팀원 정보를 입력받음
    if project.team_size is None:
        print("Team size is not set for the project.")
        return role_results, roles, session
    team_size = project.team_size

    for i in range(team_size):
        user_name = input(f"Enter the name of team member {i+1}: ")
        developer_id = get_user_id(user_name, session)
        if developer_id is None:
            print(f"User '{user_name}' not found. Skipping.")
            continue

        # 사용자 상세정보 조회 및 최대 5개의 저장소 정보만 포함
        user = session.query(User).filter(User.developer_id == developer_id).first()
        user_repos = user.repositories[:5]

        user_data = {
            "name": user.name,
            "github_url": user.github_url,
            "primary_languages": user.primary_languages,
            "experience_years": user.experience_years,
            "public_repos": user.public_repos,
            "total_stars": user.total_stars,
            "total_forks": user.total_forks,
            "profile_created_at": user.profile_created_at.isoformat() if user.profile_created_at else None,
            "last_active_date": user.last_active_date.isoformat() if user.last_active_date else None,
            "repositories": [
                {
                    "name": repo.name,
                    "url": repo.url,
                    "primary_language": repo.primary_language,
                    "stars": repo.stars,
                    "forks": repo.forks
                } for repo in user_repos
            ]
        }

        # 3. 각 역할별로 LLM에게 JSON 프롬프트(Prompt) 전송
        for idx, role in enumerate(roles):
            prompt_data = {
                "role": {
                    "role_id": role.role_id,
                    "name": role.name,
                    "description": role.description,
                    "languages_tools": role.languages_tools
                },
                "user": user_data,
                "project": {
                    "name": project.name,
                    "description": project.description,
                    "tech_stack": project.tech_stack
                }
            }
            prompt_message = (
                "Using the provided user, role, and project information in JSON format, "
                "please evaluate the user's suitability for the role. "
                "Return ONLY a JSON object in the following format without any additional text: "
                '{"score": <integer>}. '
                "Data: " + json.dumps(prompt_data, ensure_ascii=False)
            )
            
            response = agent.ask(prompt_message)
            print("Raw LLM response:", response)
            
            # JSON 부분 추출: 먼저 ```json ... ``` 코드 블록 내의 내용을 추출 시도
            json_str = ""
            match = re.search(r"```json(.*?)```", response, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
            else:
                # 코드 블록이 없으면 첫 번째 '{'부터 마지막 '}'까지 추출
                start = response.find("{")
                end = response.rfind("}")
                if start != -1 and end != -1:
                    json_str = response[start:end+1]
            
            try:
                result = json.loads(json_str)
                score = result.get("score", 0)
            except Exception as e:
                print(f"Error processing LLM response: {e}")
                score = 0
            
            # 역할별 결과에 (사용자 이름, 점수) 추가
            role_results[idx].append((user.name, score))

    # 4. 최종 결과 출력
    print("\nRole-wise user score results:")
    for idx, result in enumerate(role_results):
        print(f"{roles[idx].name}: {result}")

    return role_results, roles, session

def assign_roles_exclusive(role_results, roles, session):
    """
    각 역할의 후보 점수 결과와 역할 객체를 바탕으로,
    한 명의 사용자가 오직 하나의 역할만 맡도록 역할 배정을 진행합니다.
    
    role_results: 각 역할별 [(user_name, score), ...] 목록. role_results[i]는 roles[i]에 해당.
    roles: 데이터베이스에서 조회된 역할 객체 리스트. 각 role은 role.count (필요 인원)을 가짐.
    session: SQLAlchemy 세션 객체.
    """
    # 전역 후보 리스트 생성: 각 항목은 (role_index, user_name, score)
    candidate_list = []
    for role_index, candidates in enumerate(role_results):
        for user_name, score in candidates:
            candidate_list.append((role_index, user_name, score))
    
    # 점수가 높은 순서대로 정렬 (내림차순)
    candidate_list.sort(key=lambda x: x[2], reverse=True)
    
    # 결과 딕셔너리: 각 역할 인덱스별로 선택된 사용자 이름 목록을 저장
    assignments = {i: [] for i in range(len(roles))}
    # 이미 다른 역할에 할당된 사용자 이름을 추적하는 집합
    assigned_users = set()
    
    # 전역 후보 리스트 순회: 
    for role_index, user_name, score in candidate_list:
        # 이미 어떤 역할에 할당된 사용자라면 skip
        if user_name in assigned_users:
            continue
        # 현재 역할의 할당 인원이 role.count 미만일 경우에만 할당
        if len(assignments[role_index]) < roles[role_index].count:
            assignments[role_index].append(user_name)
            assigned_users.add(user_name)
    
    # 역할 객체의 assigned_users 관계를 업데이트
    for role_index, user_names in assignments.items():
        role = roles[role_index]
        for user_name in user_names:
            user_obj = session.query(User).filter(User.name == user_name).first()
            if user_obj and (user_obj not in role.assigned_users):
                role.assigned_users.append(user_obj)
        print(f"Role '{role.name}' assigned users: {user_names}")
    
    session.commit()
    print("Role assignments committed to the database.")

if __name__ == "__main__":
    role_results, roles, session = assign_users_to_roles()
    if role_results and roles and session:
        assign_roles_exclusive(role_results, roles, session)
    
