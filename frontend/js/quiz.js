/**
 * quiz.js — 기본소득 수령용 퀴즈 모달
 * 사용법: home.html에서 <script src="js/quiz.js"></script> 추가 후
 *         openQuizModal({ id, onResult }) 형태로 호출
 *
 * 하루 1회 제한과 정답 판정은 전부 백엔드 책임이다 (프론트에서만 막으면
 * localStorage 삭제/시간 조작/API 직접 호출로 우회 가능하기 때문).
 * 그래서 제출은 항상 서버 응답(status/correct/already_used)만 보고 화면을 갱신한다.
 */

/**
 * 오늘의 퀴즈를 불러온다. endpoint: GET /quiz?userId=
 * @returns {Promise<{status, already_used?, quiz_num?, quiz_body?, message}>}
 */
async function fetchQuiz(id) {
  const res = await fetch(`/api/quiz?id=${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error("퀴즈를 불러오지 못했습니다");
  return await res.json();
}

/**
 * 퀴즈 답안을 제출하고 채점 결과를 받는다. endpoint: POST /quiz/submit
 * @returns {Promise<{status, correct?, already_used?, balance?, message}>}
 */
async function submitQuiz({ id, quizNum, answerIndex }) {
  const res = await fetch("/api/quiz/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId: id, quiz_num: quizNum, answerIndex }),
  });
  if (!res.ok) throw new Error("퀴즈 제출에 실패했습니다");
  return await res.json();
}

/**
 * 퀴즈 모달을 띄운다.
 * @param {Object} params
 * @param {string} params.id - 현재 로그인한 사용자 ID (User_Info.ID)
 * @param {Function} params.onResult - 제출 결과를 반영할 콜백
 *   onResult({ status, balance }) 형태로 호출된다.
 *   status: "correct" | "wrong" | "already_used" | "error" | "cancelled"
 *   balance: status가 "correct"일 때만 내려오는 갱신된 총자산(User_Info.Balance)
 */
async function openQuizModal({ id, onResult }) {
  let quizData;

  try {
    quizData = await fetchQuiz(id);
  } catch (err) {
    console.error(err);
    alert("퀴즈를 불러오지 못했어요. 잠시 후 다시 시도해주세요.");
    onResult({ status: "error" });
    return;
  }

  if (quizData.status !== "success") {
    alert(quizData.message || "퀴즈를 불러오지 못했어요.");
    onResult({ status: "error" });
    return;
  }

  if (quizData.already_used || quizData.quiz_num === undefined || quizData.quiz_body === undefined) {
    alert("오늘의 퀴즈 기회는 이미 사용했습니다.");
    onResult({ status: "already_used" });
    return;
  }

  const quiz = {
    quizNum: quizData.quiz_num,
    question: quizData.quiz_body.question,
    options: quizData.quiz_body.options,
  };

  let selectedIndex = null;

  const overlay = document.createElement("div");
  overlay.className = "quiz-overlay";
  overlay.innerHTML = `
    <div class="quiz-modal">
      <p class="quiz-heading">기본소득을 받으려면 퀴즈를 풀어주세요</p>
      <p class="quiz-question">${quiz.question}</p>

      <div class="quiz-options" id="quizOptions">
        ${quiz.options.map((opt, i) => `
          <button class="quiz-option-btn" data-index="${i}">${opt}</button>
        `).join("")}
      </div>

      <p class="quiz-feedback" id="quizFeedback" hidden></p>

      <div class="quiz-actions">
        <button class="btn-secondary" id="quizCancelBtn">취소</button>
        <button class="btn-primary" id="quizSubmitBtn" disabled>제출하기</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const optionButtons = overlay.querySelectorAll(".quiz-option-btn");
  const submitBtn = overlay.querySelector("#quizSubmitBtn");
  const feedbackEl = overlay.querySelector("#quizFeedback");

  optionButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      optionButtons.forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
      selectedIndex = Number(btn.dataset.index);
      submitBtn.disabled = false;
    });
  });

  overlay.querySelector("#quizCancelBtn").addEventListener("click", () => {
    overlay.remove();
    onResult({ status: "cancelled" });
  });

  function showFeedbackWithCloseBtn(message, className) {
    feedbackEl.innerText = message;
    feedbackEl.className = `quiz-feedback ${className}`;
    feedbackEl.hidden = false;

    // 채점이 끝난 뒤에는 닫기 버튼만 남기고 취소/제출 버튼은 없앤다.
    const actionsEl = overlay.querySelector(".quiz-actions");
    actionsEl.innerHTML = "";

    const closeBtn = document.createElement("button");
    closeBtn.className = "btn-secondary quiz-close-btn";
    closeBtn.innerText = "닫기";
    closeBtn.addEventListener("click", () => overlay.remove());
    actionsEl.appendChild(closeBtn);
  }

  submitBtn.addEventListener("click", async () => {
    optionButtons.forEach(b => b.disabled = true);
    submitBtn.disabled = true;

    try {
      const data = await submitQuiz({ id, quizNum: quiz.quizNum, answerIndex: selectedIndex });

      if (data.status !== "success") {
        throw new Error(data.message || "채점에 실패했습니다");
      }

      if (data.already_used) {
        showFeedbackWithCloseBtn("오늘의 퀴즈 기회는 이미 사용했습니다.", "wrong");
        onResult({ status: "already_used" });
        return;
      }

      if (data.correct) {
        optionButtons[selectedIndex].classList.add("correct");
        showFeedbackWithCloseBtn("정답입니다! 10,000원이 지급되었습니다.", "correct");
        onResult({ status: "correct", balance: data.balance });
        return;
      }

      // data.correct === false
      optionButtons[selectedIndex].classList.add("wrong");
      showFeedbackWithCloseBtn("오답입니다. 오늘의 기회를 사용했습니다.", "wrong");
      onResult({ status: "wrong" });

    } catch (err) {
      console.error(err);
      showFeedbackWithCloseBtn("서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.", "wrong");
      onResult({ status: "error" });
    }
  });
}
