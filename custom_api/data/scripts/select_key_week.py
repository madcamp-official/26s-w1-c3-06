
"""
select_key_week.py — 30일치 크롤링 데이터에서 "전 종목 공통" 대표 1주일 구간 추출

원리:
    1. 전체 데이터에서 공통 거래일(모든 종목이 공유하는 날짜) 목록을 뽑음
    2. 5거래일 단위 슬라이딩 윈도우로 날짜 구간을 이동시키며
    3. 그 구간 동안 "전 종목 평균 변동폭(절댓값)"이 가장 큰 구간을 대표 1주일로 선정
       -> 모든 종목이 같은 날짜 범위를 공유하게 됨 (가상 시계가 전 유저 공통이므로 필수)
    4. 선정된 날짜 범위에 해당하는 전 종목 데이터를 그대로 추출해 seed_prices.csv로 저장

사용법:
    python select_key_week.py
    (data/raw/all_stocks_naver.csv를 읽어서 data/seed/seed_prices.csv 생성)
"""

import pandas as pd
import os

INPUT_PATH = "data/raw/all_stocks_naver.csv"
OUTPUT_DIR = "data/seed"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "seed_prices.csv")

WINDOW_SIZE = 5  # 1주일 = 5거래일


def find_common_best_window(df):
    """전 종목 공통 날짜 목록에서, 평균 변동폭이 가장 큰 5거래일 구간을 찾는다."""
    unique_dates = sorted(df["date"].unique())

    if len(unique_dates) < WINDOW_SIZE:
        raise ValueError(f"공통 거래일이 {len(unique_dates)}일뿐이라 {WINDOW_SIZE}일 구간을 만들 수 없습니다.")

    pivot = df.pivot_table(index="date", columns="code", values="close")

    best_start_idx = None
    best_avg_change = -1
    best_detail = None

    for start in range(0, len(unique_dates) - WINDOW_SIZE + 1):
        window_dates = unique_dates[start:start + WINDOW_SIZE]
        start_date, end_date = window_dates[0], window_dates[-1]

        start_prices = pivot.loc[start_date]
        end_prices = pivot.loc[end_date]

        valid = start_prices.notna() & end_prices.notna() & (start_prices != 0)
        change_pct = ((end_prices[valid] - start_prices[valid]) / start_prices[valid]).abs()

        if change_pct.empty:
            continue

        avg_change = change_pct.mean()

        if avg_change > best_avg_change:
            best_avg_change = avg_change
            best_start_idx = start
            best_detail = change_pct

    if best_start_idx is None:
        raise ValueError("적합한 공통 구간을 찾지 못했습니다.")

    best_window_dates = unique_dates[best_start_idx:best_start_idx + WINDOW_SIZE]
    return best_window_dates, best_avg_change, best_detail


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"], format="%Y.%m.%d")

    for col in ["close", "open", "high", "low", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    window_dates, avg_change, detail = find_common_best_window(df)

    print(f"선정된 공통 대표 1주일: {window_dates[0].date()} ~ {window_dates[-1].date()}")
    print(f"전 종목 평균 변동폭: {round(avg_change * 100, 2)}%\n")

    print("종목별 변동폭 (해당 구간 기준):")
    for code, pct in detail.sort_values(ascending=False).items():
        name = df.loc[df["code"] == code, "name"].iloc[0]
        print(f"  {name}({code}): {round(pct * 100, 2)}%")

    result = df[df["date"].isin(window_dates)].copy()
    result = result.sort_values(["code", "date"]).reset_index(drop=True)
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n완료! {result['code'].nunique()}개 종목 x {len(window_dates)}거래일 = {len(result)}행")
    print(f"저장 위치: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
