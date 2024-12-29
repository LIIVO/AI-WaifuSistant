var app = document.getElementById('app');

var typewriter = new Typewriter(app, {
    loop: true
});

typewriter.typeString('Start Chat with <u style="text-decoration: red underline;">Your Waifu</u>')
    .pauseFor(1500)
    .deleteChars(10)
    .typeString('<strong>AI-WaifuSistant.</strong>')
    .pauseFor(2500)
    .deleteAll()
    .typeString('Powered, Trained with <strong>openAI GPT Model</strong>')
    .pauseFor(2500)
    .start();