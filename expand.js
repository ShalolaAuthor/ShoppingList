const textbox = document.getElementById("userInput");
textbox.addEventListener("input", function () {
  textbox.style.height = "auto";
  textbox.style.height = textbox.scrollHeight + "px";
});
