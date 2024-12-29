function showSection(sectionId) {
    document.querySelectorAll('main > div').forEach(div => {
        div.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

async function saveEnv() {
    const content = document.getElementById('env-content').value;
    const response = await fetch('/api/env', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
    });

    if (response.ok) {
        const data = await response.json(); 
        alert(data.status);  // Display the response
    } else {
        alert('Error saving ENV');
    }
}
    
async function savePersonality() {
    const content = document.getElementById('personality-content').value;
    const response = await fetch('/api/personality', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
    });

    if (response.ok) {
        const data = await response.json(); 
        alert(data.status);  // Display the response
    } else {
        alert('Error saving personality');
    }
}

async function loadData() {
    const envResponse = await fetch('/api/env');
    const envData = await envResponse.json();

    const envContainer = document.getElementById('env-container');
    envContainer.innerHTML = ''; // Clear previous content

    // Render each key-value pair
    for (const [key, value] of Object.entries(envData)) {
        const row = document.createElement('div');
        row.className = 'flex items-center mb-2';

        const keyInput = document.createElement('input');
        keyInput.type = 'text';
        keyInput.value = key;
        keyInput.className = 'w-1/3 p-2 border rounded mr-2';
        keyInput.dataset.originalKey = key; // Save the original key for tracking edits

        const valueInput = document.createElement('input');
        valueInput.type = 'text';
        valueInput.value = value;
        valueInput.className = 'w-2/3 p-2 border rounded';

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.className = 'ml-2 bg-red-500 text-white py-1 px-2 rounded hover:bg-red-600';
        deleteButton.onclick = () => row.remove();

        row.appendChild(keyInput);
        row.appendChild(valueInput);
        row.appendChild(deleteButton);
        envContainer.appendChild(row);
    }

    const personalityResponse = await fetch('/api/personality');
    const personalityData = await personalityResponse.json();
    document.getElementById('personality-content').value = personalityData.content;

    const logResponse = await fetch('/api/log');
    const logData = await logResponse.json();
    document.getElementById('error-log-content').innerText = logData.content;

    const historyResponse = await fetch('/api/message_history');
    const historyData = await historyResponse.json();
    document.getElementById('message-history-content').innerText = historyData.content;

    const mp3Response = await fetch('/api/mp3');
    const mp3Data = await mp3Response.json();
    const mp3List = document.getElementById('mp3-files-list');
    mp3List.innerHTML = '';
    mp3Data.files.forEach(file => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.href = `/api/mp3/${file}`;
        link.innerText = file;
        link.target = '_blank';
        li.appendChild(link);
        mp3List.appendChild(li);
    });
}

window.onload = loadData;