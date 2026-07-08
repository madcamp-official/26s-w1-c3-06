document.addEventListener("DOMContentLoaded", async () => {

  const id = localStorage.getItem("id");
  if (!id) {
    window.location.href = "index.html";
    return;
  }

  const profileImage = document.getElementById("profileAvatar"); // <img> 엘리먼트 id는 그대로 둠 (화면 요소 이름이라 상관없음)
  const profileName = document.getElementById("profileName");
  const profileID = document.getElementById("profileHandle");

  const nicknameInput = document.getElementById("nicknameInput");
  const nicknameCheckMessage = document.getElementById("nicknameCheckMessage");
  const checkNicknameBtn = document.getElementById("checkNicknameBtn");
  const passwordInput = document.getElementById("passwordInput");
  const profileImageInput = document.getElementById("profileImageInput");

  let currentNickname = "";
  let isNicknameChecked = true;
  // 새로 고른 프로필 사진(base64). 안 바꿨으면 null로 두고 저장 요청에 아예 포함시키지 않는다.
  let pendingProfile = null;
  // "사진 삭제" 버튼을 눌렀는지 여부. pendingProfile=null만으로는 "안 바꿈"과 "지움"을 구분할 수
  // 없어서 별도 플래그로 구분하고, 저장 시 profile:null을 명시적으로 보낸다.
  let profileDeleted = false;

  profileImage.src = "image/default-profile.svg";
  profileID.innerText = `@${id}`;

  try {
    const res = await fetch(`/api/account?id=${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error("계좌 정보를 불러오지 못했습니다");

    const data = await res.json();
    if (data.status !== "success") throw new Error(data.message || "계좌 정보를 불러오지 못했습니다");

    currentNickname = data.mockAccount.nickname;
    profileName.innerText = currentNickname;
    nicknameInput.value = currentNickname;
    // 사진은 항상 백엔드(User_Info.Profile)를 기준으로 표시한다. localStorage 캐시는 로그아웃하면
    // 지워지므로(다른 계정 사진이 남아 보이는 것 방지) 신뢰할 수 있는 출처가 아니다.
    profileImage.src = data.mockAccount.profileImage || "image/default-profile.svg";
  } catch (err) {
    console.error(err);
    alert("계정 정보를 불러오지 못했습니다. 다시 로그인해 주세요.");
    window.location.href = "index.html";
    return;
  }

  function showMessage(element, message, isSuccess) {
    element.hidden = false;
    element.textContent = message;
    element.style.color = isSuccess ? "#2e7d32" : "#d32f2f";
  }

  nicknameInput.addEventListener("input", () => {
    const nickname = nicknameInput.value.trim();
    isNicknameChecked = (nickname === currentNickname);
    nicknameCheckMessage.hidden = true;
  });

  checkNicknameBtn.addEventListener("click", async () => {
    const nickname = nicknameInput.value.trim();

    if (!nickname) {
      showMessage(nicknameCheckMessage, "닉네임을 입력해주세요", false);
      return;
    }

    if (nickname === currentNickname) {
      isNicknameChecked = true;
      showMessage(nicknameCheckMessage, "지금 쓰고 있는 닉네임이에요", true);
      return;
    }

    try {
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

  profileImageInput.addEventListener("change", () => {
    const file = profileImageInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      // reader.result는 "data:image/png;base64,...." 형태의 base64 문자열.
      // 화면 미리보기만 바로 반영하고, 실제 저장(localStorage 캐시 + PATCH /settings 전송)은
      // 저장하기 버튼을 눌렀을 때만 이루어진다.
      pendingProfile = reader.result;
      profileDeleted = false;
      profileImage.src = reader.result;
    };
    reader.readAsDataURL(file);
  });

  document.getElementById("removeProfileImageBtn").addEventListener("click", () => {
    pendingProfile = null;
    profileDeleted = true;
    profileImageInput.value = "";
    profileImage.src = "image/default-profile.svg";
  });

  document.getElementById("saveBtn").addEventListener("click", async () => {
    const nickname = nicknameInput.value.trim();
    const password = passwordInput.value;

    if (!nickname) {
      alert("닉네임을 입력해주세요");
      return;
    }

    if (nickname !== currentNickname && !isNicknameChecked) {
      alert("닉네임 중복확인을 해주세요");
      return;
    }

    const body = { userId: id, nickname };
    if (password) body.password = password;
    if (pendingProfile) body.profile = pendingProfile;
    else if (profileDeleted) body.profile = null;

    try {
      const res = await fetch("/api/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      if (!res.ok || data.status !== "success") {
        throw new Error(data.message || "저장에 실패했습니다");
      }

      currentNickname = nickname;
      isNicknameChecked = true;
      passwordInput.value = "";

      profileName.innerText = nickname;
      localStorage.setItem("nickname", nickname);

      pendingProfile = null;
      profileDeleted = false;

      alert("저장됐어요");
    } catch (err) {
      console.error(err);
      alert(err.message || "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.");
    }
  });

  document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "index.html";
  });

  document.getElementById("deleteAccountBtn").addEventListener("click", async () => {
    const confirmed = confirm(
      "정말 계좌를 삭제하시겠어요?\n보유주식, 거래내역, 친구 목록이 모두 사라지며 복구할 수 없습니다."
    );
    if (!confirmed) return;

    try {
      const res = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: id }),
      });

      const data = await res.json();
      if (!res.ok || data.status !== "success") {
        throw new Error(data.message || "계좌 삭제에 실패했습니다");
      }

      alert("계좌가 삭제됐어요");
      localStorage.clear();
      window.location.href = "index.html";
    } catch (err) {
      console.error(err);
      alert(err.message || "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.");
    }
  });
});
