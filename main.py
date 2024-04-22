from flask import *
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from game_control import Game
from dices import Dices
import uuid
from board import Board
from chips import Chips
import time


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
game_control = Game()
dices = Dices()
board = Board()
chips = Chips()
top = board.top
middle = board.middle
bottom = board.bottom
friends = chips.friends
enemies = chips.enemies
pressed_id = "-1"
who_is_moving_in_middle = "pass"
rooms = {}
flag_of_move = False
is_pve = False
bot_goto = "pass"
first_move_ower = False


@socketio.on('socket_handler')
def handle_message(message):
    send(message, broadcast=True)

@app.route("/")
def home():
    return render_template("main.html")

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('error_page'))

@app.route("/error")
def error_page():
    return render_template("error.html"), 404

@app.route("/create")
def create():
    return render_template("create.html")

@app.route("/create-room", methods=["POST"])
def create_room():
    data = request.json
    room_name = data.get("roomName")
    room_id = str(uuid.uuid4())
    rooms[room_id] = {
        "name": room_name,
        "players": []
    }
    return jsonify(roomId=room_id)

@app.route("/enter")
def enter():
    return render_template("enter.html")

@app.route("/get-room-name")
def get_room_name():
    room_id = request.args.get('roomId')
    room_name = rooms.get(room_id, {}).get("name")
    if room_name:
        return jsonify(roomName=room_name)

@app.route("/pvp_game")
def pvp_game():
    room_id = request.args.get('roomId', None)

    if room_id:
        if room_id not in rooms:
            return redirect(url_for('error_page'))
        
    return render_template("pvp_game.html", move_owner=game_control.move_owner, roomId=room_id)


@app.route("/pve_game")
def pve_game():
    global is_pve
    is_pve = True
    room_id = request.args.get('roomId', None)

    if room_id:
        if room_id not in rooms:
            return redirect(url_for('error_page'))
        
    return render_template("pve_game.html", move_owner=game_control.move_owner, roomId=room_id)


@socketio.on('join')
def on_join(data):
    room_id = data['roomId']
    username = data['username']
    join_room(room_id)
    rooms[room_id]["players"].append(username)
    emit('status', {'msg': f'{username} has entered the room.'}, room=room_id)

@socketio.on('leave')
def on_leave(data):
    room_id = data['roomId']
    username = data['username']
    leave_room(room_id)
    rooms[room_id]["players"].remove(username)
    emit('status', {'msg': f'{username} has left the room.'}, room=room_id)

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/roll_dices_page", methods=["POST"])
def roll_dices_page():
    global game_control, dices, is_pve
    data = request.json
    if (data["reload"]):
        game_control = Game()
        dices = Dices()

    else:
        if (data["bot"]):
            time.sleep(1)
            
        dices.roll_dices()
        if (game_control.first_move):
            if (1 not in [dices.first_dice, dices.second_dice]):
                if (game_control.move_owner == "friends"):
                    game_control.move_owner = "enemies"
                elif (game_control.move_owner == "enemies"):
                    game_control.move_owner = "friends"
            else:
                game_control.first_move = False

                if (game_control.move_owner == "friends"):
                    game_control.friends_first_move = True
                else:
                    game_control.enemies_first_move = True         
        
        else:
            if (game_control.move_owner == "friends"):
                game_control.move_owner = "enemies"
            elif (game_control.move_owner == "enemies"):
                game_control.move_owner = "friends"

    response = {"first_dice": str(dices.first_dice), "second_dice": str(dices.second_dice), 
                "move_owner": game_control.move_owner, "first_move": game_control.first_move, 
                "first_move_over": not(game_control.first_move), "friends_first_move": game_control.friends_first_move,
                "enemies_first_move": game_control.enemies_first_move, "is_pve": is_pve }

    return jsonify(response), 200


@app.route("/pvp_game_handler", methods=["POST"])
def pvp_game_handler():
    return pvp_game(request.json)


@app.route("/pve_game_handler", methods=["POST"])
def pve_game_handler():
    global dices, game_control
    data = request.json
    if (data["buttonId"] == "-1"):
        data["buttonId"] = "0"

    
    return pve_game(request.json)


