const cardsContainer = document.getElementById('cards'); 
const checkBtn = document.getElementById('checkBtn');
const resetBtn = document.getElementById('resetBtn');
const scoreDisplay = document.getElementById('scoreDisplay');
const slots = document.querySelectorAll('.slot');

function enableDrag(card) {
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

// Aktywuj drag dla każdej karty
document.querySelectorAll('.draggable').forEach(card => {
  enableDrag(card);
});

// Obsługa przeciągania do slotów
slots.forEach(slot => {
  slot.addEventListener('dragover', e => e.preventDefault());

  slot.addEventListener('drop', e => {
    e.preventDefault();
    const cardId = e.dataTransfer.getData('text/plain');
    const card = document.querySelector(`[data-id='${cardId}']`);
    if (!card) return;

    // Przenieś poprzednią kartę z powrotem
    const existingCard = slot.querySelector('.card');
    if (existingCard) {
      cardsContainer.appendChild(existingCard);
      enableDrag(existingCard);
    }

    slot.appendChild(card);
    enableDrag(card);
  });
});

// Obsługa przeciągania z powrotem do kontenera kart
cardsContainer.addEventListener('dragover', e => e.preventDefault());
cardsContainer.addEventListener('drop', e => {
  e.preventDefault();
  const cardId = e.dataTransfer.getData('text/plain');
  const card = document.querySelector(`[data-id='${cardId}']`);
  if (!card) return;

  cardsContainer.appendChild(card);
  enableDrag(card);
});

// Sprawdzenie wyniku
checkBtn.addEventListener('click', () => {
  let score = 0;

  slots.forEach(slot => {
    const card = slot.querySelector('.card');
    if (!card) return;

    const droppedId = card.dataset.id;
    const correctId = slot.dataset.correct;

    if (droppedId === correctId) {
      score++;
    }
  });

  scoreDisplay.innerText = `Poprawne dopasowania: ${score} / ${slots.length}`;

  document.querySelectorAll('.card').forEach(card => {
    card.classList.add('disabled');
    card.setAttribute('draggable', false);
  });
});

// Reset gry
resetBtn.addEventListener('click', () => {
  scoreDisplay.innerText = '';

  slots.forEach(slot => {
    const card = slot.querySelector('.card');
    if (card) {
      cardsContainer.appendChild(card);
      enableDrag(card);
    }
  });

  document.querySelectorAll('.card').forEach(card => {
    enableDrag(card);
  });
});
