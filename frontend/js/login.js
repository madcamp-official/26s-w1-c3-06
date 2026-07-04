document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const userId = document.getElementById("userId").value.trim();
  const password = document.getElementById("password").value;

  if (!userId || !password) {
    alert("아이디와 비밀번호를 입력해주세요");
    return;
  }

  try {
    // TODO: 백엔드 로그인 API 완성되면 이 URL을 실제 주소로 교체
    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: userId, password }),
    });

    if (!res.ok) {
      alert("아이디 또는 비밀번호가 올바르지 않아요");
      return;
    }

    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    window.location.href = "home.html";

  } catch (err) {
    console.error(err);
    alert("서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요");
  }
});
