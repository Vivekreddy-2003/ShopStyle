function showMenu(id) {
  let menuContainer = document.getElementById(id);
  menuContainer.style.visibility = "visible";
  menuContainer.style.opacity = "1";
}
function hideMenu(id) {
  let menuContainer = document.getElementById(id);
  menuContainer.style.visibility = "hidden";
  menuContainer.style.opacity = "0";
}

var counter = 1;
setInterval(function () {
  document.getElementById("a" + counter).checked = true;
  document.getElementById("b" + counter).checked = true;
  document.getElementById("c" + counter).checked = true;
  document.getElementById("d" + counter).checked = true;
  document.getElementById("r" + counter).checked = true;
  document.getElementById("E" + counter).checked = true;
  document.getElementById("q" + counter).checked = true;
  document.getElementById("s" + counter).checked = true;

  counter++;

  if (counter > 5) {
    counter = 1;
  }
}, 2500);

var counter = 1;
setInterval(function () {
  document.getElementById("D" + counter).checked = true;
  counter++;

  if (counter > 2) {
    counter = 1;
  }
}, 1000);

var counter = 1;
setInterval(function () {
  document.getElementById("p" + counter).checked = true;
  counter++;

  if (counter > 3) {
    counter = 1;
  }
}, 1500);

let body = document.querySelector("body");
let signInBox = document.querySelector(".sign-in-box");
let signInContainer = document.querySelector(".sign-in-container");

function hideBox() {
  signInContainer.style.display = "none";
  document.body.style.overflow = "auto";
  window.location.reload();
}

function showBox() {
  signInContainer.style.display = "flex";
  document.body.style.overflow = "hidden";
}
