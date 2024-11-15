document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        height: 'auto',
        contentHeight: 'auto',
        themeSystem: 'bootstrap',
        eventTextColor: '#000',
        eventDisplay: 'block',
        events: '/api/lessons/', // Your API endpoint

        // Ensure event text is large and readable
        eventDidMount: function(info) {
            const eventEl = info.el;

            // Apply inline styles for better readability
            eventEl.style.fontSize = '1.4rem'; // Increase font size
            eventEl.style.padding = '10px'; // Add padding
            eventEl.style.backgroundColor = '#b0c4de'; // Light blue background for contrast
            eventEl.style.color = '#333'; // Dark text color
            eventEl.style.border = '1px solid #0056b3'; // Add border for better visibility
            eventEl.style.borderRadius = '4px'; // Rounded corners
        },
    });
    calendar.render();
});
