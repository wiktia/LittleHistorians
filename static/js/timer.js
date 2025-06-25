document.addEventListener('DOMContentLoaded', function() {
    function updateTimer() {
        fetch('/api/get_start_time')
            .then(response => response.json())
            .then(data => {
                if (data.start_time) {
                    const startTime = new Date(data.start_time);
                    const now = new Date();
                    const diff = Math.floor((now - startTime) / 1000); // różnica w sekundach
                    
                    const minutes = Math.floor(diff / 60);
                    const seconds = diff % 60;
                    
                    // Formatowanie czasu jako MM:SS
                    const formattedTime = 
                        (minutes < 10 ? '0' + minutes : minutes) + ':' + 
                        (seconds < 10 ? '0' + seconds : seconds);
                    
                    // Aktualizuj wszystkie elementy z klasą 'czas'
                    document.querySelectorAll('.czas').forEach(el => {
                        el.textContent = formattedTime;
                    });
                }
            })
            .catch(error => console.error('Błąd:', error));
    }
    
    // Aktualizuj timer co sekundę
    updateTimer();
    setInterval(updateTimer, 1000);
});

