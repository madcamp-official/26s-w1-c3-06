# 26s-w1-c3-06

## 공통과제 I : 웹 기반 프로젝트 (2인 1팀)

**목적:** 공통 과제를 함께 수행하며 웹 개발의 전체 흐름을 빠르게 익히고 협업에 적응하기

**결과물:** 기획부터 배포까지 완료된 웹 서비스와 관련 문서 일체

---

## 팀원

| 이름 | GitHub | 역할 |
| --- | --- | --- |
|서영빈| https://github.com/izayoieosd |  |
|김혜리| https://github.com/ireyhye| |

---

## 기획안

> 프로젝트 주제, 목적, 핵심 기능, 예상 사용자, 팀원별 역할 등 정리

**주제:** 가상자산 주식 모의투자 웹서비스

**목적:** "실제 금전 손실 위험 없이 투자 원리와 시장 감각을 익히는 경제 교육 도구

**핵심 기능:** 가상계좌 생성, 실제 기업과 연동되는 주가 추종, 가상주식 매매, 수익률 확인

**예상 사용자:**주식 투자에 관심이 있으나 법령상, 재정상의 문제로 실거래가 불가능하거나, 실습 위주의 경제 학습을 체험해보고자 하는 청소년 전용

---

## 기능 명세서

> 구현할 기능을 사용자 관점에서 정리하고, 필수 기능과 선택 기능을 구분

### 필수 기능

1. **가상계좌 관리**
  - 계정 로그인 페이지
  - 계좌 현황 (계좌명, 최근 거래 내역, 수익 금액 및 수익률, 계좌 잔고) 
  - 계정에 시드 자산 지급 (계좌 생성 직후 및 일일 기본소득 지급)
  - 계정 삭제
2. **가상주식 열람**
  - 기업별 실시간 주가 연동 (과거 데이터로 대체함)
  - 기업명, 기업 로고, 티커, 현재 주가, 주가 변동분 목록화 및 표시
  - 기업 관련 뉴스 제공
  - 현재 주가, 거래대금, 거래량 표시
3. **가상주식 매매**
  - 호가창 (호가 목록, 대기중인 주문량) 표시
  - 가상주식 주문 (거래유형 (매수 / 매도), 거래 방식 (시장가 / 지정가 매매), 주문량 설정)
  - 주문 수정 (주문량 변경)
  - 주문 체결, 취소, 실패 알림 메시지 전송
4. **소셜**
  - 친구 추가/삭제
  - 친구 목록 열람
  - 일간/주간/월간 고수익 계좌 랭킹 집계 및 표시
  - 친구 요청 / 추가 / 삭제 메시지 전송
### 선택 기능

---

## IA 및 화면 설계서

> 서비스의 전체 페이지 구조와 페이지 간 이동 흐름; 각 페이지의 주요 UI 구성, 입력 요소, 버튼, 사용자 행동 흐름 등을 간단한 와이어프레임 형태로 정리

### IA (정보 구조도)

<p align="center">
  <img src="images/IA.png" width="900" alt="IA Diagram">
</p>