def pvp_game(data):
    global dices, pressed_id, who_is_moving_in_middle, flag_of_move
    button_id = data.get("buttonId")
    dices_sum = dices.first_dice + dices.second_dice
    enemy = "pass"
    activate = "pass"
    goto_id = "pass"
    change = "pass"
    pressed_id_return = "pass"
    cell_list = list()
    add_to_friends = False
    add_to_enemies = False

    if (0 <= int(button_id) <= 15):
        if (pressed_id == "-1"):
            if (0 <= int(top[button_id]) <= 15):
                enemy = True
                activate = click_handler(button_id, True, True)
            else:
                activate = False

            pressed_id = button_id

            if (game_control.enemies_first_move):
                game_control.enemies_first_move = False
                
                if (game_control.global_first_move):
                    game_control.friends_first_move = True
                    game_control.global_first_move = False

            delta = int(pressed_id) - dices_sum
            if (delta < 0):
                for cell in range(int(pressed_id) - 1, -1, -1):
                    cell_list.append(top[str(cell)])
                for cell in range(16, 16 + abs(delta)):
                    cell_list.append(middle[str(cell)])
                goto_id = str(15 + abs(delta))
            else:
                for cell in range(int(pressed_id) - 1, delta - 1, -1):
                    cell_list.append(top[str(cell)])
                goto_id = str(delta)

            pressed_id_return = pressed_id

        else:
            if (pressed_id in top):
                check_goto = str(int(pressed_id) - dices_sum)
            else:
                check_goto = str(15 - (int(pressed_id) + dices_sum - 33))

            if (check_goto == button_id or flag_of_move):
                change = True
                flag_of_move = False

            pressed_id_return, pressed_id = pressed_id, "-1"  
            if (pressed_id_return not in top):
                top[button_id] = middle[pressed_id_return]
                middle[pressed_id_return] = "-1"
            else:
                top[button_id] = top[pressed_id_return]
                top[pressed_id_return] = "-1"


    elif (33 <= int(button_id) <= 48):
        if (pressed_id == "-1"):
            if (33 <= int(bottom[button_id]) <= 48):
                enemy = False
                activate = click_handler(button_id, False, True)
            else:
                activate = False
            
            pressed_id = button_id

            if (game_control.friends_first_move):
                game_control.friends_first_move = False

                if (game_control.global_first_move):
                    game_control.enemies_first_move = True
                    game_control.global_first_move = False

            delta = int(pressed_id) - dices_sum
            if (delta < 33):
                for cell in range(int(pressed_id) - 1, 32, -1):
                    cell_list.append(bottom[str(cell)])
                for cell in range(16, 16 + abs(delta - 33)):
                    cell_list.append(middle[str(cell)])
                goto_id = str(15 + abs(delta - 33))
            else:
                for cell in range(int(pressed_id) - 1, delta - 1, -1):
                    cell_list.append(bottom[str(cell)])
                goto_id = str(delta)
            pressed_id_return = pressed_id

        else:
            if (pressed_id in bottom):
                delta = int(pressed_id) - dices_sum
                if (delta < 0):
                    check_goto = str(15 + abs(delta - 33))
                else:
                    check_goto = str(delta)

            else:
                check_goto = str(49 - abs(32 - (int(pressed_id) + dices_sum)))

            if (check_goto == button_id or flag_of_move):
                change = True
                flag_of_move = False

            pressed_id_return, pressed_id = pressed_id, "-1"  

            if (pressed_id_return not in bottom):
                bottom[button_id] = middle[pressed_id_return]
                middle[pressed_id_return] = "-1" 
            else:
                bottom[button_id] = bottom[pressed_id_return]
                bottom[pressed_id_return] = "-1"

    else:
        if (pressed_id != "-1"):
            if (pressed_id in middle):
                delta = int(pressed_id) + dices_sum
                if (delta > 32):
                    check_goto = str(15 - (delta - 33))
                else:
                    check_goto = str(delta)

            else:
                delta = int(pressed_id) - dices_sum
                if (0 <= int(pressed_id) <= 15):
                    check_goto = str(15 + abs(delta))
                else:
                    check_goto = str(15 + abs(delta - 33))

            if (check_goto == button_id or flag_of_move):
                change = True   

            pressed_id_return, pressed_id = pressed_id, "-1"
            if (pressed_id_return in middle):
                middle[button_id] = middle[pressed_id_return] 
                middle[pressed_id_return] = "-1"
            elif (pressed_id_return in top):
                middle[button_id] = top[pressed_id_return]
                top[pressed_id_return] = "-1"
            else:
                middle[button_id] = bottom[pressed_id_return]
                bottom[pressed_id_return] = "-1"

        else:
            delta = int(button_id) + dices_sum
            if (delta > 32):
                for cell in range(int(button_id) + 1, 33):
                    cell_list.append(middle[str(cell)])

                if (middle[button_id] in bottom):
                    for cell in range(15, 14 - (delta - 33), -1):
                        cell_list.append(top[str(cell)])
                    goto_id = str(15 - (delta - 33))
                else:
                    for cell in range(48, 47 - (delta - 33), -1):
                        cell_list.append(bottom[str(cell)])
                    goto_id = str(48 - (delta - 33))

            else:
                for cell in range(int(button_id) + 1, delta + 1):
                    cell_list.append(middle[str(cell)])
                goto_id = str(delta)

            pressed_id = button_id            
            pressed_id_return = button_id
            
    if cell_list:
        if (pressed_id_return in top):
            for cell in cell_list:
                if ((cell in top and top[pressed_id_return] in top) or (cell in bottom and top[pressed_id_return] in bottom)):
                    goto_id = change_goto(goto_id, cell)
                    break
            if (goto_id in top):
                if (top[pressed_id_return] in top and top[goto_id] in bottom):
                    add_to_enemies = True
                elif (top[pressed_id_return] in bottom and top[goto_id] in top):
                    add_to_friends = True
            elif (goto_id in bottom):
                if (top[pressed_id_return] in top and bottom[goto_id] in bottom):
                    add_to_enemies = True
                elif (top[pressed_id_return] in bottom and bottom[goto_id] in top):
                    add_to_friends = True
            else:
                if (top[pressed_id_return] in top and middle[goto_id] in bottom):
                    add_to_enemies = True
                elif (top[pressed_id_return] in bottom and middle[goto_id] in top):
                    add_to_friends = True                   

        elif (pressed_id_return in middle):
            for cell in cell_list:
                if ((cell in top and middle[pressed_id_return] in top) or (cell in bottom and middle[pressed_id_return] in bottom)):
                    goto_id = change_goto(goto_id, cell)
                    break
            if (goto_id in top):
                if (middle[pressed_id_return] in top and top[goto_id] in bottom):
                    add_to_enemies = True
                elif (middle[pressed_id_return] in bottom and top[goto_id] in top):
                    add_to_friends = True
            elif (goto_id in bottom):
                if (middle[pressed_id_return] in top and bottom[goto_id] in bottom):
                    add_to_enemies = True
                elif (middle[pressed_id_return] in bottom and bottom[goto_id] in top):
                    add_to_friends = True
            else:
                if (middle[pressed_id_return] in top and middle[goto_id] in bottom):
                    add_to_enemies = True
                elif (middle[pressed_id_return] in bottom and middle[goto_id] in top):
                    add_to_friends = True   

        else:
            for cell in cell_list:
                if ((cell in top and bottom[pressed_id_return] in top) or (cell in bottom and bottom[pressed_id_return] in bottom)):
                    goto_id = change_goto(goto_id, cell)
                    break
            if (goto_id in top):
                if (bottom[pressed_id_return] in top and top[goto_id] in bottom):
                    add_to_enemies = True
                elif (bottom[pressed_id_return] in bottom and top[goto_id] in top):
                    add_to_friends = True 
            elif (goto_id in bottom):
                if (bottom[pressed_id_return] in top and bottom[goto_id] in bottom):
                    add_to_enemies = True
                elif (bottom[pressed_id_return] in bottom and bottom[goto_id] in top):
                    add_to_friends = True 
            else:
                if (bottom[pressed_id_return] in top and middle[goto_id] in bottom):
                    add_to_enemies = True
                elif (bottom[pressed_id_return] in bottom and middle[goto_id] in top):
                    add_to_friends = True     

    return jsonify({ "change": change, "enemy": enemy, "activate": activate, "go_to": goto_id, "pressed_id": pressed_id_return, "add_to_friends": add_to_friends, "add_to_enemies": add_to_enemies })


