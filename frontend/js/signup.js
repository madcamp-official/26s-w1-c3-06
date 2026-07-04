const form = document.getElementById("signupForm");
const passwordInput = document.getElementById("password");
const passwordConfirmInput = document.getElementById("passwordConfirm");
const passwordError = document.getElementById("passwordError");

function passwordsMatch() {
  return passwordInput.value === passwordConfirmInput.value;
}

passwordConfirmInput.addEventListener("input", () => {
  passwordError.hidden = passwordsMatch() || passwordConfirmInput.value === "";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nickname = document.getElementById("nickname").value.trim();
  const userId = document.getElementById("userId").value.trim();
  const password = passwordInput.value;

  if (!nickname || !userId || !password) {
    alert("모든 항목을 입력해주세요");
    return;
  }

  if (password.length < 4) {
    alert("비밀번호는 4자 이상 입력해주세요");
    return;
  }

  if (!passwordsMatch()) {
    passwordError.hidden = false;
    return;
  }

  try {
    // TODO: 백엔드 회원가입 API 완성되면 이 URL을 실제 주소로 교체
    const res = await fetch("http://localhost:8000/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nickname, id: userId, password }),
    });

    if (!res.ok) {
      alert("회원가입에 실패했어요. 이미 사용 중인 아이디일 수 있어요");
      return;
    }

    alert("회원가입이 완료됐어요!");
    window.location.href = "onboarding.html";

  } catch (err) {
    console.error(err);
    alert("서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요");
  }
});
