const cardsContainer = document.getElementById('cards');
const scoreDisplay = document.getElementById('scoreDisplay');
const slots = document.querySelectorAll('.slot');

let scoreAlreadySent = false;

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

document.querySelectorAll('.draggable').forEach((card, index) => {
  card.dataset.id = `card-${index}`;
  enableDrag(card);
});

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

  // 🔐 Zablokuj dalsze przeciąganie
  document.querySelectorAll('.card').forEach(card => {
    card.classList.add('disabled');
    card.setAttribute('draggable', false);
  });

  // 📡 Wyślij punkty do serwera, jeśli jeszcze nie wysłano
  if (!scoreAlreadySent) {
    sendMatchingScore(score);
    scoreAlreadySent = true;
  }
}

function sendMatchingScore(points) {
  fetch('/update_score', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ score: points })
  })
  .then(res => res.json())
  .then(data => {
    console.log("Wynik dopasowania zapisany:", data.new_score);
    window.location.href = "/next";
  })
  .catch(error => {
    console.error(" Błąd zapisu wyniku:", error);
  });
}

const zegar = document.getElementById('zegar');
let rotation = 0;

setInterval(() => {
    rotation += 45;
    zegar.style.transform = `rotate(${rotation}deg)`;
}, 1000);