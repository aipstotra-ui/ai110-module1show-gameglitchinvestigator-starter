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

I used **Claude Code** (Claude Opus 5.5) in agent mode for the whole project: setting up the fork and venv, scripting play-throughs, explaining logic, refactoring, writing tests, and drafting commit messages. Before each step I gave it the relevant files (`app.py`, `logic_utils.py`, the test file).

**A suggestion that was correct: the "commitment issues" bug.** I asked why a guess of 9 against a secret of 50 said "Too High". Claude walked through it step by step: on even attempts `app.py` replaces the secret with `str(secret)`, then `9 > "50"` raises `TypeError`, and `check_guess`'s `except TypeError` branch quietly falls back to comparing `"9" > "50"` as text, which is True because `"9"` sorts after `"5"`. Its fix was to delete the `str()` branch in `app.py` and also delete the string fallback in `check_guess`, so the comparison can only ever be numeric. That was right: the fallback only existed to hide the type mix-up. I checked it in the live game (secret 64, guesses 40 → 80 → 9 → 64 gave "go HIGHER", "go LOWER", "go HIGHER", "Correct!") and with `test_app_second_guess_compares_numbers`.

**A suggestion I did not accept as written: the first regression test for that bug.** Claude's first test for the string bug was the unit test `check_guess(9, 50) == "Too Low"`. It passed, but when I looked closer it would also have passed on the *original* `check_guess`, because the bug wasn't in `check_guess` when you hand it two ints. The `str()` cast was in `app.py`. So that test proved nothing about the bug it claimed to cover. I kept it as a basic numeric-comparison check, but added app-level tests with Streamlit's `AppTest` that play the actual `app.py` (guess 60, then 9, and check the hint). To verify, I temporarily swapped the original `app.py` back in: all 4 app tests **failed** on the old code, then **passed** again on the fixed code. The lesson for me: a passing test only means something if it would have failed before the fix.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

I counted a bug as fixed only when three things were true: (1) a test that targets it passes, (2) that same test fails on the original code, and (3) the live game in the browser does the right thing. For the hint direction, `test_too_high_message_says_go_lower` checks that `check_guess(60, 50)` returns "Too High" with a message saying go LOWER. For the attempt counter, `test_app_normal_allows_eight_guesses_and_counter_is_current` plays Normal in `AppTest` and checks that the box says "Attempts left: 8" at the start and "7" right after the first guess, and that the game ends after exactly 8 guesses. On the original `app.py` that test failed (it showed 7 at the start), and it passes now. The full run is **16 passed** (saved in `test_results.txt`). Then I played the fixed game in a browser: secret 64; guesses 40, 80, 9, 64 gave the right hints, the counter went 8 → 7 → 6 → 5 → 4 immediately after each guess, and I won with 55 points (three misses at -5 each, then +70 for winning on the 4th guess). Clicking New Game then gave a fresh secret with attempts 0, score 0, and empty history.

AI helped a lot with tests. Claude suggested `streamlit.testing.v1.AppTest`, which I didn't know existed. It lets a test click buttons and type into the real app without a browser, and that's what made the state bugs (New Game, attempts) testable at all. It also pointed out that the starter tests compared the whole `(outcome, message)` tuple to a string, so they could never pass even with correct logic. I fixed those tests to unpack the tuple rather than changing `check_guess` to return only a string, because the UI needs the message.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Every time you click a button or type in a box, Streamlit runs your whole Python script again from the top. That's a "rerun". So any normal variable, like `secret = random.randint(1, 100)`, gets recreated on every click, which is why a naive game "forgets" its secret. `st.session_state` is a dictionary that survives reruns, so you write `if "secret" not in st.session_state:` to set it only the first time. Two bugs here were really about reruns. The "Attempts left" box was drawn near the top of the script, *before* the code further down counted the guess, so it always showed last turn's number. I fixed that by reserving a spot with `st.empty()` and filling it at the end. And New Game only reset two of the five session-state keys, so the old "won" status survived every rerun.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

**Habit to keep:** reproduce the bug with a concrete input first (secret 50, guess 9), write it down in a table, and then prove the fix with a test that fails on the old code and passes on the new one. Swapping the old file back in to watch the tests fail took 30 seconds and caught a test that wasn't actually testing anything. I also want to keep making small commits at each phase (bug log → fix → tests → docs), so the history tells the story.

**What I'd do differently:** I'd ask the AI up front, "would this test have failed before the fix?", instead of finding out afterwards. I'd also scope my requests more tightly. When I let the agent take on all the bugs at once, I had to review a bigger diff than if I'd fixed and checked one bug at a time.

**How my view changed:** AI-generated code can look clean and still be quietly wrong. The string fallback in `check_guess` was there to make an error go away, not to handle a real case. I now read AI code asking "what is this line hiding?", not just "does it run?"
