// Send message
$('#user-input').keypress(function (e) {
    if (e.which === 13) { // 13 is the key code for Enter
        $('#send-button').click();
    }
});

$('#send-button').click(function () {
    const userInput = $('#user-input').val().trim();
    if (userInput) {
        $('#send-button').prop('disabled', true); // Disable button to prevent multiple clicks

        // Display the user's message immediately
        $('#chat-display').append(`
            <div class="self-end bg-blue-500 text-white p-3 rounded-lg max-w-xs">
                ${userInput}
            </div>
        `);

        // Scroll to the bottom to keep the latest message visible
        $('#chat-display').scrollTop($('#chat-display')[0].scrollHeight);

        // Clear the input field immediately after user input
        $('#user-input').val('').focus();

        // Send the user's message to the server
        $.post('/send_message', { user_input: userInput })
            .done(function (data) {
                // Display the bot's response after receiving it
                $('#chat-display').append(`
                    <div class="self-start bg-gray-300 p-3 rounded-lg max-w-xs">
                        ${data.response}
                    </div>
                `);
                $('#chat-display').scrollTop($('#chat-display')[0].scrollHeight); // Scroll to show the bot's response
            })
            .fail(function () {
                // Display an error message in the chat if the request fails
                $('#chat-display').append(`
                    <div class="self-start bg-red-300 p-3 rounded-lg max-w-xs">
                        Waifu: Error: Unable to process your request.
                    </div>
                `);
                $('#chat-display').scrollTop($('#chat-display')[0].scrollHeight);
            })
            .always(function () {
                $('#send-button').prop('disabled', false); // Re-enable the button
            });
    } else {
        alert('Message cannot be empty!');
    }
});

// Function to update online status
async function updateStatus() {
    try {
        const response = await fetch('/status');
        if (!response.ok) throw new Error("API status check failed.");

        const data = await response.json();
        const statusElement = document.querySelector('#api-status');

        if (data.status === 'online') {
            statusElement.textContent = `Online - API Status ${data.code} OK`;
            statusElement.classList.remove('text-gray-600');
            statusElement.classList.add('text-green-600');
        } else {
            throw new Error("API is offline.");
        }
    } catch (error) {
        const statusElement = document.querySelector('#api-status');
        statusElement.textContent = `Offline - Unable to reach API`;
        statusElement.classList.remove('text-gray-600');
        statusElement.classList.add('text-red-600');
    }
}

// Update the status on page load
document.addEventListener('DOMContentLoaded', updateStatus);
