import time
import playsound
import arcade
import random

from arcade import key

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Solitaire"

CARD_SCALE = 0.7
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

MAT_PERCENT = 1.25
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT)
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT)

VERTICAL_MARGIN_PERCENT = 0.1
HORIZONTAL_MARGIN_PERCENT = 0.1

TOP_Y = SCREEN_HEIGHT - CARD_HEIGHT / 2 - CARD_HEIGHT * VERTICAL_MARGIN_PERCENT
START_X = CARD_WIDTH / 2 + CARD_WIDTH * HORIZONTAL_MARGIN_PERCENT

TOP_CARD_Y = SCREEN_HEIGHT - CARD_HEIGHT / 2 - CARD_HEIGHT * VERTICAL_MARGIN_PERCENT * 2.5

TOP_TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

MIDDLE_Y = TOP_TOP_Y - MAT_HEIGHT - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

CARD_RANK = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
CARD_SUIT = ['Spades', 'Hearts', 'Diamonds', 'Clubs']

CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3
PILE_COUNT = 13
BOTTOM_FACE_DOWN_PILE = 0
BOTTOM_FACE_UP_PILE = 1
PLAY_PILE_1 = 2
PLAY_PILE_2 = 3
PLAY_PILE_3 = 4
PLAY_PILE_4 = 5
PLAY_PILE_5 = 6
PLAY_PILE_6 = 7
PLAY_PILE_7 = 8
TOP_PILE_1 = 9
TOP_PILE_2 = 10
TOP_PILE_3 = 11
TOP_PILE_4 = 12

FACE_DOWN_IMAGES = [":resources:images/cards/cardBack_red1.png", ":resources:images/cards/cardBack_red2.png",
                    ":resources:images/cards/cardBack_red3.png", ":resources:images/cards/cardBack_red4.png",
                    ":resources:images/cards/cardBack_red5.png", ":resources:images/cards/cardBack_green1.png",
                    ":resources:images/cards/cardBack_green2.png", ":resources:images/cards/cardBack_green3.png",
                    ":resources:images/cards/cardBack_green4.png", ":resources:images/cards/cardBack_green5.png",
                    ":resources:images/cards/cardBack_blue1.png", ":resources:images/cards/cardBack_blue2.png",
                    ":resources:images/cards/cardBack_blue3.png", ":resources:images/cards/cardBack_blue4.png",
                    ":resources:images/cards/cardBack_blue5.png"]

FACE_DOWN_INDEX = 0

SINGLE_CARD_DRAW = 1

SCORE = 0

background_music = arcade.Sound("Resources/music/backgroundMusic.mp3")
music_player = background_music.play(volume=0.5, loop=True)
music_playing = True

card_flip_sound = arcade.load_sound("Resources/soundfx/cardFlip.mp3")
card_drop_sound = arcade.load_sound("Resources/soundfx/dropCard.mp3")
sound_effects = True


# allows each card to be identified by an integer value to be used in pile logic.
def get_rank_number(rank):
    if rank == 'A':
        return 1
    elif rank == '2':
        return 2
    elif rank == '3':
        return 3
    elif rank == '4':
        return 4
    elif rank == '5':
        return 5
    elif rank == '6':
        return 6
    elif rank == '7':
        return 7
    elif rank == '8':
        return 8
    elif rank == '9':
        return 9
    elif rank == '10':
        return 10
    elif rank == 'J':
        return 11
    elif rank == 'Q':
        return 12
    elif rank == 'K':
        return 13


# Gets the color by the suit of a card passed at runtime.
def get_color_by_suit(suit):
    if suit == 'Hearts' or suit == 'Diamonds':
        print("The card is red.")
        return 'RED'
    elif suit == 'Spades' or suit == 'Clubs':
        print("The card is black.")
        return 'BLACK'


