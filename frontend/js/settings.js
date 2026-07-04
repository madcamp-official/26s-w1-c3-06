document.addEventListener("DOMContentLoaded", () => {

  // TODO: 백엔드 API 완성되면 이 더미 데이터 대신 fetch로 교체
  const mockProfile = {
    name: "김혜리",
    handle: "@ireyhye",
  };

  document.getElementById("profileName").innerText = mockProfile.name;
  document.getElementById("profileHandle").innerText = mockProfile.handle;
  document.getElementById("nicknameInput").value = mockProfile.name;

  document.getElementById("saveBtn").addEventListener("click", async () => {
    const nickname = document.getElementById("nicknameInput").value.trim();
    const password = document.getElementById("passwordInput").value;

    if (!nickname) {
      alert("닉네임을 입력해주세요");
      return;
    }

    // TODO: 백엔드 정보수정 API 호출 (닉네임, 비밀번호(입력 시에만))
    alert("저장됐어요");
  });

  document.getElementById("deleteAccountBtn").addEventListener("click", () => {
    const confirmed = confirm(
      "정말 계좌를 삭제하시겠어요?\n보유주식, 거래내역, 친구 목록이 모두 사라지며 복구할 수 없습니다."
    );
    if (!confirmed) return;

    // TODO: 백엔드 계좌 삭제 API 호출
    alert("계좌가 삭제됐어요");
    localStorage.removeItem("token");
    window.location.href = "index.html";
  });
});
