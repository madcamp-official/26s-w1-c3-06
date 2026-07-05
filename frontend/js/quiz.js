/**
 * quiz.js — 기본소득 수령용 퀴즈 모달
 * 사용법: home.html에서 <script src="js/quiz.js"></script> 추가 후
 *         openQuizModal(onCorrect) 함수를 "기본소득 받기" 버튼 클릭 시 호출
 */

// TODO: 백엔드 API 완성되면 이 문제은행 대신 fetch로 서버에서 받아오기 (정답은 서버에서만 검증해야 안전함)
const QUIZ_BANK = [
  {
    question: "'매수'는 무슨 뜻일까요?",
    options: ["주식을 사는 것", "주식을 파는 것", "주식을 보관하는 것", "주식을 등록하는 것"],
    answerIndex: 0,
  },
  {
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

function getRandomQuiz() {
  return QUIZ_BANK[Math.floor(Math.random() * QUIZ_BANK.length)];
}

/**
 * 퀴즈 모달을 띄우고, 정답을 맞히면 onCorrect 콜백을 실행한다.
 * @param {Function} onCorrect - 정답을 맞혔을 때 호출할 함수 (기본소득 지급 처리)
 */
function openQuizModal(onCorrect) {
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

  submitBtn.addEventListener("click", () => {
    // TODO: 실제로는 정답 여부를 서버에 물어봐야 함 (클라이언트에 정답이 노출되면 조작 가능)
    const isCorrect = selectedIndex === quiz.answerIndex;

    optionButtons.forEach(b => b.disabled = true);
    submitBtn.disabled = true;

    if (isCorrect) {
      optionButtons[selectedIndex].classList.add("correct");
      feedbackEl.innerText = "정답이에요! 기본소득을 받았어요";
      feedbackEl.className = "quiz-feedback correct";
      feedbackEl.hidden = false;

      setTimeout(() => {
        overlay.remove();
        onCorrect();
      }, 1200);

    } else {
      optionButtons[selectedIndex].classList.add("wrong");
      optionButtons[quiz.answerIndex].classList.add("correct");
      feedbackEl.innerText = "아쉬워요, 정답이 아니에요. 내일 다시 도전해보세요";
      feedbackEl.className = "quiz-feedback wrong";
      feedbackEl.hidden = false;

      const closeBtn = document.createElement("button");
      closeBtn.className = "btn-secondary quiz-close-btn";
      closeBtn.innerText = "닫기";
      closeBtn.addEventListener("click", () => overlay.remove());
      overlay.querySelector(".quiz-actions").appendChild(closeBtn);
    }
  });
}
