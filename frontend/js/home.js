document.addEventListener("DOMContentLoaded", async () => {

  // 계좌 정보(LastBailout 포함)는 항상 백엔드 응답 기준으로 판단한다 (localStorage로 하루 1회 제한 X)
  const account = await fetchAccount();

  const mockHoldings = [
    {
      stock_name: "삼성전자",
      stock_desc: "반도체와 스마트폰을 만드는 회사",
      own_value: 144600,
      own_pricechange: 4.6,
    },
    {
      stock_name: "카카오",
      stock_desc: "메신저와 콘텐츠 서비스 회사",
      own_value: 41200,
      own_pricechange: -1.9,
    },
  ];

  const mockNews = [
    {
      news_title: "두산, 엔비디아와 AI 동맹…에너지·로봇·소재 사업 연결",
      publisher: "alphabiz",
      news_body: "https://www.alphabiz.co.kr/news/articleView.html?idxno=152238",
      news_date: "2026-07-06",
    },
  ];

  renderAccount(account);
  renderHoldings(mockHoldings);
  renderNews(mockNews);

  document.getElementById("goToHistoryBtn").addEventListener("click", () => {
    window.location.href = "history.html";
  });
});

/**
 * 계좌 정보(User_Info)를 불러온다. LastBailout은 여기서 내려오는 값을 그대로 신뢰한다.
 * @returns {Promise<{id, nickname, reg_date, balance, return, lastBailout, profile}>}
 */
async function fetchAccount() {
  const id = localStorage.getItem("id") || "minji"; // TODO: 로그인 연동되면 세션/토큰에서 가져오기

  try {
    const res = await fetch(`http://localhost:5000/account?id=${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error("계좌 정보를 불러오지 못했습니다");
    return await res.json();
  } catch (err) {
    console.error(err);
    // 백엔드 연결 실패 시 임시 표시용. 실제로는 에러 화면/재로그인 유도가 필요함
    return {
      id,
      nickname: "(오프라인)",
      reg_date: new Date().toISOString(),
      balance: 0,
      return: 0,
      lastBailout: false,
      profile: null,
    };
  }
}

function renderAccount(account) {
  document.getElementById("userTitle").innerText =
    `${account.nickname}님의 계좌`;

  document.getElementById("virtualDay").innerText =
    `${getTodayLabel()} | 모의투자 ${calculateVirtualDay(account.reg_date)}일차`;

  // TODO: 보유 주식 평가금액이 붙으면 balance + 보유주식 평가금액 합산으로 교체
  // 지금은 보유 주식 연동 전이라 현금 잔고를 총자산으로 그대로 표시
  document.getElementById("totalAsset").innerText =
    account.balance.toLocaleString() + "원";

  const profitEl = document.getElementById("profitLoss");
  const sign = account.return >= 0 ? "+" : "";
  profitEl.innerText = `${sign}${account.return.toLocaleString()}원`;
  profitEl.className = account.return >= 0 ? "text-up" : "text-down";

  document.getElementById("cashBalance").innerText =
    account.balance.toLocaleString() + "원";

  const incomeBtn = document.getElementById("incomeBtn");

  // 퀴즈 모달이 지금 열려 있는 중인지 구분하는 변수.
  // 홈 화면에서 퀴즈를 여는 요청(클릭)과, 결과를 받아 홈 화면 상태를 갱신하는 시점
  // 양쪽에서 이 값을 확인/갱신해서 모달이 중복으로 열리는 것을 막는다.
  let isQuizOpen = false;

  function lockIncomeBtn() {
    incomeBtn.disabled = true;
    incomeBtn.innerText = "오늘의 기본 소득 받기 완료";
  }

  // 페이지 진입 시점에는 계좌 조회 응답의 LastBailout만 보고 버튼 상태를 정한다
  if (account.lastBailout) {
    lockIncomeBtn();
  }

  incomeBtn.addEventListener("click", () => {
    if (isQuizOpen) return; // 이미 퀴즈 요청이 진행 중이면 재요청(모달 중복 오픈) 무시

    isQuizOpen = true;
    incomeBtn.disabled = true;

    openQuizModal({
      id: account.id,
      onResult: (result) => {
        isQuizOpen = false;

        if (result.status === "correct") {
          account.balance = typeof result.balance === "number"
            ? result.balance
            : account.balance + 10000;

          document.getElementById("cashBalance").innerText =
            account.balance.toLocaleString() + "원";

          account.lastBailout = true;
          lockIncomeBtn();

        } else if (result.status === "wrong" || result.status === "already_used") {
          account.lastBailout = true;
          lockIncomeBtn();

        } else {
          // status === "error": 서버에 연결이 안 된 것뿐이라 하루 기회를 소모 처리하지 않고 버튼을 다시 활성화
          incomeBtn.disabled = false;
        }
      },
    });
  });
}

function renderHoldings(holdings) {
  const listEl = document.getElementById("holdingsList");

  document.getElementById("stockCount").innerText = holdings.length + "개";

  listEl.innerHTML = holdings.map(h => `
    <div class="holding-row" data-stock-name="${h.stock_name}" style="cursor:pointer;">
      <div class="holding-info">
        <div class="holding-logo"></div>
        <div>
          <p class="holding-name">${h.stock_name}</p>
          <p class="holding-desc">${h.stock_desc}</p>
        </div>
      </div>
      <span class="align-right holding-value">${h.own_value.toLocaleString()}원</span>
      <span class="align-right holding-return" style="color:${h.own_pricechange >= 0 ? 'var(--color-up)' : 'var(--color-down)'}">
        ${h.own_pricechange >= 0 ? '+' : ''}${h.own_pricechange}%
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
  const limited = newsList.slice(0, 5);

  listEl.innerHTML = limited.map(n => `
    <div class="news-item">
      <p class="news-title">${n.news_title}</p>
      <div class="news-meta">
        <span>${n.publisher} · ${n.news_date}</span>
        <a href="${n.news_body}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>
      </div>
    </div>
  `).join("");
}

function calculateVirtualDay(regDate) {
  const startDate = new Date(regDate);
  const today = new Date();

  startDate.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);

  return Math.floor((today - startDate) / (1000 * 60 * 60 * 24)) + 1;
}