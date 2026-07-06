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

  // TODO: 백엔드 계좌 API에서 실제 현금 잔고로 교체
  const mockAccount = {
    cashBalance: 312000,
  };

  const mockNews = [
    { title: "두산, 엔비디아와 AI 동맹…에너지·로봇·소재 사업 연결", day: 3, link: "#" },
    { title: "LG전자 90% 폭등 무서운 질주…지금 살까 AI에 물었더니", day: 1, link: "#" },
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

  // 퍼센트 단축 버튼
  // 매수: "지금 가진 현금으로 최대 몇 주 살 수 있는지" 기준
  // 매도: "지금 보유 중인 수량" 기준 — 둘을 절대 같은 값으로 계산하면 안 됨
  document.querySelectorAll(".qty-shortcut-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const pct = Number(btn.dataset.pct);
      const maxQty = getMaxQuantity();

      if (maxQty <= 0) {
        alert(state.tradeType === "buy" ? "살 수 있는 돈이 부족해요" : "보유한 주식이 없어요");
        return;
      }

      state.quantity = Math.max(1, Math.floor(maxQty * (pct / 100)));
      updateQuantityDisplay(mockStock.currentPrice);
    });
  });

  function getMaxQuantity() {
    if (state.tradeType === "buy") {
      // 현금 잔고 안에서 지금 가격으로 살 수 있는 최대 수량 (소수 주 불가 -> 내림)
      return Math.floor(mockAccount.cashBalance / mockStock.currentPrice);
    } else {
      // 매도는 보유 수량을 넘을 수 없음
      return mockHolding.quantity;
    }
  }

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
  // 원본 디자인 의도 그대로: 제목 + 링크만 표시. "N일차" 대신 실제 오늘 날짜로 표시
  listEl.innerHTML = newsList.map(n => `
    <a href="${n.link}" target="_blank" rel="noopener noreferrer" class="news-item-link">
      ${n.title}<span class="news-item-day">${getTodayShortLabel()}</span>
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