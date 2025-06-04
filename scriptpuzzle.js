let firstSelected = null;
let move = 0;

const totalPieces = 9;
const puzzleFolder = "puzzle-img";
const puzzleBoard = document.getElementById("puzzleBoard");
const counterElement = document.getElementById("counter");
// Zmieniamy odwołanie do nowego ID przycisku
const nextPageButton = document.getElementById("nextPageButton");

// Tablica do przechowywania elementów obrazków w ich początkowej (ułożonej) kolejności
let originalPuzzleOrder = [];

/**
 * Tworzy elementy <img> dla każdego kawałka puzzli i dodaje je do planszy.
 * Zapisuje również oryginalną kolejność puzzli.
 */
function createPuzzleImages() {
    puzzleBoard.innerHTML = ''; // Wyczyść planszę na wypadek ponownego wywołania
    originalPuzzleOrder = []; // Resetuj oryginalną kolejność

    for (let i = 1; i <= totalPieces; i++) {
        const img = document.createElement("img");
        img.src = `${puzzleFolder}/img (${i}).jpg`;
        img.classList.add("puzzle-img");
        // dataset.originalIndex będzie używany do sprawdzenia, czy puzzle są ułożone
        img.dataset.originalIndex = i.toString(); // Zapisz oryginalny indeks jako string
        puzzleBoard.appendChild(img);
        originalPuzzleOrder.push(img); // Dodaj do tablicy oryginalnej kolejności
    }
    addPuzzleClickListeners();
    // Automatycznie wymieszaj puzzle po stworzeniu, skoro nie ma przycisku "Wymieszaj"
    shufflePuzzle();
    // Początkowo wyłącz przycisk "Przejdź dalej", dopóki puzzle nie zostaną ułożone
    nextPageButton.disabled = true;
}

/**
 * Dodaje nasłuchiwacze zdarzeń kliknięcia do wszystkich kawałków puzzli.
 */
function addPuzzleClickListeners() {
    document.querySelectorAll('.puzzle-img').forEach(img => {
        img.addEventListener('click', () => {
            if (!firstSelected) {
                selectPuzzle(img);
            } else {
                if (firstSelected !== img) {
                    movePuzzle(firstSelected, img);
                }
                deselectPuzzle(firstSelected);
                firstSelected = null;
            }
        });
    });
}

function selectPuzzle(img) {
    firstSelected = img;
    img.classList.add('selected');
}

function deselectPuzzle(img) {
    img.classList.remove('selected');
}

/**
 * Zamienia miejscami dwa kawałki puzzli.
 * @param {HTMLImageElement} img1 - Pierwszy obrazek.
 * @param {HTMLImageElement} img2 - Drugi obrazek.
 */
function movePuzzle(img1, img2) {
    const tempSrc = img1.src;
    img1.src = img2.src;
    img2.src = tempSrc;

    move++;
    counterElement.innerText = "Ruchy = " + move;

    // Po każdym ruchu sprawdzamy, czy puzzle są ułożone
    checkWinCondition();
}

/**
 * Miesza puzzle na planszy.
 */
function shufflePuzzle() {
    const puzzleImgs = Array.from(document.querySelectorAll('.puzzle-img'));
    const sources = puzzleImgs.map(img => img.src);

    for (let i = sources.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [sources[i], sources[j]] = [sources[j], sources[i]];
    }

    puzzleImgs.forEach((img, index) => {
        img.src = sources[index];
    });

    move = 0;
    counterElement.innerText = "Ruchy = 0";
    if (firstSelected) {
        deselectPuzzle(firstSelected);
        firstSelected = null;
    }
    // Po przetasowaniu, puzzle na pewno nie są ułożone, więc wyłącz przycisk "Przejdź dalej"
    nextPageButton.disabled = true;
}

/**
 * Sprawdza, czy wszystkie puzzle są w poprawnej kolejności.
 * Porównuje aktualne ścieżki obrazków z ich oryginalnymi indeksami.
 */
function checkWinCondition() {
    const currentPuzzleImgs = Array.from(document.querySelectorAll('.puzzle-img'));
    let isSolved = true;

    currentPuzzleImgs.forEach((img, index) => {
        // Oczekiwany indeks dla tej pozycji to (index + 1)
        // Porównujemy ostatni człon ścieżki (np. "img (1).jpg") z oczekiwanym
        const expectedSrcPart = `img (${index + 1}).jpg`;
        if (!img.src.endsWith(expectedSrcPart)) {
            isSolved = false;
        }
    });

    if (isSolved) {
        console.log("PUZZLE UŁOŻONE!");
        // Aktywuj przycisk "Przejdź dalej", jeśli puzzle są ułożone
        nextPageButton.disabled = false;
        // Opcjonalnie: możesz dodać jakąś animację, dźwięk lub alert
        // alert("Gratulacje! Puzzle ułożone!");
    } else {
        // Jeśli puzzle nie są ułożone (lub zostały pomieszane), wyłącz przycisk
        nextPageButton.disabled = true;
    }
}

// Obsługa kliknięcia przycisku "Przejdź dalej"
nextPageButton.addEventListener("click", () => {
    // Sprawdź, czy puzzle są ułożone, zanim przejdziesz dalej (dodatkowe zabezpieczenie)
    if (nextPageButton.disabled) {
        alert("Musisz najpierw ułożyć puzzle!");
        return;
    }
    // Tutaj możesz określić, na jaką stronę chcesz przejść
    window.location.href = 'nastepna_strona.html'; // Zastąp 'nastepna_strona.html' faktyczną nazwą pliku
});

// Inicjalizacja: stwórz puzzle po załadowaniu DOM
document.addEventListener('DOMContentLoaded', createPuzzleImages);
