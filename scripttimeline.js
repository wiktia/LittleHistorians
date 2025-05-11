const cardsContainer = document.getElementById('cards');
const checkBtn = document.getElementById('checkBtn');
const resetBtn = document.getElementById('resetBtn');
const scoreDisplay = document.getElementById('scoreDisplay');
const slots = document.querySelectorAll('.slot');

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

// Nadanie unikalnych ID kartom
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
    enableDrag(card);
  });
});

// Powrót na dół
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
});

// Zatwierdzenie
checkBtn.addEventListener('click', () => {
  let score = 0;

  slots.forEach(slot => {
    const card = slot.querySelector('.card');
    if (!card) return;
    const droppedDate = card.dataset.date;
    const correctDate = slot.dataset.correct;

    if (droppedDate === correctDate) {
      score += 1;
    }
  });

  scoreDisplay.innerText = `Zdobyto ${score} / ${slots.length} punktów`;

  document.querySelectorAll('.card').forEach(card => {
    card.classList.add('disabled');
    card.setAttribute('draggable', false);
  });
});

// Reset
resetBtn.addEventListener('click', () => {
  scoreDisplay.innerText = '';

  slots.forEach(slot => {
    const card = slot.querySelector('.card');
    if (card) {
      cardsContainer.appendChild(card);
      enableDrag(card);
    }
    slot.innerHTML = '?';
  });

  document.querySelectorAll('.card').forEach(card => {
    enableDrag(card);
  });
});
