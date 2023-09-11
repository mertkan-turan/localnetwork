// On mobile the chat-rooms is toggled with a checkbox
const toggle = document.querySelector("#toggle");

document.querySelector(".chat-rooms ul").addEventListener("click", (e) => {
  e.preventDefault();
  const tar = e.target;
  if (tar.tagName === "A") {
    tar.closest("ul").querySelector(".selected").classList.remove("selected");
    tar.closest("li").classList.add("selected");
    // uncheck to hide the chat-rooms list
    toggle.checked = false;
  }
});


