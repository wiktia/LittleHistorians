const cardsContainer = document.getElementById('cards');
const scoreDisplay = document.getElementById('scoreDisplay');
const slots = document.querySelectorAll('.slot');

let scoreAlreadySent = false;

// Funkcje zarządzania timeline'ami
const getCurrentTimelineId = () => {
  const params = new URLSearchParams(window.location.search);
  return params.get('timeline_id') || 'timeline-1';
};

const getLastCompletedTimeline = () => {
  return sessionStorage.getItem('lastCompletedTimeline');
};

const setLastCompletedTimeline = (id) => {
  sessionStorage.setItem('lastCompletedTimeline', id);
};

// Sprawdź czy obecny timeline został już ukończony
const checkIfTimelineCompleted = () => {
  const current = getCurrentTimelineId();
  const lastCompleted = getLastCompletedTimeline();
  
  if (!lastCompleted) return false;
  
  const currentNum = parseInt(current.split('-')[1]);
  const lastNum = parseInt(lastCompleted.split('-')[1]);
  
  return currentNum <= lastNum;
};

// Przekieruj jeśli timeline już ukończony
if (checkIfTimelineCompleted()) {
  window.location.href = "/next";
}

// Funkcje drag & drop
function enableDrag(card) {
  card.classList.add('draggable');
  card.setAttribute('draggable', true);
  card.classList.remove('disabled');

  card.addEventListener('dragstart', e => {
    e.dataTransfer.setData('text/plain', card.dataset.id);
    setTimeout(() => card.style.display = "none", 0);
  });

  card.addEventListener('dragend', () => {
    card.style.display = "block";
  });
}

// Inicjalizacja kart
document.querySelectorAll('.draggable').forEach((card, index) => {
  card.dataset.id = `card-${index}`;
  enableDrag(card);
});

// Obsługa slotów
slots.forEach(slot => {
  slot.addEventListener('dragover', e => e.preventDefault());
  
  slot.addEventListener('drop', e => {
    e.preventDefault();
    const cardId = e.dataTransfer.getData('text/plain');
    const card = document.querySelector(`[data-id='${cardId}']`);
    
    if (!card) return;

    if (slot.querySelector('.card')) {
      const existingCard = slot.querySelector('.card');
      cardsContainer.appendChild(existingCard);
      enableDrag(existingCard);
    }

    slot.innerHTML = '';
    slot.appendChild(card);
    checkAllSlots();
  });
});

// Obsługa powrotu kart do kontenera
cardsContainer.addEventListener('dragover', e => e.preventDefault());
cardsContainer.addEventListener('drop', e => {
  e.preventDefault();
  const cardId = e.dataTransfer.getData('text/plain');
  const card = document.querySelector(`[data-id='${cardId}']`);
  
  if (!card) return;
  
  cardsContainer.appendChild(card);
  slots.forEach(slot => {
    if (slot.querySelector(`[data-id='${cardId}']`)) {
      slot.innerHTML = '?';
    }
  });
  
  checkAllSlots();
});

// Sprawdź ukończenie timeline'a
function checkAllSlots() {
  const allFilled = Array.from(slots).every(slot => slot.querySelector('.card'));
  
  if (!allFilled) {
    scoreDisplay.innerText = '';
    return;
  }

  // Oblicz wynik
  let score = 0;
  slots.forEach(slot => {
    const card = slot.querySelector('.card');
    const isCorrect = card.dataset.date === slot.dataset.correct;
    
    if (isCorrect) {
      score++;
      card.style.backgroundColor = '#5CB85C';
    } else {
      card.style.backgroundColor = '#D9534F';
    }
  });

  scoreDisplay.innerText = `Zdobyto ${score} / ${slots.length} punktów`;

  // Zablokuj edycję
  document.querySelectorAll('.card').forEach(card => {
    card.classList.add('disabled');
    card.setAttribute('draggable', false);
  });

  // Zapisz wynik tylko raz
  if (!scoreAlreadySent) {
    saveAndProceed(score);
    scoreAlreadySent = true;
  }
}

// Zapisz wynik i przejdź dalej
function saveAndProceed(score) {
  const timelineId = getCurrentTimelineId();
  
  // Zapisz w sessionStorage
  setLastCompletedTimeline(timelineId);
  
  // Wyślij wynik na serwer
  fetch('/update_timeline_score', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ 
      score: score,
      timeline_id: timelineId
    })
  })
  .then(() => {
    // Przekieruj na /next po zapisaniu
    window.location.href = "/next";
  })
  .catch(error => {
    console.error("Błąd zapisu wyniku:", error);
  });
}