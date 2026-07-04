document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체
  const mockStocks = [
    { name: "카카오", desc: "메신저 / 콘텐츠 서비스 회사", price: 41200, changePct: 0.0 },
    { name: "기업명", desc: "기업 설명", price: null, changePct: null },
    { name: "기업명", desc: "기업 설명", price: null, changePct: null },
    { name: "기업명", desc: "기업 설명", price: null, changePct: null },
    { name: "기업명", desc: "기업 설명", price: null, changePct: -8.3 },
    { name: "기업명", desc: "기업 설명", price: null, changePct: null },
    { name: "기업명", desc: "기업 설명", price: null, changePct: -8.3 },
  ];

  renderStockList(mockStocks);

  document.getElementById("searchInput").addEventListener("input", (e) => {
    const keyword = e.target.value.trim();
    const filtered = mockStocks.filter(s => s.name.includes(keyword));
    renderStockList(filtered);
  });
});

function renderStockList(stocks) {
  const listEl = document.getElementById("stockList");

  listEl.innerHTML = stocks.map(stock => {
    const priceText = stock.price !== null ? stock.price.toLocaleString() + "원" : "-----원";

    let changeText = "+--.-%";
    let changeClass = "up";
    if (stock.changePct !== null) {
      changeClass = stock.changePct >= 0 ? "up" : "down";
      const sign = stock.changePct >= 0 ? "+" : "";
      changeText = `${sign}${stock.changePct.toFixed(1)}%`;
    }

    return `
      <div class="stock-row">
        <div class="stock-info">
          <div class="stock-logo">로고</div>
          <div>
            <p class="stock-name">${stock.name}</p>
            <p class="stock-desc">${stock.desc}</p>
          </div>
        </div>
        <span class="stock-price">${priceText}</span>
        <span class="stock-change ${changeClass}">${changeText}</span>
      </div>
    `;
  }).join("");
}
