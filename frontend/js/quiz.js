/**
 * quiz.js — 기본소득 수령용 퀴즈 모달
 * 사용법: home.html에서 <script src="js/quiz.js"></script> 추가 후
 *         openQuizModal({ id, onResult }) 형태로 호출
 *
 * 하루 1회 제한과 정답 판정은 전부 백엔드 책임이다 (프론트에서만 막으면
 * localStorage 삭제/시간 조작/API 직접 호출로 우회 가능하기 때문).
 * 그래서 제출은 항상 mockSubmitQuiz()를 거쳐서 응답(status)만 보고 화면을 갱신한다.
 *
 * 지금은 백엔드 퀴즈 제출 API가 없어서 mockSubmitQuiz()가 더미로 채점한다.
 * answerIndex는 실제 서버가 붙기 전까지만 프론트가 들고 있는 임시 값이고,
 * 서버 연결 후에는 mockSubmitQuiz() 내부만 fetch로 교체하면 된다 (호출부는 그대로).
 */

const QUIZ_BANK = [
  {
    quizNum: 1,
    question: "'매수'는 무슨 뜻일까요?",
    options: ["주식을 사는 것", "주식을 파는 것", "주식을 보관하는 것", "주식을 등록하는 것"],
    answerIndex: 0,
  },
  {
    quizNum: 2,
    question: "'평균 매수가'는 무엇을 뜻할까요?",
    options: [
      "오늘 이 주식의 최고가",
      "내가 이 주식을 산 가격의 평균",
      "이 회사의 평균 매출",
      "친구들이 산 평균 가격",
    ],
    answerIndex: 1,
  },
  {
    quizNum: 3,
    question: "수익률이 '+5%'라는 건 무슨 뜻일까요?",
    options: [
      "산 가격보다 5% 떨어졌다",
      "산 가격보다 5% 올랐다",
      "5원이 늘었다",
      "5주를 더 샀다",
    ],
    answerIndex: 1,
  },
  {
    quizNum: 4,
    question: "주식을 '매도'하면 어떻게 될까요?",
    options: [
      "주식을 더 사게 된다",
      "주식을 팔아서 현금으로 바뀐다",
      "회사 직원이 된다",
      "배당금이 사라진다",
    ],
    answerIndex: 1,
  },
];

/**
 * 더미 채점 함수. 백엔드 퀴즈 제출 API가 완성되면 이 함수 내부만
 * 아래 fetch 코드로 바꾸면 된다 (요청/응답 형식은 미리 맞춰둔 상태).
 *
 *   const res = await fetch("http://localhost:8000/quiz/submit", {
 *     method: "POST",
 *     headers: { "Content-Type": "application/json" },
 *     body: JSON.stringify({ id, quizNum, answerIndex }),
 *   });
 *   if (!res.ok) throw new Error("quiz submit failed");
 *   return await res.json();
 *
 * @returns {Promise<{status: "correct"|"wrong"|"already_used", balance?: number}>}
 */
async function mockSubmitQuiz({ id, quizNum, answerIndex }) {
  const quiz = QUIZ_BANK.find(q => q.quizNum === quizNum);
  const isCorrect = quiz && answerIndex === quiz.answerIndex;

  return { status: isCorrect ? "correct" : "wrong" };
}

function getRandomQuiz() {
  return QUIZ_BANK[Math.floor(Math.random() * QUIZ_BANK.length)];
}

/**
 * 퀴즈 모달을 띄운다.
 * @param {Object} params
 * @param {string} params.id - 현재 로그인한 사용자 ID (User_Info.ID)
 * @param {Function} params.onResult - 제출 결과를 반영할 콜백
 *   onResult({ status, balance }) 형태로 호출된다.
 *   status: "correct" | "wrong" | "already_used" | "error"
 *   balance: status가 "correct"일 때만 내려오는 갱신된 잔고
 */
function openQuizModal({ id, onResult }) {
  const quiz = getRandomQuiz();
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
  });

  function showFeedbackWithCloseBtn(message, className) {
    feedbackEl.innerText = message;
    feedbackEl.className = `quiz-feedback ${className}`;
    feedbackEl.hidden = false;

    const closeBtn = document.createElement("button");
    closeBtn.className = "btn-secondary quiz-close-btn";
    closeBtn.innerText = "닫기";
    closeBtn.addEventListener("click", () => overlay.remove());
    overlay.querySelector(".quiz-actions").appendChild(closeBtn);
  }

  submitBtn.addEventListener("click", async () => {
    optionButtons.forEach(b => b.disabled = true);
    submitBtn.disabled = true;
    submitBtn.innerText = "채점 중...";

    try {
      // TODO: 백엔드 연결되면 mockSubmitQuiz를 실제 fetch 호출로 교체 (요청/응답 형식은 이미 맞춰둠)
      const data = await mockSubmitQuiz({ id, quizNum: quiz.quizNum, answerIndex: selectedIndex });

      if (data.status === "already_used") {
        showFeedbackWithCloseBtn("오늘의 퀴즈 기회는 이미 사용했습니다.", "wrong");
        onResult({ status: "already_used" });
        return;
      }

      if (data.status === "correct") {
        optionButtons[selectedIndex].classList.add("correct");
        feedbackEl.innerText = "정답입니다! 10,000원이 지급되었습니다.";
        feedbackEl.className = "quiz-feedback correct";
        feedbackEl.hidden = false;

        setTimeout(() => {
          overlay.remove();
          onResult({ status: "correct", balance: data.balance });
        }, 1200);
        return;
      }

      // status === "wrong"
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
