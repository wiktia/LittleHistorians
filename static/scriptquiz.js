const quizId = 'quiz-1';
// Elementy DOM
const questionElement = document.querySelector('.question');
const answerButtons = document.querySelector('.answers-container');
const progressBar = document.querySelector('.progress-bar-fill');
const feedbackImage = document.getElementById('feedback-image') || { src: '' };
const playerAvatar = document.getElementById('player-avatar');
const playerNameElement = document.getElementById('player-name');
const playerScoreElement = document.getElementById('player-score');

let questions = [];
let currentQuestionIndex = 0;
let score = 0;
let quizEnded = false;

// Pobierz pytania z serwera
async function fetchQuestions() {
    try {
        const response = await fetch(`/api/quiz_questions?quiz=${encodeURIComponent(quizId)}`);
        const data = await response.json();
        
        questions = data.map(q => {
            const answers = q.answers.map((text, index) => ({
                text: text,
                correct: (index + 1) === q.correct
            }));
            return {
                question: q.question,
                answers: answers
            };
        });

        startQuiz();
    } catch (error) {
        console.error('Błąd pobierania pytań:', error);
        questionElement.innerHTML = "Błąd ładowania quizu. Spróbuj odświeżyć stronę.";
    }
}
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function startQuiz() {
    if (questions.length === 0) {
        questionElement.innerHTML = "Brak pytań w bazie danych.";
        return;
    }
    currentQuestionIndex = 0;
    score = 0;
    quizEnded = false;
    showQuestion();
}

function showQuestion() {
    resetState();

    const currentQuestion = questions[currentQuestionIndex];
    questionElement.textContent = currentQuestion.question;

    // Mieszamy odpowiedzi
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
    [...answerButtons.querySelectorAll('.answer-btn')].forEach(btn => btn.remove());
}

function selectAnswer(e) {
    const selectedBtn = e.target;
    const isCorrect = selectedBtn.dataset.correct === 'true';

    if (isCorrect) {
        selectedBtn.classList.add('correct');
        score = 1; 
    } else {
        selectedBtn.classList.add('incorrect');
        feedbackImage.src = userAvatar;  // pokaz avatar gracza, jeśli źle
    }

    // Podświetl prawidłową odpowiedź i zablokuj przyciski
    [...answerButtons.querySelectorAll('.answer-btn')].forEach(button => {
        if (button.dataset.correct === 'true') {
            button.classList.add('correct');
        }
        button.disabled = true;
    });

    // Wyślij wynik i zakończ quiz
    sendQuizScore(score);
}

function sendQuizScore(points) {
    fetch('/save_score', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ score: points })
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = "/next";  // przekieruj po zapisaniu
    })
    .catch(error => {
        console.error("Error saving score:", error);
        window.location.href = "/next";  // i tak przekieruj
    });
}

const userAvatar = playerAvatar ? playerAvatar.src : '';

// Start
fetchQuestions();
