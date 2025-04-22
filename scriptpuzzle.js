let firstSelected = null;
let move = 0;

const totalPieces = 9; 
const puzzleFolder = "puzzle-img"; 
const puzzleBoard = document.getElementById("puzzleBoard");

function createPuzzleImages() {
    for (let i = 1; i <= totalPieces; i++) {
        const img = document.createElement("img");
        img.src = `${puzzleFolder}/img (${i}).jpg`;
        img.classList.add("puzzle-img");
        img.draggable = true;
        puzzleBoard.appendChild(img);
    }
    startPuzzle();
}
function startPuzzle() {
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

    move ++;
    document.getElementById("counter").innerText = "Ruchy = " +  move;
}

document.getElementById("shuffle").addEventListener("click", shufflePuzzle);

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
    document.getElementById("counter").innerText = "Ruchy = 0";
}
createPuzzleImages();

