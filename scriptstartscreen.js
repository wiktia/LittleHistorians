let selectedAvatar = null;
        let userName = '';
        let userPoints = 0;

        function selectAvatar(avatarElement) {
            // Usuń zaznaczenie z poprzedniego awatara
            const avatars = document.querySelectorAll('.avatar');
            avatars.forEach(avatar => avatar.classList.remove('selected'));

            // Zaznacz wybrany awatar
            avatarElement.classList.add('selected');
            selectedAvatar = avatarElement.src;
        }

        function start() {
            const nameInput = document.getElementById('nameInput');
            userName = nameInput.value.trim();

            if (!userName) {
                alert('Proszę wpisać swoje imię!');
                return;
            }

            if (!selectedAvatar) {
                alert('Proszę wybrać awatar!');
                return;
            }

            // Zapamiętaj dane użytkownika
            localStorage.setItem('userName', userName);
            localStorage.setItem('selectedAvatar', selectedAvatar);
            localStorage.setItem('userPoints', userPoints);

            alert(`Witaj, ${userName}! Twój awatar został zapisany.`);
        }

        function addPoints(points) {
            userPoints += points;
            localStorage.setItem('userPoints', userPoints);
            alert(`Dodano ${points} punktów! Obecna liczba punktów: ${userPoints}`);
        }

        // Funkcja do załadowania danych użytkownika po odświeżeniu strony
        function loadUserData() {
            const savedName = localStorage.getItem('userName');
            const savedAvatar = localStorage.getItem('selectedAvatar');
            const savedPoints = localStorage.getItem('userPoints');

            if (savedName && savedAvatar) {
                userName = savedName;
                selectedAvatar = savedAvatar;
                userPoints = parseInt(savedPoints) || 0;

                alert(`Witaj ponownie, ${userName}! Masz ${userPoints} punktów.`);
            }
        }

        window.onload = loadUserData;

        window.location.href = 'quiz.html';
 