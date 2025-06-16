let firstSelected = null;
let move = 0;

const totalPieces = 9;
const puzzleFolder = "/static/puzzle-img";
const puzzleBoard = document.getElementById("puzzleBoard");
const counterElement = document.getElementById("counter");
const nextPageButton = document.getElementById("nextPageButton");

let originalPuzzleOrder = [];
let scoreSent = false;  // 🔒 Czy punkty już zostały zapisane?

function createPuzzleImages() {
    puzzleBoard.innerHTML = '';
    originalPuzzleOrder = [];

    for (let i = 1; i <= totalPieces; i++) {
        const img = document.createElement("img");
        img.src = `${puzzleFolder}/img (${i}).jpg`;
        img.classList.add("puzzle-img");
        img.dataset.originalIndex = i.toString();
        puzzleBoard.appendChild(img);
        originalPuzzleOrder.push(img);
    }

    addPuzzleClickListeners();
    shufflePuzzle();
    nextPageButton.disabled = true;
}

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

function movePuzzle(img1, img2) {
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

    nextPageButton.disabled = true;
    scoreSent = false;
}

function checkWinCondition() {
    const currentPuzzleImgs = Array.from(document.querySelectorAll('.puzzle-img'));
    let isSolved = true;

    currentPuzzleImgs.forEach((img, index) => {
        const expectedSrcPart = `img (${index + 1}).jpg`;
        if (!img.src.includes(expectedSrcPart)) {
            isSolved = false;
        }
    });

    if (isSolved) {
        console.log("🧩 PUZZLE UŁOŻONE!");
        nextPageButton.disabled = false;

        if (!scoreSent) {
            sendPuzzleScore(5);  // 🏆 np. 5 punktów za ułożenie
            scoreSent = true;
            
        }
    } else {
        nextPageButton.disabled = true;
    }
}

function sendPuzzleScore(points) {
    fetch('/update_score', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ score: points })
    })
    .then(res => res.json())
    .then(data => {
        console.log(" Wynik zapisany:", data.new_score);
        window.location.href = "/next";
    })
    .catch(error => {
        console.error(" Błąd zapisu wyniku:", error);
    });
}


nextPageButton.addEventListener('click', () => {
    if (!scoreSent) {
        sendPuzzleScore(5);
        scoreSent = true;
    } else {
        window.location.href = "/next";
    }
});

document.addEventListener('DOMContentLoaded', createPuzzleImages);
