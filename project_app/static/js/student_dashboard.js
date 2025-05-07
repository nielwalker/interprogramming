
document.addEventListener('DOMContentLoaded', () => {
    const weekTabsContainer = document.querySelector('.week-tabs');
    const formContainer = document.querySelector('.form-container');
    const navButtons = document.querySelectorAll('.nav-button');

    const weekData = [
        { id: 'week1', label: 'Week 1' },
        { id: 'week2', label: 'Week 2' },
        { id: 'week3', label: 'Week 3' },
        { id: 'week4', label: 'Week 4' },
        { id: 'week5', label: 'Week 5' },
        { id: 'week6', label: 'Week 6' },
        { id: 'week7', label: 'Week 7' },
        { id: 'week8', label: 'Week 8' },
        { id: 'week9', label: 'Week 9' },
        { id: 'week10', label: 'Week 10' },
        { id: 'week11', label: 'Week 11' },
        { id: 'week12', label: 'Week 12' },
    ];

    function createWeekDropdown() {
        const weekSelect = document.getElementById('week-select');
        if (!weekSelect) {
            console.error('week-select element not found!');
            return;
        }

        weekSelect.innerHTML = ''; // Clear existing options

        // Populate the dropdown with weekData
        weekData.forEach(week => {
            const option = document.createElement('option');
            option.value = week.id;
            option.textContent = week.label;
            weekSelect.appendChild(option);
        });

        // Add event listener to handle dropdown changes
        weekSelect.addEventListener('change', (event) => {
            const selectedWeekId = event.target.value;
            showWeekReport(selectedWeekId);
        });

        // Show the first week's report by default
        if (weekData.length > 0) {
            weekSelect.value = weekData[0].id;
            showWeekReport(weekData[0].id);
        }
    }

    function showWeekReport(weekId) {
        const form = document.getElementById('week-form');
        if (!form) {
            console.error('Form element not found!');
            return;
        }

        const table = document.createElement('table');
        table.id = 'report-form';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Date</th>
                    <th>No. of Hours</th>
                    <th>Activities/Tasks</th>
                    <th>Score</th>
                    <th>New Learnings</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><input type="date" name="date"></td>
                    <td><input type="number" name="hours" min="0"></td>
                    <td><textarea name="activities"></textarea></td>
                    <td><input type="text" name="score"></td>
                    <td><textarea name="learnings"></textarea></td>
                </tr>
            </tbody>
        `;

        // Clear existing table and append the new one
        form.innerHTML = '';
        form.appendChild(table);

        const submitButton = document.createElement('button');
        submitButton.id = 'submit-button';
        submitButton.type = 'submit';
        submitButton.textContent = 'Submit';
        form.appendChild(submitButton);

        // Attach the submit event handler here!
        form.onsubmit = function(event) {
            event.preventDefault();

            const formData = new FormData(form);
            formData.append('week', weekId);

            fetch('/add-week-report/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }
            })
            .then(response => {
                if (response.ok) {
                    alert('Week report submitted successfully!');
                    form.reset();
                } else {
                    alert('Failed to submit the week report.');
                }
            })
            .catch(error => console.error('Error:', error));
        };
    }

    function handleNavClick(action) {
        formContainer.innerHTML = ''; // Clear form container

        if (action === 'add-week-report') {
            formContainer.innerHTML = `
                <div class="week-dropdown">
                    <label for="week-select" class="week-label">Select Week:</label>
                    <select id="week-select" class="week-select">
                        <!-- Options will be dynamically added here -->
                    </select>
                </div>
                <form id="week-form">
                    <!-- Table will be dynamically added here -->
                </form>
            `;
            createWeekDropdown(); // Create the dropdown for weeks
        } else if (action === 'upload-journal') {
            formContainer.innerHTML = `
                <h3>Upload Journal Section</h3>
                <p>Please upload your journal in PDF format:</p>
                <form id="upload-journal-form">
                    <input type="file" id="journal-file" name="journal-file" accept="application/pdf" />
                    <button type="submit" id="upload-button">Upload</button>
                </form>
            `;
        } else if (action === 'overview') {
            formContainer.innerHTML = `
                <h3>Overview Section</h3>
                <div>
                    <label for="overview-week-select" class="week-label">Select Week:</label>
                    <select id="overview-week-select" class="week-select"></select>
                </div>
                <div id="overview-container"></div>
            `;

            // Populate the dropdown
            const weekSelect = document.getElementById('overview-week-select');
            weekData.forEach(week => {
                const option = document.createElement('option');
                option.value = week.id;
                option.textContent = week.label;
                weekSelect.appendChild(option);
            });

            // Function to render the table for the selected week
            function renderOverviewTable(data, selectedWeek) {
                const overviewContainer = document.getElementById('overview-container');
                const filtered = data.filter(report => report.week === selectedWeek);
                if (filtered.length === 0) {
                    overviewContainer.innerHTML = '<p>No reports found for this week.</p>';
                    return;
                }
                filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
                let tableHTML = `
                    <table class="overview-table" id="overview-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>No. of Hours</th>
                                <th>Activities/Tasks</th>
                                <th>Score</th>
                                <th>New Learnings</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                filtered.forEach((report, idx) => {
                    tableHTML += `
                        <tr data-report-id="${report.id || ''}">
                            <td><input type="date" value="${report.date}" class="edit-date" disabled></td>
                            <td><input type="number" value="${report.hours}" class="edit-hours" disabled></td>
                            <td><textarea class="edit-activities" disabled>${report.activities}</textarea></td>
                            <td><input type="text" value="${report.score}" class="edit-score" disabled></td>
                            <td><textarea class="edit-learnings" disabled>${report.learnings}</textarea></td>
                            <td>
                                <button class="edit-btn">Edit</button>
                            </td>
                        </tr>
                    `;
                });
                tableHTML += `
                        </tbody>
                    </table>
                `;
                overviewContainer.innerHTML = tableHTML;

                // Add event listeners for Edit/Save buttons
                overviewContainer.querySelectorAll('.edit-btn').forEach((btn, idx) => {
                    btn.addEventListener('click', function() {
                        const row = btn.closest('tr');
                        const isEditing = btn.textContent === 'Save';
                        const inputs = row.querySelectorAll('input, textarea');
                        if (!isEditing) {
                            // Enable editing
                            inputs.forEach(input => input.disabled = false);
                            btn.textContent = 'Save';
                        } else {
                            // Disable editing and save
                            const reportId = filtered[idx].id;
                            const payload = {
                                id: reportId,
                                week: selectedWeek,
                                date: row.querySelector('.edit-date').value,
                                hours: row.querySelector('.edit-hours').value,
                                activities: row.querySelector('.edit-activities').value,
                                score: row.querySelector('.edit-score').value,
                                learnings: row.querySelector('.edit-learnings').value,
                            };
                            fetch('/update-week-report/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                                },
                                body: JSON.stringify(payload)
                            })
                            .then(response => {
                                if (response.ok) {
                                    alert('Report updated!');
                                    inputs.forEach(input => input.disabled = true);
                                    btn.textContent = 'Edit';
                                } else {
                                    alert('Failed to update report.');
                                }
                            })
                            .catch(error => alert('Error: ' + error));
                        }
                    });
                });
            }

            // Fetch data and set up event listener
            fetch('/get-week-reports/')
                .then(response => response.json())
                .then(data => {
                    // Show the first week by default
                    renderOverviewTable(data, weekSelect.value);
                    weekSelect.addEventListener('change', () => {
                        renderOverviewTable(data, weekSelect.value);
                    });
                })
                .catch(error => {
                    const overviewContainer = document.getElementById('overview-container');
                    overviewContainer.innerHTML = '<p>Failed to load reports. Please try again later.</p>';
                });
        }
    }

    // Event Listeners for Navigation Buttons
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const action = button.dataset.action;
            handleNavClick(action);
        });
    });

    // Initialize - Show "Add Week Report" section on initial load
    handleNavClick('add-week-report');
});

document.getElementById('week-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);
    const selectedWeek = document.getElementById('week-select').value; // Get the selected week
    formData.append('week', selectedWeek); // Add the selected week to the form data

    fetch('/add-week-report/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (response.ok) {
            alert('Week report submitted successfully!');
            this.reset(); // Reset the form
        } else {
            alert('Failed to submit the week report.');
        }
    })
    .catch(error => console.error('Error:', error));
});