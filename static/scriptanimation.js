    // Redirect after 5s
    setTimeout(function () {
        window.location.href = "{{ next_step_url }}";
    }, 5500);

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
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        ellipse.style.background = randomColor;

        const messageElement = document.querySelector('.NastPnymRazemSiUda');
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    
    messageElement.textContent = randomMessage;
    
    // Dodaj klasę z fade-in dopiero po ustawieniu treści
    setTimeout(() => {
        messageElement.classList.add('fade-in');
    }, 50); // małe opóźnienie, żeby przeglądarka 
    };