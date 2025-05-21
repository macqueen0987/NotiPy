from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import User,Project,Role  # models.py에서 정의한 User 클래스를 import


# 데이터베이스 엔진 생성 
engine = create_engine("sqlite:///github.db", echo=False, future=True)

def get_user_id(user_name: str, session) -> int:
    """
    주어진 이름을 갖는 유저를 찾아 developer_id를 반환합니다.
    찾지 못하면 None을 반환합니다.
    """
    user = session.query(User).filter(User.name == user_name).first()
    if user:
        return user.developer_id
    return None

def get_project_id(project_name: str, session) -> int:
    """
    주어진 프로젝트 이름을 기반으로 해당 프로젝트의 project_id를 반환합니다.
    만약 일치하는 프로젝트가 없으면 None을 반환합니다.
    """
    project = session.query(Project).filter(Project.name == project_name).first()
    if project:
        return project.project_id
    return None
