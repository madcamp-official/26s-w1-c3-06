"""Stock_DailyPrice에 더미 시세(OHLCV)를 채우는 1회성 시드 스크립트.
seed_news.py와 동일한 위치/실행 방식: `python3 seed_prices.py`를 custom_api 디렉터리에서 실행.
이미 Stock_DailyPrice에 데이터가 있으면 아무것도 하지 않는다(재실행 안전).

실제 시세 API로 교체할 때는 이 스크립트만 걷어내고, Stock_DailyPrice에 같은 구조로
(Trade_Date, Stock_Code, Open, High, Low, Close, Volume) 데이터를 채우기만 하면
account.py의 /stock-list, /stock-detail, /order가 그대로 동작한다.
"""
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import account
import stock

KST = ZoneInfo("Asia/Seoul")
TRADING_DAYS = 10  # 오늘 포함 최근 10거래일치 생성

# 오늘(가장 최근) 종가로 쓸 기준가. frontend/js/trading.js의 mock 데이터와 동일한 값을 사용해서
# 화면에서 보던 가격대와 어색하지 않게 맞춘다.
ANCHOR_PRICE = {
    "삼성전자": 72300, "SK하이닉스": 184300, "SK스퀘어": 1256000, "삼성전기": 2680000,
    "현대차": 231500, "LG에너지솔루션": 412000, "삼성생명": 118000, "삼성물산": 156000,
    "삼성바이오로직스": 1050000, "한화에어로스페이스": 890000, "KB금융": 98000, "기아": 112000,
    "신한지주": 62000, "SK": 178000, "현대모비스": 265000, "셀트리온": 189000,
    "삼성SDI": 402000, "하나금융지주": 68000, "LS ELECTRIC": 298000, "한화오션": 78000,
    "LG전자": 118000, "NAVER": 198700, "삼성화재": 412000, "두산": 289000,
    "HD한국조선해양": 178000, "POSCO홀딩스": 342000, "카카오": 41200, "크래프톤": 268000,
    "엔씨소프트": 156800, "하이브": 213000,
}


def run():
    if account.session.query(stock.StockPriceEntry).count() > 0:
        print("Stock_DailyPrice already has data, skipping seed.")
        return

    stocks = account.session.query(stock.StockEntry).all()
    today = datetime.now(KST).replace(hour=0, minute=0, second=0, microsecond=0)

    count = 0
    for s in stocks:
        anchor = ANCHOR_PRICE.get(s.Stock_Name, 50000)

        # today부터 거꾸로 랜덤워크를 만든 뒤 날짜순으로 뒤집어서, anchor가 정확히 "오늘 종가"가 되게 한다.
        closes = [anchor]
        for _ in range(TRADING_DAYS - 1):
            prevClose = closes[-1] / (1 + random.uniform(-0.03, 0.03))
            closes.append(round(prevClose))
        closes.reverse()

        for i, close in enumerate(closes):
            tradeDate = today - timedelta(days=(TRADING_DAYS - 1 - i))
            open_ = closes[i - 1] if i > 0 else close
            high = int(max(open_, close) * random.uniform(1.0, 1.02))
            low = int(min(open_, close) * random.uniform(0.98, 1.0))
            volume = random.randint(10000, 500000)

            account.session.add(stock.StockPriceEntry(
                Trade_Date=tradeDate,
                Stock_Code=s.Stock_Code,
                Open=int(open_),
                High=high,
                Low=low,
                Close=close,
                Volume=volume,
            ))
            count += 1

    account.session.commit()
    print(f"Seeded {count} daily price rows across {len(stocks)} stocks.")


if __name__ == "__main__":
    run()
