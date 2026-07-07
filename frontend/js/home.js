document.addEventListener("DOMContentLoaded", async () => {

  // 계좌 정보(hasReceivedIncomeToday 포함)는 항상 백엔드 응답 기준으로 판단한다 (localStorage로 하루 1회 제한 X)
  const home = await fetchHome();
  if (!home) return; // fetchHome 내부에서 이미 에러 처리(alert/리다이렉트)를 마쳤다

  renderAccount(home.account);
  renderHoldings(home.holdings);
  renderNews(home.news);

  document.getElementById("goToHistoryBtn").addEventListener("click", () => {
    window.location.href = "history.html";
  });
});

/**
 * 홈 화면에 필요한 데이터(계좌 요약 + 보유 종목 + 최신 뉴스)를 불러온다.
 * 백엔드 GET /account 가 이 셋을 한 번에 묶어서 내려준다. endpoint: GET /account
 *
 * @returns {Promise<{account, holdings, news}|null>} 실패 시 null (호출부는 렌더링을 건너뛴다)
 */
async function fetchHome() {
  const id = localStorage.getItem("id");

  if (!id) {
    alert("로그인이 필요합니다.");
    window.location.href = "login.html";
    return null;
  }

  try {
    const res = await fetch(`http://localhost:5000/account?userId=${encodeURIComponent(id)}`);
    const data = await res.json().catch(() => ({}));

    if (!res.ok || data.status !== "success") {
      alert(data.message || "홈 화면을 불러오지 못했습니다.");
      return null;
    }

    return {
      account: { id, ...data.mockAccount },
      holdings: data.mockHoldings || [],
      news: data.mockNews || [],
    };
  } catch (err) {
    console.error(err);
    alert("서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.");
    return null;
  }
}

function renderAccount(account) {
  document.getElementById("userTitle").innerText =
    `${account.nickname}님의 계좌`;

  document.getElementById("virtualDay").innerText =
    `${getTodayLabel()} | 모의투자 ${account.virtualDay}일차`;

  document.getElementById("totalAsset").innerText =
    account.totalAsset.toLocaleString() + "원";

  const profitEl = document.getElementById("profitLoss");
  const sign = account.profitLoss >= 0 ? "+" : "";
  profitEl.innerText = `${sign}${account.profitLoss.toLocaleString()}원`;
  profitEl.className = account.profitLoss >= 0 ? "text-up" : "text-down";

  document.getElementById("cashBalance").innerText =
    account.cashBalance.toLocaleString() + "원";

  const incomeBtn = document.getElementById("incomeBtn");

  // 퀴즈 모달이 지금 열려 있는 중인지 구분하는 변수.
  // 홈 화면에서 퀴즈를 여는 요청(클릭)과, 결과를 받아 홈 화면 상태를 갱신하는 시점
  // 양쪽에서 이 값을 확인/갱신해서 모달이 중복으로 열리는 것을 막는다.
  let isQuizOpen = false;

  function lockIncomeBtn() {
    incomeBtn.disabled = true;
    incomeBtn.innerText = "오늘의 기본 소득 받기 완료";
  }

  // 페이지 진입 시점에는 계좌 조회 응답의 hasReceivedIncomeToday만 보고 버튼 상태를 정한다
  if (account.hasReceivedIncomeToday) {
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
          account.cashBalance = typeof result.balance === "number"
            ? result.balance
            : account.cashBalance + 10000;

          document.getElementById("cashBalance").innerText =
            account.cashBalance.toLocaleString() + "원";

          account.hasReceivedIncomeToday = true;
          lockIncomeBtn();

        } else if (result.status === "wrong" || result.status === "already_used") {
          account.hasReceivedIncomeToday = true;
          lockIncomeBtn();

        } else {
          // status === "error" | "cancelled": 실제로 제출(채점)된 게 아니므로
          // 하루 기회를 소모 처리하지 않고 버튼을 다시 활성화
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
  const limited = newsList.slice(0, 5);

  listEl.innerHTML = limited.map(n => `
    <div class="news-item">
      <p class="news-title">${n.title}</p>
      <div class="news-meta">
        <span>${n.source}</span>
        <a href="${n.link}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>
      </div>
    </div>
  `).join("");
}