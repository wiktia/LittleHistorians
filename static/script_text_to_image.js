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
  });

  document.getElementById('scoreDisplay').textContent = `Poprawnych: ${correct}/3`;
}

document.getElementById('resetBtn').addEventListener('click', () => {
  const labelsContainer = document.querySelector('.labels');
  const labels = document.querySelectorAll('.draggable');
  const dropzones = document.querySelectorAll('.dropzone');

  labels.forEach(label => {
    labelsContainer.appendChild(label);
    label.style.background = '#FDF7E3';
  });

  dropzones.forEach(zone => {
    zone.innerHTML = '';
    zone.style.borderColor = '#FDF7E3';
  });

  document.getElementById('scoreDisplay').textContent = '';
});
