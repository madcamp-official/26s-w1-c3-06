"""Seed news rows and stock-news relationships from data/news.json.

Stock names in news.json are converted to stock codes through
data/seed_prices.json before News_Related rows are inserted.
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import account
import news
import stock

KST = ZoneInfo("Asia/Seoul")
DATA_DIR = Path(__file__).resolve().parent / "data"


def run():
    with open(DATA_DIR / "news.json", encoding="utf-8") as f:
        articles = json.load(f)
    with open(DATA_DIR / "seed_prices.json", encoding="utf-8") as f:
        name_to_code = json.load(f)
    with open(DATA_DIR / "desc.json", encoding="utf-8") as f:
        name_to_desc = json.load(f)

    if account.session.query(news.NewsEntry).count() > 0:
        print("News_List already has data, skipping seed.")
        return

    stock_names = sorted(set(a["stock_name"] for a in articles))
    missing_names = [name for name in stock_names if name not in name_to_code]
    if missing_names:
        raise ValueError(f"Missing stock codes in seed_prices.json: {missing_names}")

    for name in stock_names:
        stock_code, stock_desc = name_to_code[name], name_to_desc[name]
        existing_stock = account.session.get(stock.StockEntry, stock_code)
        if existing_stock is None:
            file_path="../../../frontend/logos/" + name + ".png"
            with open(file_path, "rb") as f:
                logo_bytes = f.read()
                account.session.add(stock.StockEntry(
                    Stock_Code=stock_code,
                    Stock_Name=name,
                    Stock_Desc=stock_desc,
                    Stock_Logo=logo_bytes))
        elif not existing_stock.Stock_Name:
            existing_stock.Stock_Name = name
    account.session.commit()

    for i, a in enumerate(articles, start=1):
        stock_code = name_to_code[a["stock_name"]]
        news_date = datetime.strptime(a["news_date"], "%Y-%m-%d").replace(tzinfo=KST)

        account.session.add(news.NewsEntry(
            ID=i,
            title=a["news_title"],
            body=a["news_body"],
            publisher=a["publisher"][:10],
            news_date=news_date,
        ))

        account.session.add(news.StockNewsEntry(
            News_ID=i,
            Stock_Code=stock_code,
        ))

    account.session.commit()
    print(f"Seeded {len(articles)} news articles across {len(stock_names)} stocks.")


if __name__ == "__main__":
    run()
