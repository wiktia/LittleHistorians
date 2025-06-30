const quizId = 'quiz-1';
// Elementy DOM
const questionElement = document.querySelector('.question');
const answerButtons = document.querySelector('.answers-container');
const progressBar = document.querySelector('.progress-bar-fill');
const feedbackImage = document.getElementById('feedback-image') || { src: '' };
const playerAvatar = document.getElementById('player-avatar');
const playerNameElement = document.getElementById('player-name');
const playerScoreElement = document.getElementById('player-score');

let currentQuestion = null;
let score = 0;
// Lista pytań już wyświetlonych w tej rozgrywce
let usedQuestions = JSON.parse(sessionStorage.getItem('usedQuizQuestions')) || [];
// Aktualne pytanie
let currentQuestionId = null;
const userAvatar = playerAvatar ? playerAvatar.src : '';

// Style dla odpowiedzi (dodawane dynamicznie)
const style = document.createElement('style');
style.textContent = `
    .answer-btn.correct {
        background-color: #4CAF50;
        color: white;
        border: 2px solid #45a049;
    }
    .answer-btn.incorrect {
        background-color: #f44336;
        color: white;
        border: 2px solid #d32f2f;
    }
    .answer-btn[disabled] {
        opacity: 0.7;
        cursor: not-allowed;
    }
`;
document.head.appendChild(style);

async function fetchSingleQuestion() {
    try {
        // Pobierz wszystkie dostępne pytania
        const response = await fetch('/api/quiz_questions');
        const allQuestions = await response.json();

        // Filtruj pytania, które jeszcze nie były używane w tej rozgrywce
        const availableQuestions = allQuestions.filter(q => !usedQuestions.includes(q.id));

        if (availableQuestions.length === 0) {
            // Brak nowych pytań - koniec quizu
            questionElement.textContent = "--";
            answerButtons.innerHTML = '';
            progressBar.style.width = '100%';
            
            // Wyczyść listę użytych pytań dla nowej rozgrywki
            sessionStorage.removeItem('usedQuizQuestions');
            return;
        }

        // Wybierz losowe pytanie z dostępnych
        const randomIndex = Math.floor(Math.random() * availableQuestions.length);
        const q = availableQuestions[randomIndex];
        currentQuestionId = q.id;

        currentQuestion = {
            question: q.question,
            answers: q.answers.map((text, index) => ({
                text: text,
                correct: (index + 1) === q.correct
            }))
        };

        showQuestion();
    } catch (error) {
        console.error('Błąd pobierania pytań:', error);
        questionElement.textContent = "Błąd ładowania pytań. Spróbuj odświeżyć stronę.";
    }
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function showQuestion() {
    resetState();
    questionElement.textContent = currentQuestion.question;

    const answers = shuffleArray([...currentQuestion.answers]);

    answers.forEach(answer => {
        const button = document.createElement('button');
        button.innerText = answer.text;
        button.classList.add('answer-btn');
        if (answer.correct) {
            button.dataset.correct = 'true';
        }
        button.addEventListener('click', selectAnswer);
        answerButtons.appendChild(button);
    });

    progressBar.style.width = '100%';
}

function resetState() {
    // Czyścimy kontener z odpowiedziami
    while (answerButtons.firstChild) {
        answerButtons.removeChild(answerButtons.firstChild);
    }
}

function selectAnswer(e) {
    const selectedBtn = e.target;
    const isCorrect = selectedBtn.dataset.correct === 'true';

    // Podświetlamy wybraną odpowiedź
    if (isCorrect) {
        selectedBtn.classList.add('correct');
        score = 1;
    } else {
        selectedBtn.classList.add('incorrect');
        if (feedbackImage) feedbackImage.src = userAvatar;
        score = 0;
    }

    // Podświetlamy poprawną odpowiedź (nawet jeśli wybrano złą)
    document.querySelectorAll('.answer-btn').forEach(button => {
        if (button.dataset.correct === 'true') {
            button.classList.add('correct');
        }
        button.disabled = true;
    });

    // Dodajemy bieżące pytanie do listy użytych
    usedQuestions.push(currentQuestionId);
    sessionStorage.setItem('usedQuizQuestions', JSON.stringify(usedQuestions));
    
    // Po chwili przechodzimy dalej
    setTimeout(() => {
        sendQuizScore(score);
    }, 1500); // Zwiększony czas na pokazanie podświetlenia
}

function sendQuizScore(points) {
    fetch('/save_score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ score: points })
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = "/next";
    })
    .catch(error => {
        console.error("Błąd zapisu wyniku:", error);
        window.location.href = "/next";
    });
}

// Animacja zegara
const zegar = document.getElementById('zegar');
let rotation = 0;

setInterval(() => {
    rotation = (rotation + 45) % 360;  // Obrót o 45 stopni, modulo 360 dla zapętlenia
    zegar.style.transition = 'none';   // Wyłącz animację płynną (od razu zmiana)
    zegar.style.transform = `rotate(${rotation}deg)`;
}, 1000);


// Start quizu
fetchSingleQuestion();