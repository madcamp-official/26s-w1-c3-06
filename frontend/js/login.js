document.getElementById("loginForm").addEventListener("submit", (e) => {
  e.preventDefault();

  const userId = document.getElementById("userId").value.trim();
  const password = document.getElementById("password").value;

  if (!userId || !password) {
    alert("아이디와 비밀번호를 입력해주세요");
    return;
  }

  // TODO: 백엔드 연결되면 이 부분을 실제 로그인 API 호출로 교체
  // 지금은 프론트 단독 배포/시연용으로, 입력값 검증만 하고 바로 홈으로 이동
  localStorage.setItem("token", "demo-token");
  localStorage.setItem("user_id", userId);

  window.location.href = "home.html";
});