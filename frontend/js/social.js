let currentFriends = [];
let currentFriendRequest = null;
let currentUserId = null;

document.addEventListener("DOMContentLoaded", async () => {
  currentUserId = localStorage.getItem("id");
  if (!currentUserId) {
    window.location.href = "index.html";
    return;
  }

  document.getElementById("addFriendBtn").addEventListener("click", async () => {
    const id = document.getElementById("friendIdInput").value.trim();
    if (!id) {
      alert("친구의 아이디를 입력해주세요");
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/social/request-friends", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fromId: currentUserId, toId: id }),
      });
      const data = await res.json();
      if (data.status !== "success") throw new Error(data.message || "친구 요청에 실패했습니다");

      alert(data.message);
      document.getElementById("friendIdInput").value = "";
    } catch (err) {
      console.error(err);
      alert(err.message || "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.");
    }
  });

  await loadSocialData();
});

async function loadSocialData() {
  try {
    const [socialRes, rankingRes] = await Promise.all([
      fetch(`http://localhost:5000/social?userId=${encodeURIComponent(currentUserId)}`),
      fetch(`http://localhost:5000/social/ranking?userId=${encodeURIComponent(currentUserId)}`),
    ]);

    const socialData = await socialRes.json();
    const rankingData = await rankingRes.json();

    if (socialData.status !== "success") throw new Error(socialData.message || "친구 정보를 불러오지 못했습니다");
    if (rankingData.status !== "success") throw new Error(rankingData.message || "랭킹을 불러오지 못했습니다");

    currentFriends = socialData.friendList;
    currentFriendRequest = socialData.friendRequest;

    renderFriendRequest(currentFriendRequest);
    renderFriendList(currentFriends);
    renderRanking("friendRanking", rankingData.friendRanking);
    renderRanking("globalRanking", rankingData.globalRanking);
  } catch (err) {
    console.error(err);
    alert(err.message || "소셜 정보를 불러오지 못했습니다.");
  }
}

function deleteFriend(index) {
  const friend = currentFriends[index];
  if (!friend) return;

  const confirmed = confirm(`${friend.name}님을 친구에서 삭제하시겠어요?`);
  if (!confirmed) return;

  removeFriendship(friend.id, `${friend.name}님이 친구 목록에서 삭제되었습니다.`);
}

async function removeFriendship(otherId, successMessage) {
  try {
    const res = await fetch("http://localhost:5000/social/delete-friends", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fromId: currentUserId, toId: otherId }),
    });
    const data = await res.json();
    if (data.status !== "success") throw new Error(data.message || "요청에 실패했습니다");

    if (successMessage) alert(successMessage);
    await loadSocialData();
  } catch (err) {
    console.error(err);
    alert(err.message || "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.");
  }
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

  // 이전 렌더에서 붙은 리스너가 중복으로 쌓이지 않도록 버튼을 새로 교체한다
  acceptBtn.replaceWith(acceptBtn.cloneNode(true));
  rejectBtn.replaceWith(rejectBtn.cloneNode(true));

  document.getElementById("acceptBtn").addEventListener("click", async () => {
    try {
      const res = await fetch("http://localhost:5000/social/accept-friends", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fromId: request.fromId, toId: currentUserId }),
      });
      const data = await res.json();
      if (data.status !== "success") throw new Error(data.message || "수락에 실패했습니다");

      alert(`${request.fromName}님과 친구가 되었습니다.`);
      await loadSocialData();
    } catch (err) {
      console.error(err);
      alert(err.message || "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.");
    }
  });

  document.getElementById("rejectBtn").addEventListener("click", () => {
    removeFriendship(request.fromId, `${request.fromName}님의 친구 요청을 거절했습니다.`);
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
