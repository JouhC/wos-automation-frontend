import os
import datetime
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

@st.cache_data
def reload_players():
    """Fetch and update player data in session state."""
    with st.spinner('Loading player data...'):
        try:
            response = api.list_players()
            return player_data_format(response.get('players', []))
        except Exception as e:
            st.error(f"Error loading players: {e}")
            return pd.DataFrame()

@st.cache_data
def reload_giftcodes():
    """Fetch and update gift codes in session state."""
    with st.spinner('Loading gift codes...'):
        try:
            response = api.list_giftcodes()
            return response.get('giftcodes', [])
        except Exception as e:
            st.error(f"Error loading gift codes: {e}")
            return []


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
            response = api.fetch_giftcodes()
            new_codes = response.get('new_codes', [])
            if not new_codes:
                st.info("No new gift codes available.")
            else:
                st.success(f"New gift codes fetched: {', '.join(new_codes)}")
                st.session_state.giftcodes.extend(new_codes)
        except Exception as e:
            st.error(f"Failed to fetch gift codes: {e}")


def redeem_giftcodes_callback():
    """Redeem gift codes for all players."""
    with st.spinner('Redeeming gift codes...'):
        try:
            response = api.run_main_logic()
            st.session_state.players = player_data_format(response.get('players', []))
            st.session_state.giftcodes = response.get('giftcodes', [])
            st.success("Gift codes applied to all players!")
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
        st.markdown("<style>.gift-code {"
                    "background-color: #2E8B57;"
                    "color: white;"
                    "padding: 10px 20px;"
                    "margin: 5px;"
                    "border-radius: 5px;"
                    "display: inline-block;"
                    "font-size: 18px;"
                    "text-align: center;"
                    "white-space: nowrap;"
                    "overflow: hidden;"
                    "text-overflow: ellipsis;"
                    "}</style>", unsafe_allow_html=True)

        # Display each gift code
        for code in st.session_state.giftcodes:
            st.markdown(f"<div class='gift-code'>{code}</div>", unsafe_allow_html=True)
    else:
        st.info("No gift codes available.")


# ============== Footer ==============
datenow = datetime.date.today().strftime("%d.%m.%Y")  # Formatted as DD.MM.YYYY
st.markdown(
    f'<span style="font-size: 14px">**Author:** Jouh | **Date:** {datenow} | Made for EOS friends!</span>',
    unsafe_allow_html=True
)