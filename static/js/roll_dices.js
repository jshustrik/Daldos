document.addEventListener("DOMContentLoaded", function() {
    var socket = io.connect('http://localhost:8000');
    socket.on('message', function(data) {
        if (data["firstDiceText"]) {
            var firstDiceText = document.getElementById("first_dice_text");
            var secondDiceText = document.getElementById("second_dice_text");
            firstDiceText.innerText = data["firstDiceText"];
            secondDiceText.innerText = data["secondDiceText"];
            var friendsMoveText = document.getElementById("friends_move_text");
            var enemiesMoveText = document.getElementById("enemies_move_text");
            friendsMoveText.innerText = data["friendsMoveText"];
            enemiesMoveText.innerText = data["enemiesMoveText"];
            var allButtons = document.querySelectorAll(".btn");
            if (data["mo"] == "friends") {
                allButtons.forEach(function(button) {
                    backgroundImage = window.getComputedStyle(button).getPropertyValue("background-image");
                    var temp = backgroundImage.split('/')[backgroundImage.split('/').length - 1];
                    var image = temp.substring(0, temp.length - 2);
                    if (!(image.trim() == "friend_active.png" || image.trim() == "friend_nonactive.png")) {
                        button.disabled = true;
                    }
                });
            } else {
                allButtons.forEach(function(button) {
                    backgroundImage = window.getComputedStyle(button).getPropertyValue("background-image");
                    var temp = backgroundImage.split('/')[backgroundImage.split('/').length - 1];
                    var image = temp.substring(0, temp.length - 2);
                    if (!(image.trim() == "enemy_active.png" || image.trim() == "enemy_nonactive.png")) {
                        button.disabled = true;
                    }
                });
            }
        }
    });
    var rollDicesButton = document.getElementById("roll_dices");
    rollDicesButton.addEventListener("click", function () {
        localStorage.setItem("userClicked", true);
        updatePageData();
    });
    var bots_move = document.getElementById("bots_move")
    bots_move.addEventListener("click", function() {
        botListener(bots_move);
    });

    var userClicked = localStorage.getItem("userClicked");
    if (userClicked === "true") {
        updatePageData();
    }

    else {
        reloadFillingFields();
    }
});

function reloadFillingFields() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/roll_dices_page", true);
    xhr.setRequestHeader("Content-Type", "application/json"); 
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                FillFields(response.move_owner, response.first_dice, response.second_dice, response.first_move_over,
                    response.friends_first_move, response.enemies_first_move, response.is_pve);
            } 
            else {
                console.error('Error:', xhr.status);
            }
        }
    };
    
    xhr.send(JSON.stringify({ "reload": true, "bot": false }));
}

function updatePageData() {
    var userClicked = localStorage.getItem("userClicked");
    if (userClicked === "true") {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/roll_dices_page", true);
        xhr.setRequestHeader("Content-Type", "application/json"); 
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    FillFields(response.move_owner, response.first_dice, response.second_dice, response.first_move_over,
                        response.friends_first_move, response.enemies_first_move, response.is_pve);
                } 
                else {
                    console.error('Error:', xhr.status);
                }
            }
        };

        if (document.getElementById("friends_move_text").innerText === "Да") {
            move_owner = "enemies"
        } else {
            move_owner = "friends"
        }
        xhr.send(JSON.stringify({ "reload": false, "bot": false }));
        localStorage.removeItem("userClicked");
    }
}

function botListener(button) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/roll_dices_page", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                FillFields(response.move_owner, response.first_dice, response.second_dice, response.first_move_over,
                    response.friends_first_move, response.enemies_first_move, response.is_pve);
                botHandler();
            } else {
                console.error('Error:', xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({ "reload": false, "bot": true }));
}

function FillFields(moveOwner, firstDice, secondDice, first_move_over, friends_first_move, enemies_first_move, is_pve) {
    var friendsMoveText = document.getElementById("friends_move_text");
    var enemiesMoveText = document.getElementById("enemies_move_text");
    var allButtons = document.querySelectorAll(".btn");
    var firstDiceText = document.getElementById("first_dice_text");
    var secondDiceText = document.getElementById("second_dice_text");

    if (firstDice == "1") {
        firstDiceText.innerText = "A";
    }
    else {
        firstDiceText.innerText = firstDice;
    }
    if (secondDice == "1") {
        secondDiceText.innerText = "A";
    }
    else {
        secondDiceText.innerText = secondDice;
    }
    
    if (moveOwner == "friends") {
        friendsMoveText.innerText = "Да";
        enemiesMoveText.innerText = "Нет";
    
        if (first_move_over) {
            if (friends_first_move) {
                var firstFriendsButton = document.getElementById("33");
                firstFriendsButton.disabled = false;
            }
            else {
                allButtons.forEach(function(button) {
                    backgroundImage = window.getComputedStyle(button).getPropertyValue("background-image");
                    var temp = backgroundImage.split('/')[backgroundImage.split('/').length - 1];
                    var image = temp.substring(0, temp.length - 2);
                    if (image.trim() == "friend_active.png" || image.trim() == "friend_nonactive.png") {
                        button.disabled = false;
                    }
                    else {
                        button.disabled = true;
                    }
                });
            }
        }

    } 
    else {
        friendsMoveText.innerText = "Нет";
        enemiesMoveText.innerText = "Да";


        if (first_move_over) {
            if (is_pve) {
                allButtons.forEach(function(button) {
                    button.disabled = true;
                });
                return;
            }
            if (enemies_first_move) {
                var enemiesFriendsButton = document.getElementById("0");
                enemiesFriendsButton.disabled = false;
            }

            else {
                allButtons.forEach(function(button) {
                    backgroundImage = window.getComputedStyle(button).getPropertyValue("background-image");
                    var temp = backgroundImage.split('/')[backgroundImage.split('/').length - 1];
                    var image = temp.substring(0, temp.length - 2);
                    if (image.trim() == "enemy_active.png" || image.trim() == "enemy_nonactive.png") {
                        button.disabled = false;
                    }
                    else {
                        button.disabled = true;
                    }
                });
            }
        }
    }

    var socket = io.connect('http://localhost:8000');
    socket.emit('socket_handler', {"firstDiceText": firstDiceText.innerText, "secondDiceText": secondDiceText.innerText,
     "friendsMoveText": friendsMoveText.innerText, "enemiesMoveText": enemiesMoveText.innerText, "mo": moveOwner});
}
