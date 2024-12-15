# Coin-AI-Trader
Coin AI Trader - 웹페이지를 통해 코인 투자 관련 여러 기능들을 사용하고, 프로그램을 통한 코인 트레이딩을 지원한다.

<div align=center><img src="coiincat.png" height=300></div>

**팀 구성**
- 이지헌 : AI, 프론트엔드 담당
- 오진표 : 프론트엔드, 백엔드 담당
- 한준서 : Python, 서버 담당
  - ### 기술스택
    - Deploy
      - <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"> <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">

    - OS
      - <img src="https://img.shields.io/badge/amazonwebservices-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white"> <img src="https://img.shields.io/badge/linux-FCC624?style=for-the-badge&logo=linux&logoColor=black">
    - Front
      - <img src="https://img.shields.io/badge/react-61DAFB?style=for-the-badge&logo=react&logoColor=black"> <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white"> <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white"> <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=pm2&logoColor=black"> <img src="https://img.shields.io/badge/pm2-2B037A?style=for-the-badge&logo=javascript&logoColor=black"> <img src="https://img.shields.io/badge/npm-CB3837?style=for-the-badge&logo=npm&logoColor=black">

    - Back
      - <img src="https://img.shields.io/badge/java-007396?style=for-the-badge&logo=java&logoColor=white"> <img src="https://img.shields.io/badge/gradle-02303A?style=for-the-badge&logo=gradle&logoColor=white"> <img src="https://img.shields.io/badge/springboot-6DB33F?style=for-the-badge&logo=springboot&logoColor=white"> <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
    - DB
      - <img src="https://img.shields.io/badge/amazonrds-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white"> <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white">
    - AI
      - <img src="https://img.shields.io/badge/tensorflow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"> <img src="https://img.shields.io/badge/keras-D00000?style=for-the-badge&logo=keras&logoColor=white"> <img src="https://img.shields.io/badge/scikitlearn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white">

## 개발의도
- ### 주제 선정 배경
  - 암호화폐 시장의 급격한 성장
    - 최근 몇 년간 암호화폐 시장이 급격하게 성장했다. 많은 사람들이 암호화폐를 '투자 수단'으로 여기기 시작하였으며, 이에 따라 본격적으로 트레이딩을 시도하는 사람들이 늘고 있다.
  - 그에 비해 부족한 투자지식
    - 급격히 성장한 시장에 비해, 투자자들의 투자 지식은 부족한 상태이다. 한국은행의 조사에 따르면 대한민국 성인의 디지털 금융이해력은 OECD평균에 비해 상당히 낮은편이다(OECD평균 55점, 대한민국 43점). 기존 금융 시장과는 전혀 다른 디지털 금융 시장에 적응하지 못하고 있는 것이다.
- ### 필요성
  - 암호화폐 시장의 특수성에서 오는 필요성
    - 시장 거래 가능 시간이 정해져 있는 주식 시장과는 달리, 암호화폐 거래는 24시간 가능하다. 24시간동안 열려 있는 시장의 변동에 대응하기에는 휴식이 필요한 사람이 아닌 프로그램을 통한 트레이딩이 더욱 효율적이다.
- ### 기대효과
  - 효율적 투자
    - 수동으로 트레이딩을 하는 것은 준비는 물론 실행에도 많은 시간과 노력을 필요로 한다. 기존 주식시장과는 달리 24시간동안 거래가 가능한 암호화폐 시장은 이러한 점이 더욱 극대화된다. 프로그램을 통해 사용자들은 큰 노력 없이 시장의 움직임을 파악하고 효율적인 대처가 가능해진다.
  - 객관적 투자
    - 기존 주식시장보다 변동성이 더욱 강한 암호화폐 시장에서 감정을 억누르고 객관적으로 투자한다는 것은 어려운 일이다. 프로그램을 통한 자동매매 시스템은 감정을 배제하고 철저하게 데이터를 기반으로 한 매매를 수행하기 때문에 투자의 일관성, 정확성을 보장한다.

## 시연영상
https://youtu.be/lGs7OCejPG0

## 구조
<div align=center><img src="project_structure.png" height=500></div>
<div align=center><img src="project_flowchart.png" height=500></div>



## 사용
1. 웹사이트 접속 - http://coinaitrader.site/  (현재 서버 중지중)
2. 회원가입, 로그인
   <div align=center><img src="signup.png" height=500></div>
3. 투자 기능 사용  
   1. 백테스팅  
   <div align=center><img src="backtest.png" height=300></div>
   <div align=center><img src="backtest_result.png" height=377></div>
   2. 모의 투자
   <div align=center><img src="simtrade.png" height=500></div>
   <div align=center><img src="simtrade_result.png" height=318></div>
   3. 자동 매매
   <div align=center><img src="simtrade.png" height=500></div>
