# 보안 정책 (Security Policy)

이 문서는 보안 취약점 신고 방법과 프로젝트의 대응 절차를 안내합니다.

---

## 지원 버전 (Supported Versions)
아래 브랜치 및 릴리즈에 대해 보안 업데이트를 제공합니다.  
- **master** (최신 릴리즈)  

---

## 취약점 신고 방법 (Reporting a Vulnerability)
보안 이슈는 **비공개**로 신고해 주세요.  
아래 이메일 주소로 다음 정보를 포함해 연락 바랍니다:

macqueen0987@cau.ac.kr

- 취약점 상세 설명 및 영향 범위  
- 재현 단계 (Steps to reproduce)  
- PoC(Proof of Concept) 코드나 로그 (가능한 경우)  
- 연락 가능한 이메일 또는 기타 연락처  

> ⚠️ 공개 GitHub 이슈로 신고하지 마세요. 보안 문제는 반드시 비공개 채널로 접수해야 합니다.

---

## 대응 절차 (Our Response)
1. **접수 확인**  
   48시간 이내에 수신 사실을 회신합니다.  
2. **초기 분석 및 우선순위 지정**  
   72시간 이내에 취약점 심각도 평가 및 대응 일정을 안내합니다.  
3. **패치 준비**  
   주요 패치 또는 완화 조치를 7일 이내에 제공하도록 노력합니다.  
4. **공개 배포**  
   패치 릴리즈 후 공개 공지 및 CVE 할당(필요 시)을 진행합니다.

---

## 자격 증명 관리 (Credential Management)
- 모든 비밀(Discord 봇 토큰, Notion API 토큰 등)은 환경 변수로 관리하세요.  
- 코드나 문서에 하드코딩하지 마십시오.  
- 비밀이 유출된 경우 즉시 토큰을 폐기(rotating)하고 운영진에게 알리세요.

---

## 추가 자료 (Additional Resources)
- [GitHub 보안 권고 사항](https://docs.github.com/ko/code-security/security-advisories/about-security-advisories)  
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)  
- [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct.