var socket = io();

document.getElementById("joinRoomForm").onsubmit = function(e) {
    e.preventDefault();
    const roomId = document.getElementById("roomIdInput").value;
    const username = "Имя игрока"; // TODO: имя игрока???

    fetch(`/get-room-name?roomId=${roomId}`)
        .then(response => {
            if(response.ok) {
                return response.json().then(data => {
                    alert(`Вы успешно присоединились к игре с названием «${data.roomName}»`);
                    socket.emit('join', {roomId: roomId, username: username});
                    window.location.href = `/pvp_game?roomId=${roomId}`;
                });
            } else {
                window.location.href = "/error";
            }
        })
        .catch(error => {
            console.error('Произошла ошибка при запросе к серверу:', error);
            alert("Произошла ошибка. Пожалуйста, попробуйте снова.");
        });
};
