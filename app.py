import requests
import pandas as pd
import streamlit as st
import os
if not bool(os.getenv("PROD")):
    from dotenv import load_dotenv
    load_dotenv(override=True)  # Load .env file in local development
from utils.methods import GiftCodeRedemptionAPI

URL = os.getenv("URL")
api = GiftCodeRedemptionAPI(base_url=URL)

# Function to handle player creation
def add_player_callback():
    if st.session_state.new_player:  # Access the new_player value from session_state
        with st.spinner('Adding player...'):
            try:
                response = api.create_player(player_id=str(st.session_state.new_player))
                st.success(f"Player '{st.session_state.new_player}' added successfully!")
                st.session_state.reload_data = True  # Trigger reload of data
            except Exception as e:
                st.error(f"Failed to add player: {e}")
    else:
        st.error("Player ID cannot be empty.")

def map_status_to_icon(status):
    if status == 1:
        return "✅"  # Check icon
    else:
        return "❌"  # X icon

# Load player data
def load_player_data():
    with st.spinner('Loading player data...'):
        response = api.list_players()
        players = pd.DataFrame(response['players'])

        data = players[['avatar_image', 'nickname', 'stove_lv', 'kid', 'redeemed_all']]
        data.loc[:, "redeemed_all"] = data["redeemed_all"].apply(map_status_to_icon)
        data = data.reset_index(drop=True)

        return data, players['fid'].tolist()

# Load gift codes
def load_giftcodes():
    with st.spinner('Loading gift codes...'):
        response = api.list_giftcodes()
        giftcodes = response.get('giftcodes', [])
        return giftcodes  # List of gift codes

# Fetch new gift codes
def fetch_giftcodes_callback():
    with st.spinner('Fetching gift codes...'):
        try:
            api.fetch_giftcodes()
            st.session_state.reload_data = True  # Trigger reload of data
            st.success("Gift codes fetched successfully!")
        except Exception as e:
            st.error(f"Failed to fetch gift codes: {e}")

# Redeem gift codes for all players
def redeem_giftcodes_callback(players):
    with st.spinner('Redeeming gift codes...'):
        try:
            reponse = api.run_main_logic()

            st.success("Gift codes applied to all players!")
            st.session_state.reload_data = True  # Trigger reload of data
        except Exception as e:
            st.error(f"Failed to redeem gift codes: {e}")

# Initialize session state variables
if "reload_data" not in st.session_state:
    st.session_state.reload_data = False

# Main Layout
st.markdown("<h1 style='text-align: left;'>Whiteout Survival Redeem Code Subscription</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left; font-size: 20px;'>Automatically Redeem Rewards with Official Gift Codes in Whiteout: Survival!</p>", unsafe_allow_html=True)
st.write("")

if st.session_state.reload_data:
    player_data, players = load_player_data()
    giftcodes = load_giftcodes()
    st.session_state.reload_data = False

# Sidebar input for adding a player
with st.sidebar:
    st.text_input("Add a Player to Subscribe", key="new_player", help="*Check your Player ID in-game through your Avatar on the top left corner")
    st.button("Add Player!", on_click=add_player_callback)
    st.button("Fetch Gift Codes", on_click=fetch_giftcodes_callback)
    st.button("Apply Gift Codes to All Players", on_click=redeem_giftcodes_callback, args=[players])

# Split layout into two columns with adjusted proportions
col1, col2 = st.columns([3, 2])  # Wider column for players, narrower for gift codes

# Left Column: Display Players
with col1:
    st.subheader("Subscribed Players")
    st.dataframe(player_data, hide_index=True, column_config={
        "avatar_image": st.column_config.ImageColumn(label=""),
        "nickname": st.column_config.TextColumn(label="Nickname"),
        "stove_lv": st.column_config.TextColumn(label="Stove Lv. 💬", help="📍**Furnace Level**"),
        "kid": st.column_config.TextColumn(label="State 💬", help="📍**State Number**"),
        "redeemed_all": st.column_config.TextColumn(label="Redeemed?", help="📍**If the player redeemed all the gift codes.**")
    })

# Right Column: Display Gift Codes
with col2:
    st.subheader("Available Gift Codes")

    giftcodes = load_giftcodes()
    if giftcodes:
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
        for code in giftcodes:
            st.markdown(f"<div class='gift-code'>{code}</div>", unsafe_allow_html=True)
    else:
        st.info("No gift codes available.")

# Footer
import datetime
datenow = datetime.date.today().strftime("%d.%m.%Y")  # Formatted as DD.MM.YYYY
st.markdown(f'<span style="font-size: 14px">**Author:** Jouh | **Data:** {datenow} | Made for EOS friends!</span>', unsafe_allow_html=True)
