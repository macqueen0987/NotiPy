# Notipy

**Notipy**는 Notion 데이터베이스를 모니터링하여 특정 조건이 충족되면 Discord 채널에 알림을 전송하는 Python 기반 Discord 봇입니다. 일정, 태스크 관리, 이슈 트래킹 등 다양한 협업 시나리오에서 실시간 알림 도구로 활용할 수 있습니다.

## ✨ 주요 기능

- Notion 데이터베이스 실시간 모니터링
- 새 항목 추가, 상태 변화 등 감지
- Discord 채널로 정형화된 메시지 전송
- 중복 전송 방지를 위한 캐싱 시스템 내장
- 다중 서버 대응 가능 (멀티 채널 알림 설정 가능)

---

## 🐳 Docker로 실행하기

도커 환경에서 쉽게 실행할 수 있도록 `Dockerfile`과 `docker-compose.yml`이 제공됩니다.

### 1. `.env` 파일 생성

`notipy` 루트 디렉토리에 다음 내용을 포함하는 `.env` 파일을 만듭니다:

```env
DISCORD_TOKEN=your_discord_bot_token
NOTION_TOKEN=your_notion_integration_token
DATABASE_ID=your_notion_database_id
```
### 2. Docker 이미지 빌드 및 네트워크 생성

```bash
docker build -t notipy .
docker network create nginx-proxy
docker network create notipy_backend
```
### 3. Docker 컨테이너 실행
```bash
docker compose up -d
```

---

## 🤝 Contributing

Notipy는 오픈소스 프로젝트로, 누구든지 기여할 수 있습니다.

기여 전 다음 사항을 확인해주세요:

### 🧩 기여 방법

1. 이 저장소를 **Fork**합니다.
2. 새로운 브랜치를 생성합니다:  
    ```bash
    git checkout -b dev/your-feature-name
    ```
3. 원하는 기능을 추가하거나 버그를 수정합니다.
4. Pull Request를 생성합니다.
    - PR 제목은 `[기능] 기능명` 또는 `[버그] 버그명` 형식으로 작성합니다.
    - PR 설명에는 변경 사항, 관련 이슈 번호, 테스트 방법 등을 포함합니다.
    - PR은 `dev/main` 브랜치로 생성합니다.
5. 기여한 내용을 설명하는 PR 템플릿을 작성합니다.   
    - 이때 코드는 자동으로 포맷팅됩니다.