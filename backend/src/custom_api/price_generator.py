"""실시간(모의) 주가 생성기.

Geometric Brownian Motion(GBM)으로 종목별 시세를 1초 간격으로 갱신한다:

    S(t + dt) = S(t) * exp((mu - 0.5 * sigma**2) * dt + sigma * sqrt(dt) * Z)

mu/sigma는 Stock_Params에 저장된 연 단위(annualized) 값이고, dt는 "1초를 1년의 몇 분의 1로
볼 것인가"로 변환한 값이다. 즉 실제 달력상 하루 안에서 1초마다 아주 작은 스텝을 계속 쌓아가는
방식이라, 하루가 지나는 동안 그래프가 자연스럽게 흔들린다.

하루 롤오버: 그날의 첫 틱에서 Stock_DailyPrice에 그 날짜 행이 없으면, 전날의 마지막 Close를
그 날의 새로운 Open(S0)으로 삼아 새 행을 만든다. 그 뒤로는 매 틱마다 같은 행의
Close(=최신 시세)/High/Low/Volume만 갱신한다 (하루에 한 번이 아니라 하루 안에서 계속 갱신됨).

실행: `python3 price_generator.py`를 custom_api 디렉터리에서 실행 (main.py와는 별개의 프로세스로
계속 떠 있어야 한다. main.py처럼 Ctrl+C로 종료할 때까지 무한 루프를 돈다).
"""
import math
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import account
import stock

KST = ZoneInfo("Asia/Seoul")

SECONDS_PER_TICK = 1
YEAR_SECONDS = 365 * 24 * 3600
DT_YEARS = SECONDS_PER_TICK / YEAR_SECONDS  # 1초를 연 단위 시간으로 환산


def TodayMidnight():
    ''' seed_prices.py가 Trade_Date에 쓰는 것과 같은 KST 자정 기준(tz-aware) '''
    return datetime.now(KST).replace(hour=0, minute=0, second=0, microsecond=0)


def NextPrice(currentPrice, mu, sigma):
    z = random.gauss(0, 1)
    drift = (mu - 0.5 * sigma * sigma) * DT_YEARS
    shock = sigma * math.sqrt(DT_YEARS) * z
    return currentPrice * math.exp(drift + shock)


def TickStock(stockCode, params):
    ''' 종목 하나를 한 스텝(1초치) 전진시킨다. 오늘 행이 없으면 전날 종가를 시가로 새로 만든다. '''
    today = TodayMidnight()

    todayRow = account.session.get(stock.StockPriceEntry, (today, stockCode))
    if not todayRow:
        prevRow = (
            account.session.query(stock.StockPriceEntry)
            .filter(stock.StockPriceEntry.Stock_Code == stockCode, stock.StockPriceEntry.Trade_Date < today)
            .order_by(stock.StockPriceEntry.Trade_Date.desc())
            .first()
        )
        openPrice = prevRow.Close if prevRow else max(1, round(float(params.K) or 50000))

        todayRow = stock.StockPriceEntry(
            Trade_Date=today, Stock_Code=stockCode,
            Open=openPrice, High=openPrice, Low=openPrice, Close=openPrice, Volume=0,
        )
        account.session.add(todayRow)
        account.session.flush()

    newPrice = max(1, round(NextPrice(todayRow.Close, float(params.Mu), float(params.Sigma))))
    todayRow.Close = newPrice
    todayRow.High = max(todayRow.High, newPrice)
    todayRow.Low = min(todayRow.Low, newPrice)
    todayRow.Volume = (todayRow.Volume or 0) + random.randint(100, 3000)

    return newPrice


def TickAll():
    stocks = account.session.query(stock.StockEntry).all()
    paramsByCode = {p.Stock_Code: p for p in account.session.query(stock.StockParams).all()}

    updated = 0
    for s in stocks:
        params = paramsByCode.get(s.Stock_Code)
        if not params:
            continue
        TickStock(s.Stock_Code, params)
        updated += 1

    account.session.commit()
    return updated


def run():
    print(f"[price_generator] starting, {SECONDS_PER_TICK}s per tick")
    while True:
        try:
            updated = TickAll()
            print(f"[price_generator] {datetime.now(KST).strftime('%H:%M:%S')} ticked {updated} stocks")
        except Exception as e:
            account.session.rollback()
            print(f"[price_generator] tick failed: {e}")
        time.sleep(SECONDS_PER_TICK)


if __name__ == "__main__":
    run()
