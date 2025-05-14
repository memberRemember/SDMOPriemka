document.addEventListener('DOMContentLoaded', function() {
    const actualBtn = document.querySelector('.actual-appointments-btn');
    const archivedBtn = document.querySelector('.archived-appointments-btn');
    const statusFilter = document.querySelector('#status-filter');
    const userFilter = document.querySelector('#user-filter');
    const labelDesc = document.querySelector('.label-desc');
    const idSearch = document.getElementById('id-search');
    const container = document.getElementById('appointments-container');
    const appointmentsUrl = "{% url 'priemka_lc_appointments_page' %}";
    let currentFilter = 'actual';

    function loadAppointments(filter, status) {
        const searchId = idSearch.value;
        const statusValue = statusFilter.value;
        const userValue = userFilter.value;

        let url = `${appointmentsUrl}?filter=${currentFilter}&status=${statusValue}`;
        
        if (userValue !== 'all') {
            url += `&deputy=${userValue}`;
        }
        if (searchId) {
            url += `&search_id=${searchId}`;
        }
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            container.innerHTML = '';
            if (data.appointments.length > 0) {
                data.appointments.forEach(appointment => {
                    let statusClass;
                    switch (appointment.status_id) {
                        case 1: statusClass = 'status-processing'; break;
                        case 2: statusClass = 'status-registered'; break;
                        case 3: statusClass = 'status-finished'; break;
                        case 4: statusClass = 'status-canceled'; break;
                        case 5: statusClass = 'status-declined'; break;
                        default: statusClass = 'status-processing';
                    }

                    const detailsUrl = `${appointmentsUrl}/${appointment.id}`;

                    const card = `
                        <div class="appointment-card">
                            <div class="top">
                                <div class="left-block">
                                    <div class="title">№${ appointment.id } Запись на прием к ${appointment.deputy}</div>
                                    <div class="deputy-position">${appointment.position}</div>
                                </div>
                                <div class="right-block">
                                    <div class="status">
                                        <i class="bi bi-circle-fill ${statusClass}"></i>
                                        ${appointment.status_name}
                                    </div>
                                </div>
                            </div>
                            <div class="appointment-info">
                                <div class="theme">
                                    <div class="title">Тема приема:</div>
                                    <div class="text">${appointment.theme}</div>
                                </div>
                                <div class="appointment-title">
                                    <div class="title">Заголовок:</div>
                                    <div class="text">${appointment.title}</div>
                                </div>
                                <div class="appointed-date-block">
                                    <div class="appointed-date-block-title">Прием назначен на:</div>
                                    <div class="appointed-time">${appointment.appointed_time}</div>
                                    <div class="appointed-date">${appointment.appointed_date}</div>
                                </div>
                                <div class="btns-block">
                                    <div class="appointment-creation-date">
                                        <div class="text">
                                            ${appointment.creation_date}
                                        </div>
                                    </div>
                                    <a href="${detailsUrl}" class="button details-btn">Подробнее</a>
                                </div>
                            </div>
                        </div>
                    `;
                    container.innerHTML += card;
                });
            } else {
                container.innerHTML = '<div class="no-appointments-banner"><div class="banner"><svg width="800px" height="800px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10.5 15L13.5 12M13.5 15L10.5 12" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"/><path d="M22 11.7979C22 9.16554 22 7.84935 21.2305 6.99383C21.1598 6.91514 21.0849 6.84024 21.0062 6.76946C20.1506 6 18.8345 6 16.2021 6H15.8284C14.6747 6 14.0979 6 13.5604 5.84678C13.2651 5.7626 12.9804 5.64471 12.7121 5.49543C12.2237 5.22367 11.8158 4.81578 11 4L10.4497 3.44975C10.1763 3.17633 10.0396 3.03961 9.89594 2.92051C9.27652 2.40704 8.51665 2.09229 7.71557 2.01738C7.52976 2 7.33642 2 6.94975 2C6.06722 2 5.62595 2 5.25839 2.06935C3.64031 2.37464 2.37464 3.64031 2.06935 5.25839C2 5.62595 2 6.06722 2 6.94975M21.9913 16C21.9554 18.4796 21.7715 19.8853 20.8284 20.8284C19.6569 22 17.7712 22 14 22H10C6.22876 22 4.34315 22 3.17157 20.8284C2 19.6569 2 17.7712 2 14V11" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"/></svg></div><div class="title">Записей на прием нет</div></div>';
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }

    function updateStatusLabel() {
        const selectedOption = statusFilter.options[statusFilter.selectedIndex].text;
        statusFilter.previousElementSibling.querySelector('.label-desc').textContent = selectedOption;
    }

    function updateUserLabel() {
        const selectedOption = userFilter.options[userFilter.selectedIndex].text;
        userFilter.previousElementSibling.querySelector('.label-desc').textContent = selectedOption;
    }

    idSearch.addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
        loadAppointments();
    });

    actualBtn.addEventListener('click', function() {
        actualBtn.classList.add('active');
        archivedBtn.classList.remove('active');
        currentFilter = 'actual';
        loadAppointments(currentFilter, statusFilter.value, userFilter.value);
    });

    archivedBtn.addEventListener('click', function() {
        archivedBtn.classList.add('active');
        actualBtn.classList.remove('active');
        currentFilter = 'archived';
        loadAppointments(currentFilter, statusFilter.value, userFilter.value);
    });

    statusFilter.addEventListener('change', function() {
        loadAppointments(currentFilter, statusFilter.value, userFilter.value);
        updateStatusLabel();
    });

    userFilter.addEventListener('change', function() {
        loadAppointments(currentFilter, statusFilter.value, userFilter.value);
        updateUserLabel();
    });

    loadAppointments('actual', 'all', 'all');
    updateStatusLabel();
    updateUserLabel();
});