// Elementy DOM
const maleButton = document.getElementById("male-gender");
const femaleButton = document.getElementById("famale-gender");
const avatarContainer = document.querySelector(".avatars");
const nameInput = document.getElementById("name");
const confirmButton = document.getElementById("confirm-name");

let selectedAvatar = null; // Zmienna do przechowania wybranego awatara

// Zestawy avatarów (ścieżki do obrazów)
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

// Funkcja do załadowania avatarów do kontenera (z możliwością wyboru)
function loadAvatars(avatarList) {
  avatarContainer.innerHTML = ""; 

  avatarList.forEach(src => {
    const img = document.createElement("img");
    img.src = src;
    img.alt = "Avatar";
    img.classList.add("avatar-option");

    // Obsługa kliknięcia na awatar
    img.addEventListener("click", () => {
      // Usuń zaznaczenie ze wszystkich
      document.querySelectorAll(".avatar-option").forEach(avatar => {
        avatar.classList.remove("selected-avatar");
      });

      // Zaznacz kliknięty
      img.classList.add("selected-avatar");
      selectedAvatar = src;
    });

    avatarContainer.appendChild(img);
  });
}

// Obsługa kliknięcia gender
maleButton.addEventListener("click", () => {
  loadAvatars(maleAvatars);
});

femaleButton.addEventListener("click", () => {
  loadAvatars(femaleAvatars);
});

// Obsługa wpisania pseudonimu przez Enter
nameInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    confirmName();
  }
});

// Obsługa kliknięcia przycisku "Zatwierdź"
confirmButton.addEventListener("click", confirmName);

// Funkcja pomocnicza do potwierdzenia imienia
function confirmName() {
  const name = nameInput.value.trim();

  if (!name) {
    alert("Wpisz swoje imię!");
    return;
  }

  if (!selectedAvatar) {
    alert("Wybierz awatara!");
    return;
  }

  // Możesz zapisać dane do localStorage lub przekazać je dalej
  // localStorage.setItem("userName", name);
  // localStorage.setItem("selectedAvatar", selectedAvatar);

  alert(`Witaj, ${name}! Wybrałeś awatar: ${selectedAvatar}`);
}
