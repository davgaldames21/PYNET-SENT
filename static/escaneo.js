document.addEventListener('DOMContentLoaded', function () {
    const startScanButton = document.getElementById('start-scan');
    const outputContainer = document.getElementById('output-container');
    const output = document.getElementById('output');

    // Función para agregar mensajes a la salida
    function addMessage(message) {
        output.textContent += message + '\n';
        outputContainer.scrollTop = outputContainer.scrollHeight;
    }

    // Evento click para iniciar el escaneo
    startScanButton.addEventListener('click', function () {
        // Iniciar la conexión SSE
        const eventSource = new EventSource('/scan');

        // Manejar eventos SSE
        eventSource.onmessage = function (event) {
            const message = event.data;
            addMessage(message);
        };

        eventSource.onerror = function () {
            addMessage('Error en la conexión SSE.');
            eventSource.close();
        };

        // Deshabilitar el botón después de iniciar el escaneo
        startScanButton.disabled = true;
    });
});
