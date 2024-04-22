document.getElementById('surrender-btn').addEventListener('click', function() {
    console.log(true)
    if (typeof moveOwner !== 'undefined') {
        var friendsText = document.querySelector('[data-friends]').dataset.friends;
        var enemiesText = document.querySelector('[data-enemies]').dataset.enemies;

        var winner = (moveOwner === 'friends') ? enemiesText : friendsText;

        document.getElementById('roll_dices').disabled = true;
        document.querySelectorAll('.btn').forEach(btn => {
            btn.disabled = true;
        });
        alert('Выиграли ' + winner + '!');
    } else {
        console.error('move_owner не определен');
    }
});
