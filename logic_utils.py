# FIX: Moved all game logic out of app.py into this file with Claude Code (agent mode),
# then reviewed each function's diff against the original before keeping it.


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    # FIX: Hard used 1-50, which was easier than Normal. The range now grows with difficulty.
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    # FIX: "4.9" used to be silently truncated to 4. Only whole numbers are accepted now.
    try:
        value = int(raw.strip())
    except ValueError:
        return False, None, "That is not a whole number."

    # FIX: An out-of-range guess is now rejected, so it can't waste an attempt.
    if low is not None and high is not None and not low <= value <= high:
        return False, None, f"Pick a number between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX: The messages were swapped ("Too High" said "Go HIGHER!"); Claude traced the swap.
    # I also removed the except-TypeError string fallback, so "9" vs "50" can never be
    # compared as text again. app.py now always passes ints.
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Too high, go LOWER!"
    return "Too Low", "📈 Too low, go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number (1 = first guess)."""
    # FIX: A first-guess win is worth 100, minus 10 per extra guess (minimum 10).
    if outcome == "Win":
        points = 100 - 10 * (attempt_number - 1)
        return current_score + max(points, 10)

    # FIX: Every wrong guess costs 5. "Too High" used to give +5 on even attempts.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