class Solitaire(arcade.Window):

    def __init__(self):

        print('__init__')
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.mat_colors = [arcade.color.BLEU_DE_FRANCE,
                           arcade.color.DARK_SPRING_GREEN,
                           arcade.color.CARNELIAN]

        self.mat_color_index = 0

        self.placeholder_colors = [arcade.csscolor.CORNFLOWER_BLUE, arcade.csscolor.DARK_OLIVE_GREEN,
                                   arcade.csscolor.ORANGE_RED]

        self.placeholder_color_index = 0

        self.placeholders = {}

        self.current_placeholder_color = self.placeholder_colors[self.placeholder_color_index]

        self.current_mat_color = self.mat_colors[self.mat_color_index]

        self.card_list = None

        arcade.set_background_color(self.current_mat_color)

        self.held_cards = None

        self.held_cards_original_position = None

        self.pile_mat_list = None

        self.piles = None

        # face-down items
        self.restricted_indices = {(7, 0), (6, 0), (6, 1), (5, 0), (5, 1), (5, 2),
                                   (4, 0), (4, 1), (4, 2), (4, 3), (3, 0), (3, 1),
                                   (3, 2), (3, 3), (3, 4), (2, 0), (2, 1), (2, 2),
                                   (2, 3), (2, 4), (2, 5)}

        self.action_stack = []

        self.last_clicked_card = None

        self.last_click_time = 0

        self.menu_overlay = MenuOverlay(200, 150, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.menu_active = False

        self.help_overlay = GameSummaryWindow(600, 400, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.help_active = False

    def setup(self, current_placeholder_color=None):
        print('setup')

        self.held_cards = []

        self.held_cards_original_position = []

        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # create an array which holds removed indices, combine it with self.restricted_indices
        self.restricted_indices = {(7, 0), (6, 0), (6, 1), (5, 0), (5, 1), (5, 2),
                                   (4, 0), (4, 1), (4, 2), (4, 3), (3, 0), (3, 1),
                                   (3, 2), (3, 3), (3, 4), (2, 0), (2, 1), (2, 2),
                                   (2, 3), (2, 4), (2, 5)}

        if current_placeholder_color is not None:
            placeholder_color = current_placeholder_color
        else:
            placeholder_color = self.current_placeholder_color

        for i in range(2):
            if i == 1 and SINGLE_CARD_DRAW == 3:  # Adjust the width of the right placeholder if dealing three cards
                pile = arcade.SpriteSolidColor(MAT_WIDTH + 40, MAT_HEIGHT,
                                               placeholder_color)
                pile.position = (START_X + i * X_SPACING + 20, TOP_TOP_Y)
            else:
                pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT,
                                               placeholder_color)
                pile.position = (START_X + i * X_SPACING, TOP_TOP_Y)

            self.pile_mat_list.append(pile)
        # Create placeholders for tableau piles
        for i in range(7):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, placeholder_color)
            pile.position = (SCREEN_WIDTH - CARD_WIDTH / 2 - CARD_WIDTH * HORIZONTAL_MARGIN_PERCENT - i * X_SPACING,
                             MIDDLE_Y)
            self.pile_mat_list.append(pile)
            self.placeholders[i + 1] = pile  # Store the pile sprite in the placeholders dictionary

        # Create placeholders for foundation piles
        for i in range(4):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, placeholder_color)
            pile.position = (SCREEN_WIDTH - CARD_WIDTH / 2 - CARD_WIDTH * HORIZONTAL_MARGIN_PERCENT - i * X_SPACING,
                             TOP_TOP_Y)
            self.pile_mat_list.append(pile)
            self.placeholders[i + 9] = pile  # Store the pile sprite in the placeholders dictionary

        self.card_list = arcade.SpriteList()

        for card_suit in CARD_SUIT:
            for card_rank in CARD_RANK:
                card = Card(card_rank, card_suit, CARD_SCALE)
                card.position = (START_X, TOP_CARD_Y)
                self.card_list.append(card)

        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list.swap(pos1, pos2)

        self.piles = [[] for _ in range(PILE_COUNT)]
        for card in self.card_list:
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)

        for pile_no in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            for j in range(7 - (pile_no - PLAY_PILE_1)):
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                self.piles[pile_no].append(card)
                card.position = (self.pile_mat_list[pile_no].center_x,
                                 self.pile_mat_list[pile_no].center_y - j * CARD_VERTICAL_OFFSET)
                self.pull_to_top(card)

            self.piles[pile_no][-1].face_up()

        for i in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            self.piles[i][-1].face_up()

    def on_draw(self):
        arcade.start_render()

        # call draw menu
        self.draw_game_menu()

        self.pile_mat_list.draw()
        for pile in self.piles:
            for card in pile:
                card.draw()

        draw_pile = self.piles[BOTTOM_FACE_UP_PILE]
        if SINGLE_CARD_DRAW == 3 and len(draw_pile) >= 3:
            for i, card in enumerate(draw_pile[-3:]):
                if card not in self.held_cards:
                    card.position = (START_X + CARD_WIDTH + 32 + i * 24, TOP_CARD_Y)
                card.draw()
        else:
            pass

        if SINGLE_CARD_DRAW == 3 and len(draw_pile) >= 3:
            # Update the position of the cards not visible in the draw pile
            for card in draw_pile[:-3]:
                card.position = (START_X + CARD_WIDTH + 32, TOP_CARD_Y)
        else:
            pass

        # Draw borders for each placeholder
        border_width = 2
        for i, pile in enumerate(self.pile_mat_list):
            draw_border = True

            if i == BOTTOM_FACE_UP_PILE and SINGLE_CARD_DRAW == 3:
                arcade.draw_rectangle_outline(
                    pile.center_x,
                    pile.center_y,
                    MAT_WIDTH + 34,
                    MAT_HEIGHT - border_width,
                    arcade.color.WHITE,
                    border_width
                )
            else:
                arcade.draw_rectangle_outline(
                    pile.center_x,
                    pile.center_y,
                    MAT_WIDTH - border_width,
                    MAT_HEIGHT - border_width,
                    arcade.color.WHITE,
                    border_width
                )

        self.card_list.draw()

        self.menu_overlay.draw()

        self.help_overlay.draw()

    def change_mat_color(self):
        try:
            self.mat_color_index = (self.mat_color_index + 1) % len(self.mat_colors)
            current_mat_color = self.mat_colors[self.mat_color_index]

            # Update background color
            arcade.set_background_color(current_mat_color)

            # Update mat colors
            for mat in self.pile_mat_list:
                mat.color = current_mat_color
        except Exception as e:
            print(f"An error occurred while changing mat colors: {e}")

    def change_placeholder_color(self):
        # Change the placeholder colors
        self.placeholder_color_index = (self.placeholder_color_index + 1) % len(self.placeholder_colors)
        current_placeholder_color = self.placeholder_colors[self.placeholder_color_index]

        # Update placeholder colors for draw pile placeholders
        for i in range(2):
            if i == 1 and SINGLE_CARD_DRAW == 3:  # Adjust the width of the right placeholder if dealing three cards
                self.pile_mat_list[i].color = current_placeholder_color
            else:
                self.pile_mat_list[i].color = current_placeholder_color

        # Update placeholder colors for tableau piles
        for pile_index in range(1, 8):
            if pile_index in self.placeholders:
                self.placeholders[pile_index].color = current_placeholder_color

        # Update placeholder colors for foundation piles
        for pile_index in range(TOP_PILE_1, TOP_PILE_4 + 1):
            if len(self.piles[pile_index]) == 0:
                self.placeholders[pile_index].color = current_placeholder_color
        self.draw_game_menu()

    def auto_flip_card(self):
        global SCORE

        for i in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            if len(self.piles[i]) > 0:
                top_card = self.piles[i][-1]
                if not top_card.is_face_up:
                    SCORE += 5
                    top_card.face_up()
                    # Check if the card is in restricted_indices and remove it
                    pile_idx = (i, len(self.piles[i]) - 1)
                    if pile_idx in self.restricted_indices:
                        self.restricted_indices.remove(pile_idx)

    def auto_stack_card(self, card):
        global sound_effects
        if card is None:
            return

        pile_index = self.get_pile_for_card(card)

        # Check if the card is face-up and at the top of its pile
        if not card.is_face_up or card != self.piles[pile_index][-1]:
            return
        if PLAY_PILE_1 <= pile_index <= PLAY_PILE_7:
            for top_pile_index in range(TOP_PILE_1, TOP_PILE_4 + 1):
                top_pile = self.piles[top_pile_index]
                if len(top_pile) == 0 and card.rank == 'A':
                    self.move_card_to_new_pile(card, top_pile_index)
                    if sound_effects:
                        card_drop_sound.play()
                    elif not sound_effects:
                        print("Sound effects are off right now.")
                    break
                elif len(top_pile) > 0 and top_pile[-1].suit == card.suit and get_rank_number(
                        top_pile[-1].rank) + 1 == get_rank_number(card.rank):
                    self.move_card_to_new_pile(card, top_pile_index)
                    if sound_effects:
                        card_drop_sound.play()
                    elif not sound_effects:
                        print("Sound effects are off right now.")
                    break

    def get_valid_top_pile_for_card(self, card):
        for i in range(TOP_PILE_1, TOP_PILE_4 + 1):
            top_pile = self.piles[i]
            if len(top_pile) == 0 and get_rank_number(card.rank) == 1:
                return i, None
            elif len(top_pile) > 0 and get_rank_number(top_pile[-1].rank) + 1 == get_rank_number(card.rank) and \
                    top_pile[-1].suit == card.suit:
                return i, top_pile[-1]
        return None, None

    def move_card_to_top_pile(self, card, top_pile):
        original_pile_index = self.get_pile_for_card(card)
        original_card_index = self.piles[original_pile_index].index(card)

        self.piles[original_pile_index].remove(card)
        self.piles[top_pile].append(card)

        card.position = self.pile_mat_list[top_pile].position

        if original_pile_index in range(PLAY_PILE_1, PLAY_PILE_7 + 1) and original_card_index > 0:
            below_card = self.piles[original_pile_index][original_card_index - 1]
            if (original_pile_index, original_card_index - 1) in self.restricted_indices:
                below_card.face_up()
                self.restricted_indices.remove((original_pile_index, original_card_index - 1))
            # if below_card.is_face_down:
            #     below_card.face_up()
            #     self.restricted_indices.remove((original_pile_index, original_card_index - 1))

    def on_mouse_press(self, x, y, button, key_modifiers):
        global SCORE, primary_card, sound_effects
        print('action: mouse "pressed"')
        self.auto_flip_card()

        # If the menu is open, only the menu button and the menu overlay are targetable
        if self.menu_overlay.visible:
            if button == arcade.MOUSE_BUTTON_LEFT:
                if SCREEN_WIDTH * 0.1 - SCREEN_WIDTH * 0.097 / 2 < x < SCREEN_WIDTH * 0.1 + \
                        SCREEN_WIDTH * 0.097 / 2 and \
                        SCREEN_HEIGHT * 0.5 - SCREEN_HEIGHT * 0.05 / 2 < y < SCREEN_HEIGHT * 0.5 + SCREEN_HEIGHT * 0.05 / 2:
                    # Draw menu overlay
                    print('draw_menu_overlay')
                    self.menu_overlay.toggle()
                    self.menu_active = not self.menu_active
                elif self.menu_overlay.contains_point(x, y):
                    print('menu_overlay clicked')
                    self.menu_overlay.handle_click(x, y)
            return

        # If the help overlay is open, only the help button is targetable
        if self.help_overlay.visible:
            if button == arcade.MOUSE_BUTTON_LEFT:
                if (
                        SCREEN_WIDTH * 0.1 - SCREEN_WIDTH * 0.097 / 2 < x < SCREEN_WIDTH * 0.1 + SCREEN_WIDTH * 0.097 / 2 and
                        SCREEN_HEIGHT * 0.4 - SCREEN_HEIGHT * 0.05 / 2 < y < SCREEN_HEIGHT * 0.4 + SCREEN_HEIGHT * 0.05 / 2):
                    # Help button clicked
                    print('help overlay')
                    self.help_overlay.toggle()
                    self.help_active = not self.help_active
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if SCREEN_WIDTH * 0.1 - SCREEN_WIDTH * 0.097 / 2 < x < SCREEN_WIDTH * 0.1 + \
                    SCREEN_WIDTH * 0.097 / 2 and \
                    SCREEN_HEIGHT * 0.6 - SCREEN_HEIGHT * 0.05 / 2 < y < SCREEN_HEIGHT * 0.6 + \
                    SCREEN_HEIGHT * 0.05 / 2:
                # Change Card Back button clicked
                print('card_back changed')
                self.change_card_back()
            elif SCREEN_WIDTH * 0.1 - SCREEN_WIDTH * 0.097 / 2 < x < SCREEN_WIDTH * 0.1 + \
                    SCREEN_WIDTH * 0.097 / 2 and \
                    SCREEN_HEIGHT * 0.7 - SCREEN_HEIGHT * 0.05 / 2 < y < SCREEN_HEIGHT * 0.7 + \
                    SCREEN_HEIGHT * 0.05 / 2:
                # Deal Three button clicked
                print('deal three')
                self.deal_three()
            elif SCREEN_WIDTH * 0.1 - SCREEN_WIDTH * 0.097 / 2 < x < SCREEN_WIDTH * 0.1 + \
                    SCREEN_WIDTH * 0.097 / 2 and \
                    SCREEN_HEIGHT * 0.3 - SCREEN_HEIGHT * 0.05 / 2 < y < SCREEN_HEIGHT * 0.3 + SCREEN_HEIGHT * 0.05 / 2:
                # Reset button clicked
                print('reset')
                self.reset()

            elif SCREEN_WIDTH * 0.1 - SCREEN_WIDTH * 0.097 / 2 < x < SCREEN_WIDTH * 0.1 + \
                    SCREEN_WIDTH * 0.097 / 2 and \
                    SCREEN_HEIGHT * 0.2 - SCREEN_HEIGHT * 0.05 / 2 < y < SCREEN_HEIGHT * 0.2 + SCREEN_HEIGHT * 0.05 / 2:
                # Quit button clicked
                print('quit')
                self.quit()

            elif SCREEN_WIDTH * 0.1 - SCREEN_WIDTH * 0.097 / 2 < x < SCREEN_WIDTH * 0.1 + \
                    SCREEN_WIDTH * 0.097 / 2 and \
                    SCREEN_HEIGHT * 0.5 - SCREEN_HEIGHT * 0.05 / 2 < y < SCREEN_HEIGHT * 0.5 + SCREEN_HEIGHT * 0.05 / 2:
                # Draw menu overlay
                print('draw_menu_overlay')
                self.menu_overlay.toggle()
                self.menu_active = not self.menu_active

            elif SCREEN_WIDTH * 0.1 - SCREEN_WIDTH * 0.097 / 2 < x < SCREEN_WIDTH * 0.1 + \
                    SCREEN_WIDTH * 0.097 / 2 and \
                    SCREEN_HEIGHT * 0.4 - SCREEN_HEIGHT * 0.05 / 2 < y < SCREEN_HEIGHT * 0.4 + \
                    SCREEN_HEIGHT * 0.05 / 2:
                # Change Mat Color button clicked
                print('help overlay')
                self.help_overlay.toggle()
                self.help_active = not self.help_active

        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        if len(cards) > 0:

            primary_card = cards[-1]
            assert isinstance(primary_card, Card)

            if primary_card in self.piles[BOTTOM_FACE_UP_PILE] and primary_card != self.piles[BOTTOM_FACE_UP_PILE][-1]:
                return

            current_click_time = time.time()
            if self.last_clicked_card == primary_card and current_click_time - self.last_click_time < 0.5:
                # Double-click detected+scoring
                valid_top_pile, is_play_pile = self.get_valid_top_pile_for_card(primary_card)
                if valid_top_pile is not None:
                    self.move_card_to_top_pile(primary_card, valid_top_pile)

                    if sound_effects:
                        card_drop_sound.play()
                    elif not sound_effects:
                        print("Sound effects are off right now.")
                    if is_play_pile:
                        SCORE += 10
                    else:
                        SCORE += 5
                    self.draw_game_menu()
                    return

            self.last_clicked_card = primary_card
            self.last_click_time = current_click_time

            pile_index = self.get_pile_for_card(primary_card)
            print("pile_index:", pile_index, 'card_index:', self.piles[pile_index].index(primary_card))

            if pile_index == BOTTOM_FACE_DOWN_PILE:
                # Flip one card
                for i in range(SINGLE_CARD_DRAW):
                    if len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                        break

                    card = self.piles[BOTTOM_FACE_DOWN_PILE][-1]

                    # Make sure all cards in BOTTOM_FACE_DOWN_PILE are face-down
                    if card.is_face_up and i < SINGLE_CARD_DRAW - 1:
                        card.face_down()

                    card.face_up()
                    card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position

                    # Apply horizontal offset if SINGLE_CARD_DRAW is set to 3
                    if SINGLE_CARD_DRAW == 3:
                        card.position = (card.position[0] + 20 * i, card.position[1])

                    self.piles[BOTTOM_FACE_DOWN_PILE].remove(card)
                    self.piles[BOTTOM_FACE_UP_PILE].append(card)

                    self.pull_to_top(card)

                if sound_effects:
                    card_flip_sound.play()
                elif not sound_effects:
                    print("Sound effects are off right now.")

            if TOP_PILE_1 <= pile_index <= TOP_PILE_4:
                return

            elif primary_card.is_face_down:

                try:
                    card_index = self.piles[pile_index].index(primary_card)
                except ValueError:
                    return

                # check if the card is in a restricted pile

                is_restricted_pile = (pile_index, card_index) in self.restricted_indices

                if is_restricted_pile:
                    print("is restricted pile")
                    # check if the card is the highest index in the pile

                    highest_index = max([idx for (row, idx) in self.restricted_indices if row == pile_index])

                    if card_index != highest_index:
                        print("Card not highest index")
                        return

                # check if the card is the highest index in the pile

                card_index = self.piles[pile_index].index(primary_card)

                is_primary_card = card_index == len(self.piles[pile_index]) - 1

                if is_primary_card or not is_restricted_pile:
                    print("247 IF passes")
                    # add the clicked card to the held_cards list

                    primary_card.face_up()

                    self.held_cards = [primary_card]

                    self.held_cards_original_position = [self.held_cards[0].position]

                    self.pull_to_top(self.held_cards[0])

                    print('discovering card -> 313')

                    # add any subsequent cards to the held_cards list

                    for i in range(card_index + 1, len(self.piles[pile_index])):
                        card = self.piles[pile_index][i]

                        self.held_cards.append(card)

                        self.held_cards_original_position.append(card.position)

                        self.pull_to_top(card)

                    if is_restricted_pile:
                        self.restricted_indices.remove((pile_index, card_index))

                else:
                    print("line 275 return")
                    return

        else:

            # Click on a mat instead of a card?
            mats = arcade.get_sprites_at_point((x, y), self.pile_mat_list)

            if len(mats) > 0:
                mat = mats[0]
                mat_index = self.pile_mat_list.index(mat)

                # Is it our turned over flip mat? and no cards on it?
                if mat_index == BOTTOM_FACE_DOWN_PILE and len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                    # Flip the deck back over so we can restart
                    temp_list = self.piles[BOTTOM_FACE_UP_PILE].copy()
                    for card in reversed(temp_list):
                        # Make sure all cards in BOTTOM_FACE_UP_PILE are face-up
                        if card.is_face_down and card != temp_list[-1]:
                            card.face_up()

                        card.face_down()
                        self.piles[BOTTOM_FACE_UP_PILE].remove(card)
                        self.piles[BOTTOM_FACE_DOWN_PILE].append(card)
                        card.position = self.pile_mat_list[BOTTOM_FACE_DOWN_PILE].position

                    # Handle the last card in the BOTTOM_FACE_UP_PILE
                    if len(self.piles[BOTTOM_FACE_UP_PILE]) > 0:
                        last_card = self.piles[BOTTOM_FACE_UP_PILE][-1]
                        if last_card.is_face_down:
                            last_card.face_up()
        # Just for troubleshooting, ignore
        # win condition
        # winning_condition = all(
        #     len(self.piles[pile_index]) == 13
        #     for pile_index in range(TOP_PILE_1, TOP_PILE_4 + 1)
        # )
        #
        # if winning_condition:
        #     self.card_dance()
        #
        #     # Wait for a click to start a new game
        #     self.reset()

        try:
            print('the card being clicked: ', primary_card.image_file_name)
        except UnboundLocalError as uble:
            print(uble)
            pass

        except Exception as e:
            print("An error occurred in the on_mouse_press method:")
            print(e)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        print('action: mouse "released"')
        global SCORE
        if len(self.held_cards) == 0:
            return

        _, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True

        for pile_index, current_pile in enumerate(self.piles):
            if len(current_pile) > 0:
                top_card = current_pile[-1]
            else:
                top_card = None

            if top_card is None or arcade.check_for_collision(self.held_cards[0], top_card):
                origin_pile_index = self.get_pile_for_card(self.held_cards[0])

                if pile_index == origin_pile_index:
                    pass

                # Check for PLAY_PILE
                elif PLAY_PILE_1 <= pile_index <= PLAY_PILE_7:
                    if top_card is not None and \
                            get_color_by_suit(top_card.suit) != get_color_by_suit(self.held_cards[0].suit) and \
                            (get_rank_number(self.held_cards[0].rank)) == (get_rank_number(top_card.rank) - 1):

                        for i, dropped_card in enumerate(self.held_cards):
                            dropped_card.position = top_card.center_x, \
                                top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)
                            reset_position = False

                        for card in self.held_cards:
                            self.move_card_to_new_pile(card, pile_index)

                    # Allow King piles to be moved to empty spaces
                    elif top_card is None and self.held_cards[0].rank == 'K':
                        for i, dropped_card in enumerate(self.held_cards):
                            dropped_card.position = self.pile_mat_list[pile_index].center_x, \
                                self.pile_mat_list[pile_index].center_y - CARD_VERTICAL_OFFSET * i
                            reset_position = False

                        for card in self.held_cards:
                            self.move_card_to_new_pile(card, pile_index)

                    if origin_pile_index == BOTTOM_FACE_UP_PILE:
                        SCORE += 5

                # Check for TOP_PILE
                elif TOP_PILE_1 <= pile_index <= TOP_PILE_4 and len(
                        self.held_cards) == 1:  # Ensure only one card is being held
                    if top_card is not None and self.held_cards[0].suit == top_card.suit \
                            and (get_rank_number(self.held_cards[0].rank)) == (get_rank_number(top_card.rank) + 1):
                        reset_position = False
                        for card in self.held_cards:
                            card.position = self.pile_mat_list[pile_index].center_x, self.pile_mat_list[
                                pile_index].center_y
                            self.move_card_to_new_pile(card, pile_index)
                            SCORE += 10
                            self.draw_game_menu()
                        print('Top Pile: Card placed')
                        break

                    elif top_card is None and self.held_cards[0].rank == 'A':
                        reset_position = False
                        for card in self.held_cards:
                            card.position = self.pile_mat_list[pile_index].center_x, self.pile_mat_list[
                                pile_index].center_y
                            self.move_card_to_new_pile(card, pile_index)
                            SCORE += 10
                            self.draw_game_menu()
                        print('Top Pile: Card placed')
                        break

        if reset_position:
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        self.auto_flip_card()

        # Call auto_stack_card if double-clicked
        if button == arcade.MOUSE_BUTTON_LEFT and modifiers & arcade.key.MOD_SHIFT:
            self.auto_stack_card(self.held_cards[0])

        # Clear the held_cards list
        self.held_cards = []

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):

        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def get_pile_for_card(self, card):

        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def remove_card_from_pile(self, card):

        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def move_card_to_new_pile(self, card, pile_index):

        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)

        print('11111111111111111111111111111111111')
        global sound_effects
        if sound_effects:
            card_drop_sound.play()
        elif not sound_effects:
            print("Sound effects are off right now.")

    def pull_to_top(self, card: arcade.Sprite):
        self.card_list.remove(card)
        self.card_list.append(card)

    def draw_game_menu(self):
        # Set the background color of the menu
        # Score display
        arcade.draw_text(
            f"SCORE: {SCORE}", SCREEN_WIDTH * 0.04, SCREEN_HEIGHT * 0.02,
            arcade.color.WHITE, font_size=12, anchor_x="center", anchor_y="bottom"
        )

        # Display game company and version information
        game_company = "The <<GAME>> Company"
        game_version = "Version 4.0.0"
        info_text = f"{game_company}, {game_version}"
        arcade.draw_text(
            info_text,
            SCREEN_WIDTH - 10, SCREEN_HEIGHT * 0.02,
            arcade.color.WHITE, font_size=10,
            anchor_x="right", anchor_y="bottom"
        )

        border_color = arcade.color.WHITE
        border_thickness = 2
        # Draw "Quit" button
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.2,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            self.placeholder_colors[self.placeholder_color_index]
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.2,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            border_color, border_thickness
        )
        arcade.draw_text(
            "QUIT", SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.2,
            arcade.color.WHITE, font_size=9, anchor_x="center", anchor_y="center"
        )

        arcade.draw_rectangle_filled(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.3,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            self.placeholder_colors[self.placeholder_color_index]
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.3,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            border_color, border_thickness
        )
        arcade.draw_text(
            "RESET", SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.3,
            arcade.color.WHITE, font_size=9, anchor_x="center", anchor_y="center"
        )

        if SINGLE_CARD_DRAW == 3:
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.7,
                SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
                arcade.color.FIREBRICK
            )
        else:
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.7,
                SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
                self.placeholder_colors[self.placeholder_color_index]
            )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.7,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            border_color, border_thickness
        )
        arcade.draw_text(
            "DEAL THREE", SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.7,
            arcade.color.WHITE, font_size=9, anchor_x="center", anchor_y="center"
        )

        # New card back
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.6,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            self.placeholder_colors[self.placeholder_color_index]
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.6,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            border_color, border_thickness
        )
        arcade.draw_text(
            "NEW CARD BACK", SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.6,
            arcade.color.WHITE, font_size=9, anchor_x="center", anchor_y="center"
        )
        menu_button_color = arcade.color.FIREBRICK if self.menu_active else \
            self.placeholder_colors[self.placeholder_color_index]
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.5,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            menu_button_color
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.5,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            border_color, border_thickness
        )
        arcade.draw_text(
            "SETTINGS", SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.5,
            arcade.color.WHITE, font_size=9, anchor_x="center", anchor_y="center"
        )

        help_button_color = arcade.color.FIREBRICK if self.help_active else \
            self.placeholder_colors[self.placeholder_color_index]
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.4,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            help_button_color
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.4,
            SCREEN_WIDTH * 0.097, SCREEN_HEIGHT * 0.05,
            border_color, border_thickness
        )
        arcade.draw_text(
            "HELP", SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.4,
            arcade.color.WHITE, font_size=9, anchor_x="center", anchor_y="center"
        )

    # Works fully
    def change_card_back(self):
        global FACE_DOWN_INDEX

        print(FACE_DOWN_INDEX)
        FACE_DOWN_INDEX += 1
        if FACE_DOWN_INDEX > 14:
            FACE_DOWN_INDEX = 0

        # Update all cards with the new card back, regardless of their current state
        for card in self.card_list:
            card.force_update_face_down_image(FACE_DOWN_INDEX)

    # Works
    def deal_three(self):
        global SINGLE_CARD_DRAW
        print(f'SINGLE_CARD_DRAW: {SINGLE_CARD_DRAW}')
        if SINGLE_CARD_DRAW == 1:
            print('three-handed activated -> game reset')
            SINGLE_CARD_DRAW = 3
            self.reset()
        else:
            print('one-handed activated -> game reset')
            SINGLE_CARD_DRAW = 1
            self.reset()
        self.draw_game_menu()

    # Works
    def reset(self):
        global SCORE
        SCORE = 0
        self.draw_game_menu()
        self.setup()

    # Works
    @staticmethod
    def quit():
        arcade.exit()

    def card_dance(self):
        for _ in range(100):  # You can adjust the number of "dance" steps
            for card in self.card_list:
                # Apply random movement to the card
                card.change_x = random.uniform(-5, 5)
                card.change_y = random.uniform(-5, 5)

            # Move the cards for a short period
            for _ in range(5):
                self.card_list.update()
                self.draw_game()
                arcade.pause(0.02)

            # Reset the card positions
            for card in self.card_list:
                card.change_x = 0
                card.change_y = 0


