"""data/news.json을 News_List / News_Related / (필요시) Stock_List에 적재하는 1회성 시드 스크립트.
seed_quiz.py와 동일한 위치/실행 방식: `python3 seed_news.py`를 custom_api 디렉터리에서 실행.
이미 News_List에 데이터가 있으면 아무것도 하지 않는다(재실행 안전).
"""

from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column


import json
from datetime import datetime
from zoneinfo import ZoneInfo

import account
import stock
import news

KST = ZoneInfo("Asia/Seoul")


def run():
    with open("data/news.json", encoding="utf-8") as f:
        articles = json.load(f)
    with open("data/seed_prices.json", encoding="utf-8") as f:
        name_to_code = json.load(f)

    if account.session.query(news.NewsEntry).count() > 0:
        print("News_List already has data, skipping seed.")
        return

    stock_names = sorted(set(a["stock_name"] for a in articles))
    for name in stock_names:
        account.session.add(stock.StockEntry(Stock_Code=name_to_code[name], Stock_Name=name))
    account.session.commit()

    ord_counters = {}
    for i, a in enumerate(articles, start=1):
        news_date = datetime.strptime(a["news_date"], "%Y-%m-%d").replace(tzinfo=KST)

        account.session.add(news.NewsEntry(
            ID=i,
            title=a["news_title"],
            body=a["news_body"],
            publisher=a["publisher"][:10],  # Publisher 컬럼이 VARCHAR(10)이라 잘라서 저장
            news_date=news_date,
        ))

        stock_code = name_to_code[a["stock_name"]]
        ord_counters[stock_code] = ord_counters.get(stock_code, 0) + 1
        account.session.add(news.StockNewsEntry(
            Related_Ord=ord_counters[stock_code],
            Stock_Code=stock_code,
            News_ID=i,
        ))

    account.session.commit()
    print(f"Seeded {len(articles)} news articles across {len(stock_names)} stocks.")


if __name__ == "__main__":
    run()
