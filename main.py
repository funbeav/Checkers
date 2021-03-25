class Field:
    def __init__(self, size=10):
        self.field = [[0 for _ in range(size)] for _ in range(size)]
        self.size = size

    def __str__(self):
        result = ''
        for row in self.field:
            result += " ".join(map(str, row)) + "\n"
        return result


class Checker:
    def __init__(self, field, x, y, white, king=False, already_attacked_enemies=None):
        if already_attacked_enemies is None:
            already_attacked_enemies = []
        self.field = field
        self.x, self.y = x, y
        self.white = white
        self.valid_steps = []
        self.valid_attacks = {}
        self.already_attacked_enemies = already_attacked_enemies

        # Fill simple Checker's valid actions
        enemy_checker = (2, 4) if white else (1, 3)
        allied_checker = (1, 3) if white else (2, 4)
        if not king:
            new_x = x - 1 if white else x + 1
            new_y_s = (y - 1, y + 1)
            # Valid actions forward
            for new_y in new_y_s:
                if new_x in range(0, field.size) and new_y in range(0, field.size):
                    # Valid movements forward
                    if field.field[new_x][new_y] == 0:
                        self.valid_steps.append([new_x, new_y])
                    # Valid attacks forward
                    if field.field[new_x][new_y] in enemy_checker:
                        attack_x = new_x - 1 if white else new_x + 1
                        attack_y = new_y + 1 if y < new_y else new_y - 1
                        if attack_x in range(0, field.size) and attack_y in range(0, field.size):
                            if field.field[attack_x][attack_y] == 0:
                                self.valid_attacks[(attack_x, attack_y)] = [new_x, new_y]
            # Valid attacks behind
            new_x = x + 1 if white else x - 1
            for new_y in new_y_s:
                if new_x in range(0, field.size) and new_y in range(0, field.size):
                    if field.field[new_x][new_y] in enemy_checker:
                        attack_x = new_x + 1 if white else new_x - 1
                        attack_y = new_y + 1 if y < new_y else new_y - 1
                        if attack_x in range(0, field.size) and attack_y in range(0, field.size):
                            if field.field[attack_x][attack_y] == 0:
                                self.valid_attacks[(attack_x, attack_y)] = [new_x, new_y]

        # For king
        if king:

            # Auxiliary generator
            def step_generator():
                options = [(1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
                for option in options:
                    yield option[0], option[1]

            new_x = x
            new_y = y
            reached_enemy = ()
            iter_step = step_generator()
            dx, dy = next(iter_step)
            while True:
                if dx == 0:
                    break
                new_x += dx
                new_y += dy
                stop_searching = False
                if new_x in range(0, field.size) and new_y in range(0, field.size):
                    # Turkish hit
                    if [new_x, new_y] in already_attacked_enemies:
                        stop_searching = True
                    if self.field.field[new_x][new_y] == 0 and not stop_searching:
                        if not reached_enemy:
                            self.valid_steps.append([new_x, new_y])
                        else:
                            self.valid_attacks[(new_x, new_y)] = reached_enemy
                    elif self.field.field[new_x][new_y] in allied_checker:
                        stop_searching = True

                    elif self.field.field[new_x][new_y] in enemy_checker:
                        if not reached_enemy:
                            reached_enemy = [new_x, new_y]
                        else:
                            stop_searching = True
                    if new_x == 0 or new_y == field.size - 1:
                        stop_searching = True
                else:
                    stop_searching = True
                if stop_searching:
                    dx, dy = next(iter_step)
                    reached_enemy = ()
                    new_x, new_y = x, y

        # If can attack forbid simple movements
        if self.valid_attacks:
            self.valid_steps = []


class Player:
    def __init__(self, field, white=True):
        self.field = field
        self.white = white
        self.chosen_checker = None
        self.checkers = []
        self.mandatory_attack = False
        self.there_are_attack_options = False
        self.already_attacked_enemies = []
        # Fill the table 'field' with Player's Checkers
        start, end = (field.size - (field.size // 3 + 1), field.size) if self.white else (0, field.size // 3 + 1)
        for i in range(start, end):
            for j in range(0, field.size):
                if (i + j) % 2 != 0:
                    self.field.field[i][j] = 1 if self.white else 2
        self.get_checkers()

    # Read checkers field and get Own Player's Checkers
    def get_checkers(self):
        self.checkers = []
        self.there_are_attack_options = False
        for i in range(0, self.field.size):
            for j in range(0, self.field.size):
                is_king = False
                allied_checker = (1, 3) if self.white else (2, 4)
                if self.field.field[i][j] in allied_checker:
                    self.checkers.append([i, j])
                    if self.field.field[i][j] in (3, 4):
                        is_king = True
                    tmp_checker = Checker(self.field, i, j, self.white, is_king)
                    if tmp_checker.valid_attacks:
                        self.there_are_attack_options = True

    # Choose checker from th field
    def choose_checker(self, x, y):
        # U can choose only if all Attacks are Done
        if not self.mandatory_attack:
            self.already_attacked_enemies = []
            self.get_checkers()
            if [x, y] in self.checkers:
                if self.field.field[x][y] in (3, 4):
                    self.chosen_checker = Checker(self.field, x, y, self.white, king=True)
                else:
                    self.chosen_checker = Checker(self.field, x, y, self.white)

    # Returns True if movement is ended, False - if movement unavailable or attack doesn't finished
    def move(self, x, y):
        # If checker doesn't chosen - skip action
        if not self.chosen_checker:
            return False

        # If there are movement options
        if [x, y] in self.chosen_checker.valid_steps and not self.there_are_attack_options:
            self.field.field[x][y] = self.field.field[self.chosen_checker.x][self.chosen_checker.y]
            self.field.field[self.chosen_checker.x][self.chosen_checker.y] = 0
            self.chosen_checker = None

            # Hit the kings
            if x == 0 and self.white:
                self.field.field[x][y] = 3
            if x == self.field.size - 1 and not self.white:
                self.field.field[x][y] = 4
        # If there are attack options
        elif (x, y) in self.chosen_checker.valid_attacks:
            self.field.field[x][y] = self.field.field[self.chosen_checker.x][self.chosen_checker.y]
            self.field.field[self.chosen_checker.x][self.chosen_checker.y] = 0

            # Hit the kings
            if x == 0 and self.white:
                self.field.field[x][y] = 3
            if x == self.field.size - 1 and not self.white:
                self.field.field[x][y] = 4

            # !!! Take enemy's checker
            enemy_x = self.chosen_checker.valid_attacks[(x, y)][0]
            enemy_y = self.chosen_checker.valid_attacks[(x, y)][1]
            self.already_attacked_enemies.append([enemy_x, enemy_y])
            self.field.field[enemy_x][enemy_y] = 0

            # If can attack more than 1 enemy checker
            self.mandatory_attack = False
            is_king = True if self.field.field[x][y] in (3, 4) else False
            self.chosen_checker = Checker(self.field, x, y, self.white, is_king, self.already_attacked_enemies)
            if self.chosen_checker.valid_attacks:
                self.mandatory_attack = True
                self.get_checkers()
                # Mandatory attack, move is not ended
                return False
            else:
                self.chosen_checker = None

            # Hit the kings
            if x == 0 and self.white:
                self.field.field[x][y] = 3
            if x == self.field.size - 1 and not self.white:
                self.field.field[x][y] = 4
        else:
            return False
        self.get_checkers()
        self.already_attacked_enemies = []
        return True


def main():
    field = Field()
    player1 = Player(field, white=True)
    player2 = Player(field, white=False)
    new_field = [[0 for _ in range(10)] for _ in range(10)]
    new_field[1][2] = 1
    new_field[8][7] = 2
    field.field = new_field
    print(field)

    player1.choose_checker(1, 2)
    player1.move(0, 1)

    player2.choose_checker(8, 7)
    player2.move(9, 6)

    print(field)


if __name__ == "__main__":
    main()
