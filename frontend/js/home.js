document.addEventListener("DOMContentLoaded", () => {

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
    { title: "두산, 엔비디아와 AI 동맹…에너지·로봇·소재 사업 연결", source: "alphabiz", link: "#" },
    { title: "LG전자 90% 폭등 무서운 질주…지금 살까 AI에 물었더니", source: "한국경제", link: "#" },
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

  // 홈 화면에만 실제 날짜 + "N일차"를 같이 표시 (다른 화면엔 N일차 안 보임)
  document.getElementById("virtualDay").innerText =
    `${getTodayLabel()} · 투자 시작 ${account.virtualDay}일차`;

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
      // TODO: userId는 로그인 상태(localStorage 등)에서 가져오기
      const userId = localStorage.getItem("user_id") || "guest";

      openQuizModal(userId, (result) => {
        incomeBtn.disabled = true;

        if (result.is_correct) {
          incomeBtn.innerText = "오늘의 기본 소득 받기 완료";
          if (typeof result.balance === "number") {
            document.getElementById("cashBalance").innerText = result.balance.toLocaleString() + "원";
          }
        } else {
          incomeBtn.innerText = "오늘의 퀴즈 도전 완료 (내일 다시)";
        }
      });
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

  listEl.querySelectorAll(".holding-row").forEach(row => {
    row.addEventListener("click", () => {
      const stockName = row.dataset.stockName;
      window.location.href = `stock-detail.html?stock=${encodeURIComponent(stockName)}`;
    });
  });
}

function renderNews(newsList) {
  const listEl = document.getElementById("newsList");
  const limited = newsList.slice(0, 5); // 홈 화면 뉴스는 최대 5개까지만

  listEl.innerHTML = limited.map(n => `
    <div class="news-item">
      <p class="news-title">${n.title}</p>
      <div class="news-meta">
        <span>${n.source} · ${getTodayShortLabel()}</span>
        <a href="${n.link}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>
      </div>
    </div>
  `).join("");
}