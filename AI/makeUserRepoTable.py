import os
import json
from datetime import datetime, timezone
from github import Github
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Float, JSON, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, Session
from llm_axe import OllamaChat
from models import User, Repository, Base

llm = OllamaChat(model="llama3:instruct")

def fill_repo_metadata(name: str, url: str, readme: str) -> dict:
    prompt = (
        "You are a data engineer. Given the following GitHub repository metadata, "
        "please infer and return a JSON object with two keys:\n"
        "  - category: project domain (e.g., game, web, data, devops)\n"
        "  - core_features: list of 3–5 main features of this repository\n"
        "Respond with valid JSON only.\n\n"
        f"Repository Name: {name}\n"
        f"Repository URL: {url}\n"
        f"README Content:\n```\n{readme}\n```\n"
    )
    resp = llm.ask(
        [{"role": "system", "content": "You are a helpful assistant."},
         {"role": "user",   "content": prompt}],
        format="json"
    )
    return json.loads(resp)


# ----------------------------------------
# 2) GitHub API 초기화
# ----------------------------------------
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("GITHUB_TOKEN 환경변수가 설정되지 않았습니다.")
gh = Github(token)

# ----------------------------------------
# 3) DB 연결 및 테이블 생성
# ----------------------------------------
engine = create_engine("sqlite:///github.db", echo=False, future=True)
Base.metadata.create_all(engine)

# ----------------------------------------
# 4) 데이터 수집 & 저장
# ----------------------------------------
TARGET_USERS = [
    ("DDManager",   "https://github.com/DDManager"),
    ("Ryan Nielson","https://github.com/RyanNielson"),
    ("kcy1019",   "https://github.com/kcy1019"),
    ("insertish",   "https://github.com/insertish")
]
project_id_input = int(input("참여중인 프로젝트의 id를 입력하세요: "))

with Session(engine) as session:
    for label, url in TARGET_USERS:
        username = url.rstrip("/").split("/")[-1]
        user = gh.get_user(username)

        # 4-1) 유저 수준 통계 집계
        repos = list(user.get_repos())
        # 언어 통계
        langs = {}
        for r in repos:
            for lang, cnt in r.get_languages().items():
                langs[lang] = langs.get(lang, 0) + cnt
        primary_langs = sorted(langs, key=langs.get, reverse=True)[:3]

        # 별·포크 합계
        total_stars = sum(r.stargazers_count for r in repos)
        total_forks = sum(r.forks_count       for r in repos)

        # 마지막 활동 날짜 (각 repo의 최신 커밋 일자 중 최대)
        last_dates = []
        for r in repos:
            try:
                commit = r.get_commits()[0]
                last_dates.append(commit.commit.author.date)
            except Exception:
                pass
        last_active = max(last_dates) if last_dates else None

        # User 레코드 생성
        user_rec = User(
            name               = label,
            project_id         = project_id_input,
            github_url         = url,
            primary_languages  = primary_langs,
            experience_years   = round((datetime.now(timezone.utc) - user.created_at).days / 365, 1),
            public_repos       = user.public_repos,
            total_stars        = total_stars,
            total_forks        = total_forks,
            profile_created_at = user.created_at,
            last_active_date   = last_active  # last_active 역시 aware이면 OK
        )

        session.add(user_rec)
        session.flush()  # user_rec.developer_id 채번

        # 4-2) 상위 5개 레포 저장 (별 수 기준)
                # 4-2) 상위 5개 레포 저장 (별 수 기준)
        top5 = sorted(repos, key=lambda r: r.stargazers_count, reverse=True)[:5]
        for r in top5:
            readme_content = None
            try:
                readme_file = r.get_readme()
                readme_content = readme_file.decoded_content.decode('utf-8')
            except Exception:
                readme_content = "내용이 없거나 불러오기 실패"

            repo_rec = Repository(
                user_id          = user_rec.developer_id,
                name             = r.name,
                url              = r.html_url,
                primary_language = r.language,
                stars            = r.stargazers_count,
                forks            = r.forks_count,
                description      = readme_content,
                category         = None,       
                core_features    = []          
            )


            # LLM 호출: category & core_features 채우기
            try:
                meta = fill_repo_metadata(r.name, r.html_url, readme_content)
                repo_rec.category      = meta.get("category")
                repo_rec.core_features = meta.get("core_features", [])
            except Exception as e:
                print(f"LLM 메타데이터 호출 실패 for {r.name}: {e}")
            
            session.add(repo_rec)


    session.commit()

print("✅ users & repositories 테이블에 데이터가 채워졌습니다.")