class MenuOverlay:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.visible = False
        self.music_on = True
        self.sound_fx_on = True

    def draw(self):
        if self.visible:
            arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, arcade.color.WHITE)
            arcade.draw_rectangle_outline(self.x, self.y, self.width, self.height, arcade.color.BLACK, 2)
            arcade.draw_text("SETTINGS", self.x, self.y + 35, arcade.color.BLACK, font_size=16, anchor_x="center")

            # Draw "Toggle Music" button
            # Draw "Toggle Sound FX" button
            arcade.draw_rectangle_outline(self.x, self.y,
                                          150, 30, arcade.color.BLACK, 2)
            arcade.draw_rectangle_filled(
                self.x, self.y,
                150, 30,
                arcade.color.DARK_OLIVE_GREEN if self.music_on else arcade.color.FIREBRICK
            )
            arcade.draw_text(
                "TOGGLE MUSIC", self.x, self.y,
                arcade.color.WHITE, font_size=10, anchor_x="center", anchor_y="center"
            )

            # Draw "Toggle Sound FX" button
            arcade.draw_rectangle_outline(self.x, self.y - 40,
                                          150, 30, arcade.color.BLACK, 2)
            arcade.draw_rectangle_filled(
                self.x, self.y - 40,
                150, 30,
                arcade.color.DARK_OLIVE_GREEN if self.sound_fx_on else arcade.color.FIREBRICK
            )
            arcade.draw_text(
                "TOGGLE SOUND FX", self.x, self.y - 40,
                arcade.color.WHITE, font_size=10, anchor_x="center", anchor_y="center"
            )

    def toggle(self):
        self.visible = not self.visible

    def handle_click(self, x, y):
        # Check if "Toggle Music" button is clicked
        if self.x - 75 <= x <= self.x + 75 and self.y - 15 <= y <= self.y + 15:
            self.music_on = not self.music_on
            print("Toggle Music")
            global music_playing
            global background_music
            global music_player

            if music_player.playing:
                music_player.pause()
                music_playing = False

            elif not music_player.playing:
                music_player.play()
                music_playing = True
                print("ELSE 911")

        # Check if "Toggle Sound FX" button is clicked
        elif self.x - 75 <= x <= self.x + 75 and self.y - 55 <= y <= self.y - 25:
            self.sound_fx_on = not self.sound_fx_on
            print("Toggle Sound FX")

            global sound_effects
            if sound_effects:
                sound_effects = False
            elif not sound_effects:
                sound_effects = True

    def contains_point(self, x, y):
        left = self.x - self.width / 2
        right = self.x + self.width / 2
        bottom = self.y - self.height / 2
        top = self.y + self.height / 2
        return left <= x <= right and bottom <= y <= top


