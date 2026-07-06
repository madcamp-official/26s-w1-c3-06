document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const id = document.getElementById("userId").value.trim();
  const pw = document.getElementById("password").value;

  if (!id || !pw) {
    alert("아이디와 비밀번호를 입력해주세요");
    return;
  }

  try {
    // TODO: 백엔드 로그인 API(account_Authenticate) 응답 형식 확정되면 맞춰서 조정
    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, pw }),
    });

    if (!res.ok) {
      alert("아이디 또는 비밀번호가 올바르지 않습니다");
      return;
    }

    const data = await res.json().catch(() => ({}));

    localStorage.setItem("token", data.token || "");
    localStorage.setItem("id", id);

    window.location.href = "home.html";

  } catch (err) {
    console.error(err);
    alert("서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요");
  }
});