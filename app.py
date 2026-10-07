import random
import streamlit as st

# FIX: Logic now lives in logic_utils.py (refactored with Claude Code); app.py is UI only.
from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score


def start_new_game(low: int, high: int, difficulty: str):
    # FIX: New Game used to reset only attempts and secret (always 1-100), leaving status "won"/"lost"
    # so the game stayed stuck. Claude suggested resetting every piece of state in one place.
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.difficulty = difficulty


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FIX: attempts now starts at 0 (it started at 1, costing a guess), and switching difficulty
# starts a fresh game so the secret always matches the range on screen.
if st.session_state.get("difficulty") != difficulty:
    start_new_game(low, high, difficulty)

st.subheader("Make a guess")

# FIX: The info box used to be drawn before the guess was counted, so "Attempts left" lagged
# by one. It is now a placeholder filled in after the submit handler runs.
info_box = st.empty()

with st.expander("Developer Debug Info"):
    debug_box = st.empty()

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    start_new_game(low, high, difficulty)
    st.success("New game started.")

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")

elif submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX: Invalid input shows an error but no longer uses up an attempt.
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: The secret used to become a string on even attempts, so check_guess compared
        # text ("9" > "50"). Found by asking Claude to explain the TypeError fallback step by step.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )

info_box.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with debug_box.container():
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
