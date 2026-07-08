/** changePct(전일 대비 등락률)를 거꾸로 적용해 5개 지점짜리 그래프용 더미 이력을 만듦 */
function buildPriceHistory(currentPrice, changePct) {
  const startPrice = Math.round(currentPrice / (1 + changePct / 100));
  const points = 5;
  const history = [];
  for (let i = 0; i < points; i++) {
    const ratio = i / (points - 1);
    history.push(Math.round(startPrice + (currentPrice - startPrice) * ratio));
  }
  history[points - 1] = currentPrice;
  return history;
}

document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const requestedStock = params.get("stock") ? decodeURIComponent(params.get("stock")) : "삼성전자";

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체 (trading.js의 mockStocks와 동일한 목록)
  const mockStocks = [
    { name: "삼성전자", desc: "반도체와 스마트폰을 만드는 회사", price: 72300, changePct: 2.3 },
    { name: "SK하이닉스", desc: "반도체 메모리를 만드는 회사", price: 184300, changePct: 0.9 },
    { name: "SK스퀘어", desc: "여러 IT·게임 회사에 투자하는 지주회사", price: 1256000, changePct: 1.87 },
    { name: "삼성전기", desc: "전자제품 속 핵심 부품을 만드는 회사", price: 2680000, changePct: -3.2 },
    { name: "현대차", desc: "자동차를 만드는 회사", price: 231500, changePct: 4.1 },
    { name: "LG에너지솔루션", desc: "배터리를 만드는 회사", price: 412000, changePct: -1.1 },
    { name: "삼성생명", desc: "생명보험 서비스를 하는 회사", price: 118000, changePct: 2.8 },
    { name: "삼성물산", desc: "건설과 무역, 패션 사업을 하는 회사", price: 156000, changePct: 0.4 },
    { name: "삼성바이오로직스", desc: "의약품을 위탁 생산하는 회사", price: 1050000, changePct: 1.2 },
    { name: "한화에어로스페이스", desc: "항공기 엔진과 방위산업 장비를 만드는 회사", price: 890000, changePct: 5.6 },
    { name: "KB금융", desc: "은행과 금융 서비스를 하는 지주회사", price: 98000, changePct: 0.2 },
    { name: "기아", desc: "자동차를 만드는 회사", price: 112000, changePct: 3.1 },
    { name: "신한지주", desc: "은행과 금융 서비스를 하는 지주회사", price: 62000, changePct: 0.6 },
    { name: "SK", desc: "여러 계열사를 관리하는 지주회사", price: 178000, changePct: -0.8 },
    { name: "현대모비스", desc: "자동차 부품을 만드는 회사", price: 265000, changePct: 1.9 },
    { name: "셀트리온", desc: "바이오 의약품을 만드는 회사", price: 189000, changePct: 2.5 },
    { name: "삼성SDI", desc: "배터리를 만드는 회사", price: 402000, changePct: -2.1 },
    { name: "하나금융지주", desc: "은행과 금융 서비스를 하는 지주회사", price: 68000, changePct: 0.3 },
    { name: "LS ELECTRIC", desc: "전력 설비와 전기 장비를 만드는 회사", price: 298000, changePct: 4.4 },
    { name: "한화오션", desc: "선박을 만드는 회사", price: 78000, changePct: 3.8 },
    { name: "LG전자", desc: "가전제품과 전자기기를 만드는 회사", price: 118000, changePct: 6.2 },
    { name: "NAVER", desc: "검색과 인터넷 서비스를 하는 회사", price: 198700, changePct: 1.8 },
    { name: "삼성화재", desc: "손해보험 서비스를 하는 회사", price: 412000, changePct: 0.9 },
    { name: "두산", desc: "에너지·로봇·소재 사업을 하는 회사", price: 289000, changePct: 5.9 },
    { name: "HD한국조선해양", desc: "선박을 만드는 회사", price: 178000, changePct: 2.2 },
    { name: "POSCO홀딩스", desc: "철강을 만드는 회사", price: 342000, changePct: -1.4 },
    { name: "카카오", desc: "메신저와 콘텐츠 서비스를 하는 회사", price: 41200, changePct: 0.0 },
    { name: "크래프톤", desc: "게임을 만드는 회사", price: 268000, changePct: 0.5 },
    { name: "엔씨소프트", desc: "게임을 만드는 회사", price: 156800, changePct: 1.2 },
    { name: "하이브", desc: "아이돌 소속사, 엔터테인먼트 회사", price: 213000, changePct: -0.5 },
  ];

  const mockStockCatalog = mockStocks.map(s => ({
    name: s.name,
    desc: s.desc,
    currentPrice: s.price,
    changePct: s.changePct,
    priceHistory: buildPriceHistory(s.price, s.changePct),
  }));

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

  let state = {
    tradeType: "buy",
    quantity: 1,
  };

  renderStockHeader(mockStock);
  renderHolding(mockStock.name, mockHolding);
  renderChart(mockStock.priceHistory);
  updateTradeAmount(mockStock.currentPrice, state.quantity);
  loadNews(mockStock.name);

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

async function loadNews(stockName) {
  try {
    const res = await fetch(`http://localhost:5000/stock/news?stock=${encodeURIComponent(stockName)}`);
    if (!res.ok) throw new Error("관련 뉴스를 불러오지 못했습니다");

    const data = await res.json();
    if (data.status !== "success") throw new Error(data.message || "관련 뉴스를 불러오지 못했습니다");

    renderNews(data.news);
  } catch (err) {
    console.error(err);
    renderNews([]);
  }
}

function renderStockHeader(stock) {
  document.getElementById("stockName").innerText = stock.name;
  document.getElementById("stockDesc").innerText = stock.desc;
  document.getElementById("currentPrice").innerText = stock.currentPrice.toLocaleString() + "원";

  const logoEl = document.getElementById("stockLogo");
  logoEl.style.backgroundImage = `url('logos/${encodeURIComponent(stock.name)}.png')`;

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
    listEl.innerHTML = `<p class="card-caption">오늘 관련 뉴스가 없습니다.</p>`;
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