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

  // 그래프에 "확정"되는 점은 5분(300초) 단위로만 늘어난다. 그 사이에는 liveHead가 매초
  // 시세를 따라 움직이며 그래프의 머리 역할만 하고, 5분 슬롯이 넘어가는 순간 그 직전
  // liveHead 값이 그대로 확정점으로 고정된다 (초 단위 시세를 전부 찍으면 그래프가 난잡해짐).
  let chartState = initChartState(stockData.openPrice, stockData.currentPrice);

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
      const res = await fetch("http://localhost:5000/order", {
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
 * @returns {Promise<{status, message, stock}>} stock: {stockCode, name, desc, currentPrice, changePct, priceHistory, holding}
 */
async function fetchStockDetail(stockName, userId) {
  const res = await fetch(
    `http://localhost:5000/stock-detail?stock=${encodeURIComponent(stockName)}&userId=${encodeURIComponent(userId)}`
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
  const res = await fetch(`http://localhost:5000/account?id=${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error("계좌 정보를 불러오지 못했습니다");

  const data = await res.json();
  if (data.status !== "success") throw new Error(data.message || "계좌 정보를 불러오지 못했습니다");

  return data;
}

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
  document.getElementById("stockDesc").innerText = stock.desc || "";
  document.getElementById("currentPrice").innerText = (stock.currentPrice || 0).toLocaleString() + "원";

  const logoEl = document.getElementById("stockLogo");
  logoEl.style.backgroundImage = `url('logos/${encodeURIComponent(stock.name)}.png')`;

  const changeEl = document.getElementById("priceChange");
  const isUp = stock.changePct >= 0;
  changeEl.innerText = `${isUp ? "▲" : "▼"}${Math.abs(stock.changePct || 0).toFixed(1)}%`;
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

const SECONDS_PER_DAY = 86400;
const CHART_SLOT_SECONDS = 300; // 그래프에 새 점이 "확정"되는 간격 (5분)

function secondsSinceMidnight() {
  const now = new Date();
  return now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
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

/**
 * 그래프 상태를 초기화한다. confirmedPoints는 5분 슬롯 경계마다 "확정"된 점들이고,
 * liveHead는 아직 안 끝난 현재 슬롯에서 매초 시세를 따라 움직이는 그래프의 머리다.
 * 자정부터 지금까지 지난 완료 슬롯은 실제 이력이 없으므로(하루 중간에 페이지를 열었을 수도
 * 있음) 전부 시가로 수평 채운다.
 */
function initChartState(openPrice, currentPrice) {
  const nowT = secondsSinceMidnight();
  const slotIndex = Math.floor(nowT / CHART_SLOT_SECONDS);

  const confirmedPoints = [{ t: 0, price: openPrice }];
  for (let i = 1; i < slotIndex; i++) {
    confirmedPoints.push({ t: i * CHART_SLOT_SECONDS, price: openPrice });
  }

  return {
    confirmedPoints,
    liveHead: { t: nowT, price: currentPrice },
    slotIndex,
  };
}

/** 매초 폴링마다 호출. 5분 슬롯을 넘었으면 직전 liveHead 값을 확정점으로 고정한다. */
function advanceChartState(chartState, newPrice) {
  const nowT = secondsSinceMidnight();
  const newSlotIndex = Math.floor(nowT / CHART_SLOT_SECONDS);

  while (chartState.slotIndex < newSlotIndex) {
    chartState.slotIndex += 1;
    chartState.confirmedPoints.push({
      t: chartState.slotIndex * CHART_SLOT_SECONDS,
      price: chartState.liveHead.price, // 슬롯이 넘어가기 직전까지의 마지막 시세로 확정
    });
  }

  chartState.liveHead = { t: nowT, price: newPrice };
}

function chartDrawPoints(chartState) {
  return chartState.confirmedPoints.concat([chartState.liveHead]);
}

/** 가격 크기(참고가)에 맞춰 눈금 간격으로 쓸 "보기 좋은" 단위를 고른다 (100원/1,000원/10,000원 ...) */
function niceUnit(referencePrice) {
  const steps = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000];
  const target = Math.max(referencePrice, 1) / 20; // 세로축에 대략 20칸 눈금이 들어가도록
  return steps.reduce((best, s) =>
    Math.abs(Math.log(s) - Math.log(target)) < Math.abs(Math.log(best) - Math.log(target)) ? s : best
  , steps[0]);
}

/**
 * 세로축 범위를 정한다. 0원부터 시작하지 않고, 오늘의 고가/저가(실시간 생성 데이터 기준)를
 * 여유 있게 감싸면서, 종목의 참고가(K)를 기준으로 보기 좋은 단위로 반올림한다.
 */
function computeYAxisRange(low, high, referencePrice) {
  const safeLow = Math.min(low, referencePrice);
  const safeHigh = Math.max(high, referencePrice);
  const rawRange = Math.max(safeHigh - safeLow, referencePrice * 0.01); // 하루 종일 안 움직여도 최소 여백 확보
  const padding = rawRange * 0.25;

  const unit = niceUnit(referencePrice);
  let min = Math.max(0, Math.floor((safeLow - padding) / unit) * unit);
  let max = Math.ceil((safeHigh + padding) / unit) * unit;
  if (max - min < unit) max = min + unit;

  return { min, max, unit };
}

/**
 * 그래프를 그린다: 가로축(시간, 6시간 간격 라벨) / 세로축(원 단위 가격, 격자+ 라벨) +
 * 가격 선(상승=빨강/하락=파랑) + 현재가 라벨(오른쪽 끝점 근처, 같은 색).
 */
function renderChart(chartState, stock) {
  const canvas = document.getElementById("priceChart");
  const ctx = canvas.getContext("2d");
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = 260;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const points = chartDrawPoints(chartState);
  const referencePrice = stock.k || stock.openPrice || stock.currentPrice || 1;
  const low = Math.min(stock.todayLow ?? stock.openPrice, stock.openPrice);
  const high = Math.max(stock.todayHigh ?? stock.openPrice, stock.openPrice);
  const { min: yMin, max: yMax, unit } = computeYAxisRange(low, high, referencePrice);

  const paddingLeft = 64;
  const paddingRight = 16;
  const paddingTop = 16;
  const paddingBottom = 26;
  const w = canvas.width - paddingLeft - paddingRight;
  const h = canvas.height - paddingTop - paddingBottom;

  const toX = (t) => paddingLeft + (t / SECONDS_PER_DAY) * w;
  const toY = (price) => paddingTop + h - ((price - yMin) / (yMax - yMin)) * h;

  // 세로축: 격자선 + 원 단위 라벨
  ctx.strokeStyle = "#EDEDF2";
  ctx.fillStyle = "#9B9BA3";
  ctx.font = "11px sans-serif";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  ctx.lineWidth = 1;
  for (let price = yMin; price <= yMax + unit * 0.5; price += unit) {
    const y = toY(price);
    ctx.beginPath();
    ctx.moveTo(paddingLeft, y);
    ctx.lineTo(paddingLeft + w, y);
    ctx.stroke();
    ctx.fillText(Math.round(price).toLocaleString(), paddingLeft - 8, y);
  }

  // 가로축: 6시간 간격 시각 라벨
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (let hour = 0; hour <= 24; hour += 6) {
    const x = toX(hour * 3600);
    ctx.fillText(`${String(hour).padStart(2, "0")}:00`, x, paddingTop + h + 6);
  }

  // 가격 선
  const isUp = points[points.length - 1].price >= points[0].price;
  const color = isUp ? "#E23744" : "#1E6FEE"; // --color-up / --color-down
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
