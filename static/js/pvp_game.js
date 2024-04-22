document.addEventListener("DOMContentLoaded", addListenersToButtons);
localStorage.setItem("add_to_friends", false);
localStorage.setItem("add_to_enemies", false);

function addListenersToButtons() {
    var buttons = document.querySelectorAll(".btn");
    buttons.forEach(function(button) {
        button.addEventListener("click", function() {
            buttonListener(button);
        });
    });
}
var socket = io.connect('http://localhost:8000');
    socket.on('message', function(data) {
        if (data["id"]) {
            var button = document.getElementById(data["id"]);
            button.style.backgroundImage = data["bg"];
        } else if (data["change"]) {
            var old_id = document.getElementById(data["old"]);
            old_id.style.backgroundImage = data["old_bg"];
            var new_id = document.getElementById(data["new"]);
            new_id.style.backgroundImage = data["new_bg"];
            var friends_score = document.getElementById("friends_score_text");
            var enemies_score = document.getElementById("enemies_score_text");
            friends_score.innerText = data["fscore"];
            enemies_score.innerText = data["escore"];
        }
    });

function buttonListener(button) {
    var socket = io.connect('http://localhost:8000');
    var buttonId = button.id;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/pvp_game_handler", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);

                if (response.add_to_friends || response.add_to_enemies) {
                    localStorage.setItem("add_to_friends", response.add_to_friends);
                    localStorage.setItem("add_to_enemies", response.add_to_enemies);
                }

                if (response.go_to !== "pass") {
                    document.getElementById(response.go_to).disabled = false;
                }

                if (response.activate == true) {
                    if (response.enemy == true) {
                        button.style.backgroundImage = "url('/static/img/enemy_active.png')";
                        socket.emit('socket_handler', {"id": button.id, "bg": "url('/static/img/enemy_active.png')" });
                    }
                    else if (response.enemy == false) {
                        button.style.backgroundImage = "url('/static/img/friend_active.png')";
                        socket.emit('socket_handler', {"id": button.id, "bg": "url('/static/img/friend_active.png')" });
                    }
                }


                if (response.change == true) {
                    var pressed_button = document.getElementById(response.pressed_id);
                    pressed_button.disabled = true;
                    var background_image = window.getComputedStyle(pressed_button).getPropertyValue("background-image");
                    pressed_button.style.backgroundImage = "none";
                    button.style.backgroundImage = background_image;

                    var friends_score = parseInt(document.getElementById("friends_score_text").innerText);
                    var enemies_score = parseInt(document.getElementById("enemies_score_text").innerText);
                    if (localStorage.getItem("add_to_friends") === "true") {
                        friends_score += 1;
                        document.getElementById("friends_score_text").innerText = friends_score.toString();
                        localStorage.setItem("add_to_friends", false);
                    } else if (localStorage.getItem("add_to_enemies") === "true") {
                        enemies_score += 1;
                        document.getElementById("enemies_score_text").innerText = enemies_score.toString();
                        localStorage.setItem("add_to_enemies", false);
                    }

                    socket.emit('socket_handler', {"change": true, "old": response.pressed_id, "new": button.id, "old_bg": "none", "new_bg": background_image, "fscore": friends_score.toString(), "escore": enemies_score.toString()});


                    if (friends_score == 15) {
                        document.getElementById('roll_dices').disabled = true;
                        document.querySelectorAll('.btn').forEach(btn => {
                            btn.disabled = true;
                        });
                        alert("Красные выиграли! Игра окончена!");
                    } else if (enemies_score == 15) {
                        document.getElementById('roll_dices').disabled = true;
                        document.querySelectorAll('.btn').forEach(btn => {
                            btn.disabled = true;
                        });
                        alert("Синие выиграли! Игра окончена!");
                    }
                }

                // var buttons = document.querySelectorAll('.btn');
                // buttons.forEach(function(button) {
                //     var backgroundImage = window.getComputedStyle(button).getPropertyValue('background-image');
                //     socket.emit('socket_handler', {"id": button.id, "bg": backgroundImage });
                // });

                // socket.on('message', function(data) {
                //     var button = document.getElementById(data["id"]);
                //     button.style.backgroundImage = data["bg";]
                // });

            } else {
                console.error('Error:', xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({ "buttonId": buttonId }));
}