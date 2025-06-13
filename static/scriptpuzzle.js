let firstSelected = null;
let move = 0;

const totalPieces = 9;
const puzzleFolder = "/static/puzzle-img"; // Poprawiona ścieżka do folderu w Flask
const puzzleBoard = document.getElementById("puzzleBoard");
const counterElement = document.getElementById("counter");
const nextPageButton = document.getElementById("nextPageButton");

let originalPuzzleOrder = [];

function createPuzzleImages() {
    puzzleBoard.innerHTML = '';
    originalPuzzleOrder = [];

    for (let i = 1; i <= totalPieces; i++) {
        const img = document.createElement("img");
        img.src = `${puzzleFolder}/img (${i}).jpg`;  // Poprawiona ścieżka
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
        console.log("PUZZLE UŁOŻONE!");
        nextPageButton.disabled = false;
    } else {
        nextPageButton.disabled = true;
    }
}

nextPageButton.addEventListener("click", () => {
    if (nextPageButton.disabled) {
        alert("Musisz najpierw ułożyć puzzle!");
        return;
    }
    window.location.href = "/nastepna_strona";  
});

document.addEventListener('DOMContentLoaded', createPuzzleImages);