document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 URL 파라미터(?stock=삼성전자) 등으로 실제 종목 받아와 교체
  const mockStock = {
    name: "삼성전자",
    desc: "반도체와 스마트폰을 만드는 회사",
    currentPrice: 72300,
    changePct: 2.3, // 양수=상승(빨강), 음수=하락(파랑)
    priceHistory: [68400, 69200, 70100, 71400, 72300], // 종가 순서대로
  };

  const mockHolding = {
    quantity: 2,
    avgPrice: 69100,
    value: 144600,
    profit: 6400,
  };

  const mockNews = [
    { title: "(삼성전자 관련 뉴스 제목)", day: 1, link: "#" },,
  ];

  let state = {
    tradeType: "buy",
    quantity: 1,
  };

  renderStockHeader(mockStock);
  renderHolding(mockStock.name, mockHolding);
  renderNews(mockNews);
  renderChart(mockStock.priceHistory);
  updateTradeAmount(mockStock.currentPrice, state.quantity);

  // 매수/매도 토글
  document.getElementById("buyBtn").addEventListener("click", () => setTradeType("buy"));
  document.getElementById("sellBtn").addEventListener("click", () => setTradeType("sell"));

  function setTradeType(type) {
    state.tradeType = type;
    document.getElementById("buyBtn").classList.toggle("active", type === "buy");
    document.getElementById("sellBtn").classList.toggle("active", type === "sell");
    document.getElementById("orderBtn").innerText =
      type === "buy" ? `${state.quantity}주 매수 주문 넣기` : `${state.quantity}주 매도 주문 넣기`;
  }

  // 수량 증감
  document.getElementById("increaseBtn").addEventListener("click", () => {
    state.quantity += 1;
    updateQuantityDisplay(mockStock.currentPrice);
  });
  document.getElementById("decreaseBtn").addEventListener("click", () => {
    if (state.quantity > 1) state.quantity -= 1;
    updateQuantityDisplay(mockStock.currentPrice);
  });

  // 퍼센트 단축 버튼 (보유 수량 또는 보유 현금 기준, 지금은 예시로 최대 10주 가정)
  document.querySelectorAll(".qty-shortcut-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const pct = Number(btn.dataset.pct);
      const maxQty = 10; // TODO: 실제 보유 현금/수량 기준으로 계산
      state.quantity = Math.max(1, Math.round(maxQty * (pct / 100)));
      updateQuantityDisplay(mockStock.currentPrice);
    });
  });

  function updateQuantityDisplay(price) {
    document.getElementById("quantityValue").innerText = `${state.quantity}주`;
    setTradeType(state.tradeType);
    updateTradeAmount(price, state.quantity);
  }

  // 주문 넣기
  document.getElementById("orderBtn").addEventListener("click", () => {
    // TODO: 백엔드 주문 API 호출 (stock, type, quantity 전달)
    alert(`${mockStock.name} ${state.quantity}주 ${state.tradeType === "buy" ? "매수" : "매도"} 완료!`);
  });
});

function renderStockHeader(stock) {
  document.getElementById("stockName").innerText = stock.name;
  document.getElementById("stockDesc").innerText = stock.desc;
  document.getElementById("currentPrice").innerText = stock.currentPrice.toLocaleString() + "원";

  const changeEl = document.getElementById("priceChange");
  const isUp = stock.changePct >= 0;
  changeEl.innerText = `${isUp ? "▲" : "▼"}${Math.abs(stock.changePct).toFixed(1)}%`;
  changeEl.className = `price-change ${isUp ? "up" : "down"}`;
}

function renderHolding(stockName, holding) {
  document.getElementById("holdingTitle").innerText = `내가 가진 (${stockName})`;
  document.getElementById("holdingQty").innerText = `${holding.quantity}주`;
  document.getElementById("holdingAvgPrice").innerText = holding.avgPrice.toLocaleString() + "원";
  document.getElementById("holdingValue").innerText = holding.value.toLocaleString() + "원";

  const profitEl = document.getElementById("holdingProfit");
  const sign = holding.profit >= 0 ? "+" : "";
  profitEl.innerText = `${sign}${holding.profit.toLocaleString()}원`;
  profitEl.style.color = holding.profit >= 0 ? "#FF0000" : "#004DFF";
}

function renderNews(newsList) {
  const listEl = document.getElementById("newsList");
  // 원본 디자인 의도 그대로: 제목 + 링크만 표시 (본문/이미지 없음)
  listEl.innerHTML = newsList.map(n => `
    <a href="${n.link}" target="_blank" rel="noopener noreferrer" class="news-item-link">
      ${n.title}<span class="news-item-day">${n.day}일차</span>
    </a>
  `).join("");
}

function updateTradeAmount(price, quantity) {
  document.getElementById("tradeAmount").innerText = (price * quantity).toLocaleString() + "원";
}

function renderChart(priceHistory) {
  // TODO: Chart.js 등으로 실제 그래프 렌더링 (현재는 자리만 확보)
  const canvas = document.getElementById("priceChart");
  const ctx = canvas.getContext("2d");
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = 260;
  ctx.font = "14px sans-serif";
  ctx.fillStyle = "#9B9BA3";
  ctx.textAlign = "center";
  ctx.fillText("[ 주가 그래프 영역 ]", canvas.width / 2, canvas.height / 2);
}
