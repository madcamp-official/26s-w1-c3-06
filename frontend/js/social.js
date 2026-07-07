let currentFriends = [];
let currentFriendRequest = null;

document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 아래 더미 데이터 대신 fetch로 교체
  currentFriendRequest = { fromName: "OO" }; // 요청이 없으면 null로 두면 카드 자체가 숨겨짐

  currentFriends = [
    { name: "aaa" },
    { name: "bbb" },
  ];

  const mockFriendRanking = [
    { rank: 1, name: "aaa", pct: 6.2, isMe: false },
    { rank: 2, name: "bbb", pct: 3.1, isMe: false },
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

  renderFriendRequest(currentFriendRequest);
  renderFriendList(currentFriends);
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

function deleteFriend(index) {
  const friend = currentFriends[index];
  if (!friend) return;

  const confirmed = confirm(`${friend.name}님을 친구에서 삭제하시겠어요?`);
  if (!confirmed) return;

  currentFriends.splice(index, 1);
  renderFriendList(currentFriends);
  alert(`${friend.name}님이 친구 목록에서 삭제되었습니다.`);
  // TODO: 친구 삭제 API 호출
}

function renderFriendRequest(request) {
  const card = document.getElementById("friendRequestCard");
  if (!request) {
    card.hidden = true;
    return;
  }
  card.hidden = false;
  document.getElementById("requestText").innerText = `${request.fromName}님이 친구 요청을 보냈어요`;

  const acceptBtn = document.getElementById("acceptBtn");
  const rejectBtn = document.getElementById("rejectBtn");

  acceptBtn.replaceWith(acceptBtn.cloneNode(true));
  rejectBtn.replaceWith(rejectBtn.cloneNode(true));

  document.getElementById("acceptBtn").addEventListener("click", () => {
    currentFriends.push({ name: request.fromName });
    currentFriendRequest = null;
    renderFriendRequest(currentFriendRequest);
    renderFriendList(currentFriends);
    alert(`${request.fromName}님과 친구가 되었습니다.`);
    // TODO: 친구 요청 수락 API 호출
  });

  document.getElementById("rejectBtn").addEventListener("click", () => {
    currentFriendRequest = null;
    renderFriendRequest(currentFriendRequest);
    alert(`${request.fromName}님의 친구 요청을 거절했습니다.`);
    // TODO: 친구 요청 거절 API 호출
  });
}

function renderFriendList(friends) {
  const listEl = document.getElementById("friendList");
  const countEl = document.getElementById("friendCount");
  if (countEl) countEl.innerText = `${friends.length}명`;

  listEl.innerHTML = friends.map((f, index) => `
    <div class="friend-row">
      <div class="avatar-circle"></div>
      <span class="friend-name">${f.name}</span>
      <button class="friend-delete-btn" data-friend-index="${index}" aria-label="친구 삭제">×</button>
    </div>
  `).join("");

  listEl.querySelectorAll(".friend-delete-btn").forEach(button => {
    button.addEventListener("click", () => {
      const index = Number(button.dataset.friendIndex);
      deleteFriend(index);
    });
  });
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
