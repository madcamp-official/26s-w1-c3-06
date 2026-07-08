document.addEventListener("DOMContentLoaded", async () => {
  const id = localStorage.getItem("id");
  if (!id) {
    window.location.href = "index.html";
    return;
  }

  try {
    const res = await fetch(`/api/history?id=${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error("거래 내역을 불러오지 못했습니다.");

    const data = await res.json();
    if (data.status !== "success") {
      throw new Error(data.message || "거래 내역을 불러오지 못했습니다.");
    }

    renderHistory(data.history);
  } catch (err) {
    console.error(err);
    renderHistory([]);
  }
});

/**
 * @param {Array} history - {type, stockName, quantity, amount, order_date} 목록
 */
function renderHistory(history) {
  const listEl = document.getElementById("historyList");
  if (!listEl) return;

  if (!history || history.length === 0) {
    listEl.innerHTML = `<p class="card-caption">아직 거래 내역이 없어요.</p>`;
    return;
  }

  listEl.innerHTML = history.map(item => {
    const tagLabel = item.type === "buy" ? "매수" : "매도";
    const tagClass = item.type === "buy" ? "buy" : "sell";
    const amount = Number(item.amount || 0).toLocaleString();

    return `
      <div class="history-row">
        <span class="history-date">${formatOrderDate(item.order_date)}</span>
        <div class="history-content">
          <span class="trade-tag ${tagClass}">${tagLabel}</span>
          <span class="history-stock-name">${item.stockName || "-"}</span>
        </div>
        <span class="align-right history-quantity">${Number(item.quantity || 0).toLocaleString()}주</span>
        <span class="align-right history-amount">${amount}원</span>
      </div>
    `;
  }).join("");
}

function formatOrderDate(orderDate) {
  if (!orderDate) return "-";

  const date = new Date(orderDate);
  if (Number.isNaN(date.getTime())) return orderDate;

  return `${date.getMonth() + 1}월 ${date.getDate()}일`;
}
