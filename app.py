import os
import datetime
import time
import pandas as pd
import streamlit as st

if not bool(os.getenv("PROD")):
    from dotenv import load_dotenv
    load_dotenv(override=True)  # Load .env file in local development

from utils.methods import GiftCodeRedemptionAPI

# Initialize API
URL = os.getenv("URL")
api = GiftCodeRedemptionAPI(base_url=URL)

# ============== Utility Functions ==============

def map_status_to_icon(status):
    """Map redemption status to check/X icons."""
    return "✅" if status == 1 else "❌"

def player_data_format(players):
    """Format player data for display."""
    if not players:
        return pd.DataFrame()  # Return an empty DataFrame if no players exist
    
    df = pd.DataFrame(players)
    if df.empty:
        return df  # Ensure it returns an empty DataFrame properly
    
    required_columns = ['avatar_image', 'nickname', 'stove_lv', 'kid', 'redeemed_all']
    df = df[required_columns]
    df["redeemed_all"] = df["redeemed_all"].apply(map_status_to_icon)

    return df

@st.cache_data(ttl=3600)
def reload_players():
    """Fetch and update player data in session state."""
    with st.spinner('Loading player data...'):
        try:
            response = api.list_players()
            return player_data_format(response.get('players', []))
        except Exception as e:
            st.error(f"Error loading players: {e}")
            return pd.DataFrame()

@st.cache_data(ttl=3600)
def reload_giftcodes():
    """Fetch and update gift codes in session state."""
    with st.spinner('Loading gift codes...'):
        try:
            response = api.list_giftcodes()
            return response.get('giftcodes', [])
        except Exception as e:
            st.error(f"Error loading gift codes: {e}")
            return []

def redemption_process(method: str):
    # Step 0: Check for inprogress task if yes, skip Step 1 and 2
    inprogress_task_id = api.get_check_inprogress()
    
    if inprogress_task_id is None:
        # Step 1: Start the automate-all task
        if method == "automate-all":
            response = api.run_main_logic()
        elif method == "expired-check":
            response = api.expired_check()
        task_id = response.get('task_id', None)
        if not task_id:
            st.error("Failed to initiate redemption process.")
            return
        
        st.success(f"Task started! Tracking progress...")

        # Step 2: Track progress
        progress_bar = st.progress(0)
    else:
        task_id = inprogress_task_id
        task_status = api.get_task_status(task_id)
        progress = task_status.get('progress', 0)
        progress_bar = st.progress(progress)
        st.success(f"Task already started! Tracking progress...")
    
    status_text = st.empty()

    while True:
        time.sleep(5)  # Poll every 5 seconds
        task_status = api.get_task_status(task_id)
        progress = task_status.get('progress', 0)
        status = task_status.get('status', 'Processing')

        progress_bar.progress(progress / 100)  # Convert to percentage
        status_text.text(f"Progress: {progress}% - {status}")

        if status == "Completed" or status == "Failed":
            break  # Stop polling when done
    
    return task_status

def add_player_callback():
    """Handle player creation and update session state."""
    player_id = st.session_state.get("new_player", "").strip()
    if not player_id:
        st.error("Player ID cannot be empty.")
        return
    
    with st.spinner('Adding player...'):
        try:
            response = api.create_player(player_id=str(player_id))
            st.success(response.get('message', 'Player added successfully!'))
            st.session_state.players = reload_players()
        except Exception as e:
            st.error(f"Failed to add player: {e}")


def fetch_giftcodes_callback():
    """Fetch new gift codes and update session state."""
    with st.spinner('Fetching gift codes...'):
        try:
            response = redemption_process("expired-check")

            # Step 3: Update session state
            if response['status'] == "Completed":
                st.session_state.players = player_data_format(response.get('players', []))
                new_codes = response.get('new_codes', [])
                giftcodes = response.get('giftcodes', [])

                new_codes_true = [val for val in new_codes if val in giftcodes]
                if not new_codes_true:
                    st.info("No new gift codes available.")
                else:
                    st.success(f"New gift codes fetched: {', '.join(new_codes_true)}")
                st.session_state.giftcodes = response.get('giftcodes', [])
            else:
                raise f"Task failed: {response.get('error', 'Unknown error')}"
        except Exception as e:
            st.error(f"Failed to fetch gift codes: {e}")


