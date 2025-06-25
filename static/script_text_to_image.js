let scoreSent = false; // tylko raz wysyłamy wynik

document.querySelectorAll('.draggable').forEach(label => {
  label.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('text/plain', label.dataset.id);
    setTimeout(() => label.classList.add('hide'), 0);
  });

  label.addEventListener('dragend', () => {
    label.classList.remove('hide');
  });
});

document.querySelectorAll('.dropzone').forEach(zone => {
  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('over');
  });

  zone.addEventListener('dragleave', () => {
    zone.classList.remove('over');
  });

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('over');

    if (zone.children.length > 0) return; // nie pozwól na nadpisanie

    const draggedId = e.dataTransfer.getData('text/plain');
    const label = document.querySelector(`.draggable[data-id='${draggedId}']`);

    zone.appendChild(label);

    // Automatyczne sprawdzenie po uzupełnieniu wszystkich
    const total = document.querySelectorAll('.dropzone').length;
    const filled = Array.from(document.querySelectorAll('.dropzone')).filter(z => z.children.length > 0).length;

    if (filled === total) checkAnswers();
  });
});

function checkAnswers() {
  let correct = 0;

  document.querySelectorAll('.dropzone').forEach(zone => {
    const expectedId = zone.dataset.id;
    const label = zone.querySelector('.draggable');

    if (label && label.dataset.id === expectedId) {
      correct++;
      label.style.background = '#5CB85C';
    } else if (label) {
      label.style.background = '#D9534F';
    }

    if (label) {
      label.setAttribute('draggable', false);
      label.classList.add('disabled');
    }
  });

  const scoreDisplay = document.getElementById('scoreDisplay');
  if (scoreDisplay) {
    scoreDisplay.textContent = `Poprawnych: ${correct}/3`;
  }

  console.log("Wynik:", correct, "poprawne odpowiedzi"); 
  sendLabelScore(correct); 
}

function sendLabelScore(points) {
  console.log("Próba wysłania wyniku:", points); 
  
  fetch('/save_score', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ score: points })
  })
  .then(response => {
    console.log("Odpowiedź serwera:", response.status); 
    if (!response.ok) {
      throw new Error('Błąd sieci');
    }
    return response.json();
  })
  .then(data => {
    console.log("Odpowiedź JSON:", data); 
    if (data.next_step_url) {
        window.location.href = data.next_step_url;
    }
})
  .catch(error => {
    console.error("Błąd:", error); 
    alert("Wystąpił błąd: " + error.message);
  });
}



const zegar = document.getElementById('zegar');
let rotation = 0;

setInterval(() => {
    rotation += 45;
    zegar.style.transform = `rotate(${rotation}deg)`;
}, 1000);

