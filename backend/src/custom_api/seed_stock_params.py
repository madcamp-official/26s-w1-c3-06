"""Stock_Params에 종목별 GBM 파라미터(mu, sigma, r, K)를 채우는 1회성 시드 스크립트.
seed_prices.py와 동일한 위치/실행 방식: `python3 seed_stock_params.py`를 custom_api 디렉터리에서 실행.
이미 Stock_Params에 데이터가 있으면 아무것도 하지 않는다(재실행 안전).

price_generator.py는 이 표의 Mu/Sigma로 하루 안에서 10초 간격 시세를 생성한다.
"""
import random

import account
import stock

# 위험 없는 이자율(r)은 종목별로 다를 이유가 없어서 전 종목 동일하게 둔다.
RISK_FREE_RATE = 0.035


def run():
    if account.session.query(stock.StockParams).count() > 0:
        print("Stock_Params already has data, skipping seed.")
        return

    stocks = account.session.query(stock.StockEntry).all()

    count = 0
    for s in stocks:
        latestPrice = stock.CurrentPrice(s.Stock_Code) or 50000

        mu = round(random.uniform(-0.05, 0.15), 6)      # 연 5% 손실 ~ 15% 성장
        sigma = round(random.uniform(0.15, 0.45), 6)    # 연 15% ~ 45% 변동성
        k = latestPrice                                  # 참고 기준가 = 현재 종가

        account.session.add(stock.StockParams(
            Stock_Code=s.Stock_Code, Mu=mu, Sigma=sigma, R=RISK_FREE_RATE, K=k,
        ))
        count += 1

    account.session.commit()
    print(f"Seeded params for {count} stocks.")


if __name__ == "__main__":
    run()
