document.addEventListener('DOMContentLoaded', function() {
    const cardsContainer = document.getElementById('cards');
    const scoreDisplay = document.getElementById('scoreDisplay');
    const slots = document.querySelectorAll('.slot');
    const timelineId = document.body.getAttribute('data-timeline-id');
    let scoreAlreadySent = false;

    // Initialize draggable cards
    function initializeCards() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('dragstart', dragStart);
            card.addEventListener('dragend', dragEnd);
        });

        // Initialize slots
        slots.forEach(slot => {
            slot.addEventListener('dragover', dragOver);
            slot.addEventListener('drop', drop);
            slot.addEventListener('dragleave', dragLeave);
            slot.addEventListener('dragenter', dragEnter);
        });

        // Allow dropping back to cards container
        cardsContainer.addEventListener('dragover', dragOver);
        cardsContainer.addEventListener('drop', dropToContainer);
    }

    // Drag and drop functions
    function dragStart(e) {
        e.dataTransfer.setData('text/plain', this.dataset.id);
        setTimeout(() => this.classList.add('dragging'), 0);
    }

    function dragEnd() {
        this.classList.remove('dragging');
    }

    function dragOver(e) {
        e.preventDefault();
    }

    function dragEnter(e) {
        e.preventDefault();
        this.classList.add('hovered');
    }

    function dragLeave() {
        this.classList.remove('hovered');
    }

    function drop(e) {
        e.preventDefault();
        this.classList.remove('hovered');
        
        const cardId = e.dataTransfer.getData('text/plain');
        const card = document.querySelector(`[data-id="${cardId}"]`);
        
        if (!card) return;

        // If slot already has a card, return it to container
        if (this.querySelector('.card')) {
            const existingCard = this.querySelector('.card');
            cardsContainer.appendChild(existingCard);
        }

        // Add the new card to the slot
        this.innerHTML = '';
        this.appendChild(card);
        
        checkAllSlots();
    }

    function dropToContainer(e) {
        e.preventDefault();
        const cardId = e.dataTransfer.getData('text/plain');
        const card = document.querySelector(`[data-id="${cardId}"]`);
        
        if (!card) return;
        
        cardsContainer.appendChild(card);
        
        // Clear the slot if this card was in one
        slots.forEach(slot => {
            if (slot.contains(card)) {
                slot.innerHTML = '?';
            }
        });
        
        checkAllSlots();
    }

    // Check if all slots are filled and calculate score
    function checkAllSlots() {
        const allFilled = Array.from(slots).every(slot => slot.querySelector('.card'));
        
        if (!allFilled) {
            scoreDisplay.textContent = '';
            return;
        }

        // Calculate score
        let score = 0;
        slots.forEach(slot => {
            const card = slot.querySelector('.card');
            if (card.dataset.date === slot.dataset.correct) {
                score++;
                slot.style.backgroundColor = 'rgba(76, 175, 80, 0.3)';
            } else {
                slot.style.backgroundColor = 'rgba(244, 67, 54, 0.3)';
            }
        });

        scoreDisplay.textContent = `Zdobyto ${score} / ${slots.length} punktów`;

        // Disable further dragging
        document.querySelectorAll('.card').forEach(card => {
            card.removeEventListener('dragstart', dragStart);
            card.removeEventListener('dragend', dragEnd);
            card.draggable = false;
        });

        // Save score and proceed (only once)
        if (!scoreAlreadySent) {
            saveAndProceed(score);
            scoreAlreadySent = true;
        }
    }

    // Send score to server and proceed to next step
    function saveAndProceed(score) {
        fetch('/save_score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                score: score,
                timeline_id: timelineId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.next_step_url) {
                setTimeout(() => {
                    window.location.href = data.next_step_url;
                }, 2000); // 2 second delay before redirect
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    initializeCards();
});