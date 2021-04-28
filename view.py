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
new_game_flag = quit_flag = next_turn_flag = end_game_flag = False
menu_alpha_max, rect_alpha_max = (255, 40)
rect_alpha = rect_alpha_max
menu_alpha = menu_alpha_max
alpha_step_fast = 20
alpha_step_slow = 5
new_game_color = quit_color = end_game_color = WHITE
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
    border_coord = ((0, 0), (RESOLUTION, 0),
                    (RESOLUTION, RESOLUTION), (0, RESOLUTION))
    border_thickness = CIRCLE_WIDTH * 2
    border_color = WHITE if current_player.white else BLACK
    if end_game_flag:
        border_color = WHITE if not current_player.white else BLACK
    pygame.draw.lines(screen, border_color, True, border_coord, border_thickness)

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

    # Draw transparent Rect
    transparent_black = BLACK + (rect_alpha,)
    rect_coord = [0, 0, RESOLUTION, RESOLUTION]
    shape_surf = pygame.Surface(pygame.Rect(rect_coord).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, transparent_black, shape_surf.get_rect())

    # New Game Button Description
    new_game_text = MAIN_FONT.render('New Game', True, new_game_color)
    new_game_button = new_game_text.get_rect(
        center=(RESOLUTION // 2, RESOLUTION // 2 - (RESOLUTION // FIELD_SIZE // 2)))

    # Quit Button Description
    quit_text = MAIN_FONT.render('Quit', True, quit_color)
    quit_button = quit_text.get_rect(center=(RESOLUTION // 2, RESOLUTION // 2 + (RESOLUTION // FIELD_SIZE // 2)))

    # End game Button Description
    if current_player.white:
        winner_text, end_game_color = ('Black', BLACK)
    else:
        winner_text, end_game_color = ('White', WHITE)
    end_game_text = MAIN_FONT.render(f'{winner_text} wins!', True, end_game_color)
    end_game_button = end_game_text.get_rect(center=(RESOLUTION // 2, RESOLUTION // 2))

    # If menu is active
    if not new_game_flag and not quit_flag:
        # Selected option
        x, y = pygame.mouse.get_pos()
        if new_game_button.collidepoint(x, y):
            new_game_text = MAIN_FONT.render('New Game', True, BLACK)
        if quit_button.collidepoint(x, y):
            quit_text = MAIN_FONT.render('Quit', True, BLACK)

        # Draw transparent rectangle
        screen.blit(shape_surf, rect_coord)
        # Draw options
        screen.blit(new_game_text, new_game_button)
        screen.blit(quit_text, quit_button)

    # If there is no any steps available (Game is finished)
    if end_game_flag:
        # Slowly show transparent rectangle
        if rect_alpha < rect_alpha_max:
            rect_alpha += alpha_step_slow
        screen.blit(shape_surf, rect_coord)

        # Define winner's label
        x, y = pygame.mouse.get_pos()
        end_game_text = MAIN_FONT.render(f'{winner_text} wins!', True, end_game_color)
        end_game_button = end_game_text.get_rect(center=(RESOLUTION // 2, RESOLUTION // 2))
        if end_game_button.collidepoint(x, y):
            end_game_text = MAIN_FONT.render(f'{winner_text} wins!', True,
                                             WHITE if end_game_color == BLACK else BLACK)

        # Slowly fade back menu
        if menu_alpha < menu_alpha_max:
            menu_alpha += alpha_step_fast
        end_game_text.set_alpha(menu_alpha)
        screen.blit(end_game_text, end_game_button)

    # Labels fading away (if clicked new_game or quit and not game_ended)
    if (new_game_flag or quit_flag) and not end_game_flag:
        # Menu options are fading away
        if menu_alpha > alpha_step_fast:
            # set new alpha level
            new_game_text.set_alpha(menu_alpha)
            quit_text.set_alpha(menu_alpha)
            # draw menu labels
            screen.blit(new_game_text, new_game_button)
            screen.blit(quit_text, quit_button)
            menu_alpha -= alpha_step_fast
        # Transparent rectangle is fading away
        if new_game_flag and rect_alpha > alpha_step_slow:
            screen.blit(shape_surf, rect_coord)
            rect_alpha -= alpha_step_slow
        # Do not fade away transparent rectangle, if quit
        if quit_flag:
            screen.blit(shape_surf, rect_coord)
    # When menu options faded away (menu_alpha ~= 0), close Application
    if quit_flag and menu_alpha < alpha_step_fast + 1:
        running = False

    # Event input
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

        # check if left mouse button is pressed
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Menu
            if not new_game_flag and not quit_flag:
                # clicked new game
                if new_game_button.collidepoint(event.pos):
                    get_movement_sound().play()
                    new_game_flag = True
                    new_game_color = BLACK
                # clicked quit
                if quit_button.collidepoint(event.pos):
                    get_movement_sound().play()
                    quit_flag = True
                    quit_color = BLACK
                    if menu_alpha < alpha_step_fast + 1:
                        running = False
            if end_game_flag:
                if end_game_button.collidepoint(event.pos):
                    get_movement_sound().play()
                    end_game_flag = new_game_flag = quit_flag = False
                    new_game_color = quit_color = WHITE
                    menu_alpha = menu_alpha_max

                    field = main.Field(FIELD_SIZE)
                    player1 = main.Player(field, white=True)
                    player2 = main.Player(field, white=False)
                    current_player = player1

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
                        # if there is no options to move
                        if not current_player.get_checkers():
                            end_game_flag = True
                    # Not finished turn
                    if current_player.chosen_checker:
                        if current_player.chosen_checker.x == clicked_x and \
                                current_player.chosen_checker.y == clicked_y:
                            get_movement_sound().play()

    # After outdrawing, flip display to show frame to user
    pygame.display.flip()

pygame.quit()