class GameSummaryWindow:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.visible = False

    def draw(self):
        if self.visible:
            arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, arcade.color.WHITE)
            arcade.draw_rectangle_outline(self.x, self.y, self.width, self.height, arcade.color.BLACK, 2)
            arcade.draw_text("SOLITAIRE HELP", self.x, self.y + self.height / 2 - 30, arcade.color.BLACK, font_size=16,
                             anchor_x="center")

            # Add your game summary information here
            # Game summary information
            summary_text = [
                "",
                "Solitaire Rules:",
                "- The goal is to move all cards to the foundation piles.",
                "- Foundation piles are built up by suit from Ace to King.",
                "- The tableau piles are built down by alternating colors.",
                "- Only a King can be placed on an empty tableau pile.",
                "- You can draw cards from the stock pile to help.",
                "",
                "Scoring:",
                "- Moving a card from the stock to the tableau: 5 points.",
                "- Moving a card from the stock to the foundation: 10 points.",
                "- Moving a card from the tableau to the foundation: 10 points.",
                "- Turning over a card in the tableau: 5 points.",
                "",
                "For more information, please refer to the official rulebook which can be found here:",
                "",
                "https://bicyclecards.com/how-to-play/solitaire"
            ]

            line_height = 16
            horizontal_padding = (self.width - 20) / 2  # Adjust the padding to match the desired horizontal position
            for i, line in enumerate(summary_text):
                arcade.draw_text(
                    line,
                    self.x - horizontal_padding, self.y + self.height / 2 - 60 - i * line_height,
                    arcade.color.BLACK, font_size=10, anchor_x="left", anchor_y="top", align="left"
                )

    def toggle(self):
        self.visible = not self.visible

    def handle_click(self, x, y):
        # Check if "Close" button is clicked
        if self.x - 50 <= x <= self.x + 50 and self.y - self.height / 2 + 15 <= y <= self.y - self.height / 2 + 45:
            self.toggle()

    def contains_point(self, x, y):
        left = self.x - self.width / 2
        right = self.x + self.width / 2
        bottom = self.y - self.height / 2
        top = self.y + self.height / 2
        return left <= x <= right and bottom <= y <= top


