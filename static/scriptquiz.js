// Elementy DOM
const questionElement = document.querySelector('.question');
const answerButtons = document.querySelector('.answers-container');
const nextButton = document.createElement('button');
nextButton.className = 'answer-btn';
nextButton.style.marginTop = '20px';
nextButton.textContent = 'Dalej';
nextButton.style.display = 'none';
answerButtons.parentElement.appendChild(nextButton);

const progressBar = document.querySelector('.progress-bar-fill');
const feedbackImage = document.getElementById('feedback-image') || { src: '' };
const playerAvatar = document.getElementById('player-avatar');
const playerNameElement = document.getElementById('player-name');
const playerScoreElement = document.getElementById('player-score');

// Zmienne quizu
let questions = [];  // Będziemy ładować pytania z serwera
let currentQuestionIndex = 0;
let score = 0;
let quizEnded = false;

// Pobierz pytania z serwera
async function fetchQuestions() {
    try {
        const response = await fetch('/api/quiz_questions');
        const data = await response.json();
        
        // Przekształć dane z API do formatu oczekiwanego przez quiz
        questions = data.slice(0, 1).map(q => {
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
    nextButton.innerHTML = 'Dalej';
    nextButton.style.display = 'none';
    
    // Pomieszaj kolejność pytań
    shuffleArray(questions);
    
    showQuestion();
}

function showQuestion() {
    resetState();

    const currentQuestion = questions[currentQuestionIndex];
    questionElement.innerHTML = `${currentQuestionIndex + 1}. ${currentQuestion.question}`;

    // Pomieszaj odpowiedzi
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

    // Aktualizuj pasek postępu
    const progressPercent = ((currentQuestionIndex + 1) / questions.length) * 100;
    progressBar.style.width = progressPercent + '%';
}

function resetState() {
    nextButton.style.display = 'none';
    [...answerButtons.querySelectorAll('.answer-btn')].forEach(btn => btn.remove());
}

function selectAnswer(e) {
    const selectedBtn = e.target;
    const isCorrect = selectedBtn.dataset.correct === 'true';

    // Podświetl wybraną odpowiedź
    if (isCorrect) {
        selectedBtn.style.backgroundColor = '#cde667'; // zielony dla poprawnej
        selectedBtn.style.color = 'white';
    } else {
        selectedBtn.style.backgroundColor = '#da4252'; // czerwony dla błędnej
        selectedBtn.style.color = 'white';
    }

    // Podświetl poprawną odpowiedź (jeśli wybrano błędną)
    if (!isCorrect) {
        [...answerButtons.querySelectorAll('.answer-btn')].forEach(button => {
            if (button.dataset.correct === 'true') {
                button.style.backgroundColor = '#cde667'; // zielony
                button.style.color = 'white';
            }
        });
    }

    // Zablokuj wszystkie przyciski po wyborze
    [...answerButtons.querySelectorAll('.answer-btn')].forEach(button => {
        button.disabled = true;
    });

    if (isCorrect) {
        score++;
    }

    // Pokaż przycisk "Dalej" i przejdź do następnego pytania po chwili


    // Automatyczne przejście po 1.5 sekundy
    setTimeout(() => {
        handleNextButton();
    }, 1500);
}

function handleNextButton() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        showQuestion();
    } else {
        showScore();
    }
}

function showScore() {
    sendQuizScore(score);
}

function sendQuizScore(points) {
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
        setTimeout(() => {
            window.location.href = "/next";  
        }, 1500);
    })
    .catch(error => {
        console.error("Błąd zapisu wyniku:", error);
    });
}

const zegar = document.getElementById('zegar');
let rotation = 0;

setInterval(() => {
    rotation += 45;
    zegar.style.transform = `rotate(${rotation}deg)`;
}, 1000);

// Rozpocznij proces pobierania pytań i uruchomienia quizu
fetchQuestions();