def pve_game(data):
    global dices, pressed_id, who_is_moving_in_middle, flag_of_move, game_control, bot_goto, first_move_ower
    button_id = data.get("buttonId")
    dices_sum = dices.first_dice + dices.second_dice
    enemy = "pass"
    activate = "pass"
    goto_id = "pass"
    change = "pass"
    pressed_id_return = "pass"
    cell_list = list()
    add_to_friends = False
    add_to_enemies = False
    bot_should_move = False
    block = (dices.first_dice == 1) or (dices.second_dice) == 1 or not(data["bot"])

    if (0 <= int(button_id) <= 15):
        if (pressed_id == "-1"):
            if (0 <= int(top[button_id]) <= 15):
                enemy = True
                activate = click_handler(button_id, True, block)
            else:
                activate = False

            pressed_id = button_id

            if (game_control.enemies_first_move):
                game_control.enemies_first_move = False
                
                if (game_control.global_first_move):
                    game_control.friends_first_move = True
                    game_control.global_first_move = False

            delta = int(pressed_id) - dices_sum
            if (delta < 0):
                for cell in range(int(pressed_id) - 1, -1, -1):
                    cell_list.append(top[str(cell)])
                for cell in range(16, 16 + abs(delta)):
                    cell_list.append(middle[str(cell)])
                goto_id = str(15 + abs(delta))
            else:
                for cell in range(int(pressed_id) - 1, delta - 1, -1):
                    cell_list.append(top[str(cell)])
                goto_id = str(delta)

            pressed_id_return = pressed_id
            if (data["bot"]):
                bot_should_move = True

        else:
            if (pressed_id in top):
                check_goto = str(int(pressed_id) - dices_sum)
            else:
                check_goto = str(15 - (int(pressed_id) + dices_sum - 33))

            if (check_goto == button_id or flag_of_move):
                change = True
                flag_of_move = False

            pressed_id_return, pressed_id = pressed_id, "-1"  
            if (pressed_id_return not in top):
                top[button_id] = middle[pressed_id_return]
                middle[pressed_id_return] = "-1"
            else:
                top[button_id] = top[pressed_id_return]
                top[pressed_id_return] = "-1"


    elif (33 <= int(button_id) <= 48):
        if (pressed_id == "-1"):
            if (33 <= int(bottom[button_id]) <= 48):
                enemy = False
                activate = click_handler(button_id, False, block)
            else:
                activate = False
            
            pressed_id = button_id

            if (game_control.friends_first_move):
                game_control.friends_first_move = False

                if (game_control.global_first_move):
                    game_control.enemies_first_move = True
                    game_control.global_first_move = False

            delta = int(pressed_id) - dices_sum
            if (delta < 33):
                for cell in range(int(pressed_id) - 1, 32, -1):
                    cell_list.append(bottom[str(cell)])
                for cell in range(16, 16 + abs(delta - 33)):
                    cell_list.append(middle[str(cell)])
                goto_id = str(15 + abs(delta - 33))
            else:
                for cell in range(int(pressed_id) - 1, delta - 1, -1):
                    cell_list.append(bottom[str(cell)])
                goto_id = str(delta)
            pressed_id_return = pressed_id
            if (data["bot"]):
                bot_should_move = True

        else:
            if (pressed_id in bottom):
                delta = int(pressed_id) - dices_sum
                if (delta < 0):
                    check_goto = str(15 + abs(delta - 33))
                else:
                    check_goto = str(delta)

            else:
                check_goto = str(49 - abs(32 - (int(pressed_id) + dices_sum)))

            if (check_goto == button_id or flag_of_move):
                change = True
                flag_of_move = False

            pressed_id_return, pressed_id = pressed_id, "-1"  

            if (pressed_id_return not in bottom):
                bottom[button_id] = middle[pressed_id_return]
                middle[pressed_id_return] = "-1" 
            else:
                bottom[button_id] = bottom[pressed_id_return]
                bottom[pressed_id_return] = "-1"

    else:
        if (pressed_id != "-1"):
            if (pressed_id in middle):
                delta = int(pressed_id) + dices_sum
                if (delta > 32):
                    check_goto = str(15 - (delta - 33))
                else:
                    check_goto = str(delta)

            else:
                delta = int(pressed_id) - dices_sum
                if (0 <= int(pressed_id) <= 15):
                    check_goto = str(15 + abs(delta))
                else:
                    check_goto = str(15 + abs(delta - 33))

            if (check_goto == button_id or flag_of_move):
                change = True   

            pressed_id_return, pressed_id = pressed_id, "-1"
            if (pressed_id_return in middle):
                middle[button_id] = middle[pressed_id_return] 
                middle[pressed_id_return] = "-1"
            elif (pressed_id_return in top):
                middle[button_id] = top[pressed_id_return]
                top[pressed_id_return] = "-1"
            else:
                middle[button_id] = bottom[pressed_id_return]
                bottom[pressed_id_return] = "-1"

        else:
            delta = int(button_id) + dices_sum
            if (delta > 32):
                for cell in range(int(button_id) + 1, 33):
                    cell_list.append(middle[str(cell)])

                if (middle[button_id] in bottom):
                    for cell in range(15, 14 - (delta - 33), -1):
                        cell_list.append(top[str(cell)])
                    goto_id = str(15 - (delta - 33))
                else:
                    for cell in range(48, 47 - (delta - 33), -1):
                        cell_list.append(bottom[str(cell)])
                    goto_id = str(48 - (delta - 33))

            else:
                for cell in range(int(button_id) + 1, delta + 1):
                    cell_list.append(middle[str(cell)])
                goto_id = str(delta)

            pressed_id = button_id            
            pressed_id_return = button_id
            if (data["bot"]):
                bot_should_move = True
            
    if cell_list:
        if (pressed_id_return in top):
            for cell in cell_list:
                if ((cell in top and top[pressed_id_return] in top) or (cell in bottom and top[pressed_id_return] in bottom)):
                    goto_id = change_goto(goto_id, cell)
                    break
            if (goto_id in top):
                if (top[pressed_id_return] in top and top[goto_id] in bottom):
                    add_to_enemies = True
                elif (top[pressed_id_return] in bottom and top[goto_id] in top):
                    add_to_friends = True
            elif (goto_id in bottom):
                if (top[pressed_id_return] in top and bottom[goto_id] in bottom):
                    add_to_enemies = True
                elif (top[pressed_id_return] in bottom and bottom[goto_id] in top):
                    add_to_friends = True
            else:
                if (top[pressed_id_return] in top and middle[goto_id] in bottom):
                    add_to_enemies = True
                elif (top[pressed_id_return] in bottom and middle[goto_id] in top):
                    add_to_friends = True                   

        elif (pressed_id_return in middle):
            for cell in cell_list:
                if ((cell in top and middle[pressed_id_return] in top) or (cell in bottom and middle[pressed_id_return] in bottom)):
                    goto_id = change_goto(goto_id, cell)
                    break
            if (goto_id in top):
                if (middle[pressed_id_return] in top and top[goto_id] in bottom):
                    add_to_enemies = True
                elif (middle[pressed_id_return] in bottom and top[goto_id] in top):
                    add_to_friends = True
            elif (goto_id in bottom):
                if (middle[pressed_id_return] in top and bottom[goto_id] in bottom):
                    add_to_enemies = True
                elif (middle[pressed_id_return] in bottom and bottom[goto_id] in top):
                    add_to_friends = True
            else:
                if (middle[pressed_id_return] in top and middle[goto_id] in bottom):
                    add_to_enemies = True
                elif (middle[pressed_id_return] in bottom and middle[goto_id] in top):
                    add_to_friends = True   

        else:
            for cell in cell_list:
                if ((cell in top and bottom[pressed_id_return] in top) or (cell in bottom and bottom[pressed_id_return] in bottom)):
                    goto_id = change_goto(goto_id, cell)
                    break
            if (goto_id in top):
                if (bottom[pressed_id_return] in top and top[goto_id] in bottom):
                    add_to_enemies = True
                elif (bottom[pressed_id_return] in bottom and top[goto_id] in top):
                    add_to_friends = True 
            elif (goto_id in bottom):
                if (bottom[pressed_id_return] in top and bottom[goto_id] in bottom):
                    add_to_enemies = True
                elif (bottom[pressed_id_return] in bottom and bottom[goto_id] in top):
                    add_to_friends = True 
            else:
                if (bottom[pressed_id_return] in top and middle[goto_id] in bottom):
                    add_to_enemies = True
                elif (bottom[pressed_id_return] in bottom and middle[goto_id] in top):
                    add_to_friends = True     

    if activate:
        first_move_ower = True
        
    if bot_should_move:
        change = True
        pressed_id = "-1"
        if first_move_ower:
            activate = True
    return jsonify({ "change": change, "enemy": enemy, "activate": activate, "go_to": goto_id, "pressed_id": pressed_id_return, "add_to_friends": add_to_friends, "add_to_enemies": add_to_enemies, "bot_should_move": bot_should_move, "buttonId": button_id })


def click_handler(button_id, enemy, block):
    activate = False
    if not(block):
        return activate
    if enemy:
        chip_id = top[button_id]
    else:
        chip_id = bottom[button_id]

    if (chip_id != "-1"):
        if (chip_id in friends):
            if friends[chip_id] == "non-active":
                friends[chip_id] = "active"
                activate = True
        else:
            if enemies[chip_id] == "non-active":
                enemies[chip_id] = "active" 
                activate = True

    return activate


def change_goto(goto_id, cell):
    global flag_of_move
    index = "pass"

    for check_cell in top:
        if top[check_cell] == cell:
            index = check_cell
            break
    for check_cell in middle:
        if middle[check_cell] == cell:
            index = check_cell
            break
    for check_cell in bottom:
        if bottom[check_cell] == cell:
            index = check_cell
            break

    if (index in middle):
        if (index == "16"):
            goto_id = "33"
        else:
            goto_id = str(int(index) - 1)
    elif (index in top):
        if (index == "15"):
            goto_id = "32"
        else:
            goto_id = str(int(index) + 1)
    else:
        if (index == "48"):
            goto_id = "32"
        else:
            goto_id = str(int(index) + 1)

    flag_of_move = True

    return goto_id


if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=8000)