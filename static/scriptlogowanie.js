// Elementy DOM
const maleButton = document.getElementById("male-gender");
const femaleButton = document.getElementById("famale-gender");
const avatarContainer = document.querySelector(".avatars");
const nameInput = document.getElementById("name");
const avatarHiddenInput = document.getElementById("selected-avatar");
const form = document.getElementById("user-form");

let selectedAvatar = null;

// Zestawy avatarów
const maleAvatars = [
  "/static/obrazki/23.png",
  "/static/obrazki/21.png",
  "/static/obrazki/19.png",
  "/static/obrazki/17.png",
  "/static/obrazki/15.png",
  "/static/obrazki/13.png"
];

const femaleAvatars = [
  "/static/obrazki/1.png",
  "/static/obrazki/3.png",
  "/static/obrazki/5.png",
  "/static/obrazki/7.png",
  "/static/obrazki/9.png",
  "/static/obrazki/11.png"
];

// Funkcja ładująca avatary
function loadAvatars(avatarList) {
  avatarContainer.innerHTML = "";

  avatarList.forEach(src => {
    const img = document.createElement("img");
    img.src = src;
    img.alt = "Avatar";
    img.classList.add("avatar-option");

    img.addEventListener("click", () => {
      document.querySelectorAll(".avatar-option").forEach(avatar => {
        avatar.classList.remove("selected-avatar");
      });

      img.classList.add("selected-avatar");
      selectedAvatar = src;
      avatarHiddenInput.value = src; // ustaw hidden input do formularza
    });

    avatarContainer.appendChild(img);
  });
}

// Obsługa wyboru płci
maleButton.addEventListener("click", () => loadAvatars(maleAvatars));
femaleButton.addEventListener("click", () => loadAvatars(femaleAvatars));

// Walidacja przy submit
form.addEventListener("submit", (e) => {
  if (!nameInput.value.trim()) {
    alert("Wpisz swoje imię!");
    e.preventDefault();
  } else if (!selectedAvatar) {
    alert("Wybierz awatara!");
    e.preventDefault();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  loadAvatars(maleAvatars); 
});