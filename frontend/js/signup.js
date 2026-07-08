const form = document.getElementById("signupForm");

const nicknameInput = document.getElementById("nickname");
const nicknameCheckMessage = document.getElementById("nicknameCheckMessage");
const checkNicknameBtn = document.getElementById("checkNicknameBtn");

const userIdInput = document.getElementById("userId");
const userIdCheckMessage = document.getElementById("userIdCheckMessage");
const checkUserIdBtn = document.getElementById("checkUserIdBtn");

const passwordInput = document.getElementById("password");
const passwordConfirmInput = document.getElementById("passwordConfirm");
const passwordError = document.getElementById("passwordError");

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

passwordConfirmInput.addEventListener("input", () => {
  passwordError.hidden = passwordsMatch() || passwordConfirmInput.value === "";
});

// 닉네임/아이디를 다시 입력하면 이전 중복확인 결과는 무효로 처리
nicknameInput.addEventListener("input", () => {
  isNicknameChecked = false;
  nicknameCheckMessage.hidden = true;
});

userIdInput.addEventListener("input", () => {
  isUserIdChecked = false;
  userIdCheckMessage.hidden = true;
});

checkNicknameBtn.addEventListener("click", async () => {
  const nickname = nicknameInput.value.trim();

  if (!nickname) {
    showMessage(nicknameCheckMessage, "닉네임을 입력해주세요", false);
    return;
  }

  try {
    // TODO: 백엔드 완성되면 실제 응답 형식에 맞춰 조정
    const res = await fetch(
      `/api/auth/check-nickname?nickname=${encodeURIComponent(nickname)}`
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
    isNicknameChecked = false;
    showMessage(nicknameCheckMessage, "중복확인에 실패했어요", false);
  }
});

checkUserIdBtn.addEventListener("click", async () => {
  const id = userIdInput.value.trim();

  if (!id) {
    showMessage(userIdCheckMessage, "아이디를 입력해주세요", false);
    return;
  }

  try {
    // TODO: 백엔드 완성되면 실제 응답 형식에 맞춰 조정
    const res = await fetch(
      `/api/auth/check-id?id=${encodeURIComponent(id)}`
    );

    if (!res.ok) throw new Error("id check failed");

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
    isUserIdChecked = false;
    showMessage(userIdCheckMessage, "중복확인에 실패했어요", false);
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nickname = nicknameInput.value.trim();
  const id = userIdInput.value.trim();
  const pw = passwordInput.value;

  if (!nickname || !id || !pw) {
    alert("모든 항목을 입력해주세요");
    return;
  }

  if (pw.length < 8) {
    alert("비밀번호는 8자 이상 입력해주세요");
    return;
  }

  if (!passwordsMatch()) {
    passwordError.hidden = false;
    return;
  }

  if (!isNicknameChecked) {
    showMessage(nicknameCheckMessage, "닉네임 중복확인을 해주세요", false);
    return;
  }

  if (!isUserIdChecked) {
    showMessage(userIdCheckMessage, "아이디 중복확인을 해주세요", false);
    return;
  }

  try {
    // TODO: 백엔드 회원가입 API(account_Create) 응답 형식 확정되면 맞춰서 조정
    const res = await fetch("/api/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nickname, id, pw }),
    });

    if (!res.ok) {
      alert("회원가입에 실패했어요. 이미 사용 중인 아이디일 수 있어요");
      return;
    }

    alert("회원가입이 완료됐어요! 로그인해주세요");
    window.location.href = "index.html";

  } catch (err) {
    console.error(err);
    alert("서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요");
  }
});
