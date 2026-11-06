const quiz = document.querySelector("#quiz");
const result = document.querySelector("#result");

quiz.addEventListener("submit", (event) => {
  event.preventDefault();
  const questions = [...quiz.querySelectorAll("fieldset")];
  let score = 0;
  let unanswered = 0;

  questions.forEach((question) => {
    const selected = question.querySelector("input:checked");
    const feedback = question.querySelector(".feedback");
    const correct = selected?.value === question.dataset.answer;
    if (!selected) unanswered += 1;
    if (correct) score += 1;

    feedback.className = `feedback visible ${correct ? "correct" : "incorrect"}`;
    feedback.textContent = `${correct ? "Correct." : selected ? "Not quite." : "No answer selected."} ${question.dataset.explanation}`;
  });

  result.textContent = unanswered
    ? `Group score: ${score} out of ${questions.length}. ${unanswered} question${unanswered === 1 ? " is" : "s are"} unanswered.`
    : `Group score: ${score} out of ${questions.length}. Review the explanations together.`;
});

quiz.addEventListener("reset", () => {
  quiz.querySelectorAll(".feedback").forEach((feedback) => {
    feedback.className = "feedback";
    feedback.textContent = "";
  });
  result.textContent = "";
});