### 화면 설계 (Figma)
[Figma 화면 설계](https://www.figma.com/design/UA0CwwncocjZ67imzxZzoA/%EC%A0%9C%EB%AA%A9-%EC%97%86%EC%9D%8C?node-id=0-1&p=f&t=eJf0nP6BjuCCft16-0)

---

## DB 스키마

> 필요한 테이블, 주요 필드, 데이터 타입, 테이블 간 관계를 정리

<center>
  <img
    src="./public/image/proj_erd.png"
    width="90%"
  />
</center>

---

## API 문서

> API 주소, 요청 방식, 요청값, 응답값, 에러 상황을 정리

| Method | Endpoint | 설명 | 요청 | 응답 |
|---|---|---|---|---|
| account_Create | | 계좌 및 계정 생성; 기본금 1,000,000원 지급 | | |
| account_Authenticate | | 계좌 아이디 및 비밀번호 정보 일치 확인 | | |
| account_Show | | 계좌명, 보유 주식, 최근 거래 내역, 수익 금액 및 수익률, 계좌 잔고 불러오기 | | |
| account_Edit | | 계좌 정보를 변경 | | |
| account_DailyBailout | | 구제금을 요청한 계좌에서 매일 하루에 한하여 10,000원의 수익 지급. 중복 지급 요청시 거부 | | |
| account_Delete | | 계정 삭제 | | | 
| news_View | | 단일 주식의 관련 뉴스 확인 | | |
| friends_Request | | 친구 요청 발신 | | |
| friends_Show | | 친구 목록 확인 | | |
| friends_Delete | | 친구 삭제 | | |
| stock_PriceUpToDate | | 가상주식 가격을 연동 (50ms 단위) | | | 
| stock_ShowList | | 가상주식 목록 - 기업명, 기업 로고, 현재 주가, 주가 변동분 표시 (보유 주식과 검색 결과로 나온 주식 모두 적용) | | |
| stock_Search | | 주식을 기업명 일치에 의해 검색 | | |
| stock_ShowEntry | | 단일 주식의 그래프, 현재 주가 표시 | | | 
| order_Create | | 가상주식 주문 (매수 / 매도, 주문량 설정) | | |
| order_Edit | | 가상주식 주문 수정 (주문량 변경) | | |
| order_Destroy | | 가상주식 주문 취소 | | |
| order_Sign | | 주문 가격 도달시 가상주식 주문 체결 | | |
| ranking_Update | | 일간 주식 수익 랭킹 업데이트 | | |
| ranking_Show | | 일간 주식 수익 랭킹 표시 | | |
| notify_Stock | | 마지막 공지 시점으로부터 단일 주식의 주가 변화를 알림으로 공지함 | | |
| notify_Order | | 주문의 체결 성공 / 실패 / 취소를 알림으로 공지함 | | |
| notify_Friends | | 친구 요청 발신 / 수신, 친구 삭제를 알림으로 공지함 | | |
| tutorial_Terms | | 생소한 주식 관련 용어 설명 | | |
| tutorial_Dict | | 주식 용어 사전 열람 | | |

---

## 배포 결과물

> 접속 가능한 링크, 실행 방법, 주요 구현 내용

- **서비스 URL:**
- **실행 방법:**

```bash
# 실행 방법 작성
```

---

## 회고 문서

> 개발 과정에서의 어려움, 해결 방법, 역할 분담, 다음에 개선할 점 (KPT 방법론 참고)

### Keep

### Problem

### Try

---

## 참고 자료

- [SDD(스펙 주도 개발) 이해하기](https://news.hada.io/topic?id=21338)
- [Software Design Document Best Practices](https://www.atlassian.com/work-management/project-management/design-document)
- [IA 정보구조도 작성 방법](https://brunch.co.kr/@nyonyo/7)
- [기획자 화면설계서 작성법](https://brunch.co.kr/@soup/10)
- [Figma 와이어프레임 가이드](https://www.figma.com/ko-kr/resource-library/what-is-wireframing/)
- [무료 Figma 와이어프레임 키트](https://www.figma.com/ko-kr/templates/wireframe-kits/)
- [ERD/DB 설계 총정리](https://inpa.tistory.com/entry/DB-%F0%9F%93%9A-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EB%AA%A8%EB%8D%B8%EB%A7%81-%EA%B0%9C%EB%85%90-ERD-%EB%8B%A4%EC%9D%B4%EC%96%B4%EA%B7%B8%EB%9E%A8)
- [API 명세서 작성 가이드라인](https://velog.io/@sebinChu/BackEnd-API-%EB%AA%85%EC%84%B8%EC%84%9C-%EC%9E%91%EC%84%B1-%EA%B0%80%EC%9D%B4%EB%93%9C-%EB%9D%BC%EC%9D%B8)
- [좋은 README 작성하는 방법](https://velog.io/@sabo/good-readme)
- [단기 프로젝트 회고 KPT 방법론](https://velog.io/@habwa/%EB%8B%A8%EA%B8%B0-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%ED%9A%8C%EA%B3%A0-KPT-%EB%B0%A9%EB%B2%95%EB%A1%A0)
