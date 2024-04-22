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



function buttonListener(button) {
    var buttonId = button.id;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/pve_game_handler", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log(response);

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
                    }
                    else if (response.enemy == false) {
                        button.style.backgroundImage = "url('/static/img/friend_active.png')";
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

            } else {
                console.error('Error:', xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({ "buttonId": buttonId, "bot": false }));
}

function botHandler() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/pve_game_handler", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log(response);
                button = document.getElementById(response.buttonId);
                if (response.activate == true) {
                    setTimeout(() => { 
                        button.style.backgroundImage = "url('/static/img/enemy_active.png')"; },
                        1000);
                }
                if (response.change == true) {
                    setTimeout(() => { 
                        var pressed_button = document.getElementById(response.go_to);
                        var background_image = window.getComputedStyle(pressed_button).getPropertyValue("background-image");
                        pressed_button.style.backgroundImage = button.style.backgroundImage;
                        button.style.backgroundImage = "none"; }, 
                        1000);

                }
            } else {
                console.error('Error:', xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({ "buttonId": "-1", "bot": true }));
}