const form = document.getElementById("signupForm");

const nicknameInput = document.getElementById("nickname");
const userIdInput = document.getElementById("userId");
const passwordInput = document.getElementById("password");
const passwordConfirmInput = document.getElementById("passwordConfirm");

const passwordError = document.getElementById("passwordError");
const nicknameCheckMessage = document.getElementById("nicknameCheckMessage");
const userIdCheckMessage = document.getElementById("userIdCheckMessage");

const checkNicknameBtn = document.getElementById("checkNicknameBtn");
const checkUserIdBtn = document.getElementById("checkUserIdBtn");

let isNicknameChecked = false;
let isUserIdChecked = false;

function passwordsMatch() {
  return passwordInput.value === passwordConfirmInput.value;
}

function showMessage(element, message, isSuccess) {
  element.hidden = false;
  element.textContent = message;
  element.style.color = isSuccess ? "#2e7d32" : "#d32f2f";
}

nicknameInput.addEventListener("input", () => {
  isNicknameChecked = false;
  nicknameCheckMessage.hidden = true;
});

userIdInput.addEventListener("input", () => {
  isUserIdChecked = false;
  userIdCheckMessage.hidden = true;
});

passwordConfirmInput.addEventListener("input", () => {
  passwordError.hidden = passwordsMatch() || passwordConfirmInput.value === "";
});

checkNicknameBtn.addEventListener("click", async () => {
  const nickname = nicknameInput.value.trim();

  if (!nickname) {
    showMessage(nicknameCheckMessage, "닉네임을 입력해주세요", false);
    return;
  }

  try {
    const res = await fetch(
      `http://localhost:8000/auth/check-nickname?nickname=${encodeURIComponent(nickname)}`
    );

    if (!res.ok) throw new Error("nickname check failed");

    const data = await res.json();

    if (data.available) {
      isNicknameChecked = true;
      showMessage(nicknameCheckMessage, "사용 가능한 닉네임이에요", true);
    } else {
      isNicknameChecked = false;
      showMessage(nicknameCheckMessage, "이미 사용 중인 닉네임이에요", false);
    }
  } catch (err) {
    console.error(err);
    showMessage(nicknameCheckMessage, "중복확인에 실패했어요", false);
  }
});

checkUserIdBtn.addEventListener("click", async () => {
  const userId = userIdInput.value.trim();

  if (!userId) {
    showMessage(userIdCheckMessage, "아이디를 입력해주세요", false);
    return;
  }

  try {
    const res = await fetch(
      `http://localhost:8000/auth/check-userid?userId=${encodeURIComponent(userId)}`
    );

    if (!res.ok) throw new Error("userId check failed");

    const data = await res.json();

    if (data.available) {
      isUserIdChecked = true;
      showMessage(userIdCheckMessage, "사용 가능한 아이디예요", true);
    } else {
      isUserIdChecked = false;
      showMessage(userIdCheckMessage, "이미 사용 중인 아이디예요", false);
    }
  } catch (err) {
    console.error(err);
    showMessage(userIdCheckMessage, "중복확인에 실패했어요", false);
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nickname = nicknameInput.value.trim();
  const userId = userIdInput.value.trim();
  const password = passwordInput.value;

  if (!nickname || !userId || !password) {
    alert("모든 항목을 입력해주세요");
    return;
  }

  if (!isNicknameChecked) {
    alert("닉네임 중복확인을 해주세요");
    return;
  }

  if (!isUserIdChecked) {
    alert("아이디 중복확인을 해주세요");
    return;
  }

  if (password.length < 8) {
    alert("비밀번호는 8자 이상 입력해주세요");
    return;
  }

  if (!passwordsMatch()) {
    passwordError.hidden = false;
    return;
  }

  try {
    const res = await fetch("http://localhost:8000/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nickname, userId, password }),
    });

    if (!res.ok) {
      alert("회원가입에 실패했어요");
      return;
    }

    alert("회원가입이 완료됐어요!");
    window.location.href = "onboarding.html";
  } catch (err) {
    console.error(err);
    alert("서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요");
  }
});