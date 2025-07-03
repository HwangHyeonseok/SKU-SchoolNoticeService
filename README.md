<div align="center">
<h2>📢디스코드를 활용한 성결대학교 공지사항 알리미 서비스📢</h2>
매번 확인하기 번거로운 공지사항, 이제 알림으로 전달받자!<br><br>

<img src="https://github.com/user-attachments/assets/a559e709-8e03-4db2-929a-871b75b11ad6" alt="project_intro" />
</div>

## 👩‍🏫 프로젝트 발표 영상
https://github.com/user-attachments/assets/6bb9dbb7-6b9c-44b9-920b-6786f2173b5d

## 👨‍👩‍👧‍👦 팀원 구성

<div align="center">

| **황현석** | **정윤지** |
| :------: |  :------: |
| [<img src="https://avatars.githubusercontent.com/HwangHyeonseok" height=150 width=150> <br/> @HwangHyeonseok](https://github.com/HwangHyeonseok)<br>서비스 기획<br>이해관계자(교직원) 커뮤니케이션<br>구현 및 배포, 유지운영 | [<img src="https://avatars.githubusercontent.com/yooonzi040" height=150 width=150> <br/> @yooonzi040](https://github.com/yooonzi040)<br>홍보용 카드뉴스 제작<br>대외 홍보<br>PPT 디자인 제작 |

</div>

<br>

## 📅 개발 개요
- 개발 기간 : 2024.03~2024.08
- 서비스 기간 : 2024.03.29~2025.05.17
- 기술 스택
<div style="display: flex; justify-content: space-evenly; flex-wrap: wrap;">
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white">
  <img src="https://img.shields.io/badge/discord-5865F2?style=for-the-badge&logo=discord&logoColor=white">
  <img src="https://img.shields.io/badge/Google%20Cloud%20Platform-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white">
</div>

## 💡 기획 계기
- 대학 입장 : 비교과 프로그램 홍보에 비용 발생 (SMS, 카카오톡 알림 1회 당 8~80원)
- 학생 입장 : 매번 홈페이지에 들어가서 공지를 확인하는 것이 번거롭다는 문제
![develop_motivation](https://github.com/user-attachments/assets/fe70fb42-f0bd-43a7-9a9a-b45515f34f6d)

- --> 교내 공지사항 알리미 서비스를 만들면 한 달 1~2만원 내외의 유지 비용으로 공지사항 안내 서비스 가능 (디스코드 채널 1개당 최대 수용 인원 10,000명)

## ✅ 기획 고려사항
### 알림 플랫폼 선정 -> 디스코드(Discord) 플랫폼 선정
- 유지 운영 비용이 24시간 서버 비용만 발생함 (알림을 보내기 위한 다른 비용 발생 X)
- 대학생 팀프로젝트로 자주 사용하는 플랫폼
- PC, Mobile 모든 환경에서 접속 및 알림 가능
![platform_choose](https://github.com/user-attachments/assets/b2a5fb20-a6fa-4278-95d5-d539a85269a0)


### 시스템 도입 이점
**- 비용 절감**
- 알리미 서비스 한 달 운영 비용 : 10,000~20,000원
- 홍보를 위한 SMS,카카오톡 메시지 전송 : 한 건당 8~80원

[서비스 도입 이전 한 달 홍보 비용]
게시물 개수 : 한 달 운영 시 '비교과' 탭 평균 공지 게시 횟수 5.42건 * 12개 게시판 = 65.04건
SMS/카카오톡 메시지 전송 비용 : 최소치 8원
성결대학교 재학생 수 : 약 7,000명
한 달 게시물 홍보 비용 : 65.04 * 8 * 7000 = **3,642,240**원

[서비스 도입 이후 한 달 홍보 비용]
서비스 운영 비용 : 10,000~**20,000**원

### Risk
**- Q1. 무분별하게 스크래핑하면 홈페이지 서버에 부담을 주는 행위 아닌가요?**
<br>A. 20분마다 정보를 수집하는 방식을 사용하고 있어 서버 부담을 줄이고 있습니다. 1년 넘게 해당 서비스를 가동하면서 홈페이지에 문제가 발생한 적은 없었습니다.
<br>
![image](https://github.com/user-attachments/assets/19342d1b-c82a-477d-b825-574841b96f8e)

**- Q2. 디스코드는 해외 서버인데, 학교의 중요한 정보가 넘어갈 수 있는 것 아닌가요?**
<br>A. 공지사항 알림을 위한 최소 정보만 스크래핑합니다. 게시글의 제목과 URL만 수집하고 홈페이지에 공개된 정보만 스크래핑하여 학교 홈페이지의 자원 사용을 최소화하고 보안 리스크를 최소화 하였습니다.
 
## 🧩 시스템 아키텍처
![architecture](https://github.com/user-attachments/assets/416ac74b-c5f7-4425-b90c-aafcc03b9d2f)

## ⚙️ 주요 기능
### 공지사항 크롤링 및 알림
- 새로운 공지사항을 크롤링하여 Discord 채널로 알림을 보냅니다.

|<img src="https://github.com/user-attachments/assets/b79f4279-434b-4c22-800a-690c6255bb08" alt="mobile_alert" height="auto" width="600px" />|<img src="https://github.com/user-attachments/assets/8359d44e-bc7e-488c-a04a-18600eb7e8a0" alt="dalmuti_ingame" height="auto" width="600px" />|
|:---:|:---:|
|mobile|PC|

## 🏆 성과
|<img src="https://github.com/user-attachments/assets/a29f1111-55b6-424d-b23d-d380b5effd3b" alt="dalmuti_intro_logic" height="auto" width="500px"/>|<img src="https://github.com/user-attachments/assets/7fbd92f2-1f50-40de-9e54-7105d8d4a3b4" alt="user_cnt_img" height="auto" width="500px"/>|<img src="https://github.com/user-attachments/assets/7ecb33d6-34e7-40bc-bff4-53885b8d0518" alt="development_document" height="auto" width="500px"/>|
|:---:|:---:|:---:|
|2024-1 창의문제해결 프로젝트 총장상(상금 100만원, 지원금 60만원)|사용자 수 264명|45장의 개발문서|

## 📝 배운점
- 프로젝트를 개발하고 유지보수 운영을 하는 과정에서 개발 문서를 작성하게 되었습니다. 개발 문서 작성 이후 이슈 해결 시간이 7일 내외로 감소했습니다. 이런 과정에서 서비스의 고객은 실사용자가 될 수도 있지만 내부 관리자도 될 수 있다는 점을 배울 수 있었습니다.
- Selenium의 `driver.quit()`으로 운영 초반 메모리 문제를 해결하는 과정에서 Google Cloud Platform 환경에서 Python 코드를 올려 동작시키고 메모리를 모니터링 하는 방법에 대해 학습하였습니다.
- 학교 관계자 입장에서 기대 효과와 Risk를 고려하고 서비스 운영을 설득하는 과정에서, 제 3자(교직원,학교 관계자)과 커뮤니케이션을 하는 과정에서 프로젝트를 만드는 사람 입장이 아닌 설득하려는 청자를 대상을 고려하여 설득해야 한다는 것을 몸소 느낄 수 있었습니다.
