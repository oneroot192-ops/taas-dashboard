"""
TAAS API 데이터 수집 스크립트
API 키 발급 후 이 스크립트가 실제 데이터를 수집합니다.
GitHub Actions에서 자동 실행됩니다.
"""

import os
import requests
import pandas as pd
from datetime import datetime

API_KEY = os.environ.get("TAAS_API_KEY", "")
OUTPUT_PATH = "data/drunk_driving_accidents.csv"


def fetch_taas_data(year: int) -> list[dict]:
    """공공데이터포털 교통사고 API 호출 (API 키 발급 후 활성화)"""
    if not API_KEY:
        print("⚠️  API 키 없음 — 샘플 데이터 유지")
        return []

    url = "https://apis.data.go.kr/B552061/trafficAccidentDeath/getTrafficAccidentDeath"
    params = {
        "serviceKey": API_KEY,
        "pageNo": 1,
        "numOfRows": 1000,
        "year": year,
        "accidentType": "음주",  # 음주운전 필터
        "type": "json",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("items", {}).get("item", [])


def main():
    current_year = datetime.now().year
    rows = []

    for year in range(current_year - 4, current_year + 1):
        items = fetch_taas_data(year)
        for item in items:
            rows.append({
                "사고년도": item.get("year", year),
                "시도": item.get("sido", ""),
                "시군구": item.get("sigungu", ""),
                "사고건수": int(item.get("accidentCount", 0)),
                "사망자수": int(item.get("deathCount", 0)),
                "부상자수": int(item.get("injuryCount", 0)),
                "중상자수": int(item.get("seriousInjuryCount", 0)),
                "경상자수": int(item.get("minorInjuryCount", 0)),
                "위도": float(item.get("lat", 0)),
                "경도": float(item.get("lon", 0)),
            })

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"✅ {len(df)}건 저장 완료 → {OUTPUT_PATH}")
    else:
        print("ℹ️  새 데이터 없음 — 기존 파일 유지")


if __name__ == "__main__":
    main()
