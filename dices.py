from random import randint


class Dices:
    def __init__(self):
        self.first_dice = 1
        self.second_dice = 1

    def roll_dices(self):
        self.first_dice, self.second_dice = randint(1, 4), randint(1, 4)