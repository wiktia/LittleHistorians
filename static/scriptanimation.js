// Losowe kolory dla Ellipse1
const colors = [
    'rgba(255, 99, 132, 0.7)',   // różowy
    'rgba(54, 162, 235, 0.7)',   // niebieski
    'rgba(255, 206, 86, 0.7)',   // żółty
    'rgba(75, 192, 192, 0.7)',   // turkusowy
    'rgba(153, 102, 255, 0.7)',  // fioletowy
    'rgba(255, 159, 64, 0.7)'    // pomarańczowy
];

// Losowe napisy motywacyjne
const messages = [
    "Świetnie Ci idzie!",
    "Brawo!",
    "Oby tak dalej!",
    "Tak trzymaj!",
    "Jest moc!",
    "Rewelacyjnie!",
    "Fantastycznie sobie radzisz!",
    "Cudownie!",
    "Super robota!",
    "Mega progres!"
];

window.onload = function () {
    const ellipse = document.querySelector('.Ellipse1');
    const messageElement = document.querySelector('.NastPnymRazemSiUda');
    const nextStepUrl = document.body.dataset.nextUrl;

    // Ustaw losowy kolor
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    if (ellipse) ellipse.style.background = randomColor;

    // Ustaw losowy tekst
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    if (messageElement) {
        messageElement.textContent = randomMessage;
        setTimeout(() => {
            messageElement.classList.add('fade-in');
        }, 50);
    }

    // Przekierowanie po 5.5 sekundy
    setTimeout(function () {
        if (nextStepUrl) {
            window.location.href = nextStepUrl;
        }
    }, 5500);
};
