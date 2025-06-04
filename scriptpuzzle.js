let firstSelected = null;
let move = 0;

const totalPieces = 9;
const puzzleFolder = "puzzle-img"; // Upewnij się, że to poprawna ścieżka do folderu z kawałkami puzzli
const puzzleBoard = document.getElementById("puzzleBoard");
const counterElement = document.getElementById("counter"); // Odwołanie do elementu licznika
const shuffleButton = document.getElementById("shuffle"); // Odwołanie do przycisku mieszania

/**
 * Tworzy elementy <img> dla każdego kawałka puzzli i dodaje je do planszy.
 */
function createPuzzleImages() {
    // Wyczyść planszę na wypadek ponownego wywołania
    puzzleBoard.innerHTML = '';

    for (let i = 1; i <= totalPieces; i++) {
        const img = document.createElement("img");
        img.src = `${puzzleFolder}/img (${i}).jpg`; // Ścieżka do obrazka
        img.classList.add("puzzle-img");
        // img.draggable = true; // draggable jest potrzebne tylko dla drag and drop, nie dla click
        img.dataset.originalIndex = i; // Zachowaj oryginalny indeks, przydatny do sprawdzenia rozwiązania
        puzzleBoard.appendChild(img);
    }
    // Po utworzeniu obrazków, dodaj do nich nasłuchiwacze zdarzeń
    addPuzzleClickListeners();
    // Wymieszaj puzzle po stworzeniu, aby nie były od razu ułożone
    shufflePuzzle();
}

/**
 * Dodaje nasłuchiwacze zdarzeń kliknięcia do wszystkich kawałków puzzli.
 */
function addPuzzleClickListeners() {
    document.querySelectorAll('.puzzle-img').forEach(img => {
        img.addEventListener('click', () => {
            if (!firstSelected) {
                // Jeśli nic nie jest zaznaczone, zaznacz ten obrazek
                selectPuzzle(img);
            } else {
                // Jeśli coś jest już zaznaczone
                if (firstSelected !== img) {
                    // Jeśli kliknięto inny obrazek, zamień miejscami
                    movePuzzle(firstSelected, img);
                }
                // Niezależnie od tego, czy był to ten sam obrazek, czy inny, odznacz pierwszy
                deselectPuzzle(firstSelected);
                firstSelected = null; // Zresetuj zaznaczenie
            }
        });
    });
}

/**
 * Zaznacza kawałek puzzla.
 * @param {HTMLImageElement} img - Element obrazka do zaznaczenia.
 */
function selectPuzzle(img) {
    firstSelected = img;
    img.classList.add('selected');
}

/**
 * Odznacza kawałek puzzla.
 * @param {HTMLImageElement} img - Element obrazka do odznaczenia.
 */
function deselectPuzzle(img) {
    img.classList.remove('selected');
}

/**
 * Zamienia miejscami dwa kawałki puzzli.
 * @param {HTMLImageElement} img1 - Pierwszy obrazek.
 * @param {HTMLImageElement} img2 - Drugi obrazek.
 */
function movePuzzle(img1, img2) {
    // Wymiana obrazków poprzez zamianę wartości 'src'
    const tempSrc = img1.src;
    img1.src = img2.src;
    img2.src = tempSrc;

    // Zwiększ licznik ruchów
    move++;
    counterElement.innerText = "Ruchy = " + move;

    // Opcjonalnie: Sprawdź, czy puzzle są ułożone po każdym ruchu
    // checkWinCondition();
}

/**
 * Miesza puzzle na planszy.
 */
function shufflePuzzle() {
    const puzzleImgs = Array.from(document.querySelectorAll('.puzzle-img'));
    // Pobierz ścieżki do obrazków z aktualnych puzzli
    const sources = puzzleImgs.map(img => img.src);

    // Algorytm Fisher-Yates shuffle do mieszania tablicy ścieżek
    for (let i = sources.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [sources[i], sources[j]] = [sources[j], sources[i]]; // Zamiana elementów
    }

    // Przypisz wymieszane ścieżki z powrotem do elementów <img>
    puzzleImgs.forEach((img, index) => {
        img.src = sources[index];
    });

    // Zresetuj licznik ruchów
    move = 0;
    counterElement.innerText = "Ruchy = 0";
    // Odznacz ewentualnie zaznaczony puzzel
    if (firstSelected) {
        deselectPuzzle(firstSelected);
        firstSelected = null;
    }
}

// Dodaj nasłuchiwacz zdarzeń do przycisku mieszania
shuffleButton.addEventListener("click", shufflePuzzle);

// Inicjalizacja: stwórz puzzle po załadowaniu DOM
document.addEventListener('DOMContentLoaded', createPuzzleImages);

