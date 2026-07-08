document.addEventListener("DOMContentLoaded", async () => {
  const id = localStorage.getItem("id");
  if (!id) {
    window.location.href = "index.html";
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const requestedStock = params.get("stock") ? decodeURIComponent(params.get("stock")) : "삼성전자";

  let stockData;
  let holding = { quantity: 0, avgPrice: 0 };
  let cashBalance = 0;

  try {
    const [stockJson, accountJson] = await Promise.all([
      fetchStockDetail(requestedStock, id),
      fetchAccount(id),
    ]);

    stockData = stockJson.stock;
    holding = stockData.holding || { quantity: 0, avgPrice: 0 };
    cashBalance = accountJson.mockAccount.cashBalance;
  } catch (err) {
    console.error(err);
    alert(err.message || "종목 정보를 불러오지 못했습니다. 다시 시도해주세요.");
    window.location.href = "trading.html";
    return;
  }

  let state = {
    tradeType: "buy",
    quantity: 1,
  };

  // 페이지를 연 뒤 수신한 가격을 최근 10분 동안 누적해 실시간 흐름을 그린다.
  let chartState = initChartState(stockData.currentPrice, stockData.intradayHistory);

  renderStockHeader(stockData);
  renderHolding(stockData.name, buildHoldingView(holding, stockData.currentPrice));
  updateOhlcLabels(stockData);
  renderChart(chartState, stockData);
  updateTradeAmount(stockData.currentPrice, state.quantity);
  loadNews(stockData.name);

  // price_generator.py가 1초마다 시세를 갱신하므로, 화면도 같은 주기로 다시 불러와서
  // 현재가/등락률/당일 고가·저가를 갱신하고 그래프 머리를 그만큼 움직인다.
  setInterval(async () => {
    try {
      const refreshed = await fetchStockDetail(stockData.name, id);
      stockData.currentPrice = refreshed.stock.currentPrice;
      stockData.changePct = refreshed.stock.changePct;
      stockData.todayHigh = refreshed.stock.todayHigh;
      stockData.todayLow = refreshed.stock.todayLow;

      renderStockHeader(stockData);
      updateTradeAmount(stockData.currentPrice, state.quantity);
      renderHolding(stockData.name, buildHoldingView(holding, stockData.currentPrice));
      updateOhlcLabels(stockData);

      advanceChartState(chartState, stockData.currentPrice);
      renderChart(chartState, stockData);
    } catch (err) {
      console.error(err);
    }
  }, 1000);

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
    updateQuantityDisplay(stockData.currentPrice);
  });
  document.getElementById("decreaseBtn").addEventListener("click", () => {
    if (state.quantity > 1) state.quantity -= 1;
    updateQuantityDisplay(stockData.currentPrice);
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
      updateQuantityDisplay(stockData.currentPrice);
    });
  });

  // 현금 보유량(매수) / 보유 수량(매도)로 최대 수량의 bound가 결정된다
  function getMaxQuantity() {
    if (state.tradeType === "buy") {
      return stockData.currentPrice > 0 ? Math.floor(cashBalance / stockData.currentPrice) : 0;
    } else {
      return holding.quantity;
    }
  }

  function updateQuantityDisplay(price) {
    document.getElementById("quantityValue").innerText = `${state.quantity}주`;
    setTradeType(state.tradeType);
    updateTradeAmount(price, state.quantity);
  }

  // 주문 넣기
  document.getElementById("orderBtn").addEventListener("click", async () => {
    const totalAmount = stockData.currentPrice * state.quantity;

    // 매수인데 현금이 부족하면 주문 실패 (백엔드에서도 다시 검증하지만, 미리 막아서 헛요청을 줄인다)
    if (state.tradeType === "buy" && totalAmount > cashBalance) {
      alert("잔고가 부족해요. 주문이 체결되지 않았어요.");
      return;
    }

    // 매도인데 보유 수량이 부족하면 주문 실패
    if (state.tradeType === "sell" && state.quantity > holding.quantity) {
      alert("보유한 주식보다 많은 수량을 매도할 수 없어요.");
      return;
    }

    try {
      const res = await fetch("/api/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: id,
          stockCode: stockData.stockCode,
          quantity: state.quantity,
          position: state.tradeType === "buy" ? "BTO" : "STC",
        }),
      });

      const data = await res.json();
      if (!res.ok || data.status !== "success") {
        throw new Error(data.message || "주문에 실패했습니다");
      }

      cashBalance = data.cashBalance;
      alert(data.message);

      // 체결 후 보유 수량/평단가를 다시 불러와서 카드와 최대 수량 bound를 갱신한다
      const refreshed = await fetchStockDetail(stockData.name, id);
      holding = refreshed.stock.holding || { quantity: 0, avgPrice: 0 };
      renderHolding(stockData.name, buildHoldingView(holding, stockData.currentPrice));

      state.quantity = 1;
      updateQuantityDisplay(stockData.currentPrice);
    } catch (err) {
      console.error(err);
      alert(err.message || "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.");
    }
  });
});

