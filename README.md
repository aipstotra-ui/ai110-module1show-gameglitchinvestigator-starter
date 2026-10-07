# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **The game's purpose.** A Streamlit number-guessing game. The app picks a secret number in a range set by the difficulty (Easy 1–20, Normal 1–100, Hard 1–200). You get a limited number of guesses (6 / 8 / 5), each guess gets a "too high / too low" hint, and your score starts at 100 for a first-guess win, dropping by 10 for each extra guess and by 5 for each miss.
- [x] **Bugs I found** (full reproduction log in [reflection.md](reflection.md)):
  1. Hints were backwards: a guess above the secret said "Go HIGHER!".
  2. On every even attempt the secret was turned into a string, so `"9" > "50"` was compared as text and the hint was wrong.
  3. New Game never reset `status`, `score`, or `history`, so after a win or loss the game stayed stuck on "You already won".
  4. Attempts started at 1 (Normal gave 7 guesses, not 8), and "Attempts left" lagged one guess behind and always said "1 and 100".
  5. Hard (1–50) was easier than Normal, a wrong "Too High" guess could *gain* points, invalid input used up an attempt, and the starter tests compared a tuple to a string.
- [x] **Fixes I applied:**
  - Moved `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` into `logic_utils.py`; `app.py` now only imports and renders.
  - `check_guess` returns the right message for each direction and only compares numbers (removed the `str()` cast in `app.py` and the `except TypeError` string fallback).
  - One `start_new_game()` helper resets all session state using the current difficulty's range; changing difficulty also starts a new game.
  - Attempts start at 0, invalid or out-of-range input doesn't cost an attempt, and the info box is an `st.empty()` placeholder filled after the guess is processed.
  - Hard is 1–200, every miss is -5, and the win score is `100 - 10 * (attempt - 1)` with a minimum of 10.
  - 16 pytest tests, including 4 `AppTest` tests that drive the real app and fail on the original code.

## 📸 Demo Walkthrough

A sample Normal game (range 1–100, 8 attempts). I opened Developer Debug Info and the secret was **64**:

1. The game starts: "Guess a number between 1 and 100. Attempts left: 8", score 0.
2. User enters a guess of **40**. The game says **"📈 Too low, go HIGHER!"**, Attempts left drops to 7, and the score is -5.
3. User enters **80**. The game says **"📉 Too high, go LOWER!"**, Attempts left is 6, and the score is -10.
4. User enters **9** (the case the old code got wrong on the 3rd guess). The game says **"📈 Too low, go HIGHER!"**, Attempts left is 5, and the score is -15.
5. User enters **64**. The game shows **"🎉 Correct!"** and balloons, and "You won! The secret was 64. Final score: 55" (−15 for three misses, +70 for winning on the 4th guess).
6. User clicks **New Game 🔁**. The game shows "New game started.", picks a new secret, and resets Attempts left to 8, score to 0, and history to empty.
7. Typing `abc` or `150` shows an error ("That is not a whole number." / "Pick a number between 1 and 100.") and does **not** use an attempt.
8. If the user misses 8 times, the game ends with "Out of attempts! The secret was …".

**Screenshot** *(optional)*: not included; the walkthrough above is from a real play-through of the fixed app.

## 🧪 Test Results

Run with `python -m pytest -v` (also saved to [test_results.txt](test_results.txt)):

```
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0 -- ai110-module1show-gameglitchinvestigator-starter/.venv/bin/python
cachedir: .pytest_cache
rootdir: ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collecting ... collected 16 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  6%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 12%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 18%]
tests/test_game_logic.py::test_too_high_message_says_go_lower PASSED     [ 25%]
tests/test_game_logic.py::test_too_low_message_says_go_higher PASSED     [ 31%]
tests/test_game_logic.py::test_single_digit_guess_compares_as_number PASSED [ 37%]
tests/test_game_logic.py::test_hard_range_is_bigger_than_normal PASSED   [ 43%]
tests/test_game_logic.py::test_parse_guess_rejects_text_and_decimals PASSED [ 50%]
tests/test_game_logic.py::test_parse_guess_rejects_out_of_range PASSED   [ 56%]
tests/test_game_logic.py::test_parse_guess_accepts_padded_number PASSED  [ 62%]
tests/test_game_logic.py::test_wrong_guess_never_adds_points PASSED      [ 68%]
tests/test_game_logic.py::test_first_guess_win_scores_100 PASSED         [ 75%]
tests/test_game_logic.py::test_app_second_guess_compares_numbers PASSED  [ 81%]
tests/test_game_logic.py::test_app_normal_allows_eight_guesses_and_counter_is_current PASSED [ 87%]
tests/test_game_logic.py::test_app_invalid_input_does_not_use_an_attempt PASSED [ 93%]
tests/test_game_logic.py::test_app_new_game_after_win_starts_fresh PASSED [100%]

============================== 16 passed in 0.69s ==============================
```

## 🚀 Stretch Features

- [x] **Advanced edge-case testing:** decimals, blank input, padded input (`" 42 "`), out-of-range guesses, the score floor, and app-level `AppTest` tests for state bugs. See `tests/test_game_logic.py` and [ai_interactions.md](ai_interactions.md).
- [x] **Agent workflow:** the refactor and fixes were done with Claude Code in agent mode. What it did and what I checked by hand is logged in [ai_interactions.md](ai_interactions.md).
