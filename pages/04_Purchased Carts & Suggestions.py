import streamlit as st
import requests
import datetime

# Ρυθμίσεις της σελίδας (τίτλος και διάταξη)
st.set_page_config(page_title="Purchased Carts", layout="wide")
st.title("🛒 Purchased Carts & Suggestions")

# Βασικό URL για τα API endpoints
API_URL = "http://localhost:5000"

# Λήψη όλων των παιχνιδιών από το backend
@st.cache_data
def get_all_games():
    res = requests.get(f"{API_URL}/games")
    return res.json() if res.status_code == 200 else []

# Λήψη όλων των αγορασμένων καλαθιών
@st.cache_data
def get_purchased_carts():
    res = requests.get(f"{API_URL}/purchases")
    if res.status_code == 200:
        return res.json()["purchased_carts"]
    else:
        st.error(f"Error retrieving purchased carts: {res.status_code} {res.reason}")
        return []

# Λήψη προτάσεων για ένα καλάθι
@st.cache_data
def get_suggestions(cart_id):
    try:
        res = requests.get(f"{API_URL}/suggest/{cart_id}")
        if res.status_code == 200:
            return res.json().get("suggestions", "No proposals were returned.")
        else:
            return f"Error in suggestions: {res.text}"
    except Exception as e:
        return f"Error during recovery of suggestions: {e}"

# Κουμπί ανανέωσης δεδομένων
if st.button("🔄 Reload Purchased Carts"):
    st.cache_data.clear()
    st.rerun()

# Φόρτωση δεδομένων από το API
all_games = get_all_games()

if isinstance(all_games, list):
    games_price_lookup = {g["id"]: g["price"] for g in all_games}
elif isinstance(all_games, dict):
    games_price_lookup = {
        g["id"]: g["price"]
        for games in all_games.values()
        for g in games
    }
else:
    st.error("Unexpected format from /games.")
    st.stop()

purchased_carts = get_purchased_carts()

# Αν δεν υπάρχουν αγορασμένα καλάθια, εμφάνισε μήνυμα
if not purchased_carts:
    st.info("Purchased carts not found.")
    st.stop()

# Εμφάνιση κάθε αγορασμένου καλαθιού με τα παιχνίδια του
for cart in purchased_carts:
    with st.expander(f"🛍️ Cart #{cart['purchased_cart_id'][:8]} - Purchased at {cart['purchased_at']}"):
        total_price = 0.0
        for item in cart["items"]:
            title = item["game_title"]
            game_id = item["game_id"]
            price = games_price_lookup.get(game_id, 0.0)
            total_price += price
            st.markdown(f"- **{title}** (${price:.2f})")

        # Εμφάνιση συνολικού κόστους του καλαθιού
        st.markdown(f"**💰 Total Price:** ${total_price:.2f}")

        # Κουμπί για λήψη προτάσεων παιχνιδιών
        if st.button("🤖 Suggest Games", key=f"suggest_{cart['purchased_cart_id']}"):
            with st.spinner("Receiving suggestions..."):
                suggestions = get_suggestions(cart["purchased_cart_id"])
            st.markdown(f"**🤖 Suggested Games:**\n{suggestions}")