class Card(arcade.Sprite):

    def __init__(self, rank, suit, scale):
        self.rank = rank
        self.suit = suit

        # Any expressions or variables enclosed in curly braces {}
        # within the string are evaluated and inserted into the string using the f-string
        # with the file path
        self.image_file_name = f':resources:images/cards/card{self.suit}{self.rank}.png'
        self.is_face_up = False
        self.face_down_image_index = FACE_DOWN_INDEX
        super().__init__(FACE_DOWN_IMAGES[self.face_down_image_index], scale=scale, hit_box_algorithm='None')

    def update_card_texture(self):
        if self.is_face_up:
            self.texture = arcade.load_texture(self.image_file_name)
        else:
            self.texture = arcade.load_texture(FACE_DOWN_IMAGES[FACE_DOWN_INDEX])

    def face_down(self):
        self.texture = arcade.load_texture(FACE_DOWN_IMAGES[self.face_down_image_index])
        self.is_face_up = False
        print('card is face-down')

    def face_up(self):
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True

    def is_face_down(self):
        return not self.is_face_up

    def update_face_down_image(self, index):
        self.face_down_image_index = index
        if not self.is_face_up:
            self.texture = arcade.load_texture(FACE_DOWN_IMAGES[self.face_down_image_index])

    def force_update_face_down_image(self, index):
        self.face_down_image_index = index
        if not self.is_face_up:
            self.texture = arcade.load_texture(FACE_DOWN_IMAGES[self.face_down_image_index])


def main():
    print('main')
    window = Solitaire()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
