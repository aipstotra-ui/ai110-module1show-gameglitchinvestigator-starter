# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

"Move `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` from `app.py` into `logic_utils.py`, fix the high/low hint bug and the string-secret bug at the FIXME markers, make New Game fully reset the game, update the import in `app.py`, then write pytest cases that target each fix." (Claude Code, Claude Opus 5.5, agent mode.)

**What did the agent do?**

1. Forked and cloned the repo, created `.venv`, installed `requirements.txt`, and ran `pytest` (3 failed with `NotImplementedError`).
2. Wrote a throwaway script with `streamlit.testing.v1.AppTest` to play four games against the buggy app and print every hint, score, and counter. That output became the bug log in `reflection.md`.
3. Added `# FIXME` comments at each bug location in `app.py` and committed the bug log.
4. Rewrote `logic_utils.py` with the four fixed functions, and changed `app.py` to import them, add a `start_new_game()` helper, start attempts at 0, and render "Attempts left" from an `st.empty()` placeholder.
5. Updated the starter tests to unpack the `(outcome, message)` tuple and added unit tests plus 4 `AppTest` tests. Ran `pytest` (16 passed).
6. Started the app with `streamlit run` and played a full game in a browser (secret 64: 40 → 80 → 9 → 64, then New Game).

**What did you have to verify or fix manually?**

- The agent's first regression test for the string bug, `check_guess(9, 50) == "Too Low"`, would also have passed on the *old* code, because the `str()` cast lived in `app.py`, not in `check_guess`. I required a test that fails before the fix, so we added `AppTest` tests and confirmed them by temporarily restoring the original `app.py`: 4 failed, then 16 passed after restoring the fix.
- I reviewed the diff for each file. The one design call I made was to update the starter tests to unpack the tuple rather than change `check_guess` to return only the outcome, because the UI needs the message.
- Score math in the live game: three misses (-15) plus a 4th-guess win (+70) = 55, which matched the screen.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Single-digit guess vs two-digit secret (string comparison) | "Write a test that would have caught the `"9" > "50"` bug." | First `check_guess(9, 50)`, then `test_app_second_guess_compares_numbers` (AppTest: guess 60, then 9) | Unit test: passed on old *and* new code. App test: failed on old, passed on new | The unit test didn't cover the real cause (the cast in `app.py`), so I kept the app test as the regression test |
| Decimal / non-numeric / blank input | "What inputs could break `parse_guess`?" | `test_parse_guess_rejects_text_and_decimals` (`"abc"`, `"4.9"`, `""`) | Passed | `"4.9"` used to be silently truncated to 4, so rejecting it is clearer for the player |
| Out-of-range guess | "Should 150 be allowed on Normal?" | `test_parse_guess_rejects_out_of_range` | Passed | An out-of-range guess can never be right, so it shouldn't cost an attempt |
| Invalid input uses an attempt | "Test that typing abc doesn't use up an attempt." | `test_app_invalid_input_does_not_use_an_attempt` | Failed on old code, passed after fix | Confirms the counter only moves on a real guess |
| Score floor on a very late win | "Edge cases for `update_score`?" | `update_score(0, "Win", 20) == 10` | Passed | Points must never go below 10 for a win |

---

## Linting & Style (SF9)

Not attempted.

---

## Model Comparison (SF11)

Not attempted.
