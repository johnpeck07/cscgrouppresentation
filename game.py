import pygame
import random
import string

pygame.init()

# ---------------------------------
# Window Setup
# ---------------------------------
WIDTH, HEIGHT = 900, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Puzzle Game - Pygame Version")

FONT = pygame.font.SysFont("arial", 32)
LARGE_FONT = pygame.font.SysFont("arial", 48)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (190, 190, 190)
BLUE = (80, 160, 255)
GREEN = (80, 250, 120)
RED = (255, 80, 80)


# ---------------------------------
# Player Class
# ---------------------------------
class Player:
    def __init__(self):
        self.lives = 5
        self.current_level = 1
        self.errors = 0

    def lose_life(self):
        self.lives -= 1
        self.errors = 0

    def reset_errors(self):
        self.errors = 0


# ---------------------------------
# Score Class
# ---------------------------------
class Score:
    def __init__(self):
        self.points = 0

    def add_correct(self):
        self.points += 10

    def add_incorrect(self):
        self.points -= 10

    def level_complete(self):
        self.points += 100

    def bonus_win(self):
        self.points += 500


# ---------------------------------
# Puzzle Class
# ---------------------------------
class Puzzle:
    def __init__(self, sentence):
        self.original_sentence = sentence
        self.display_sentence = self._remove_letters(sentence)

    def _remove_letters(self, s):
        out = ""
        for ch in s:
            if ch.isalpha() and random.random() < 0.45:
                out += "_"
            else:
                out += ch
        return out

    def reveal(self, letter):
        new_text = ""
        found = False

        for orig, disp in zip(self.original_sentence, self.display_sentence):
            if orig.lower() == letter and disp == "_":
                new_text += orig
                found = True
            else:
                new_text += disp

        self.display_sentence = new_text
        return found

    def completed(self):
        return self.display_sentence == self.original_sentence


# ---------------------------------
# Puzzle Generator
# ---------------------------------
class PuzzleGenerator:
    SENTENCES = [
        "The cat jumped over the fence",
        "Learning Python is very fun",
        "Always follow your dreams",
        "Practice makes perfect",
        "Never give up on yourself",
        "The quick brown fox jumps high",
        "Success comes from hard work",
        "Believe in the power of words",
        "A journey begins with a step",
        "Knowledge is a lifelong gift"
    ]

    def generate_puzzle(self, level):
        return Puzzle(random.choice(self.SENTENCES))


# ---------------------------------
# Keyboard Button Class
# ---------------------------------
class LetterButton:
    def __init__(self, letter, x, y):
        self.letter = letter
        self.rect = pygame.Rect(x, y, 50, 50)
        self.clicked = False

    def draw(self, win):
        color = GRAY if self.clicked else BLUE
        pygame.draw.rect(win, color, self.rect)
        txt = FONT.render(self.letter.upper(), True, WHITE)
        win.blit(txt, (self.rect.x + 15, self.rect.y + 10))

    def click(self, pos):
        if self.rect.collidepoint(pos) and not self.clicked:
            self.clicked = True
            return True
        return False


# ---------------------------------
# Game Manager
# ---------------------------------
class Game:
    def __init__(self):
        self.player = Player()
        self.score = Score()
        self.generator = PuzzleGenerator()
        self.puzzle = self.generator.generate_puzzle(1)
        self.keyboard = self.build_keyboard()
        self.running = True
        self.message = ""

    def build_keyboard(self):
        keys = []
        start_x = 80
        start_y = 400

        for i, letter in enumerate(string.ascii_lowercase):
            x = start_x + (i % 13) * 60
            y = start_y + (i // 13) * 70
            keys.append(LetterButton(letter, x, y))
        return keys

    def draw(self):
        WIN.fill(WHITE)

        # Display puzzle
        sen = LARGE_FONT.render(self.puzzle.display_sentence, True, BLACK)
        WIN.blit(sen, (50, 100))

        # Display stats
        stats = FONT.render(
            f"Lives: {self.player.lives}   Errors: {self.player.errors}/3   Score: {self.score.points}",
            True, BLACK
        )
        WIN.blit(stats, (50, 20))

        # Display message
        if self.message:
            msg = FONT.render(self.message, True, RED if "Incorrect" in self.message else GREEN)
            WIN.blit(msg, (50, 160))

        # Draw keyboard
        for key in self.keyboard:
            key.draw(WIN)

        pygame.display.update()

    def check_letter(self, letter):
        if self.puzzle.reveal(letter):
            self.score.add_correct()
            self.message = "Correct!"
        else:
            self.score.add_incorrect()
            self.player.errors += 1
            self.message = "Incorrect!"

            if self.player.errors >= 3:
                self.player.lose_life()
                if self.player.lives == 0:
                    self.game_over()
                else:
                    self.message = "Lost a life! New puzzle..."
                    self.puzzle = self.generator.generate_puzzle(self.player.current_level)
                    self.keyboard = self.build_keyboard()

    def next_level(self):
        self.score.level_complete()
        self.player.current_level += 1
        self.player.reset_errors()

        if self.player.current_level > 10:
            self.score.bonus_win()
            self.win_game()
        else:
            self.puzzle = self.generator.generate_puzzle(self.player.current_level)
            self.keyboard = self.build_keyboard()
            self.message = f"Level {self.player.current_level}!"

    def game_over(self):
        self.running = False
        WIN.fill(WHITE)
        msg = LARGE_FONT.render("GAME OVER", True, RED)
        WIN.blit(msg, (300, 250))
        pygame.display.update()
        pygame.time.delay(2500)

    def win_game(self):
        self.running = False
        WIN.fill(WHITE)
        msg = LARGE_FONT.render("YOU WIN!", True, GREEN)
        WIN.blit(msg, (320, 250))
        score_msg = FONT.render(f"Final Score: {self.score.points}", True, BLACK)
        WIN.blit(score_msg, (350, 320))
        pygame.display.update()
        pygame.time.delay(3000)

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    for key in self.keyboard:
                        if key.click(pos):
                            self.check_letter(key.letter)

            # Check for puzzle completion
            if self.puzzle.completed():
                self.message = "Level Complete!"
                pygame.display.update()
                pygame.time.delay(800)
                self.next_level()

            self.draw()


# ---------------------------------
# Run Game
# ---------------------------------
if __name__ == "__main__":
    Game().run()
    pygame.quit()
