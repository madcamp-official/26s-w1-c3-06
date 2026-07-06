document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체
  const mockAccount = {
    nickname: "민지",
    virtualDay: 2,
    totalAsset: 1043200,
    profitLoss: 43200,
    cashBalance: 312000,
    stockCount: 3,
    hasReceivedIncomeToday: false,
  };

  const mockHoldings = [
    { name: "삼성전자", desc: "반도체와 스마트폰을 만드는 회사", value: 144600, returnPct: 4.6 },
    { name: "카카오", desc: "메신저와 콘텐츠 서비스 회사", value: 41200, returnPct: -1.9 },
  ];

  const mockNews = [
    { title: "두산, 엔비디아와 AI 동맹…에너지·로봇·소재 사업 연결", source: "alphabiz", day: 3, link: "#" },
    { title: "LG전자 90% 폭등 무서운 질주…지금 살까 AI에 물었더니", source: "한국경제", day: 1, link: "#" },
  ];

  renderAccount(mockAccount);
  renderHoldings(mockHoldings);
  renderNews(mockNews);

  document.getElementById("goToHistoryBtn").addEventListener("click", () => {
    window.location.href = "history.html";
  });
});

function renderAccount(account) {
  document.getElementById("userTitle").innerText = `${account.nickname}님의 계좌`;
  document.getElementById("virtualDay").innerText = `가상거래 ${account.virtualDay}일차`;
  document.getElementById("totalAsset").innerText = account.totalAsset.toLocaleString() + "원";

  const profitEl = document.getElementById("profitLoss");
  const sign = account.profitLoss >= 0 ? "+" : "";
  profitEl.innerText = `${sign}${account.profitLoss.toLocaleString()}원`;
  profitEl.className = account.profitLoss >= 0 ? "text-up" : "text-down";

  document.getElementById("cashBalance").innerText = account.cashBalance.toLocaleString() + "원";
  document.getElementById("stockCount").innerText = account.stockCount + "개";

  const incomeBtn = document.getElementById("incomeBtn");
  if (account.hasReceivedIncomeToday) {
    incomeBtn.disabled = true;
    incomeBtn.innerText = "오늘의 기본 소득 받기 완료";
  } else {
    incomeBtn.addEventListener("click", () => {
      alert("10,000원을 받았어요!");
      incomeBtn.disabled = true;
      incomeBtn.innerText = "오늘의 기본 소득 받기 완료";
    });
  }
}

function renderHoldings(holdings) {
  const listEl = document.getElementById("holdingsList");

  listEl.innerHTML = holdings.map(h => `
    <div class="holding-row" data-stock-name="${h.name}" style="cursor:pointer;">
      <div class="holding-info">
        <div class="holding-logo"></div>
        <div>
          <p class="holding-name">${h.name}</p>
          <p class="holding-desc">${h.desc}</p>
        </div>
      </div>
      <span class="align-right holding-value">${h.value.toLocaleString()}원</span>
      <span class="align-right holding-return" style="color:${h.returnPct >= 0 ? 'var(--color-up)' : 'var(--color-down)'}">
        ${h.returnPct >= 0 ? '+' : ''}${h.returnPct}%
      </span>
    </div>
  `).join("");

  // 보유 주식 행 클릭 시 종목 상세 화면으로 이동
  listEl.querySelectorAll(".holding-row").forEach(row => {
    row.addEventListener("click", () => {
      const stockName = row.dataset.stockName;
      window.location.href = `stock-detail.html?stock=${encodeURIComponent(stockName)}`;
    });
  });
}

function renderNews(newsList) {
  const listEl = document.getElementById("newsList");
  listEl.innerHTML = newsList.map(n => `
    <div class="news-item">
      <p class="news-title">${n.title}</p>
      <div class="news-meta">
        <span>${n.source} · ${n.day}일차</span>
        <a href="${n.link}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>
      </div>
    </div>
  `).join("");
}