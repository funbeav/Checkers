import pygame
import random
import main


def get_movement_sound():
    rnd = random.randint(1, 4)
    sound = pygame.mixer.Sound(f'Sounds/{rnd}.mp3')
    sound.set_volume(0.25)
    return sound


def get_config_info(param, file_name="Config.ini"):
    value = 0
    with open(file_name, 'r') as file:
        for line in file:
            line = line.split()
            if line[0] == param:
                value = int(line[2])
    return value


RESOLUTION = get_config_info('RESOLUTION') if get_config_info('RESOLUTION') != 0 else 720
FIELD_SIZE = get_config_info('FIELD_SIZE') if get_config_info('FIELD_SIZE') != 0 else 8
CIRCLE_WIDTH = 3
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (71, 71, 71)
GRAY = (190, 190, 190)
# BLACK = (0, 0, 0)
# RED = (255, 0, 0)
# GREEN = (0, 255, 0)
# BLUE = (0, 0, 255)
LIGHT_CELL = (232, 208, 170)
DARK_CELL = (166, 125, 93)

FONT_SIZE = RESOLUTION // FIELD_SIZE + FIELD_SIZE
CELL_SIZE = RESOLUTION // FIELD_SIZE

# Create Window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((RESOLUTION, RESOLUTION))
pygame.display.set_caption("Checkers")
pygame.display.set_icon(pygame.image.load("Icon.ico"))
clock = pygame.time.Clock()

field = main.Field(FIELD_SIZE)
player1 = main.Player(field, white=True)
player2 = main.Player(field, white=False)
current_player = player1

MAIN_FONT = pygame.font.SysFont('Arial Bold', FONT_SIZE)


def test():
    new_field = [[0 for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)]
    new_field[0][5] = 3
    new_field[5][4] = 2
    new_field[2][3] = 2
    new_field[1][2] = 2
    new_field[5][2] = 2
    # new_field[8][7] = 3
    field.field = new_field
    player1.get_checkers()
    player2.get_checkers()
# test()


