const cardsContainer = document.getElementById('cards');
const scoreDisplay = document.getElementById('scoreDisplay');
const slots = document.querySelectorAll('.slot');

let scoreAlreadySent = false;

// Pobierz ID aktualnej osi czasu
const getCurrentTimelineId = () => {
  return document.body.dataset.timelineId || 'timeline-1';
};

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

  // Oblicz wynik - PORÓWNUJEMY LICZBY (ROK)
  let score = 0;
  slots.forEach(slot => {
    const card = slot.querySelector('.card');

    const isCorrect = parseInt(card.dataset.year) === parseInt(slot.dataset.correct);
    
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

// Zapisz wynik i przejdź dalej - UPROSZCZONE
function saveAndProceed(score) {
  const timelineId = getCurrentTimelineId();
  
  // Wyślij wynik na serwer
  fetch('/update_timeline_score', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ 
      score: score,
      timeline_id: timelineId
    })
  })
  .then(response => {
    if (response.ok) {
      // Przekieruj na /next po zapisaniu
      window.location.href = "/next";
    } else {
      console.error("Błąd zapisu wyniku:", response.statusText);
      scoreAlreadySent = false; // Zezwól na ponowną próbę
    }
  })
  .catch(error => {
    console.error("Błąd sieci:", error);
    scoreAlreadySent = false; // Zezwól na ponowną próbę
  });
}


    // Inicjalizacja zegara
    const zegar = document.getElementById('zegar');
    if (zegar) {
        let rotation = 0;
        setInterval(() => {
            rotation += 45;
            zegar.style.transform = `rotate(${rotation}deg)`;
        }, 1000);
    }
