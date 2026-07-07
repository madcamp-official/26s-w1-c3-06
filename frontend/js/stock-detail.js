document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const requestedStock = params.get("stock") ? decodeURIComponent(params.get("stock")) : "삼성전자";

  const mockStockCatalog = [
    { name: "삼성전자", desc: "반도체와 스마트폰을 만드는 회사", currentPrice: 72300, changePct: 2.3, priceHistory: [68400, 69200, 70100, 71400, 72300] },
    { name: "SK하이닉스", desc: "반도체 메모리를 만드는 회사", currentPrice: 184300, changePct: 0.9, priceHistory: [180000, 182500, 183600, 184100, 184300] },
    { name: "LG전자", desc: "가전제품과 전자기기를 만드는 회사", currentPrice: 118000, changePct: 6.2, priceHistory: [112000, 113500, 115000, 116500, 118000] },
    { name: "카카오", desc: "메신저와 콘텐츠 서비스를 하는 회사", currentPrice: 41200, changePct: 0.0, priceHistory: [41000, 41200, 41100, 41200, 41200] },
  ];

  const mockStock = mockStockCatalog.find(s => s.name === requestedStock) || {
    name: requestedStock,
    desc: "선택한 종목의 정보를 불러오는 중입니다.",
    currentPrice: 0,
    changePct: 0,
    priceHistory: [0, 0, 0, 0, 0],
  };

  const mockHoldingsMap = {
    "삼성전자": { quantity: 2, avgPrice: 69100, value: 144600, profit: 6400 },
    "SK하이닉스": { quantity: 1, avgPrice: 180000, value: 184300, profit: 4300 },
    "LG전자": { quantity: 3, avgPrice: 110000, value: 354000, profit: 24000 },
    "카카오": { quantity: 0, avgPrice: 0, value: 0, profit: 0 },
  };

  const mockHolding = mockHoldingsMap[mockStock.name] || { quantity: 0, avgPrice: 0, value: 0, profit: 0 };

  // TODO: 백엔드 계좌 API에서 실제 현금 잔고로 교체
  const mockAccount = {
    cashBalance: 312000,
  };

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체
  const mockNewsMap = {
    "삼성전자": [
      { title: "삼성전자 ‘비스포크 AI 스팀’ 로봇청소기, 월 판매 2만 대 돌파", link: "#" },
      { title: "삼성전자 미국 법인, 9월부터 이전‥인력 감축은 무관", link: "#" },
    ],
    "SK하이닉스": [
      { title: "SK하이닉스 부스 찾은 젠슨 황…HBM웨이퍼에 더 만들어주세요", link: "#" },
      { title: "삼성전자·SK하이닉스 주식 10년 묻어둔 가수 소유…수익금 보태 집 샀다", link: "#" },
    ],
    "LG전자": [
      { title: "젠슨 황 효과에 LG전자 이틀 연속 상한가…사진보다 주문서가 중요", link: "#" },
      { title: "LG전자 주가 올 들어 300% 폭등…AI 동맹 기대감", link: "#" },
    ],
    "카카오": [
      { title: "카톡 개편 이끈 홍민택 CPO 퇴사…카카오 조직개편 본격화", link: "#" },
      { title: "카카오 노조, 파업 돌입한다…4시간 부분파업 예고", link: "#" },
    ],
  };
  const mockNews = mockNewsMap[mockStock.name] || [
    { title: `${mockStock.name} 관련 최신 뉴스를 불러오는 중입니다.`, link: "#" },
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
      return Math.floor(mockAccount.cashBalance / mockStock.currentPrice);
    } else {
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
    const totalAmount = mockStock.currentPrice * state.quantity;

    // 매수인데 현금이 부족하면 주문 실패
    if (state.tradeType === "buy" && totalAmount > mockAccount.cashBalance) {
      alert("잔고가 부족해요. 주문이 체결되지 않았어요.");
      return;
    }

    // 매도인데 보유 수량이 부족하면 주문 실패 (같은 원리로 같이 처리)
    if (state.tradeType === "sell" && state.quantity > mockHolding.quantity) {
      alert("보유한 주식보다 많은 수량을 매도할 수 없어요.");
      return;
    }

    // TODO: 백엔드 주문 API 호출 (stock_name, order_type, quantity 전달)
    // 성공 시 응답의 balance로 mockAccount.cashBalance를 갱신해야 함
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

/**
 * @param {Array} newsList - {title, link} 목록
 */
function renderNews(newsList) {
  const listEl = document.getElementById("newsList");
  // 원본 디자인 의도 그대로: 제목 + 링크만 표시, 날짜는 표시하지 않음
  if (!newsList || newsList.length === 0) {
    listEl.innerHTML = `<p class="card-caption">관련 뉴스를 찾을 수 없습니다.</p>`;
    return;
  }
  listEl.innerHTML = newsList.map(n => `
    <a href="${n.link}" target="_blank" rel="noopener noreferrer" class="news-item-link">
      ${n.title}
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