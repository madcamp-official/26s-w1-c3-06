document.addEventListener("DOMContentLoaded", async () => {

  const id = localStorage.getItem("id");
  if (!id) {
    window.location.href = "index.html";
    return;
  }

  // 계좌 정보(hasReceivedIncomeToday 포함)는 항상 백엔드 응답 기준으로 판단한다 (localStorage로 하루 1회 제한 X)
  let data;
  try {
    data = await fetchAccount(id);
  } catch (err) {
    console.error(err);
    alert("계좌 정보를 불러오지 못했습니다. 다시 로그인해 주세요.");
    return;
  }

  const account = data.mockAccount;
  account.id = id;

  renderAccount(account);
  renderHoldings(data.mockHoldings);
  renderNews(data.mockNews);

  document.getElementById("goToHistoryBtn").addEventListener("click", () => {
    window.location.href = "history.html";
  });
});

/**
 * 계좌 정보(User_Info)를 불러온다. GET /account?id= 응답을 그대로 반환한다.
 * @returns {Promise<{status, message, mockAccount, mockHoldings, mockNews}>}
 */
async function fetchAccount(id) {
  const res = await fetch(`/api/account?id=${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error("계좌 정보를 불러오지 못했습니다");

  const data = await res.json();
  if (data.status !== "success") throw new Error(data.message || "계좌 정보를 불러오지 못했습니다");

  return data;
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
    if (isQuizOpen) return; // 이미 퀴즈 모달이 열려 있으면 재요청(중복 오픈) 무시

    isQuizOpen = true;
    // 버튼은 여기서 비활성화하지 않는다: 채점(제출) 결과가 와야만 하루 기회를 소모한 것으로 본다.
    // 문제를 안 풀고 취소하면 버튼이 다시 눌릴 수 있어야 한다.

    openQuizModal({
      id: account.id,
      onResult: (result) => {
        isQuizOpen = false;

        if (result.status === "correct") {
          // result.balance는 서버가 내려주는 갱신된 총자산(User_Info.Balance)이다.
          // 현금 보유량은 총자산에서 보유 주식 평가금액을 뺀 값이라, 같은 폭(gained)만큼만 더해준다.
          const newTotalAsset = typeof result.balance === "number"
            ? result.balance
            : account.totalAsset + 10000;
          const gained = newTotalAsset - account.totalAsset;

          account.totalAsset = newTotalAsset;
          account.cashBalance += gained;

          document.getElementById("totalAsset").innerText =
            account.totalAsset.toLocaleString() + "원";
          document.getElementById("cashBalance").innerText =
            account.cashBalance.toLocaleString() + "원";

          account.hasReceivedIncomeToday = true;
          lockIncomeBtn();

        } else if (result.status === "wrong" || result.status === "already_used") {
          account.hasReceivedIncomeToday = true;
          lockIncomeBtn();
        }
        // status === "error" | "cancelled": 제출까지 가지 않았으므로 하루 기회를 소모하지 않고
        // 버튼은 그대로 눌러볼 수 있는 상태(isQuizOpen = false)로 둔다.
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
        <div class="holding-logo" style="background-image: url('logos/${encodeURIComponent(h.name)}.png')"></div>
        <div>
          <p class="holding-name">${h.name}</p>
          <p class="holding-desc">${h.desc}</p>
        </div>
      </div>
      <span class="align-right holding-value">${h.value.toLocaleString()}원</span>
      <span class="align-right holding-return" style="color:${h.returnPct >= 0 ? 'var(--color-up)' : 'var(--color-down)'}">
        ${h.returnPct >= 0 ? '+' : ''}${Number(h.returnPct).toFixed(2)}%
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
        <span>${n.source} · ${n.date}</span>
        <a href="${n.link}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>
      </div>
    </div>
  `).join("");
}