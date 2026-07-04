document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체
  // type은 "buy"(매수) 또는 "sell"(매도)만 사용 — 기본소득 등 다른 항목은 여기 안 넣음
  const mockHistory = [
    { date: "0월 0일", type: "sell", stockName: "삼성전자", quantity: "1주", amount: 300000 },
    { date: "0월 0일", type: "buy", stockName: "삼성전자", quantity: "1주", amount: 300000 },
  ];

  renderHistory(mockHistory);
});

function renderHistory(history) {
  const listEl = document.getElementById("historyList");

  listEl.innerHTML = history.map(item => {
    const tagLabel = item.type === "buy" ? "매수" : "매도";
    const tagClass = item.type === "buy" ? "buy" : "sell";

    return `
      <div class="history-row">
        <span class="history-date">${item.date}</span>
        <div class="history-content">
          <span class="trade-tag ${tagClass}">${tagLabel}</span>
          <span class="history-stock-name">${item.stockName}</span>
        </div>
        <span class="align-right history-quantity">${item.quantity}</span>
        <span class="align-right history-amount">${item.amount.toLocaleString()}</span>
      </div>
    `;
  }).join("");
}
