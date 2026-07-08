"""Realtime mock stock price generator.

Updates today's Stock_DailyPrice row once per second using a simple
geometric Brownian motion step. The Flask app starts this in a daemon
thread from main.py.
"""

import math
import random
import time
from collections import defaultdict, deque
from datetime import datetime
from threading import Lock
from zoneinfo import ZoneInfo

import account
import notify
import stock

KST = ZoneInfo("Asia/Seoul")

SECONDS_PER_TICK = 1
YEAR_SECONDS = 365 * 24 * 3600
DT_YEARS = SECONDS_PER_TICK / YEAR_SECONDS
STOCK_MOVE_NOTICE_THRESHOLD = 3.0
PRICE_HISTORY_SECONDS = 10 * 60
PRICE_HISTORY_MAX_POINTS = PRICE_HISTORY_SECONDS // SECONDS_PER_TICK + 1

_recent_prices = defaultdict(lambda: deque(maxlen=PRICE_HISTORY_MAX_POINTS))
_recent_prices_lock = Lock()


def RecordRecentPrice(stockCode, price, timestamp=None):
    point = {
        "timestamp": timestamp if timestamp is not None else time.time(),
        "price": price,
    }
    with _recent_prices_lock:
        _recent_prices[stockCode].append(point)


def GetRecentPrices(stockCode):
    cutoff = time.time() - PRICE_HISTORY_SECONDS
    with _recent_prices_lock:
        history = _recent_prices.get(stockCode)
        if not history:
            return []
        while history and history[0]["timestamp"] < cutoff:
            history.popleft()
        return list(history)


def TodayMidnight():
    return datetime.now(KST).replace(hour=0, minute=0, second=0, microsecond=0)


def NextPrice(currentPrice, mu, sigma):
    z = random.gauss(0, 1)
    drift = (mu - 0.5 * sigma * sigma) * DT_YEARS
    shock = sigma * math.sqrt(DT_YEARS) * z
    return currentPrice * math.exp(drift + shock)


def TickStock(db_session, stockEntry, params):
    stockCode = stockEntry.Stock_Code
    today = TodayMidnight()

    todayRow = db_session.get(stock.StockPriceEntry, (today, stockCode))
    if not todayRow:
        prevRow = (
            db_session.query(stock.StockPriceEntry)
            .filter(stock.StockPriceEntry.Stock_Code == stockCode, stock.StockPriceEntry.Trade_Date < today)
            .order_by(stock.StockPriceEntry.Trade_Date.desc())
            .first()
        )
        openPrice = prevRow.Close if prevRow else max(1, round(float(params.K) or 50000))

        todayRow = stock.StockPriceEntry(
            Trade_Date=today,
            Stock_Code=stockCode,
            Open=openPrice,
            High=openPrice,
            Low=openPrice,
            Close=openPrice,
            Volume=0,
        )
        db_session.add(todayRow)
        db_session.flush()

    newPrice = max(1, round(NextPrice(todayRow.Close, float(params.Mu), float(params.Sigma))))
    todayRow.Close = newPrice
    todayRow.High = max(todayRow.High, newPrice)
    todayRow.Low = min(todayRow.Low, newPrice)
    todayRow.Volume = (todayRow.Volume or 0) + random.randint(100, 3000)

    if todayRow.Open:
        changePct = (newPrice - todayRow.Open) / todayRow.Open * 100
        if abs(changePct) >= STOCK_MOVE_NOTICE_THRESHOLD:
            notify.NotifyStockMove(stockCode, stockEntry.Stock_Name, changePct, db_session=db_session)

    return newPrice


def TickAll():
    db_session = account.Session()
    try:
        stocks = db_session.query(stock.StockEntry).all()
        paramsByCode = {p.Stock_Code: p for p in db_session.query(stock.StockParams).all()}

        updated = 0
        generatedPrices = []
        for stockEntry in stocks:
            params = paramsByCode.get(stockEntry.Stock_Code)
            if not params:
                continue
            newPrice = TickStock(db_session, stockEntry, params)
            generatedPrices.append((stockEntry.Stock_Code, newPrice))
            updated += 1

        db_session.commit()
        timestamp = time.time()
        for stockCode, price in generatedPrices:
            RecordRecentPrice(stockCode, price, timestamp)
        return updated
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()


def run():
    print(f"[price_generator] starting, {SECONDS_PER_TICK}s per tick")
    while True:
        try:
            updated = TickAll()
            print(f"[price_generator] {datetime.now(KST).strftime('%H:%M:%S')} ticked {updated} stocks")
        except Exception as e:
            print(f"[price_generator] tick failed: {e}")
        time.sleep(SECONDS_PER_TICK)


if __name__ == "__main__":
    run()
