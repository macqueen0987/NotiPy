# Contributing to Notipy

먼저 Notipy에 관심을 가져주셔서 감사합니다!

이 프로젝트는 Notion과 Discord를 연동하는 실시간 알림 시스템입니다. 오픈소스로 공개되어 있으므로 누구나 기능을 개선하거나 버그를 수정하며 함께 발전시킬 수 있습니다.

---

## 📌 기본 원칙

- 모든 기여는 `dev/main` 브랜치로 Pull Request를 보내야 합니다.
- 코드 스타일은 프로젝트 내의 기존 코드와 일관되게 유지해주세요.
- PR 생성 시 **변경 사항 요약, 관련 이슈, 테스트 방법**을 포함해 주세요.
- **자동 포맷팅**이 적용되므로, 코드 스타일은 자동으로 정리됩니다.

---

## 🧩 기여 흐름

1. 이 저장소를 Fork 합니다.
2. 자신의 Fork에서 브랜치를 생성합니다. (`feature/기능명`, `fix/버그명` 등의 형식 권장)
3. 기능을 추가하거나 버그를 수정합니다.
4. 변경 사항을 커밋하고 푸시합니다.
5. Pull Request를 생성합니다.
    - 제목 예시: `[기능] 디스코드 OAuth 연동 개선`, `[버그] 페이지 변경 감지 오류 수정`
    - 가능한 한 상세한 설명 부탁드립니다.

---

## 🧪 개발 환경 준비

이 프로젝트는 `Docker` 기반으로 실행됩니다. 다음 명령어를 참고하세요:

```bash
# 이미지 빌드 및 네트워크 구성
docker build -t notipy .
docker network create nginx-proxy
docker network create notipy_backend

# 컨테이너 실행
docker compose up database backend discordbot -d
```

`.env` 파일은 `var.env.example`을 참고하여 생성하세요. 기여 전 개발 환경에서 충분히 테스트해주세요.

---

## 🧠 기타 참고사항

* **Notion Integration 토큰**은 개인별로 발급되어야 합니다. 테스트 시 주의하세요.
* PR 생성 후 리뷰 요청이 필요할 경우 Discord 지원 서버에서 문의해주세요.
* 본 프로젝트는 Apache 2.0 라이선스를 따릅니다.

---

## 🙋 도움이 필요하신가요?

* [Discord 지원 서버](https://discord.gg/HzAnBSCN7t)
* 또는 공식 GitHub 저장소 이슈를 통해 남겨주세요.
