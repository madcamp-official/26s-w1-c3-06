document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체 (설명은 계속 getStockDesc로 보충)
  const mockStocks = [
    { name: "삼성전자", price: 72300, changePct: 2.3 },
    { name: "SK하이닉스", price: 184300, changePct: 0.9 },
    { name: "SK스퀘어", price: 1256000, changePct: 1.87 },
    { name: "삼성전기", price: 2680000, changePct: -3.2 },
    { name: "현대차", price: 231500, changePct: 4.1 },
    { name: "LG에너지솔루션", price: 412000, changePct: -1.1 },
    { name: "삼성생명", price: 118000, changePct: 2.8 },
    { name: "삼성물산", price: 156000, changePct: 0.4 },
    { name: "삼성바이오로직스", price: 1050000, changePct: 1.2 },
    { name: "한화에어로스페이스", price: 890000, changePct: 5.6 },
    { name: "KB금융", price: 98000, changePct: 0.2 },
    { name: "기아", price: 112000, changePct: 3.1 },
    { name: "신한지주", price: 62000, changePct: 0.6 },
    { name: "SK", price: 178000, changePct: -0.8 },
    { name: "현대모비스", price: 265000, changePct: 1.9 },
    { name: "셀트리온", price: 189000, changePct: 2.5 },
    { name: "삼성SDI", price: 402000, changePct: -2.1 },
    { name: "하나금융지주", price: 68000, changePct: 0.3 },
    { name: "LS ELECTRIC", price: 298000, changePct: 4.4 },
    { name: "한화오션", price: 78000, changePct: 3.8 },
    { name: "LG전자", price: 118000, changePct: 6.2 },
    { name: "NAVER", price: 198700, changePct: 1.8 },
    { name: "삼성화재", price: 412000, changePct: 0.9 },
    { name: "두산", price: 289000, changePct: 5.9 },
    { name: "HD한국조선해양", price: 178000, changePct: 2.2 },
    { name: "POSCO홀딩스", price: 342000, changePct: -1.4 },
    { name: "카카오", price: 41200, changePct: 0.0 },
    { name: "크래프톤", price: 268000, changePct: 0.5 },
    { name: "엔씨소프트", price: 156800, changePct: 1.2 },
    { name: "하이브", price: 213000, changePct: -0.5 },
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
    const priceText = stock.price.toLocaleString() + "원";
    const changeClass = stock.changePct >= 0 ? "up" : "down";
    const sign = stock.changePct >= 0 ? "+" : "";
    const changeText = `${sign}${stock.changePct.toFixed(1)}%`;

    // 설명은 DB가 아니라 stock-descriptions.js의 매핑에서 가져옴
    const desc = getStockDesc(stock.name);

    return `
      <div class="stock-row" data-stock-name="${stock.name}">
        <div class="stock-info">
          <div class="stock-logo">로고</div>
          <div>
            <p class="stock-name">${stock.name}</p>
            ${desc ? `<p class="stock-desc">${desc}</p>` : ""}
          </div>
        </div>
        <span class="stock-price">${priceText}</span>
        <span class="stock-change ${changeClass}">${changeText}</span>
      </div>
    `;
  }).join("");

  listEl.querySelectorAll(".stock-row").forEach(row => {
    row.addEventListener("click", () => {
      const stockName = row.dataset.stockName;
      window.location.href = `stock-detail.html?stock=${encodeURIComponent(stockName)}`;
    });
  });
}