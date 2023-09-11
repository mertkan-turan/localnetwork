function appendLogMessage(element, message) {
    const newLi = document.createElement('li'); // Create a new <li> element

    // Split the message into parts based on a separator (e.g., ' - ')
    const parts = message.split(' - ');

    // Check if the message has the expected format (assuming it should have three parts)
    if (parts.length === 3) {
        const [ip, time, content] = parts; // Destructure the parts into variables

        // Create <div> elements for sender, time-stamp, and message content
        const newSender = document.createElement('div');
        newSender.classList.add('sender'); // Add a CSS class
        newSender.textContent = ip; // Set the sender's IP address

        const newTime = document.createElement('div');
        newTime.classList.add('time-stamp'); // Add a CSS class
        newTime.textContent = time; // Set the timestamp

        const newMessage = document.createElement('div');
        newMessage.classList.add('message'); // Add a CSS class
        newMessage.textContent = content; // Set the message content

        // Append the sender, timestamp, and message content to the <li> element
        newLi.appendChild(newSender);
        newLi.appendChild(newMessage);
        newLi.appendChild(newTime);

        // Append the newly created <li> element to the specified HTML element
        element.appendChild(newLi);

        // Automatically scroll to the new message by setting the scrollTop property
        element.scrollTop = element.scrollHeight;
        
    } else {
        // Handle messages with unexpected format here
        // You can choose to display them differently or log an error
        console.error('Unexpected message format', message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    var logDataDiv = document.getElementById('log-content');
    var eventSource = new EventSource('/stream_log');

    eventSource.onmessage = function (event) {
        appendLogMessage(logDataDiv, event.data)
    };

});

//SIGN  UP   INFORMATION GET
// Assuming you have JavaScript code to collect the username and port data from the signup form
document.getElementById('signupForm').addEventListener('SignUp', function (event) {
    event.preventDefault(); // Prevent the default form submission
    console.log('Form submitted'); // Add this line
    var username = document.getElementById('signup-username').value;
    var port = document.getElementById('signup-port').value;

    // Create a JSON object with the data
    var data = {
        'username': username,
        'port': port
    };

    // Send the data to the server
    fetch('/save_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                console.error('Error:', result.error);
            } else {
                console.log('Data saved successfully:', result.message);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
});

///////GET INFO FROM MESSAGE BUTTON


