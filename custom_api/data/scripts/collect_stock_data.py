import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import os

HEADERS = {"User-Agent": "Mozilla/5.0"}

TARGET_STOCKS = {
    "005930": "삼성전자", "000660": "SK하이닉스", "402340": "SK스퀘어",
    "009150": "삼성전기", "005380": "현대차", "373220": "LG에너지솔루션",
    "032830": "삼성생명", "028260": "삼성물산", "207940": "삼성바이오로직스",
    "012450": "한화에어로스페이스", "105560": "KB금융", "000270": "기아",
    "055550": "신한지주", "034730": "SK", "012330": "현대모비스",
    "068270": "셀트리온", "006400": "삼성SDI", "086790": "하나금융지주",
    "010120": "LS ELECTRIC", "042660": "한화오션", "066570": "LG전자",
    "035420": "NAVER", "000810": "삼성화재", "000150": "두산",
    "009540": "HD한국조선해양", "005490": "POSCO홀딩스",
    "035720": "카카오", "259960": "크래프톤", "036570": "엔씨소프트",
    "352820": "하이브",
}

OUTPUT_DIR = "data/raw"

def get_daily_price(code, pages=3):
    all_rows = []
    for page in range(1, pages + 1):
        url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={page}"
        res = requests.get(url, headers=HEADERS)
        res.encoding = "euc-kr"
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.type2 tr")
        for row in rows:
            cols = row.select("td")
            if len(cols) == 7 and cols[0].text.strip():
                all_rows.append({
                    "date": cols[0].text.strip(),
                    "close": cols[1].text.strip().replace(",", ""),
                    "open": cols[3].text.strip().replace(",", ""),
                    "high": cols[4].text.strip().replace(",", ""),
                    "low": cols[5].text.strip().replace(",", ""),
                    "volume": cols[6].text.strip().replace(",", ""),
                })
        time.sleep(0.3)
    return pd.DataFrame(all_rows)

def collect_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_dfs = []
    for i, (code, name) in enumerate(TARGET_STOCKS.items(), start=1):
        print(f"[{i}/{len(TARGET_STOCKS)}] {name}({code}) 수집 중...")
        try:
            df = get_daily_price(code, pages=3)
            if df.empty:
                print(f"  ⚠️ {name}: 데이터 없음")
                continue
            df["code"] = code
            df["name"] = name
            df.to_csv(f"{OUTPUT_DIR}/{code}_{name}.csv", index=False, encoding="utf-8-sig")
            all_dfs.append(df)
        except Exception as e:
            print(f"  ❌ {name} 실패: {e}")
        time.sleep(0.5)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv(f"{OUTPUT_DIR}/all_stocks_naver.csv", index=False, encoding="utf-8-sig")
    print(f"\n완료! 총 {len(all_dfs)}개 종목, {len(combined)}행")

if __name__ == "__main__":
    collect_all()
