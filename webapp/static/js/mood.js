document.addEventListener('DOMContentLoaded', () => {
    const today = new Date();
    currentYear = today.getFullYear();
    currentMonth = today.getMonth();
    createCalendar(currentYear, currentMonth);
    loadMoods();
});

const calendarContainer = document.getElementById('calendar');
const selectedDateInput = document.getElementById('selected-date');
const monthLabel = document.getElementById('month-label');
const moodSelect = document.getElementById('mood');
let currentYear, currentMonth;

function createCalendar(year, month) {
    calendarContainer.innerHTML = '';
    const date = new Date(year, month);
    monthLabel.textContent = date.toLocaleString('default', { month: 'long', year: 'numeric' });
    
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    // Fill initial empty cells for the starting day of the month
    for (let i = 0; i < firstDay; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'day empty';
        calendarContainer.appendChild(emptyCell);
    }
    
    // Fill days of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'day';
        dayElement.textContent = day;
        const dateKey = new Date(year, month, day).toISOString().slice(0, 10);
        dayElement.setAttribute('data-date', dateKey);
        dayElement.addEventListener('click', () => selectDate(dateKey, dayElement));
        calendarContainer.appendChild(dayElement);
    }
}

function changeMonth(delta) {
    currentMonth += delta;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    } else if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    createCalendar(currentYear, currentMonth);
    loadMoods();
}

function selectDate(dateKey, dayElement) {
    document.querySelectorAll('.day').forEach(day => day.classList.remove('selected'));
    dayElement.classList.add('selected');
    selectedDateInput.value = dateKey;
}

function saveMood() {
    const dateKey = selectedDateInput.value;
    const selectedMood = moodSelect.value;

    if (!dateKey || !selectedMood) {
        alert("Please select a date and a mood.");
        return;
    }

    fetch("{% url 'save_mood' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ date: dateKey, mood: selectedMood })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayMood(dateKey, selectedMood);
            } else {
                alert('Failed to save mood');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function loadMoods() {
    fetch('{% url "get_moods" %}')
        .then(response => response.json())
        .then(data => {
            for (const [date, mood] of Object.entries(data)) {
                displayMood(date, mood);
            }
        });
}

function displayMood(dateKey, mood) {
    const dayElement = document.querySelector(`.day[data-date="${dateKey}"]`);
    if (dayElement) {
        let moodEmoji;
        switch (mood) {
            case 'happy': moodEmoji = '😊'; break;
            case 'neutral': moodEmoji = '😐'; break;
            case 'sad': moodEmoji = '😞'; break;
            case 'excited': moodEmoji = '😄'; break;
            case 'anxious': moodEmoji = '😟'; break;
            default: moodEmoji = '';
        }

        const existingMood = dayElement.querySelector('.mood');
        if (existingMood) existingMood.remove();

        const moodSpan = document.createElement('span');
        moodSpan.className = 'mood';
        moodSpan.textContent = moodEmoji;
        dayElement.appendChild(moodSpan);
    }
}