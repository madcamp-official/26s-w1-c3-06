document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 아래 더미 데이터 대신 fetch로 교체
  const mockFriendRequest = { fromName: "OO" }; // 요청이 없으면 null로 두면 카드 자체가 숨겨짐

  const mockFriends = [
    { name: "김지우" },
    { name: "김서연" },
  ];

  const mockFriendRanking = [
    { rank: 1, name: "서연", pct: 6.2, isMe: false },
    { rank: 2, name: "지우", pct: 3.1, isMe: false },
    { rank: 3, name: "나", pct: 0.8, isMe: true },
  ];

  const mockGlobalRanking = [
    { rank: 1, name: "OOO", pct: 6.2, isMe: false },
    { rank: 2, name: "OOO", pct: 3.1, isMe: false },
    { rank: 3, name: "나", pct: 0.8, isMe: true },
    { rank: 4, name: "OOO", pct: -0.2, isMe: false },
    { rank: 5, name: "OOO", pct: -6.2, isMe: false },
    { rank: 6, name: "OOO", pct: -16.2, isMe: false },
  ];

  renderFriendRequest(mockFriendRequest);
  renderFriendList(mockFriends);
  renderRanking("friendRanking", mockFriendRanking);
  renderRanking("globalRanking", mockGlobalRanking);

  document.getElementById("addFriendBtn").addEventListener("click", () => {
    const id = document.getElementById("friendIdInput").value.trim();
    if (!id) {
      alert("친구의 아이디를 입력해주세요");
      return;
    }
    // TODO: 친구 요청 보내기 API 호출
    alert(`${id}님에게 친구 요청을 보냈어요`);
    document.getElementById("friendIdInput").value = "";
  });
});

function renderFriendRequest(request) {
  const card = document.getElementById("friendRequestCard");
  if (!request) {
    card.hidden = true;
    return;
  }
  card.hidden = false;
  document.getElementById("requestText").innerText = `${request.fromName}님이 친구 요청을 보냈어요`;

  document.getElementById("acceptBtn").addEventListener("click", () => {
    // TODO: 친구 요청 수락 API 호출
    card.hidden = true;
  });
  document.getElementById("rejectBtn").addEventListener("click", () => {
    // TODO: 친구 요청 거절 API 호출
    card.hidden = true;
  });
}

function renderFriendList(friends) {
  const listEl = document.getElementById("friendList");
  const countEl = document.getElementById("friendCount");
  if (countEl) countEl.innerText = `${friends.length}명`;

  listEl.innerHTML = friends.map(f => `
    <div class="friend-row">
      <div class="avatar-circle"></div>
      <span class="friend-name">${f.name}</span>
    </div>
  `).join("");
}

function renderRanking(containerId, rankingList) {
  const listEl = document.getElementById(containerId);
  listEl.innerHTML = rankingList.map(r => {
    const pctClass = r.pct >= 0 ? "up" : "down";
    const sign = r.pct >= 0 ? "+" : "";
    return `
      <div class="ranking-row ${r.isMe ? 'me' : ''}">
        <span class="rank-number">${r.rank}</span>
        <div class="avatar-circle"></div>
        <span class="ranking-name ${r.isMe ? 'me' : ''}">${r.name}</span>
        <span class="ranking-pct ${pctClass}">${sign}${r.pct}%</span>
      </div>
    `;
  }).join("");
}
