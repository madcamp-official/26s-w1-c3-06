"""data/news.json을 News_List / News_Related / (필요시) Stock_List에 적재하는 1회성 시드 스크립트.
seed_quiz.py와 동일한 위치/실행 방식: `python3 seed_news.py`를 custom_api 디렉터리에서 실행.
이미 News_List에 데이터가 있으면 아무것도 하지 않는다(재실행 안전).
"""
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

    if account.session.query(news.NewsEntry).count() > 0:
        print("News_List already has data, skipping seed.")
        return

    stock_names = sorted(set(a["stock_name"] for a in articles))

    # Stock_List의 PK는 이제 Stock_Code라, 이름으로 뉴스를 다는 이 스크립트는 먼저 이름->코드를
    # 알아야 한다. 기사에 나온 종목인데 아직 Stock_List에 없으면 새 코드를 배정해서 추가한다.
    name_to_code = {s.Stock_Name: s.Stock_Code for s in account.session.query(stock.StockEntry).all()}
    next_code = max(name_to_code.values(), default=0) + 1
    for name in stock_names:
        if name not in name_to_code:
            account.session.add(stock.StockEntry(Stock_Code=next_code, Stock_Name=name))
            name_to_code[name] = next_code
            next_code += 1
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
