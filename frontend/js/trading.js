document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체
  // 실제 API 응답에는 stock_desc 필드가 DB(Stock_List.Stock_Desc)에서 그대로 내려옴
  
  //임시...
  const mockStocks = [ 
    { name: "삼성전자", stock_desc: "반도체와 스마트폰을 만드는 회사", price: 72300, changePct: 2.3 },
    { name: "SK하이닉스", stock_desc: "반도체 메모리를 만드는 회사", price: 184300, changePct: 0.9 },
    { name: "SK스퀘어", stock_desc: "여러 IT·게임 회사에 투자하는 지주회사", price: 1256000, changePct: 1.87 },
    { name: "삼성전기", stock_desc: "전자제품 속 핵심 부품을 만드는 회사", price: 2680000, changePct: -3.2 },
    { name: "현대차", stock_desc: "자동차를 만드는 회사", price: 231500, changePct: 4.1 },
    { name: "LG에너지솔루션", stock_desc: "배터리를 만드는 회사", price: 412000, changePct: -1.1 },
    { name: "삼성생명", stock_desc: "생명보험 서비스를 하는 회사", price: 118000, changePct: 2.8 },
    { name: "삼성물산", stock_desc: "건설과 무역, 패션 사업을 하는 회사", price: 156000, changePct: 0.4 },
    { name: "삼성바이오로직스", stock_desc: "의약품을 위탁 생산하는 회사", price: 1050000, changePct: 1.2 },
    { name: "한화에어로스페이스", stock_desc: "항공기 엔진과 방위산업 장비를 만드는 회사", price: 890000, changePct: 5.6 },
    { name: "KB금융", stock_desc: "은행과 금융 서비스를 하는 지주회사", price: 98000, changePct: 0.2 },
    { name: "기아", stock_desc: "자동차를 만드는 회사", price: 112000, changePct: 3.1 },
    { name: "신한지주", stock_desc: "은행과 금융 서비스를 하는 지주회사", price: 62000, changePct: 0.6 },
    { name: "SK", stock_desc: "여러 계열사를 관리하는 지주회사", price: 178000, changePct: -0.8 },
    { name: "현대모비스", stock_desc: "자동차 부품을 만드는 회사", price: 265000, changePct: 1.9 },
    { name: "셀트리온", stock_desc: "바이오 의약품을 만드는 회사", price: 189000, changePct: 2.5 },
    { name: "삼성SDI", stock_desc: "배터리를 만드는 회사", price: 402000, changePct: -2.1 },
    { name: "하나금융지주", stock_desc: "은행과 금융 서비스를 하는 지주회사", price: 68000, changePct: 0.3 },
    { name: "LS ELECTRIC", stock_desc: "전력 설비와 전기 장비를 만드는 회사", price: 298000, changePct: 4.4 },
    { name: "한화오션", stock_desc: "선박을 만드는 회사", price: 78000, changePct: 3.8 },
    { name: "LG전자", stock_desc: "가전제품과 전자기기를 만드는 회사", price: 118000, changePct: 6.2 },
    { name: "NAVER", stock_desc: "검색과 인터넷 서비스를 하는 회사", price: 198700, changePct: 1.8 },
    { name: "삼성화재", stock_desc: "손해보험 서비스를 하는 회사", price: 412000, changePct: 0.9 },
    { name: "두산", stock_desc: "에너지·로봇·소재 사업을 하는 회사", price: 289000, changePct: 5.9 },
    { name: "HD한국조선해양", stock_desc: "선박을 만드는 회사", price: 178000, changePct: 2.2 },
    { name: "POSCO홀딩스", stock_desc: "철강을 만드는 회사", price: 342000, changePct: -1.4 },
    { name: "카카오", stock_desc: "메신저와 콘텐츠 서비스를 하는 회사", price: 41200, changePct: 0.0 },
    { name: "크래프톤", stock_desc: "게임을 만드는 회사", price: 268000, changePct: 0.5 },
    { name: "엔씨소프트", stock_desc: "게임을 만드는 회사", price: 156800, changePct: 1.2 },
    { name: "하이브", stock_desc: "아이돌 소속사, 엔터테인먼트 회사", price: 213000, changePct: -0.5 },
  ];

  renderStockList(mockStocks);

  document.getElementById("searchInput").addEventListener("input", (e) => {
    const keyword = e.target.value.trim().toLowerCase();
    const filtered = mockStocks.filter(s => s.name.toLowerCase().includes(keyword));
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

    // 설명은 DB(Stock_List.Stock_Desc)에서 API 응답으로 그대로 내려오는 값
    const desc = stock.stock_desc || "";

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