document.addEventListener('DOMContentLoaded', function() {
    const encryptButton = document.getElementById('encrypt-button');
    const decryptButton = document.getElementById('decrypt-button');
    const inputField = document.getElementById('input-data');
    const outputField = document.getElementById('output-data');

    encryptButton.addEventListener('click', function() {
        const data = inputField.value;
        fetch('/api/encrypt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ data: data })
        })
        .then(response => response.json())
        .then(data => {
            outputField.value = data.encrypted_data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    decryptButton.addEventListener('click', function() {
        const encryptedData = outputField.value;
        fetch('/api/decrypt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ encrypted_data: encryptedData })
        })
        .then(response => response.json())
        .then(data => {
            inputField.value = data.decrypted_data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});