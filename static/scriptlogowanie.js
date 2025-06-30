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
  "obrazki/23.png",
  "obrazki/21.png",
  "obrazki/19.png",
  "obrazki/17.png",
  "obrazki/15.png",
  "obrazki/13.png"
];

const femaleAvatars = [
  "obrazki/1.png",
  "obrazki/3.png",
  "obrazki/5.png",
  "obrazki/7.png",
  "obrazki/9.png",
  "obrazki/11.png"
];

// Funkcja ładująca avatary
// Zmodyfikowana funkcja loadAvatars
function loadAvatars(avatarList) {
  avatarContainer.innerHTML = "";

  avatarList.forEach(src => {
    const img = document.createElement("img");
    img.src = "/static/" + src;
    img.alt = "Avatar";
    img.classList.add("avatar-option");

    img.addEventListener("click", () => {
      document.querySelectorAll(".avatar-option").forEach(avatar => {
        avatar.classList.remove("selected-avatar");
      });

      img.classList.add("selected-avatar");
      selectedAvatar = src;
      // Zmiana: zapisujemy tylko nazwę pliku (np. "5.png"), a nie pełną ścieżkę
      avatarHiddenInput.value = src.split('/').pop(); 
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