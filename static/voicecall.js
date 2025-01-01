let isTalkingModeActive = false;
let pollInterval = null;

$('#voice-call-button').click(function () {
    const toggleMode = !isTalkingModeActive;

    $.post('/talking_mode_poll', { talking_mode: toggleMode })
        .done(function (data) {
            isTalkingModeActive = toggleMode;
            $('#voice-call-button').html(toggleMode
                ? '<i class="fa-solid fa-phone-slash"></i>'
                : '<i class="fa-solid fa-phone"></i>'
            );

            if (toggleMode) {
                // Start polling
                pollInterval = setInterval(() => {
                    $.get('/talking_mode_status')
                        .done(function (data) {
                            if (data.response) {
                                $('#chat-display').append(`
                                    <div class="self-start bg-gray-300 p-3 rounded-lg max-w-xs">
                                        Waifu: ${data.response}
                                    </div>
                                `);
                            }
                        });
                }, 2000); // Poll every 2 seconds
            } else {
                // Stop polling
                clearInterval(pollInterval);
                pollInterval = null;
            }
        })
        .fail(function () {
            alert('Error toggling talking mode.');
        });
});