def redeem_giftcodes_callback():
    """Redeem gift codes for all players with real-time progress tracking."""
    with st.spinner('Starting redemption process...'):
        try:
            response = redemption_process("automate-all")

            # Step 3: Update session state
            if response['status'] == "Completed":
                st.session_state.players = player_data_format(response.get('players', []))
                new_codes = response.get('new_codes', [])
                if not new_codes:
                    st.info("No new gift codes available.")
                else:
                    st.success(f"New gift codes fetched: {', '.join(new_codes)}")
                st.session_state.giftcodes = response.get('giftcodes', [])
                st.success("Gift codes applied to all players!")
            else:
                st.error(f"Task failed: {response.get('error', 'Unknown error')}")

        except Exception as e:
            st.error(f"Failed to redeem gift codes: {e}")
            st.session_state.reload_data = True  # Trigger reload of data


# ============== Session State Initialization ==============

if "players" not in st.session_state:
    st.session_state.players = reload_players()
if "giftcodes" not in st.session_state:
    st.session_state.giftcodes = reload_giftcodes()
if "reload_data" not in st.session_state:
    st.session_state.reload_data = False  # Set to False initially

# Reload data if explicitly requested
if st.session_state.reload_data:
    st.cache_data.clear()
    st.session_state.players = reload_players()
    st.session_state.giftcodes = reload_giftcodes()
    st.session_state.reload_data = False


# ============== UI Layout ==============

st.markdown(
    "<h1 style='text-align: left;'>Whiteout Survival Redeem Code Subscription</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: left; font-size: 20px;'>Automatically Redeem Rewards with Official Gift Codes in Whiteout: Survival!</p>",
    unsafe_allow_html=True
)
st.write("")

# Sidebar with actions
with st.sidebar:
    st.text_input("Add a Player to Subscribe", key="new_player",
                  help="*Check your Player ID in-game through your Avatar on the top left corner")
    st.button("Add Player!", on_click=add_player_callback)
    st.markdown("---")
    st.button("Fetch Gift Codes", on_click=fetch_giftcodes_callback)
    st.button("Apply Gift Codes to All Players", on_click=redeem_giftcodes_callback)
    st.markdown("---")
    if st.button("Refresh Data"):
        st.session_state.reload_data = True

# Split layout into two columns
col1, col2 = st.columns([3, 2])  # Players column is wider than gift codes

# ============== Players Table ==============
with col1:
    st.subheader("Subscribed Players")

    st.dataframe(st.session_state.players, hide_index=True, height=35*len(st.session_state.players)+38,
    column_config={
        "avatar_image": st.column_config.ImageColumn(label=""),
        "nickname": st.column_config.TextColumn(label="Nickname"),
        "stove_lv": st.column_config.TextColumn(label="Stove Lv. 💬", help="📍**Furnace Level**"),
        "kid": st.column_config.TextColumn(label="State 💬", help="📍**State Number**"),
        "redeemed_all": st.column_config.TextColumn(label="Redeemed?", help="📍**If the player redeemed all the gift codes.**")
    })


# ============== Gift Codes Display ==============
with col2:
    st.subheader("Available Gift Codes")
    if st.session_state.giftcodes:
        for code in st.session_state.giftcodes:
            st.code(code, language="plaintext")
    else:
        st.info("No gift codes available.")


# ============== Footer ==============
datenow = datetime.date.today().strftime("%d.%m.%Y")  # Formatted as DD.MM.YYYY
st.markdown(
    f'<span style="font-size: 14px">**Author:** <a href="https://github.com/JouhC" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="14" style="vertical-align: middle;"> Jouh</a> | **Date:** {datenow} | Made for EOS friends!</span>',
    unsafe_allow_html=True
)
