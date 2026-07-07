document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체
  // profile: DB의 User_Info.Profile(BINARY) 그대로 대응되는 필드명
  const mockProfile = {
    nickname: "김혜리",
    userId: "@ireyhye",
    profile: localStorage.getItem("profileImage") || "https://placehold.co/96x96",
  };

  const currentNickname = mockProfile.nickname;

  const profileImage = document.getElementById("profileAvatar"); // <img> 엘리먼트 id는 그대로 둠 (화면 요소 이름이라 상관없음)
  const profileName = document.getElementById("profileName");
  const profileID = document.getElementById("profileHandle");

  const nicknameInput = document.getElementById("nicknameInput");
  const nicknameCheckMessage = document.getElementById("nicknameCheckMessage");
  const checkNicknameBtn = document.getElementById("checkNicknameBtn");
  const passwordInput = document.getElementById("passwordInput");
  const profileImageInput = document.getElementById("profileImageInput");

  let isNicknameChecked = true;

  profileImage.src = mockProfile.profile;
  profileName.innerText = mockProfile.nickname;
  profileID.innerText = mockProfile.userId;
  nicknameInput.value = mockProfile.nickname;

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
        `http://localhost:5000/auth/check-nickname?nickname=${encodeURIComponent(nickname)}`
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
      // reader.result는 "data:image/png;base64,...." 형태의 base64 문자열
      // TODO: 백엔드 연결 시 이 base64 문자열을 Profile(BINARY) 필드로 서버에 전송해야 함
      profileImage.src = reader.result;
      localStorage.setItem("profileImage", reader.result);
    };
    reader.readAsDataURL(file);
  });

  document.getElementById("saveBtn").addEventListener("click", () => {
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

    profileName.innerText = nickname;
    localStorage.setItem("nickname", nickname);

    // TODO: 백엔드 정보수정 API 호출
    // profile 필드는 base64 문자열(reader.result)을 그대로 보내거나,
    // 백엔드가 원하는 형식(예: multipart/form-data)에 맞춰 다시 변환해서 보내야 함
    alert("저장됐어요");
  });

  document.getElementById("deleteAccountBtn").addEventListener("click", () => {
    const confirmed = confirm(
      "정말 계좌를 삭제하시겠어요?\n보유주식, 거래내역, 친구 목록이 모두 사라지며 복구할 수 없습니다."
    );
    if (!confirmed) return;

    alert("계좌가 삭제됐어요");
    localStorage.removeItem("token");
    window.location.href = "index.html";
  });
});