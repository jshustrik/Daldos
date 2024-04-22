document.getElementById("createRoomForm").onsubmit = async function(e) {
    e.preventDefault();
    const roomName = document.getElementById("roomName").value;
    const response = await fetch('/create-room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ roomName: roomName }),
    });
    const data = await response.json();
    const roomIdDisplay = document.getElementById("roomIdDisplay");
    const roomIdValue = document.getElementById("roomIdValue");
    const copyIcon = document.getElementById("copyIcon");

    if(data.roomId) {
        roomIdValue.innerText = data.roomId;
        roomIdDisplay.style.display = "block";
        copyIcon.onclick = function() {
            navigator.clipboard.writeText(data.roomId)
                .then(() => alert(`ID комнаты "${roomName}" скопирован: ` + data.roomId))
                .catch(err => console.error("Ошибка при копировании: ", err));
        };
    } else {
        roomIdDisplay.innerText = "Ошибка при создании комнаты";
        roomIdDisplay.style.display = "block";
    }
};
