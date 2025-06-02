let adminModalOpened = false;

document.querySelector(".admin-icon").addEventListener("click", () => {
    const modal = document.getElementById("admin-modal");
    modal.style.display = "flex";

    // 잠깐 뒤에 외부 클릭 감지를 시작
    setTimeout(() => {
        adminModalOpened = true;
    }, 10);
});

document.addEventListener("click", function (event) {
    const modal = document.getElementById("admin-modal");
    const modalContent = document.getElementById("admin-modal-content");

    if (!modal || modal.style.display !== "flex" || !adminModalOpened) return;

    if (!modalContent.contains(event.target)) {
        modal.style.display = "none";
        adminModalOpened = false;
    }
});

document.querySelectorAll(".faq li").forEach(item => {
  item.addEventListener("click", () => {
    const answerBox = item.querySelector(".faq-answer");
    const answer = item.dataset.answer;

    if (answerBox.style.display === "none") {
      answerBox.textContent = answer;
      answerBox.style.display = "block";
    } else {
      answerBox.style.display = "none";
    }
  });
});