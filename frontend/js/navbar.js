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

// id는 서버가 내려주는 실제 Noti_Num. 삭제 요청에 그대로 실어 보낸다.
let notifications = [];

function setupNotificationBell() {
  const bell = document.getElementById("notificationBell");
  const dropdown = document.getElementById("notificationDropdown");

  loadNotifications();

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

async function loadNotifications() {
  const userId = localStorage.getItem("id");
  if (!userId) {
    notifications = [];
    renderNotifications();
    return;
  }

  try {
    const res = await fetch(`/api/notifications?id=${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error("알림을 불러오지 못했습니다");

    const data = await res.json();
    if (data.status !== "success") throw new Error(data.message || "알림을 불러오지 못했습니다");

    notifications = data.notifications;
  } catch (err) {
    console.error(err);
    notifications = [];
  }
  renderNotifications();
}

/** 서버가 내려주는 ISO 시각 문자열을 "12분 전" 같은 상대 시간으로 바꾼다 */
function formatRelativeTime(isoString) {
  const diffMin = Math.floor((Date.now() - new Date(isoString).getTime()) / 60000);
  if (diffMin < 1) return "방금 전";
  if (diffMin < 60) return `${diffMin}분 전`;

  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour}시간 전`;

  const diffDay = Math.floor(diffHour / 24);
  return diffDay === 1 ? "어제" : `${diffDay}일 전`;
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
          <p class="notification-time">${formatRelativeTime(n.time)}</p>
        </div>
      </a>
      <button class="notification-delete-btn" data-id="${n.id}" aria-label="알림 삭제">×</button>
    </div>
  `).join("");

  // 삭제 버튼 이벤트 연결
  listEl.querySelectorAll(".notification-delete-btn").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const notiNum = Number(btn.dataset.id);
      const userId = localStorage.getItem("id");

      try {
        const res = await fetch("/api/notifications/delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ userId, notiNum }),
        });

        const data = await res.json();
        if (!res.ok || data.status !== "success") {
          throw new Error(data.message || "알림 삭제에 실패했습니다");
        }

        notifications = notifications.filter(n => n.id !== notiNum);
        renderNotifications();
      } catch (err) {
        console.error(err);
        alert(err.message || "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.");
      }
    });
  });
}
