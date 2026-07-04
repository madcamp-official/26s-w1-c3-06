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
    return `<a href="${tab.href}" style="
      color: ${isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)'};
      font-weight: ${isActive ? '600' : '400'};
      border-bottom: ${isActive ? '2px solid var(--color-accent)' : 'none'};
      text-decoration: none; padding-bottom: 4px; font-size: 13px;
    ">${tab.label}</a>`;
  }).join("");

  navbarEl.innerHTML = `
    <nav style="height:64px; background:#fff; border-bottom:1px solid var(--color-border);
      display:flex; align-items:center; padding:0 3%; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:28px;">
        <span style="font-weight:700; color:var(--color-accent); font-size:15px;">모의투자</span>
        <div style="display:flex; gap:20px;">${tabsHtml}</div>
      </div>
      <div style="display:flex; align-items:center; gap:16px;">
        <span style="font-size:18px;">🔔</span>
        <div style="width:28px; height:28px; border-radius:50%; background:#EEF0FF;
          display:flex; align-items:center; justify-content:center; font-size:11px;
          font-weight:600; color:var(--color-accent);">민</div>
      </div>
    </nav>
  `;
});