/**
 * @returns {Promise<{status, message, stock}>} stock: {stockCode, name, desc, currentPrice, changePct, priceHistory, intradayHistory, holding}
 */
async function fetchStockDetail(stockName, id) {
  const res = await fetch(
    `/api/stock-detail?stock=${encodeURIComponent(stockName)}&id=${encodeURIComponent(id)}`
  );
  if (!res.ok) throw new Error("종목 정보를 불러오지 못했습니다");

  const data = await res.json();
  if (data.status !== "success") throw new Error(data.message || "종목 정보를 불러오지 못했습니다");

  return data;
}

/**
 * @returns {Promise<{status, message, mockAccount, mockHoldings, mockNews}>}
 */
async function fetchAccount(id) {
  const res = await fetch(`/api/account?id=${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error("계좌 정보를 불러오지 못했습니다");

  const data = await res.json();
  if (data.status !== "success") throw new Error(data.message || "계좌 정보를 불러오지 못했습니다");

  return data;
}

const STOCK_DESC_FALLBACK = {
  "삼성전자": "반도체와 스마트폰을 만드는 회사",
  "SK하이닉스": "반도체 메모리를 만드는 회사",
  "SK스퀘어": "여러 IT·게임 회사에 투자하는 지주회사",
  "삼성전기": "전자제품 속 핵심 부품을 만드는 회사",
  "현대차": "자동차를 만드는 회사",
  "LG에너지솔루션": "배터리를 만드는 회사",
  "삼성생명": "생명보험 서비스를 하는 회사",
  "삼성물산": "건설과 무역, 패션 사업을 하는 회사",
  "삼성바이오로직스": "의약품을 위탁 생산하는 회사",
  "한화에어로스페이스": "항공기 엔진과 방위산업 장비를 만드는 회사",
  "KB금융": "은행과 금융 서비스를 하는 지주회사",
  "기아": "자동차를 만드는 회사",
  "신한지주": "은행과 금융 서비스를 하는 지주회사",
  "SK": "여러 계열사를 관리하는 지주회사",
  "현대모비스": "자동차 부품을 만드는 회사",
  "셀트리온": "바이오 의약품을 만드는 회사",
  "삼성SDI": "배터리를 만드는 회사",
  "하나금융지주": "은행과 금융 서비스를 하는 지주회사",
  "LS ELECTRIC": "전력 설비와 전기 장비를 만드는 회사",
  "한화오션": "선박을 만드는 회사",
  "LG전자": "가전제품과 전자기기를 만드는 회사",
  "NAVER": "검색과 인터넷 서비스를 하는 회사",
  "삼성화재": "손해보험 서비스를 하는 회사",
  "두산": "에너지·로봇·소재 사업을 하는 회사",
  "HD한국조선해양": "선박을 만드는 회사",
  "POSCO홀딩스": "철강을 만드는 회사",
  "카카오": "메신저와 콘텐츠 서비스를 하는 회사",
  "크래프톤": "게임을 만드는 회사",
  "엔씨소프트": "게임을 만드는 회사",
  "하이브": "아이돌 소속사, 엔터테인먼트 회사",
};

async function loadNews(stockName) {
  try {
    const res = await fetch(`/api/stock/news?stock=${encodeURIComponent(stockName)}`);
    if (!res.ok) throw new Error("관련 뉴스를 불러오지 못했습니다");

    const data = await res.json();
    if (data.status !== "success") throw new Error(data.message || "관련 뉴스를 불러오지 못했습니다");

    renderNews(data.news);
  } catch (err) {
    console.error(err);
    renderNews([]);
  }
}

/**
 * 서버가 내려주는 {quantity, avgPrice}에 현재가를 곱해 화면에 필요한 평가금액/평가손익을 만든다.
 */
function buildHoldingView(holding, currentPrice) {
  const quantity = holding.quantity || 0;
  const avgPrice = holding.avgPrice || 0;
  const value = quantity * currentPrice;
  const profit = quantity > 0 ? Math.round((currentPrice - avgPrice) * quantity) : 0;
  return { quantity, avgPrice, value, profit };
}

function renderStockHeader(stock) {
  document.getElementById("stockName").innerText = stock.name;
  document.getElementById("stockDesc").innerText = getStockDesc(stock);
  document.getElementById("currentPrice").innerText = (stock.currentPrice || 0).toLocaleString() + "원";

  const logoEl = document.getElementById("stockLogo");
  logoEl.style.backgroundImage = `url('logos/${encodeURIComponent(stock.name)}.png')`;

  const changeEl = document.getElementById("priceChange");
  const isUp = stock.changePct >= 0;
  changeEl.innerText = `${isUp ? "▲" : "▼"}${Math.abs(stock.changePct || 0).toFixed(1)}%`;
  changeEl.className = `price-change ${isUp ? "up" : "down"}`;
}

function getStockDesc(stock) {
  return stock.desc || stock.stock_desc || STOCK_DESC_FALLBACK[stock.name] || "";
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

const CHART_WINDOW_SECONDS = 10 * 60;
const CHART_X_TICK_COUNT = 6;

function chartNowSeconds() {
  return Date.now() / 1000;
}

function formatChartTime(timestamp) {
  return new Date(timestamp * 1000).toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function formatWon(price) {
  return price === null || price === undefined ? "-" : Math.round(price).toLocaleString() + "원";
}

function updateOhlcLabels(stock) {
  document.getElementById("openPriceLabel").innerText = formatWon(stock.openPrice);
  document.getElementById("highPriceLabel").innerText = formatWon(stock.todayHigh);
  document.getElementById("lowPriceLabel").innerText = formatWon(stock.todayLow);
  document.getElementById("nowPriceLabel").innerText = formatWon(stock.currentPrice);
}

/** 서버가 준비한 최근 10분 이력에 현재가를 이어 그래프 상태를 초기화한다. */
function initChartState(currentPrice, intradayHistory = []) {
  const cutoff = chartNowSeconds() - CHART_WINDOW_SECONDS;
  const points = intradayHistory
    .filter(point =>
      Number.isFinite(Number(point.timestamp)) &&
      Number.isFinite(Number(point.price)) &&
      Number(point.timestamp) >= cutoff
    )
    .map(point => ({
      t: Number(point.timestamp),
      price: Number(point.price),
    }))
    .sort((a, b) => a.t - b.t);

  const lastPoint = points[points.length - 1];
  if (!lastPoint || chartNowSeconds() - lastPoint.t > 0.5) {
    points.push({ t: chartNowSeconds(), price: currentPrice });
  } else {
    lastPoint.price = currentPrice;
  }

  return {
    points,
  };
}

/** 폴링으로 받은 가격을 추가하고 최근 10분보다 오래된 점을 제거한다. */
function advanceChartState(chartState, newPrice) {
  const nowT = chartNowSeconds();
  const lastPoint = chartState.points[chartState.points.length - 1];

  if (lastPoint && nowT - lastPoint.t < 0.5) {
    lastPoint.t = nowT;
    lastPoint.price = newPrice;
  } else {
    chartState.points.push({ t: nowT, price: newPrice });
  }

  const cutoff = nowT - CHART_WINDOW_SECONDS;
  chartState.points = chartState.points.filter(point => point.t >= cutoff);
}

function chartDrawPoints(chartState) {
  return chartState.points;
}

/** 실제 표시 범위에 맞춰 1, 2, 5 단위의 읽기 좋은 눈금 간격을 고른다. */
function niceTickStep(rawStep) {
  const safeStep = Math.max(rawStep, 1);
  const magnitude = 10 ** Math.floor(Math.log10(safeStep));
  const normalized = safeStep / magnitude;
  const multiplier = normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10;
  return multiplier * magnitude;
}

/**
 * 화면에 실제로 그리는 가격을 기준으로 세로축 범위를 정한다.
 * 변동이 작을 때도 선의 움직임이 보이도록 최소 0.2% 범위를 보장하고 15%의 여백을 둔다.
 */
function computeYAxisRange(prices, referencePrice) {
  const low = Math.min(...prices);
  const high = Math.max(...prices);
  const center = (low + high) / 2;
  const minimumRange = Math.max(referencePrice, 1) * 0.002;
  const paddedRange = Math.max(high - low, minimumRange) * 1.15;
  const tickCount = 5;
  const tickStep = niceTickStep(paddedRange / (tickCount - 1));
  let min = Math.floor((center - (tickStep * (tickCount - 1)) / 2) / tickStep) * tickStep;
  let max = min + tickStep * (tickCount - 1);

  while (low < min) {
    min -= tickStep;
    max -= tickStep;
  }
  while (high > max) {
    min += tickStep;
    max += tickStep;
  }

  if (min < 0) {
    min = 0;
    max = tickStep * (tickCount - 1);
  }

  const ticks = Array.from({ length: tickCount }, (_, i) => min + tickStep * i);

  return { min, max, ticks };
}

/**
 * 그래프를 그린다: 최근 10분 가로축 / 가격에 맞춘 세로축 / 상승·하락 가격선과 영역 +
 * 현재가 라벨(오른쪽 끝점 근처, 같은 색).
 */
function renderChart(chartState, stock) {
  const canvas = document.getElementById("priceChart");
  const ctx = canvas.getContext("2d");
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = 260;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const points = chartDrawPoints(chartState);
  const referencePrice = stock.k || stock.openPrice || stock.currentPrice || 1;
  const visiblePrices = points.map(point => point.price);
  const { min: yMin, max: yMax, ticks: yTicks } = computeYAxisRange(visiblePrices, referencePrice);

  const paddingLeft = 64;
  const paddingRight = 16;
  const paddingTop = 16;
  const paddingBottom = 26;
  const w = canvas.width - paddingLeft - paddingRight;
  const h = canvas.height - paddingTop - paddingBottom;

  const xMax = chartNowSeconds();
  const xMin = xMax - CHART_WINDOW_SECONDS;
  const toX = (t) => paddingLeft + ((t - xMin) / CHART_WINDOW_SECONDS) * w;
  const toY = (price) => paddingTop + h - ((price - yMin) / (yMax - yMin)) * h;

  // 세로축: 격자선 + 원 단위 라벨
  ctx.strokeStyle = "#EDEDF2";
  ctx.fillStyle = "#9B9BA3";
  ctx.font = "11px sans-serif";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  ctx.lineWidth = 1;
  yTicks.forEach((price) => {
    const y = toY(price);
    ctx.beginPath();
    ctx.moveTo(paddingLeft, y);
    ctx.lineTo(paddingLeft + w, y);
    ctx.stroke();
    ctx.fillText(Math.round(price).toLocaleString(), paddingLeft - 8, y);
  });

  // 가로축: 최근 10분을 2분 간격으로 표시한다.
  ctx.textBaseline = "top";
  for (let i = 0; i < CHART_X_TICK_COUNT; i++) {
    const ratio = i / (CHART_X_TICK_COUNT - 1);
    const timestamp = xMin + CHART_WINDOW_SECONDS * ratio;
    const x = paddingLeft + w * ratio;

    ctx.strokeStyle = "#F3F3F6";
    ctx.beginPath();
    ctx.moveTo(x, paddingTop);
    ctx.lineTo(x, paddingTop + h);
    ctx.stroke();

    ctx.fillStyle = "#9B9BA3";
    ctx.textAlign = i === 0 ? "left" : i === CHART_X_TICK_COUNT - 1 ? "right" : "center";
    ctx.fillText(formatChartTime(timestamp), x, paddingTop + h + 6);
  }

  // 가격 선
  const isUp = points[points.length - 1].price >= points[0].price;
  const color = isUp ? "#E23744" : "#1E6FEE"; // --color-up / --color-down
  if (points.length > 1) {
    const areaGradient = ctx.createLinearGradient(0, paddingTop, 0, paddingTop + h);
    areaGradient.addColorStop(0, isUp ? "rgba(226, 55, 68, 0.14)" : "rgba(30, 111, 238, 0.14)");
    areaGradient.addColorStop(1, "rgba(255, 255, 255, 0)");

    ctx.fillStyle = areaGradient;
    ctx.beginPath();
    points.forEach((p, i) => {
      const x = toX(p.t);
      const y = toY(p.price);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.lineTo(toX(points[points.length - 1].t), paddingTop + h);
    ctx.lineTo(toX(points[0].t), paddingTop + h);
    ctx.closePath();
    ctx.fill();
  }

  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath();
  points.forEach((p, i) => {
    const x = toX(p.t);
    const y = toY(p.price);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  // 현재가: 그래프 오른쪽 끝점 근처에 같은 색으로 강조 표시
  const last = points[points.length - 1];
  const lastX = toX(last.t);
  const lastY = toY(last.price);

  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(lastX, lastY, 3.5, 0, Math.PI * 2);
  ctx.fill();

  const nearRightEdge = lastX > paddingLeft + w - 50;
  ctx.font = "bold 12px sans-serif";
  ctx.textAlign = nearRightEdge ? "right" : "left";
  ctx.textBaseline = "bottom";
  ctx.fillText(Math.round(last.price).toLocaleString() + "원", lastX + (nearRightEdge ? -8 : 8), lastY - 6);
}
