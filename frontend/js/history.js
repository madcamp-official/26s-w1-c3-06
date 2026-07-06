document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체
  // order_date: 실제 Stock_Order.Order_Date 값 그대로 (YYYY-MM-DD)
  const mockHistory = [
    { type: "sell", stockName: "삼성전자", quantity: "1주", amount: 300000, order_date: "2026-06-02" },
    { type: "buy", stockName: "삼성전자", quantity: "1주", amount: 300000, order_date: "2026-06-01" },
  ];

  renderHistory(mockHistory);
});

/**
 * @param {Array} history - {type, stockName, quantity, amount, order_date} 목록
 *   order_date: DB의 Stock_Order.Order_Date 그대로 (YYYY-MM-DD) -> 계산 없이 그대로 표시
 */
function renderHistory(history) {
  const listEl = document.getElementById("historyList");

  listEl.innerHTML = history.map(item => {
    const tagLabel = item.type === "buy" ? "매수" : "매도";
    const tagClass = item.type === "buy" ? "buy" : "sell";

    //  DB에 저장된 실제 날짜를 그대로 포맷만 해서 표시
    const dateLabel = formatOrderDate(item.order_date);

    return `
      <div class="history-row">
        <span class="history-date">${dateLabel}</span>
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

function formatOrderDate(orderDate) {
  const date = new Date(orderDate);
  return `${date.getMonth() + 1}월 ${date.getDate()}일`;
}