from flask import Flask, render_template, request, redirect, url_for, session, jsonify # Import jsonify
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

# Hangman stages (list of image filenames)
# Index 0: 6 attempts left (0 incorrect) -> 1.png (empty gallows)
# Index 1: 5 attempts left (1 incorrect) -> 2.png (head)
# ...
# Index 6: 0 attempts left (6 incorrect) -> 7.png (full hangman)
HANGMAN_STAGES = [
    '1.png', # 0 incorrect guesses (6 attempts left)
    '2.png', # 1 incorrect guess (5 attempts left)
    '3.png', # 2 incorrect guesses (4 attempts left)
    '4.png', # 3 incorrect guesses (3 attempts left)
    '5.png', # 4 incorrect guesses (2 attempts left)
    '6.png', # 5 incorrect guesses (1 attempt left)
    '7.png'  # 6 incorrect guesses (0 attempts left) - Full hangman
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

    # Check if a game is in progress
    game_in_progress = 'word' in session and 'attempts_left' in session and 'guessed_letters' in session

    if game_in_progress:
        word = session['word']
        guessed_letters = session['guessed_letters']
        attempts_left = session['attempts_left']
        game_over, outcome = is_game_over(word, guessed_letters, attempts_left)

        # If game is over, clear session and show game over state via template
        if game_over:
            correct_word = session.get('word')
            outcome = is_game_over(correct_word, session.get('guessed_letters', []), session.get('attempts_left', 0))[1]

            # Determine the final hangman image based on outcome
            if outcome == 'win':
                final_hangman_image = '0.png' # Use 0.png for win
            else: # outcome == 'lose'
                final_hangman_image = HANGMAN_STAGES[MAX_ATTEMPTS] # Use 7.png for lose


            session.pop('word', None)
            session.pop('guessed_letters', None)
            session.pop('attempts_left', None)
            session.pop('category', None)
            return render_template('index.html',
                                   game_over=True,
                                   outcome=outcome,
                                   correct_word=correct_word,
                                   categories=sorted(words_by_category.keys()),
                                   hangman_image=final_hangman_image) # Pass final image filename

        # Game is in progress, render game template
        display_word = get_display_word(word, guessed_letters)
        hangman_index = MAX_ATTEMPTS - attempts_left
        current_hangman_image = HANGMAN_STAGES[hangman_index]

        return render_template('index.html',
                               display_word=display_word,
                               guessed_letters=sorted(guessed_letters),
                               attempts_left=attempts_left,
                               game_over=False, # Explicitly False when game is in progress
                               current_category=session.get('category'),
                               hangman_image=current_hangman_image) # Pass image filename


    # No game in progress, show category selection
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
        # If session is invalid, return an error or redirect (redirect is simpler for now)
        return jsonify({'error': 'Game not in progress'}), 400 # Return JSON error

    guess = request.form.get('letter', '').strip().upper()

    word = session['word']
    guessed_letters = session['guessed_letters']
    attempts_left = session['attempts_left']

    if len(guess) == 1 and guess.isalpha():
        if guess not in guessed_letters: # Only process if letter hasn't been guessed
            guessed_letters.append(guess)
            session['guessed_letters'] = guessed_letters

            if guess not in word:
                session['attempts_left'] -= 1
                attempts_left = session['attempts_left'] # Update local variable

    # Check if game is over after the guess
    game_over, outcome = is_game_over(word, guessed_letters, attempts_left)

    # Determine the hangman image for the response
    if game_over and outcome == 'win':
        response_hangman_image = '0.png' # Use 0.png for win in JSON response
    else:
        response_hangman_image = HANGMAN_STAGES[MAX_ATTEMPTS - attempts_left] # Use current stage or lose image

    # Prepare the response data
    response_data = {
        'display_word': get_display_word(word, guessed_letters),
        'guessed_letters': sorted(guessed_letters),
        'attempts_left': attempts_left,
        'game_over': game_over,
        'outcome': outcome,
        'hangman_image': response_hangman_image # Use the determined image
    }

    if game_over:
        response_data['correct_word'] = word
        # Clear session *after* getting correct_word for the response
        session.pop('word', None)
        session.pop('guessed_letters', None)
        session.pop('attempts_left', None)
        session.pop('category', None)
        # The index route will handle displaying the game over state on the next full load (e.g. restart)
        # But for the AJAX response, we provide the final state details.


    return jsonify(response_data) # Return JSON response

@app.route('/hint', methods=['POST'])
def hint():
    # Ensure game state exists before processing hint
    if 'word' not in session or 'guessed_letters' not in session or 'attempts_left' not in session:
        return jsonify({'error': 'Game not in progress'}), 400

    word = session['word']
    guessed_letters = session['guessed_letters']
    attempts_left = session['attempts_left']

    # Check if game is already over or no attempts left
    game_over, outcome = is_game_over(word, guessed_letters, attempts_left)
    if game_over:
         return jsonify({'error': 'Game is already over'}), 400

    # Find unguessed letters
    unguessed_letters = [letter for letter in word if letter not in guessed_letters]

    if not unguessed_letters:
        # All letters are already guessed (shouldn't happen if game_over is False, but good check)
        # Recalculate game_over state to ensure it's 'win' if all letters are now guessed
        game_over, outcome = is_game_over(word, guessed_letters, attempts_left)
        if game_over and outcome == 'win':
             # If winning by getting the last letter via hint, proceed to game over logic below
             pass
        else:
             return jsonify({'message': 'No unguessed letters left'}), 200 # Or maybe 400?

    else: # There are unguessed letters, provide a hint
        # Choose a random unguessed letter
        hint_letter = random.choice(unguessed_letters)

        # Add the hint letter to guessed letters
        guessed_letters.append(hint_letter)
        session['guessed_letters'] = guessed_letters

        # Decrease attempts for using a hint
        session['attempts_left'] -= 1
        attempts_left = session['attempts_left'] # Update local variable

        # Check if game is over after the hint
        game_over, outcome = is_game_over(word, guessed_letters, attempts_left)


    # Determine the hangman image for the response
    if game_over and outcome == 'win':
        response_hangman_image = '0.png' # Use 0.png for win in JSON response
    else:
        response_hangman_image = HANGMAN_STAGES[MAX_ATTEMPTS - attempts_left] # Use current stage or lose image


    # Prepare the response data
    response_data = {
        'display_word': get_display_word(word, guessed_letters),
        'guessed_letters': sorted(guessed_letters),
        'attempts_left': attempts_left,
        'game_over': game_over,
        'outcome': outcome,
        'hangman_image': response_hangman_image # Use the determined image
    }

    if game_over:
        response_data['correct_word'] = word
        # Clear session *after* getting correct_word for the response
        session.pop('word', None)
        session.pop('guessed_letters', None)
        session.pop('attempts_left', None)
        session.pop('category', None)

    return jsonify(response_data)


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
