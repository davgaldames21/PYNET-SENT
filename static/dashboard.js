$(document).ready(function() {
    // Array de direcciones IP de los equipos a verificar
    var equipos = ["1.1.1.1", "2.2.2.2", "192.168.1.3"];

    // Función para realizar un ping a una dirección IP
    function pingEquipo(ip) {
        $.ajax({
            url: "/ping", // Ruta de tu Flask para realizar el ping
            data: { "ip": ip },
            success: function(data) {
                // Actualizar el estado del equipo en el dashboard
                if (data === "activo") {
                    $("#dashboard").append("<p>" + ip + " está activo.</p>");
                } else {
                    $("#dashboard").append("<p>" + ip + " está inactivo.</p>");
                }
            }
        });
    }

    // Realizar ping a cada equipo y actualizar el estado cada 5 segundos
    setInterval(function() {
        $("#dashboard").empty(); // Limpiar el dashboard antes de actualizar
        equipos.forEach(function(ip) {
            pingEquipo(ip);
        });
    }, 5000); // Actualizar cada 5 segundos
});
