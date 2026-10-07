# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The first time I ran it, the game looked fine: a title, a text box, Submit / New Game buttons, and a "Developer Debug Info" expander that shows the secret. Nothing crashed. The problems only showed up once I opened the debug panel so I knew the secret and compared it against what the game told me. I played four games (Normal twice, Normal to the end and then New Game, and Hard). The starter `pytest` run also failed 3 of 3, because `logic_utils.py` only had `NotImplementedError` stubs.

The bugs I found, with the trigger, what I expected, what happened, and where the cause is:

1. **The hints point the wrong way.** Trigger: secret 50, guess 60. Expected: "Too high, go lower". Actual: "📈 Go HIGHER!". Cause: `check_guess` in `app.py` returns the outcome `"Too High"` but pairs it with the message "Go HIGHER!" (and "Too Low" with "Go LOWER!"). The outcome label is right, but the message the player reads is backwards.
2. **On every even-numbered attempt the secret is compared as text.** Trigger: secret 50, first guess 9. Expected: "go higher" (9 < 50). Actual: the outcome was "Too High". Cause: the submit block in `app.py` does `secret = str(st.session_state.secret)` when `attempts % 2 == 0`. `9 > "50"` raises `TypeError`, and the `except TypeError` branch in `check_guess` falls back to string comparison, where `"9" > "50"` is True because `"9"` sorts after `"5"`. So the hint is wrong about half the time, depending on how many guesses you've made.
3. **New Game doesn't actually start a new game.** Trigger: finish a game (win or lose), then click New Game and guess. Expected: a fresh game. Actual: "You already won. Start a new game to play again." no matter how many times you click. Cause: the `if new_game:` block resets `attempts` and `secret` but never resets `status`, `score`, or `history`, so the `status != "playing"` check calls `st.stop()` forever. It also picks the new secret with `randint(1, 100)` regardless of difficulty.
4. **You get one fewer guess than advertised, and the counter lags.** Trigger: start a Normal game (limit 8). Expected: "Attempts left: 8", and 8 guesses. Actual: it shows 7 before any guess, still shows 7 after the first guess, and the game ends after 7 guesses. Cause: `st.session_state.attempts` starts at `1` instead of `0`, and the `st.info(...)` line is drawn before the submit handler increments the counter. The same line also hard-codes "between 1 and 100" for every difficulty.
5. **Smaller bugs:** Hard uses range 1 to 50, which is easier than Normal's 1 to 100 (`get_range_for_difficulty`). A wrong "Too High" guess gives +5 points on even attempts (`update_score`), so in Game 1 my score went up after a wrong guess. Typing `abc` still uses up an attempt (submit block). Decimals like `4.9` are silently truncated to 4 (`parse_guess`).

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error | Suspected Code Location |
|-------|-------------------|-----------------|------------------------|-------------------------|
| Secret 50, guess `60` | "Too high, go lower" | Hint "📈 Go HIGHER!" | none | `app.py`, `check_guess` (message strings swapped) |
| Secret 50, guess `40` | "Too low, go higher" | Hint "📉 Go LOWER!" | none | `app.py`, `check_guess` (message strings swapped) |
| Secret 50, first guess `9` (the counter is already 2 here, so the secret is a string) | Outcome "Too Low" (9 < 50) | Outcome "Too High", score +5 | none (the `TypeError` is silently caught) | `app.py` submit block, `secret = str(...)` on even attempts, plus the `except TypeError` string fallback in `check_guess` |
| Secret 7, guesses 1 through 7 on Normal (limit 8) | 8 guesses allowed; "Attempts left: 8" at start | "Attempts left: 7" at start, still 7 after the first guess; won on the 7th guess with a score of -20 | none | `app.py`, `attempts` initialised to `1`; `st.info` rendered before the submit handler |
| Win a game, click **New Game**, guess `10` | A fresh game starts | "You already won. Start a new game to play again." forever; score stays -20 | none | `app.py`, `if new_game:` block (doesn't reset `status`/`score`/`history`) |
| Type `abc`, Submit | Error message, no attempt used | "That is not a number." and Attempts left drops by 1 | none | `app.py`, `attempts += 1` runs before `parse_guess` |
| Difficulty Hard | Bigger range than Normal | Range is 1 to 50 (Normal is 1 to 100); info box still says "1 and 100" | none | `app.py`, `get_range_for_difficulty` and the hard-coded `st.info` text |
| `pytest` on the starter code | Tests run | 3 failed: `NotImplementedError: Refactor this function from app.py into logic_utils.py` | `NotImplementedError` | `logic_utils.py` stubs; the tests also compare the tuple from `check_guess` to a plain string |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
