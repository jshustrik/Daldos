class Game:
    def __init__(self):
        self.first_move = True
        self.friends_first_move = False
        self.enemies_first_move = False
        self.global_first_move = True
        self.move_owner = "friends"
        self.friends = dict()
        self.enemies = dict()
        self.neutral = dict()
        self.pressed_id = "-1"
        self.friends_score = 0
        self.enemies_score = 0

    def set_move(self):
        pass