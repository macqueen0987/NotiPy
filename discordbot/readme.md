# Notipy Discord Bot

**Notipy Discord Bot**은 Notion, GitHub 등의 외부 플랫폼과 Discord 간의 연동을 담당하는 봇으로, 다양한 자동화 기능을 제공합니다. 본 봇은 FastAPI 기반 백엔드 서버와 연동되어 동작하며, Slash 명령어 및 컴포넌트 인터랙션을 통해 실시간 알림과 프로젝트 관리를 지원합니다.

## 주요 기능

- Notion 페이지 생성 및 변경 시 Discord 포럼 스레드 자동 생성 또는 갱신
- GitHub 커밋, PR 변경 시 자동 알림 전송
- 사용자별 Notion 토큰 인증 및 연결
- 서버별 다중 Notion 데이터베이스 지원
- Discord 슬래시 명령어 및 셀렉트 메뉴를 통한 사용자 상호작용 제공

## 인증 및 보안
Notion 토큰은 디스코드 서버 단위로 설정되며, 각 서버별로 데이터 접근이 분리됩니다.

Notion 및 Discord API 사용 약관에 따라 사용이 제한될 수 있습니다.

민감한 정보(예: Notion 토큰)는 추후 암호화 저장 기능 도입 예정입니다.
