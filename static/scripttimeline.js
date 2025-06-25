const cardsContainer = document.getElementById('cards');
const scoreDisplay = document.getElementById('scoreDisplay');
const slots = document.querySelectorAll('.slot');

let scoreAlreadySent = false;
// Lista ukończonych ośi czasu w tej rozgrywce
const completedTimelines = JSON.parse(sessionStorage.getItem('completedTimelines')) || [];

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

// Pobierz aktualny timeline_id z URL
function getCurrentTimelineId() {
  const params = new URLSearchParams(window.location.search);
  return params.get('timeline_id') || 'timeline-1';
}

// Sprawdź czy obecna oś czasu była już ukończona
function checkIfTimelineCompleted() {
  const timeline_id = getCurrentTimelineId();
  return completedTimelines.includes(timeline_id);
}

// Jeśli oś czasu była już ukończona, przekieruj na /next
if (checkIfTimelineCompleted()) {
  window.location.href = "/next";
}

// Inicjalizacja kart
document.querySelectorAll('.draggable').forEach((card, index) => {
  card.dataset.id = `card-${index}`;
  enableDrag(card);
});

// Obsługa przeciągania i upuszczania
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
    enableDrag(card);

    slot.style.height = slot.style.height;

    checkAllSlots();
  });
});

cardsContainer.addEventListener('dragover', e => e.preventDefault());
cardsContainer.addEventListener('drop', e => {
  e.preventDefault();
  const cardId = e.dataTransfer.getData('text/plain');
  const card = document.querySelector(`[data-id='${cardId}']`);
  if (!card) return;
  cardsContainer.appendChild(card);
  enableDrag(card);

  slots.forEach(slot => {
    const child = slot.querySelector(`[data-id='${cardId}']`);
    if (child) {
      slot.innerHTML = '?';
    }
  });

  checkAllSlots();
});

function checkAllSlots() {
  const allFilled = Array.from(slots).every(slot => slot.querySelector('.card'));

  if (!allFilled) {
    scoreDisplay.innerText = '';
    return;
  } else {
    slots.forEach(slot => {
      slot.style.backgroundColor = 'transparent';
    });
  }

  let score = 0;
  slots.forEach(slot => {
    const card = slot.querySelector('.card');
    const droppedDate = card.dataset.date;
    const correctDate = slot.dataset.correct;
    if (droppedDate === correctDate) {
      score++;
      card.style.backgroundColor = '#5CB85C';
    } else {
      card.style.backgroundColor = '#D9534F';
    }
  });

  scoreDisplay.innerText = `Zdobyto ${score} / ${slots.length} punktów`;

  // Zablokuj dalsze przeciąganie
  document.querySelectorAll('.card').forEach(card => {
    card.classList.add('disabled');
    card.setAttribute('draggable', false);
  });

  // Wyślij punkty do serwera, jeśli jeszcze nie wysłano
  if (!scoreAlreadySent) {
    const timeline_id = getCurrentTimelineId();
    
    // Dodaj obecną oś czasu do listy ukończonych
    if (!completedTimelines.includes(timeline_id)) {
      completedTimelines.push(timeline_id);
      sessionStorage.setItem('completedTimelines', JSON.stringify(completedTimelines));
    }
    
    sendMatchingScore(score);
    scoreAlreadySent = true;
  }
}

function sendMatchingScore(points) {
  const timeline_id = getCurrentTimelineId();
  
  fetch('/update_timeline_score', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ 
      score: points,
      timeline_id: timeline_id
    })
  })
  .then(res => res.json())
  .then(data => {
    console.log("Wynik zapisany:", data);
    // Zawsze przekierowujemy na /next po ukończeniu
    window.location.href = "/next";
  })
  .catch(error => {
    console.error("Błąd zapisu wyniku:", error);
  });
}


function getNextTimeline() {
  // Jeśli nie ma ukończonych timeline'ów, zaczynamy od pierwszego
  if (completedTimelines.length === 0) {
    return 'timeline-1';
  }
  
  // Znajdź najwyższy ukończony timeline
  const lastCompleted = completedTimelines.reduce((max, current) => {
    const currentNum = parseInt(current.split('-')[1]);
    const maxNum = parseInt(max.split('-')[1]);
    return currentNum > maxNum ? current : max;
  }, 'timeline-0');
  
  // Wygeneruj następny timeline (o 1 większy)
  const lastNumber = parseInt(lastCompleted.split('-')[1]);
  return `timeline-${lastNumber + 1}`;
}

