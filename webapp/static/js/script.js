function myFunction() {
    window.location.href = "http://127.0.0.1:8000/assessment";
}



// navbar
let list = document.querySelectorAll(".navigation li");

function activeLink() {
    list.forEach((item) => {
        item.classList.remove("hovered");
    });
    this.classList.add("hovered");
}

list.forEach((item) => item.addEventListener("mouseover", activeLink));

// Menu Toggle
let toggle = document.querySelector(".toggle");
let navigation = document.querySelector(".navigation");
let main = document.querySelector(".main");

toggle.onclick = function () {
    navigation.classList.toggle("active");
    main.classList.toggle("active");
};

//exercise popup
function timetogglePopup() {
    document.getElementById("time-popup1").classList.toggle("active");
}
//mind popup
function mindtogglePopup() {
    document.getElementById("mind-popup1").classList.toggle("active");
}

//distract popup
function distracttogglePopup() {
    document.getElementById("distract-popup1").classList.toggle("active");
}
//ground popup
function groundtogglePopup() {
    document.getElementById("ground-popup1").classList.toggle("active");
}

function aromatogglePopup() {
    document.getElementById("aroma-popup1").classList.toggle("active");
}

function cbttogglePopup() {
    document.getElementById("cbt-popup1").classList.toggle("active");
}


function defusiontogglePopup() {
    document.getElementById("defusion-popup1").classList.toggle("active");
}

function religiontogglePopup() {
    document.getElementById("religion-popup1").classList.toggle("active");
}


// comments

document.addEventListener('DOMContentLoaded', function () {
    const commentToggles = document.querySelectorAll('.toggle-comments');

    commentToggles.forEach(button => {
        button.addEventListener('click', function () {
            const postId = this.dataset.postId;
            const commentsSection = document.getElementById('comments-' + postId);
            if (commentsSection.style.display === 'none' || commentsSection.style.display === '') {
                commentsSection.style.display = 'block';
                this.textContent = 'Hide Comments';
            } else {
                commentsSection.style.display = 'none';
                this.textContent = 'Comments';
            }
        });
    });
});

// sort table

function sortTable(columnIndex) {
    const table = document.getElementById("profiletable");
    const rows = Array.from(table.rows).slice(1); // Get all rows except the header
    const isAscending = table.getAttribute('data-sort-order') === 'asc'; // Determine the sort order

    // Sort the rows based on the column index
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].innerText.toLowerCase();
        const bText = b.cells[columnIndex].innerText.toLowerCase();
        return (aText < bText ? -1 : aText > bText ? 1 : 0) * (isAscending ? 1 : -1);
    });

    // Remove existing rows
    for (let i = 1; i < table.rows.length; i++) {
        table.deleteRow(1);
    }

    // Append sorted rows back to the table
    rows.forEach(row => table.appendChild(row));

    // Update sort order for the next click
    table.setAttribute('data-sort-order', isAscending ? 'desc' : 'asc');
}

//comment

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.upvote-button').forEach(button => {
        button.addEventListener('click', function () {
            const commentId = this.getAttribute('data-id');
            fetch(`/comment/upvote/${commentId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    this.textContent = `⬆️ Upvote (${data.upvotes})`;
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        });
    });

    document.querySelectorAll('.downvote-button').forEach(button => {
        button.addEventListener('click', function () {
            const commentId = this.getAttribute('data-id');
            fetch(`/comment/downvote/${commentId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    this.textContent = `⬇️ Downvote (${data.downvotes})`;
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        });
    });
});



// search form
function filterSearch() {
    const searchInput = document.getElementById('search').value.toLowerCase();
    const tableRows = document.querySelectorAll('#profiletable tbody tr');

    tableRows.forEach(row => {
        const rowData = row.textContent.toLowerCase();
        if (rowData.includes(searchInput)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function filterSearch() {
    const searchInput = document.getElementById('search').value.toLowerCase();
    const tableRows = document.querySelectorAll('#psychologist-table tbody tr'); // Updated the selector

    tableRows.forEach(row => {
        const rowData = row.textContent.toLowerCase();
        if (rowData.includes(searchInput)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}


// delete 

function confirmDelete() {
    return confirm("Are you sure you want to delete this journal entry?");
}

function confirmPost() {
    return confirm("Are you sure you want to post this update?");
}

function deletePost() {
    return confirm("Are you sure you want to delete this post?");
}
function confirmLogout() {
    return confirm("Are you sure you want to log out?");
}



// gad7


    function calculateScore() {
        let totalScore = 0;
        
        // Get all the select elements with class 'gad7-question'
        const questions = document.querySelectorAll('.gad7-question');
        
        // Loop through each question and sum the selected values
        questions.forEach(question => {
            totalScore += parseInt(question.value);
        });

        // Update the total score in the DOM
        document.getElementById('total-score').textContent = totalScore;

        // Display the interpretation based on the score
        let interpretation = '';
        let interpretationElement = document.getElementById('interpretation');
        
        // Set the interpretation and change text color for severe anxiety
        if (totalScore <= 4) {
            interpretation = "Minimal Anxiety";
            interpretationElement.style.color = ""; // Reset color
        } else if (totalScore <= 9) {
            interpretation = "Mild Anxiety";
            interpretationElement.style.color = ""; // Reset color
        } else if (totalScore <= 14) {
            interpretation = "Moderate Anxiety";
            interpretationElement.style.color = ""; // Reset color
        } else {
            interpretation = "Severe Anxiety";
            interpretationElement.style.color = "red"; // Set text color to red for severe anxiety
        }

        // Display the interpretation
        interpretationElement.textContent = interpretation;
    }

    // Function to submit the form
    function submitGad7() {
        const totalScore = parseInt(document.getElementById('total-score').textContent);

        // You can do some additional checks or processing here before submitting
        if (isNaN(totalScore)) {
            alert("Please answer all the questions before submitting.");
            return false; // Prevent form submission if validation fails
        }
        const confirmSubmit = confirm("Are you sure you want to submit the form?");

        // If the user confirms, submit the form, else do nothing
        if (confirmSubmit) {
            document.getElementById('gad7-form').submit(); // Submit the form
        } else {
            return false; // Don't submit the form
        }
        return true; // Allow form submission if everything is fine
    }

