document.addEventListener("DOMContentLoaded", () => {
  const navbarEl = document.getElementById("navbar");
  if (!navbarEl) return;

  const currentPage = location.pathname.split("/").pop();

  const tabs = [
    { label: "홈", href: "home.html" },
    { label: "주식 거래", href: "trading.html" },
    { label: "소셜", href: "social.html" },
    { label: "설정", href: "settings.html" },
  ];

  const tabsHtml = tabs.map(tab => {
    const isActive = currentPage === tab.href;
    return `<a href="${tab.href}" class="navbar-tab ${isActive ? 'active' : ''}">${tab.label}</a>`;
  }).join("");

  navbarEl.innerHTML = `
    <nav class="navbar">
      <div class="navbar-left">
        <span class="navbar-logo">모의투자</span>
        ${tabsHtml}
      </div>
      <div class="navbar-right">
        <div class="notification-bell" id="notificationBell">
          🔔
          <span class="notification-badge" id="notificationBadge" hidden>0</span>
        </div>
        <div class="notification-dropdown" id="notificationDropdown" hidden>
          <p class="notification-dropdown-title">알림</p>
          <div id="notificationList"></div>
        </div>
      </div>
    </nav>
  `;

  setupNotificationBell();
});

// TODO: 백엔드 완성되면 이 더미 데이터 대신 fetch("http://localhost:8000/notifications?user_id=...")로 교체
// id는 프론트에서 삭제 처리할 때 구분용으로만 씀 (실제로는 noti_num 등을 쓰면 됨)
let notifications = [
  { id: 1, type: "order", title: "삼성전자 1주 매수가 체결됐어요", time: "12분 전" },
  { id: 2, type: "owned", title: "카카오, 오늘 3.1% 올랐어요", time: "1시간 전", related_name: "카카오" },
  { id: 3, type: "friend", title: "민수님이 친구 요청을 보냈어요", time: "3시간 전" },
  { id: 4, type: "owned", title: "LG전자, 오늘 4.6% 올랐어요", time: "5시간 전", related_name: "LG전자" },
  { id: 5, type: "order", title: "카카오 2주 매도가 체결됐어요", time: "어제" },
];

function setupNotificationBell() {
  const bell = document.getElementById("notificationBell");
  const dropdown = document.getElementById("notificationDropdown");

  renderNotifications();

  bell.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.hidden = !dropdown.hidden;
  });

  // 바깥 클릭하면 닫기
  document.addEventListener("click", () => {
    dropdown.hidden = true;
  });

  // 드롭다운 안쪽 클릭은 바깥 클릭으로 안 치게(닫힘 방지)
  dropdown.addEventListener("click", (e) => {
    e.stopPropagation();
  });
}

function renderNotifications() {
  const badge = document.getElementById("notificationBadge");
  const listEl = document.getElementById("notificationList");

  // 뱃지: 읽음/안읽음 구분 없이 그냥 현재 남아있는 알림 개수
  if (notifications.length > 0) {
    badge.hidden = false;
    badge.innerText = notifications.length > 9 ? "9+" : notifications.length;
  } else {
    badge.hidden = true;
  }

  if (notifications.length === 0) {
    listEl.innerHTML = `<p class="notification-empty">아직 알림이 없어요</p>`;
    return;
  }

  const iconMap = { order: "✅", owned: "📈", friend: "👥" };
  const linkMap = {
    order: () => "history.html",
    owned: (n) => `stock-detail.html?stock=${encodeURIComponent(n.related_name || "")}`,
    friend: () => "social.html",
  };

  listEl.innerHTML = notifications.map(n => `
    <div class="notification-item" data-id="${n.id}">
      <a class="notification-item-link" href="${linkMap[n.type](n)}">
        <span class="notification-icon">${iconMap[n.type] || "🔔"}</span>
        <div class="notification-content">
          <p class="notification-title">${n.title}</p>
          <p class="notification-time">${n.time}</p>
        </div>
      </a>
      <button class="notification-delete-btn" data-id="${n.id}" aria-label="알림 삭제">×</button>
    </div>
  `).join("");

  // 삭제 버튼 이벤트 연결
  listEl.querySelectorAll(".notification-delete-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const id = Number(btn.dataset.id);
      // TODO: 백엔드 완성되면 여기서 삭제 API 호출 (또는 읽음 처리 API)
      notifications = notifications.filter(n => n.id !== id);
      renderNotifications();
    });
  });
}
