        // Parametry konfetti
        const confettiColors = ['yellow', 'red', 'blue', 'green', 'pink', 'purple', 'orange'];
        const confettiCount = 60; // więcej konfetti
        const confettiContainer = document.getElementById('confetti');

        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.classList.add('confetti-piece');
            confetti.classList.add(confettiColors[Math.floor(Math.random() * confettiColors.length)]);
            // Losowa pozycja startowa
            confetti.style.left = (Math.random() * 98) + '%';
            confetti.style.top = '-40px'; // zawsze startuje tuż nad ekranem
            // Losowy czas trwania animacji
            const duration = 2.5 + Math.random() * 2.5; // 2.5s - 5s
            confetti.style.animationDuration = duration + 's';
            confetti.style.animationDelay = (Math.random() * 2) + 's';
            // Losowy obrót na starcie i końcu
            const rotateStart = Math.floor(Math.random() * 360);
            const rotateEnd = rotateStart + 180 + Math.floor(Math.random() * 180);
            confetti.style.setProperty('--rotate', rotateStart + 'deg');
            confetti.style.setProperty('--rotate-end', rotateEnd + 'deg');
            // Losowa szerokość i wysokość
            confetti.style.width = (8 + Math.random() * 8) + 'px';
            confetti.style.height = (18 + Math.random() * 18) + 'px';
            confettiContainer.appendChild(confetti);
        }