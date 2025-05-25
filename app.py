from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key' # Change this to a random secret key

# Load words from the file, grouped by category
def load_words():
    words_by_category = {}
    try:
        with open('words.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    category, word = line.split(':', 1)
                    category = category.strip().upper()
                    word = word.strip().upper()
                    if category and word:
                        if category not in words_by_category:
                            words_by_category[category] = []
                        words_by_category[category].append(word)
        return words_by_category
    except FileNotFoundError:
        print("Error: words.txt not found.")
        return {}

words_by_category = load_words()
MAX_ATTEMPTS = 6

# Hangman stages (from empty gallows to full hangman)
# Index 0: 6 attempts left (0 incorrect)
# Index 1: 5 attempts left (1 incorrect)
# ...
# Index 6: 0 attempts left (6 incorrect)
HANGMAN_STAGES = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========
    """, # 0 incorrect guesses (6 attempts left)
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    """, # 1 incorrect guess (5 attempts left)
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    """, # 2 incorrect guesses (4 attempts left)
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========
    """, # 3 incorrect guesses (3 attempts left)
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========
    """, # 4 incorrect guesses (2 attempts left)
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========
    """, # 5 incorrect guesses (1 attempt left)
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========
    """ # 6 incorrect guesses (0 attempts left) - Full hangman
]


def start_new_game(category=None):
    if not words_by_category:
        return False # No words loaded

    if category and category in words_by_category and words_by_category[category]:
        word = random.choice(words_by_category[category])
        session['category'] = category
        session['word'] = word
        session['guessed_letters'] = []
        session['attempts_left'] = MAX_ATTEMPTS
        return True
    elif not category and words_by_category:
         # If no category specified, pick a random one (optional, or force selection)
         # For now, let's just return False to force category selection
         return False
    else:
        return False # Category not found or empty

def get_display_word(word, guessed_letters):
    display = ''
    for letter in word:
        if letter in guessed_letters:
            display += letter
        else:
            display += '_'
        display += ' '
    return display.strip()

def is_game_over(word, guessed_letters, attempts_left):
    if attempts_left <= 0:
        return True, 'lose'
    if all(letter in guessed_letters for letter in word):
        return True, 'win'
    return False, None

@app.route('/')
def index():
    if not words_by_category:
        return "Erro: Lista de palavras vazia ou não encontrada.", 500

    # Check if a game is in progress and not over
    game_in_progress = 'word' in session and 'attempts_left' in session and 'guessed_letters' in session
    if game_in_progress:
        word = session['word']
        guessed_letters = session['guessed_letters']
        attempts_left = session['attempts_left']
        game_over, outcome = is_game_over(word, guessed_letters, attempts_left)

        if not game_over:
             display_word = get_display_word(word, guessed_letters)
             # Calculate hangman stage index (0 is empty gallows, MAX_ATTEMPTS is full)
             hangman_index = MAX_ATTEMPTS - attempts_left
             current_hangman = HANGMAN_STAGES[hangman_index]

             return render_template('index.html',
                                   display_word=display_word,
                                   guessed_letters=sorted(guessed_letters),
                                   attempts_left=attempts_left,
                                   game_over=False,
                                   current_category=session.get('category'),
                                   hangman_drawing=current_hangman) # Pass hangman drawing
        else:
            # Game is over, clear session and show result/restart option
            correct_word = session.get('word')
            outcome = is_game_over(correct_word, session.get('guessed_letters', []), session.get('attempts_left', 0))[1] # Recalculate outcome
            # Show empty gallows on win (index 0), full hangman on lose (index MAX_ATTEMPTS)
            # MAX_ATTEMPTS is now a valid index for the full hangman stage
            final_hangman = HANGMAN_STAGES[0] if outcome == 'win' else HANGMAN_STAGES[MAX_ATTEMPTS]

            session.pop('word', None)
            session.pop('guessed_letters', None)
            session.pop('attempts_left', None)
            session.pop('category', None)
            return render_template('index.html',
                                   game_over=True,
                                   outcome=outcome,
                                   correct_word=correct_word,
                                   categories=sorted(words_by_category.keys()),
                                   hangman_drawing=final_hangman) # Pass final hangman drawing


    # No game in progress or game just ended, show category selection
    session.pop('word', None) # Ensure old game state is cleared
    session.pop('guessed_letters', None)
    session.pop('attempts_left', None)
    session.pop('category', None)
    return render_template('index.html', categories=sorted(words_by_category.keys()))

@app.route('/start', methods=['POST'])
def start_game_route():
    if not words_by_category:
         return "Erro: Lista de palavras vazia ou não encontrada.", 500

    selected_category = request.form.get('category')
    if start_new_game(selected_category):
        return redirect(url_for('index'))
    else:
        # Handle case where category is invalid or empty
        return render_template('index.html',
                               categories=sorted(words_by_category.keys()),
                               error="Selecione uma categoria válida.")


@app.route('/guess', methods=['POST'])
def guess():
    # Ensure game state exists before processing guess
    if 'word' not in session or 'guessed_letters' not in session or 'attempts_left' not in session:
        return redirect(url_for('index')) # Redirect to index if session is not set up

    guess = request.form.get('letter', '').strip().upper()

    if len(guess) == 1 and guess.isalpha():
        guessed_letters = session['guessed_letters']
        word = session['word']

        if guess not in guessed_letters: # Only process if letter hasn't been guessed
            guessed_letters.append(guess)
            session['guessed_letters'] = guessed_letters

            if guess not in word:
                session['attempts_left'] -= 1

    # Check if game is over after the guess
    game_over, outcome = is_game_over(session['word'], session['guessed_letters'], session['attempts_left'])
    if game_over:
        # Redirect to index, which will handle displaying the game over state
        return redirect(url_for('index'))

    # Game is not over, redirect back to the game page
    return redirect(url_for('index'))

@app.route('/restart')
def restart():
    # Redirect to index, which will show category selection
    session.pop('word', None)
    session.pop('guessed_letters', None)
    session.pop('attempts_left', None)
    session.pop('category', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    # In a real application, use a production-ready server like Gunicorn or uWSGI
    app.run(debug=True)
