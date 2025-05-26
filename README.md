# Notipy
Notipy는 Notion 데이터베이스를 모니터링하여 특정 조건이 충족되면 Discord 채널에 알림을 전송하는 Python 기반 Discord 봇입니다. 일정, 태스크 관리, 이슈 트래킹 등 다양한 협업 시나리오에서 실시간 알림 도구로 활용할 수 있습니다.     
FastAPI 기반의 백엔드 서버와 SQLAlchemy ORM을 통해 구조적으로 관리되며, Notion API 및 Discord 인터랙션 시스템과의 연계를 지원합니다.    

## ✨ 주요 기능
### 📌 Notion 웹훅 수신 및 처리
- Notion에서 발생하는 페이지 생성, 수정, 삭제 등의 이벤트를 웹훅을 통해 수신하고, 해당 정보를 Discord 채널로 전송합니다.
- 포럼 채널 내 스레드 생성 또는 기존 메시지 업데이트 기능을 지원합니다.
- 페이지와 스레드 간의 연동 정보를 데이터베이스에 저장해 알림의 지속적 연결성을 유지합니다.

### 🗃️ Notion 데이터베이스 연동
- 사용자가 등록한 Notion 데이터베이스의 페이지 속성들을 동기화하여 알림의 필터링 조건이나 출력 메시지로 활용합니다.
- 페이지 내용 변경 여부를 감지하고, 변경된 페이지에 대한 정보를 Discord에 주기적으로 갱신할 수 있습니다.
- 서버별로 다중 데이터베이스 연결을 지원합니다.

### 🧠 GitHub 프로필 분석 및 요약
- 사용자가 제공한 GitHub URL 기반으로 프로필 데이터를 수집하고, LLM을 활용해 핵심 정보를 요약합니다.
- 요약된 결과는 Discord 상에서 자신이 허용한 경우 다른 사용자가 조회할 수 있습니다.

### 🛠️ 프로젝트 생성 및 관리
- 사용자는 Discord 명령어 또는 인터랙션을 통해 새로운 프로젝트를 생성할 수 있습니다.
- 생성된 프로젝트는 내부적으로 서버 ID 및 사용자 ID를 기반으로 구분되며, 사용자 단위로 자신이 속한 프로젝트 목록을 확인할 수 있습니다.
- 각 프로젝트는 제목, 설명, 분류(category) 등의 메타데이터를 가지며, Discord UI를 통해 쉽게 편집 가능합니다.

### 🔒 내부 통신 보안 및 구조
- 모든 내부 API 요청은 미들웨어 혹은 데코레이터를 통해 검증되며, X-Internal-Request 헤더를 통해 Nginx에서 요청 유효성을 보장합니다.
- Docker 기반으로 구성되어 있으며, Discord 봇, 백엔드 서버, 프록시 등이 독립적으로 컨테이너화되어 네트워크 분리된 환경에서 동작합니다.


---

## 🐳 Docker로 실행하기

도커 환경에서 쉽게 실행할 수 있도록 `Dockerfile`과 `docker-compose.yml`이 제공됩니다.

### 1. `.env` 파일 생성

현재 기본적으로 `var.env.example` 파일이 제공되어 있습니다.    
이를 복서하여 `notipy` 루트 디렉토리에 다음 내용을 포함하는 `.env` 파일을 만듭니다:

✅ **수정이 반드시 필요한 값들**
| 항목                   | 설명                                                                        |
| -------------------- | ------------------------------------------------------------------------- |
| `GITHUB_TOKEN`       | GitHub Personal Access Token                                              |
| `DISCORD_TOKEN`      | Discord 봇 토큰                                                              |
| `DISCORD_CLIENT_ID`  | Discord 애플리케이션 클라이언트 ID                                                   |
| `DISCORD_SECRET`     | Discord 애플리케이션 클라이언트 Secret                                               |
| `DISCORD_DEVSERVER`  | 테스트용 Discord 서버 ID (예: `123456789012345678`)                              |
| `DISCORD_DEVELOPERS` | Discord 개발자 ID들, 쉼표로 구분 (예: `123,456,789`)                                |
| `DISCORD_OAUTH2_URL` | Discord OAuth2 인증 URL (예: `https://discord.com/api/oauth2/authorize?...`) |
| `REDIRECT_URI`       | OAuth2 인증 후 리디렉션될 URI (예: `https://yourdomain.com/discord/redirect`)      |
| `NOTION_TOKEN`       | Notion integration 토큰                                                     |
| `MYSQL_USER`         | MySQL 사용자 이름                                                              |
| `MYSQL_PASSWORD`     | MySQL 비밀번호                                                                |
| `MYSQL_DATABASE`     | 사용할 MySQL 데이터베이스 이름                                                       |

🟡 **선택적으로 수정 가능한 값들**
| 항목                   | 설명                               |
| -------------------- | -------------------------------- |
| `DISCORD_DEBUG_FILE` | 디버그 로그 파일 경로 (기본: `"debug.log"`) |
| `DISCORD_ERROR_LOG`  | 에러 로그 파일 경로 (기본: `"error.log"`)  |
| `DISCORD_PORT`       | Discord 서비스 포트 (기본: `9090`)      |
| `BACKEND_PORT`       | 백엔드 서비스 포트 (기본: `9091`)          |
| `MYSQL_TCP_PORT`     | MySQL 포트 (기본: `3306`)            |


### 2. Docker 이미지 빌드 및 네트워크 생성

```bash
docker build -t notipy .
docker network create nginx-proxy
docker network create notipy_backend
```

### 3. Docker-Compose 설정
| 위치                              | 항목                              | 설명                                                                                                                                                          |
| ------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `discordbot` → `container_name` | `notipy-discordbot`             | 필요 시 컨테이너명 변경 가능, 변경시 Docker Network 접근 URL 이 달라지니 비추천                                                                                                                                    |
| `backend` → `container_name`    | `notipy-backend`                | 이 또한 필요시 변경                                                                                                                                     |
| `database` → `volumes`          | `./database:/var/lib/mysql`     | 실제 볼륨 경로 확인 및 유지 가능                                                                                                                                         |
| `networks`                      | `nginx-proxy`, `notipy_backend` | 2번 단계에서 생성된 네트워크 이름과 일치해야함 |

이 밖에도 각종 포트번호가 var.env 파일과 일치하는지 확인  


### 3. Docker 컨테이너 실행
```bash
docker compose up -d
```
nginx, Ollama 컨테이너는 사용하지 않으실 경우 굳이 생성하실 필요는 없습니다.   

---

## 🤝 Contributing

Notipy는 오픈소스 프로젝트로, 누구든지 기여할 수 있습니다.

기여 전 다음 사항을 확인해주세요:

### 🧩 기여 방법

1. 이 저장소를 **Fork**합니다.
2. 새로운 브랜치를 생성합니다:  
3. 원하는 기능을 추가하거나 버그를 수정합니다.
4. Pull Request를 생성합니다.
    - PR 제목은 `[기능] 기능명` 또는 `[버그] 버그명` 형식으로 작성합니다.
    - PR 설명에는 변경 사항, 관련 이슈 번호, 테스트 방법 등을 포함합니다.
    - PR은 `dev/main` 브랜치로 생성합니다.
5. 기여한 내용을 설명하는 PR 템플릿을 작성합니다.   
    - 이때 코드는 자동으로 포맷팅됩니다.
