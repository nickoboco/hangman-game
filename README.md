# Web Hangman Game (Brazilian Portuguese)

This is a simple web-based Hangman game implemented using Python with the Flask framework. The game is played in Brazilian Portuguese and features category selection, a visual hangman drawing that updates with incorrect guesses, and an optional hint button.

## How to Play

1.  Start the application (see "How to Run" below).
2.  Open your web browser and navigate to the provided address (usually `http://127.0.0.1:5000/`).
3.  On the main page, select a word category to start a new game.
4.  Guess letters one by one to reveal the word.
5.  Each incorrect guess adds a part to the hangman drawing and reduces your attempts left.
6.  You win if you guess all the letters before the hangman is complete.
7.  You lose if the hangman is completed before you guess the word.
8.  You can use the "Dica" (Hint) button to reveal a random unguessed letter, but it costs one attempt.
9.  Click "Mudar Categoria / Reiniciar" or "Jogar Novamente" to start a new game or choose a different category.

## Features

*   Web interface using Flask and HTML/CSS/JavaScript.
*   Words grouped by categories.
*   Visual hangman drawing that updates based on incorrect guesses (using images).
*   Displays guessed letters and remaining attempts.
*   Game over states for win and lose.
*   Hint button (costs one attempt).
*   Automatic focus on the input field for faster gameplay.

## Prerequisites

*   Python 3.6+
*   pip (Python package installer)

## Setup and Installation

1.  **Clone or Download:** Get the project files and place them in a directory (e.g., `c:\hangman`).
2.  **Navigate to Project Directory:** Open your terminal or command prompt and go to the project directory:
    ```bash
    cd c:\hangman
    ```
3.  **Install Dependencies:** Install the required Python packages (Flask) using pip:
    ```bash
    pip install Flask
    ```
4.  **Prepare Word List:** Ensure you have the `words.txt` file in the project directory with words formatted as `CATEGORY:WORD`.
5.  **Prepare Hangman Images:** Create a `static` directory inside the project directory (`c:\hangman\static`). Place your hangman image files (`0.png`, `1.png`, `2.png`, `3.png`, `4.png`, `5.png`, `6.png`, `7.png`) inside the `static` directory. `0.png` is for the win state, `1.png` is the empty gallows (start), and `2.png` through `7.png` are the progressive stages of the hangman.

## How to Run

1.  Open your terminal or command prompt and navigate to the project directory (`c:\hangman`).
2.  Run the Flask application:
    ```bash
    python app.py
    ```
3.  The application will start, and you will see output indicating the server is running. By default, it runs on `http://127.0.0.1:5000/`.
4.  Open your web browser and go to `http://127.0.0.1:5000/` to play the game.

## Project Structure

```
c:\hangman\
├── app.py          # Flask application with game logic and routes
├── words.txt       # List of words by category
├── templates\
│   └── index.html  # HTML template for the game interface
└── static\
    ├── style.css   # CSS for styling the page
    ├── 0.png       # Hangman image for win state
    ├── 1.png       # Hangman image for empty gallows (start)
    ├── 2.png       # Hangman image (1 incorrect guess)
    ├── 3.png       # Hangman image (2 incorrect guesses)
    ├── 4.png       # Hangman image (3 incorrect guesses)
    ├── 5.png       # Hangman image (4 incorrect guesses)
    ├── 6.png       # Hangman image (5 incorrect guesses)
    └── 7.png       # Hangman image (6 incorrect guesses - lose)
```

## Customization

*   **Words:** Edit `words.txt` to add, remove, or change words and categories.
*   **Attempts:** Change the `MAX_ATTEMPTS` variable in `app.py` to adjust the difficulty. Make sure you have `MAX_ATTEMPTS + 1` hangman images (from index 0 to MAX_ATTEMPTS).
*   **Appearance:** Modify `static/style.css` to change the look and feel.
*   **Images:** Replace the images in the `static` folder with your own hangman drawings. Ensure they are named `0.png` through `7.png` (or adjust `HANGMAN_STAGES` in `app.py` accordingly).

Enjoy the game!
