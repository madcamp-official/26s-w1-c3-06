document.addEventListener("DOMContentLoaded", async () => {
  const id = localStorage.getItem("id");
  if (!id) {
    window.location.href = "index.html";
    return;
  }

  try {
    const res = await fetch(`http://localhost:5000/history?userId=${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error("거래 내역을 불러오지 못했습니다");

    const data = await res.json();
    if (data.status !== "success") throw new Error(data.message || "거래 내역을 불러오지 못했습니다");

    renderHistory(data.history);
  } catch (err) {
    console.error(err);
    renderHistory([]);
  }
});

/**
 * @param {Array} history - {type, stockName, quantity, amount, order_date} 목록
 *   order_date: DB에 저장된 실제 날짜(YYYY-MM-DD) 그대로 -> 계산 없이 포맷만 해서 표시
 */
function renderHistory(history) {
  const listEl = document.getElementById("historyList");

  if (!history || history.length === 0) {
    listEl.innerHTML = `<p class="card-caption">아직 거래 내역이 없어요.</p>`;
    return;
  }

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
