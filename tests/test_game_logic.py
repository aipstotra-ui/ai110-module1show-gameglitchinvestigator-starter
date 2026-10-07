from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score

# FIX: check_guess returns (outcome, message), so the starter tests now unpack the tuple
# instead of comparing the whole tuple to a string.


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Regression tests for the bugs fixed in Phase 2 (generated with Claude Code, reviewed by me) ---

def test_too_high_message_says_go_lower():
    # Bug 1: a guess above the secret used to say "Go HIGHER!"
    _, message = check_guess(60, 50)
    assert "LOWER" in message


def test_too_low_message_says_go_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


def test_single_digit_guess_compares_as_number():
    # Bug 2: with a string secret, "9" > "50" was True. 9 is below 50, so this must be Too Low.
    outcome, _ = check_guess(9, 50)
    assert outcome == "Too Low"


def test_hard_range_is_bigger_than_normal():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high


def test_parse_guess_rejects_text_and_decimals():
    assert parse_guess("abc")[0] is False
    assert parse_guess("4.9")[0] is False
    assert parse_guess("") == (False, None, "Enter a guess.")


def test_parse_guess_rejects_out_of_range():
    ok, value, err = parse_guess("150", 1, 100)
    assert ok is False and value is None and "1 and 100" in err


def test_parse_guess_accepts_padded_number():
    assert parse_guess(" 42 ", 1, 100) == (True, 42, None)


def test_wrong_guess_never_adds_points():
    # Bug 5: "Too High" on an even attempt used to give +5.
    for attempt in range(1, 9):
        assert update_score(0, "Too High", attempt) == -5
        assert update_score(0, "Too Low", attempt) == -5


def test_first_guess_win_scores_100():
    assert update_score(0, "Win", 1) == 100
    assert update_score(0, "Win", 20) == 10  # never below the 10-point floor


# --- App-level tests: drive the real Streamlit script, so they catch bugs that live in app.py ---

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _guess(at, value):
    at.text_input[0].set_value(value)
    at.button[0].click().run()


def test_app_second_guess_compares_numbers():
    # Bug 2: on the 2nd attempt the secret became "50", and a guess of 9 came back "Too High".
    at = AppTest.from_file(APP).run()
    at.session_state.secret = 50
    _guess(at, "60")
    _guess(at, "9")
    assert "go HIGHER" in at.warning[0].value


def test_app_normal_allows_eight_guesses_and_counter_is_current():
    # Bug 4: Normal started at "Attempts left: 7" and the counter lagged one guess behind.
    at = AppTest.from_file(APP).run()
    at.session_state.secret = 100
    assert "Attempts left: 8" in at.info[0].value
    _guess(at, "1")
    assert "Attempts left: 7" in at.info[0].value
    for _ in range(7):
        _guess(at, "1")
    assert at.session_state.status == "lost"
    assert len(at.session_state.history) == 8


def test_app_invalid_input_does_not_use_an_attempt():
    at = AppTest.from_file(APP).run()
    _guess(at, "abc")
    assert at.session_state.attempts == 0


def test_app_new_game_after_win_starts_fresh():
    # Bug 3: after a win, New Game left status "won" and the game stayed stuck.
    at = AppTest.from_file(APP).run()
    at.session_state.secret = 42
    _guess(at, "42")
    assert at.session_state.status == "won"
    at.button[1].click().run()
    assert at.session_state.status == "playing"
    assert at.session_state.score == 0 and at.session_state.history == []