# Game Loop
running = True
new_game_flag = False
quit_flag = False
next_turn_flag = False
menu_alpha = alpha = 255
new_game_color = quit_color = WHITE
while running:
    # Holding loop on correct speed
    clock.tick(FPS)

    # Render
    screen.fill(LIGHT_CELL)

    # Cells
    current_cell = LIGHT_CELL
    for i in range(0, RESOLUTION, RESOLUTION // FIELD_SIZE):
        current_cell = DARK_CELL if current_cell == LIGHT_CELL else LIGHT_CELL
        for j in range(0, RESOLUTION, RESOLUTION // FIELD_SIZE):
            current_cell = DARK_CELL if current_cell == LIGHT_CELL else LIGHT_CELL
            pygame.draw.rect(screen, current_cell, [i, j, i + RESOLUTION // FIELD_SIZE, j + RESOLUTION // FIELD_SIZE])

    # Draw the border
    border_coord = ((0, 0), (RESOLUTION - CIRCLE_WIDTH, 0),
                    (RESOLUTION - CIRCLE_WIDTH, RESOLUTION - CIRCLE_WIDTH), (0, RESOLUTION - CIRCLE_WIDTH))
    border_thickness = CIRCLE_WIDTH * 2
    pygame.draw.lines(screen, WHITE if current_player.white else BLACK, True, border_coord, border_thickness)

    # Menu Outdraw:
    # New Game Button
    new_game_text = MAIN_FONT.render('New Game', True, new_game_color)
    new_game_button = new_game_text.get_rect(
        center=(RESOLUTION // 2, RESOLUTION // 2 - (RESOLUTION // FIELD_SIZE // 2)))
    # Quit Button
    quit_text = MAIN_FONT.render('Quit', True, quit_color)
    quit_button = quit_text.get_rect(center=(RESOLUTION // 2, RESOLUTION // 2 + (RESOLUTION // FIELD_SIZE // 2)))

    # Menu is active
    if not new_game_flag and not quit_flag:
        screen.blit(new_game_text, new_game_button)
        screen.blit(quit_text, quit_button)

        # Selected option
        x, y = pygame.mouse.get_pos()
        if new_game_button.collidepoint(x, y):
            new_game_text = MAIN_FONT.render('New Game', True, BLACK)
        if quit_button.collidepoint(x, y):
            quit_text = MAIN_FONT.render('Quit', True, BLACK)

        screen.blit(new_game_text, new_game_button)
        screen.blit(quit_text, quit_button)

    # New Game Process
    if new_game_flag:
        # Update
        for i in range(0, FIELD_SIZE):
            for j in range(0, FIELD_SIZE):
                x = RESOLUTION // FIELD_SIZE * j + RESOLUTION // (FIELD_SIZE * 2)
                y = RESOLUTION // FIELD_SIZE * i + RESOLUTION // (FIELD_SIZE * 2)
                if [i, j] in current_player.already_attacked_enemies:
                    pygame.draw.circle(screen, GRAY, (x, y), RESOLUTION // (FIELD_SIZE / 0.4))
                if field.field[i][j] in (2, 4):
                    pygame.draw.circle(screen, BLACK, (x, y), RESOLUTION // (FIELD_SIZE / 0.4))
                    # Black King
                    if field.field[i][j] == 4:
                        pygame.draw.circle(screen, WHITE, (x, y), RESOLUTION // (FIELD_SIZE / 0.2), CIRCLE_WIDTH)
                elif field.field[i][j] in (1, 3):
                    pygame.draw.circle(screen, WHITE, (x, y), RESOLUTION // (FIELD_SIZE / 0.4))
                    # White King
                    if field.field[i][j] == 3:
                        pygame.draw.circle(screen, BLACK, (x, y), RESOLUTION // (FIELD_SIZE / 0.2), CIRCLE_WIDTH)

        # Select checker
        if current_player.chosen_checker:
            pos_x = current_player.chosen_checker.x * RESOLUTION // FIELD_SIZE + RESOLUTION // (FIELD_SIZE * 2)
            pos_y = current_player.chosen_checker.y * RESOLUTION // FIELD_SIZE + RESOLUTION // (FIELD_SIZE * 2)
            pygame.draw.circle(screen, BLACK if current_player == player1 else WHITE,
                               (pos_y, pos_x), RESOLUTION // (FIELD_SIZE / 0.4), CIRCLE_WIDTH)

    # Menu fading away
    if new_game_flag or quit_flag:
        if menu_alpha > 0:
            menu_alpha -= 10
            new_game_text.set_alpha(menu_alpha)
            quit_text.set_alpha(menu_alpha)
            screen.blit(new_game_text, new_game_button)
            screen.blit(quit_text, quit_button)
    if quit_flag and menu_alpha < 0:
        running = False

    # Event input
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

        # check if left mouse button is pressed
        clicked_color = ()
        if event.type == pygame.MOUSEBUTTONDOWN:

            # Menu
            if not new_game_flag:
                if new_game_button.collidepoint(event.pos):
                    new_game_flag = True
                    new_game_color = BLACK
                if quit_button.collidepoint(event.pos):
                    quit_flag = True
                    quit_color = BLACK
                    if menu_alpha < 0:
                        running = False

            clicked_color = screen.get_at(pygame.mouse.get_pos())

            clicked_x = int(pygame.mouse.get_pos()[1] / RESOLUTION * FIELD_SIZE)
            clicked_y = int(pygame.mouse.get_pos()[0] / RESOLUTION * FIELD_SIZE)

            if [clicked_x, clicked_y] in current_player.checkers:
                current_player.choose_checker(clicked_x, clicked_y)
            else:
                if current_player.chosen_checker:
                    go_try = current_player.move(clicked_x, clicked_y)
                    # End of turn
                    if go_try:
                        current_player = player2 if current_player == player1 else player1
                        get_movement_sound().play()
                        next_turn_flag = True
                    # Not finished turn
                    if current_player.chosen_checker:
                        if current_player.chosen_checker.x == clicked_x and \
                                current_player.chosen_checker.y == clicked_y:
                            get_movement_sound().play()

    # After outdrawing, flip display to show frame to user
    pygame.display.flip()

pygame.quit()
