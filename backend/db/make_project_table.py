import json
import os
from datetime import datetime, timezone

from llm_axe import OllamaChat
from models import Base, Project  # 미리 정의해 둔 SQLAlchemy 모델
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# 1) LLM 초기화 (프로젝트만 분석)
llm = OllamaChat(model="llama3:instruct")

# 2) 프로젝트 설명 (설명만 제공)
project_description = """
I am planning to create a travel destination recommendation website and mobile application.
Please help me identify the category of this project and extract its core features.

The goal of the project is to allow users to receive personalized travel destination suggestions based on their preferences and behavior.
Users can input their interests (e.g., nature, culture, food), and the system recommends destinations using location data and user reviews.
The website may also include features like maps, user accounts, and social sharing.

Please answer with a suitable project category and a list of 3–5 core features in English.
"""

# 3) LLM에 보낼 프롬프트 생성 함수
#    category와 team_size 필드 추가 요청


def build_project_prompt(description: str) -> str:
    return f"""
You are a data engineer. Given the following project description, fill in all required fields
for the `projects` table.

Respond ONLY with valid JSON. The response MUST include ALL of the following keys exactly as shown:
- name
- category
- core_features (a list)
- tech_stack (a list)
- complexity (low/medium/high)
- database (string)
- platform (web/mobile/web&mobile)
- notifications (true/false)
- map_integration (true/false)
- auth_required (true/false)

The response must be a valid JSON object with no explanations or comments.
For example:
{{
  "name": "TravelBuddy",
  "category": "travel",
  "core_features": ["Personalized suggestions", "Map integration", "User reviews"],
  "tech_stack": ["React", "Node.js", "PostgreSQL"],
  "complexity": "medium",
  "database": "PostgreSQL",
  "platform": "web",
  "notifications": true,
  "map_integration": true,
  "auth_required": true
}}

Project Description: {description}
"""


# 4) LLM 호출 및 JSON 파싱


def analyze_project(description: str) -> dict:
    prompt = build_project_prompt(description)
    response = llm.ask(
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        format="json",
    )
    return json.loads(response)


# 5) DB에 저장


def save_project(record: dict):
    engine = create_engine("sqlite:///github.db", future=True)
    Base.metadata.create_all(engine)  # 테이블이 없으면 생성

    # 모델의 default created_at, updated_at 사용
    proj = Project(
        name=record["name"],
        description=project_description,
        category=record.get("category"),
        team_size=4,
        core_features=record["core_features"],
        tech_stack=record["tech_stack"],
        complexity=record["complexity"],
        database=record.get("database"),
        platform=record["platform"],
        notifications=record.get("notifications", False),
        map_integration=record.get("map_integration", False),
        auth_required=record.get("auth_required", False),
    )

    with Session(engine) as session:
        session.add(proj)
        session.commit()
        print(f"✅ project_id={proj.project_id} 로 저장되었습니다.")


if __name__ == "__main__":
    # LLM 분석
    project_data = analyze_project(project_description)
    print("프로젝트 필드:")
    print(json.dumps(project_data, indent=2, ensure_ascii=False))

    # DB 저장
    save_project(project_data)
