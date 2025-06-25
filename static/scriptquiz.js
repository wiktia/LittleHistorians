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

async function fetchSingleQuestion() {
    try {
        // Pobierz wszystkie dostępne pytania
        const response = await fetch('/api/quiz_questions');
        const allQuestions = await response.json();

        // Filtruj pytania, które jeszcze nie były używane w tej rozgrywce
        const availableQuestions = allQuestions.filter(q => !usedQuestions.includes(q.id));

        if (availableQuestions.length === 0) {
            // Brak nowych pytań - koniec quizu
            questionElement.textContent = "To już koniec quizu!";
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
}

function showQuestion() {
    resetState();
    questionElement.textContent = currentQuestion.question;

    const answers = [...currentQuestion.answers];
    shuffleArray(answers);

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
    answerButtons.innerHTML = '';
}

function selectAnswer(e) {
    const selectedBtn = e.target;
    const isCorrect = selectedBtn.dataset.correct === 'true';

    if (isCorrect) {
        selectedBtn.classList.add('correct');
        score = 1;
    } else {
        selectedBtn.classList.add('incorrect');
        feedbackImage.src = userAvatar;
        score = 0;
    }

    // Podświetl poprawną odpowiedź
    [...answerButtons.querySelectorAll('.answer-btn')].forEach(button => {
        if (button.dataset.correct === 'true') {
            button.classList.add('correct');
        }
        button.disabled = true;
    });

    // Dodaj bieżące pytanie do listy użytych
    usedQuestions.push(currentQuestionId);
    sessionStorage.setItem('usedQuizQuestions', JSON.stringify(usedQuestions));
    
    // Po chwili przechodzimy dalej
    setTimeout(() => {
        sendQuizScore(score);
    }, 1000);
}

function sendQuizScore(points) {
    fetch('/save_score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ score: points })
    })
        .then(response => response.json())
        .then(data => {
            window.location.href = "/next";  // przekieruj dalej
        })
        .catch(error => {
            console.error("Błąd zapisu wyniku:", error);
            window.location.href = "/next";  // i tak przekieruj
        });
}

// Start quizu
fetchSingleQuestion();