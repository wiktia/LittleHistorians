let firstSelected = null;
let move = 0;
let isPuzzleSolved = false;

const totalPieces = 9;
const puzzleFolder = "/static/puzzle-img";
const puzzleBoard = document.getElementById("puzzleBoard");
const counterElement = document.getElementById("counter");
const nextPageButton = document.getElementById("nextPageButton");

// Element debugowania
const debugInfo = document.createElement("div");
debugInfo.id = "debugInfo";
debugInfo.style.cssText = "color: red; margin: 10px auto; text-align: center;";
document.querySelector(".container").appendChild(debugInfo);

function createPuzzleImages() {
    puzzleBoard.innerHTML = '';
    firstSelected = null;
    move = 0;
    isPuzzleSolved = false;
    nextPageButton.disabled = true;
    debugInfo.textContent = "";
    
    for (let i = 1; i <= totalPieces; i++) {
        const img = document.createElement("img");
        img.src = `${puzzleFolder}/img (${i}).jpg`;
        img.classList.add("puzzle-img");
        img.dataset.originalIndex = i.toString(); // Zapisz oryginalny indeks
        puzzleBoard.appendChild(img);
    }

    addPuzzleClickListeners();
    shufflePuzzle();
}

function addPuzzleClickListeners() {
    document.querySelectorAll('.puzzle-img').forEach(img => {
        img.addEventListener('click', () => {
            if (isPuzzleSolved) return;
            
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

function movePuzzle(img1, img2) {
    // Zamień źródła obrazków
    const tempSrc = img1.src;
    img1.src = img2.src;
    img2.src = tempSrc;

    move++;
    counterElement.innerText = "Ruchy = " + move;

    checkWinCondition();
}

function shufflePuzzle() {
    const puzzleImgs = Array.from(document.querySelectorAll('.puzzle-img'));
    const sources = puzzleImgs.map(img => img.src);

    // Fisher-Yates shuffle
    for (let i = sources.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [sources[i], sources[j]] = [sources[j], sources[i]];
    }

    puzzleImgs.forEach((img, index) => {
        img.src = sources[index];
    });

    move = 0;
    counterElement.innerText = "Ruchy = 0";
    debugInfo.textContent = "Puzzle przetasowane. Zacznij układanie!";

    if (firstSelected) {
        deselectPuzzle(firstSelected);
        firstSelected = null;
    }

    nextPageButton.disabled = true;
    isPuzzleSolved = false;
}

function checkWinCondition() {
    const currentPuzzleImgs = Array.from(document.querySelectorAll('.puzzle-img'));
    let isSolved = true;

    currentPuzzleImgs.forEach(img => {
        const originalIndex = img.dataset.originalIndex;
        
        // dekodowanie URL i obsługa spacji
        const decodedSrc = decodeURIComponent(img.src);
        const currentFilename = decodedSrc.split('/').pop();
        
        // wyciąganie numeru z nazwy pliku
        const match = currentFilename.match(/img\s*\((\d+)\)/i);
        const currentIndex = match ? match[1] : null;
        
        if (currentIndex !== originalIndex) {
            isSolved = false;
        }
    });

    if (isSolved) {
        console.log("🧩 PUZZLE UŁOŻONE POPRAWNIE!");
        isPuzzleSolved = true;
        nextPageButton.disabled = false;
        window.location.href = "/next";
        debugInfo.textContent = "Gratulacje! Puzzle ułożone poprawnie!";
        debugInfo.style.color = "green";
        
        // Automatycznie wyślij wynik
        sendPuzzleScore(calculateScore());
    } else {
        debugInfo.textContent = `Układanie w toku... (ruch ${move})`;
        debugInfo.style.color = "orange";
    }
}

function calculateScore() {
    const maxScore = 10;
    const penalty = Math.min(move, 15);
    return Math.max(maxScore - penalty, 1);
}

function sendPuzzleScore(points) {
    fetch('/save_score', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ score: points })
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`HTTP ${response.status}: ${text}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log("Odpowiedź serwera:", data);
        debugInfo.textContent += ` | Wynik zapisany: +${points}pkt!`;
    })
    .catch(error => {
        console.error("Błąd zapisu wyniku:", error);
        debugInfo.textContent = "Błąd zapisu: " + error.message;
        debugInfo.style.color = "red";
    });
}

document.addEventListener('DOMContentLoaded', createPuzzleImages);