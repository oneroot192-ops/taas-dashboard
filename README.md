# 🚨 음주운전 사고 분석 대시보드

TAAS(교통사고분석시스템) 데이터를 활용한 음주운전 사고 시각화 웹 대시보드입니다.

## 배포 방법 (GitHub → Streamlit Cloud)

### 1단계: GitHub에 레포 생성 및 파일 업로드
1. GitHub에서 새 레포지토리 생성 (예: `taas-dashboard`)
2. 이 폴더의 모든 파일을 업로드

### 2단계: Streamlit Cloud 배포
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. "New app" → 레포지토리 선택 → `app.py` 선택 → Deploy

### 3단계: API 키 연동 (발급 후)
1. [data.go.kr](https://data.go.kr) 에서 교통사고 API 신청
2. GitHub 레포 → Settings → Secrets → `TAAS_API_KEY` 추가
3. Actions 탭에서 `Update TAAS Data` 수동 실행

## 기능
- 전국/시도별 음주운전 사고 현황 지도 시각화
- 연도별 사고 추이 분석
- 시도별 사고건수·사망자수 비교 차트
- 핵심 지표 카드 (전년 대비 증감 포함)
