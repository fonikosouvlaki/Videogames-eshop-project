import streamlit as st
import requests

# Διαμόρφωση της σελίδας με τίτλο και διάταξη
st.set_page_config(page_title="Browse Games", layout="wide")
st.title("🛒 Browse Games")

# Διεύθυνση του API backend(εκτός κι αν την έχουμε αλλάξει)
API_URL = "http://localhost:5000"

# --- Cache API κλήσεις ---

# Επιστρέφει τα διαθέσιμα carts από το backend
def get_carts():
    res = requests.get(f"{API_URL}/carts")
    return res.json() if res.status_code == 200 else []

# Κλήση στα διαθέσιμα παιχνίδια
@st.cache_data
def get_games():
    res = requests.get(f"{API_URL}/games")
    return res.json() if res.status_code == 200 else []

# Προσθέτει ένα παιχνίδι σε συγκεκριμένο cart
def add_to_cart(cart_id, game_id):
    payload = {"game_id": game_id}
    url = f"{API_URL}/cart/{cart_id}/add"
    res = requests.post(url, json=payload)
    return res.status_code == 200

# Δημιουργεί ένα νέο cart
def create_cart():
    res = requests.post(f"{API_URL}/cart")
    return res.status_code == 201

# Κάνει αναζήτηση παιχνιδιών με φίλτρα και caching
@st.cache_data
def search_games(title="", genre="", platform="", price=None, sort_by="title", order="asc"):
    params = {}
    if title: params["title"] = title
    if genre: params["genre"] = genre
    if platform: params["platform"] = platform
    if price is not None: params["price"] = price
    if sort_by: params["sort_by"] = sort_by
    if order: params["order"] = order

    res = requests.get(f"{API_URL}/games/search", params=params)
    return res.json() if res.status_code == 200 else []

# Παίρνει περίληψη παιχνιδιού από backend/groq
@st.cache_data
def fetch_game_summary(title):
    try:
        res = requests.get(f"{API_URL}/games/summary", params={"title": title})
        if res.status_code == 200:
            return res.json().get("summary", "No summary available.")
        else:
            return f"Error: {res.json().get('error', 'Failed to fetch summary')}"
    except Exception as e:
        return f"Exception occurred: {e}"

# Scrap από consoleclub & gamestory από backend
def fetch_console_club_price(game_id):
    try:
        res = requests.get(f"{API_URL}/scrape", params={"id": game_id})
        return res.text if res.status_code == 200 else f"Error: {res.text}"
    except Exception as e:
        return f"Exception occurred: {e}"
def fetch_gamestory_price(game_id):
    try:
        res = requests.get(f"{API_URL}/scrape/gamestory", params={"id": game_id})
        return res.text if res.status_code == 200 else f"Error: {res.text}"
    except Exception as e:
        return f"Exception occurred: {e}"
    
# --- Καλάθια(Active/Διαθέσιμα) ---

# Παίρνει όλα τα carts και εμφανίζει επιλογή στον χρήστη
carts = get_carts()
st.markdown("### 🛒 Carts")

if not carts:
    st.warning("No carts available. Please create one.")
    if st.button("➕ Create New Cart"):
        if create_cart():
            st.success("Cart created successfully!")
            st.rerun()
        else:
            st.error("Failed to create cart.")
    st.stop()

# Δημιουργεί dictionary με τις επιλογές των carts
cart_options = {f"Cart #{c['cart_id'][:8]}": c["cart_id"] for c in carts}
col1, col2 = st.columns([4, 1])

# Επιλογή ενεργού cart από τον χρήστη
with col1:
    selected_cart_label = st.selectbox("Select Active Cart", options=list(cart_options.keys()))
    active_cart_id = cart_options[selected_cart_label]

# Κουμπί για δημιουργία νέου cart
with col2:
    if st.button("➕ Create New Cart"):
        if create_cart():
            st.success("New cart created!")
            st.rerun()
        else:
            st.error("Failed to create a new cart.")

# --- Αναζήτηση/Φίλτρα ---
st.markdown("### 🔍 Search Games")

with st.expander("Search Filters"):
    title = st.text_input("Title")
    genre = st.text_input("Genre")
    platform = st.text_input("Platform")
    max_price = st.number_input("Max Price", min_value=0.0, value=0.0, step=1.0)
    sort_by = st.selectbox("Sort by", ["title", "price", "platform", "genre"])
    order = st.radio("Order", ["asc", "desc"])
    search_btn = st.button("🔍 Search")

# --- Games Προβολή ---

# Εμφανίζει τα αποτελέσματα αναζήτησης ή όλα τα παιχνίδια
if search_btn:
    results = search_games(title, genre, platform, max_price if max_price > 0 else None, sort_by, order)
    games = results
else:
    games = get_games()

st.markdown("### 🎮 Available Games")

if not games:
    st.info("No games available.")
else:
    for platform, games_in_platform in games.items():
        st.markdown(f"## 🎮 Platform: {platform}")
        for game in games_in_platform:
            with st.container():
                st.markdown("---")

            # Κουμπιά για περίληψη και έλεγχο τιμής
            btn_cols = st.columns([1, 1, 1])
            with btn_cols[0]:
                if st.button("🤖 Suggest Summary", key=f"summ_{game['id']}"):
                    summary = fetch_game_summary(game["title"])
                    st.info(summary)

            with btn_cols[1]:
                if st.button("💸 Check Price on Console Club", key=f"price_{game['id']}"):
                    price_info = fetch_console_club_price(game["id"])
                    st.info(price_info)
            with btn_cols[2]:
                if st.button("🏷️ Check Price on GameStory", key=f"price_gamestory_{game['id']}"):
                    gamestory_price = fetch_gamestory_price(game["id"])
                    st.info(gamestory_price)
                    
            # Πληροφορίες παιχνιδιών
            cols = st.columns([1, 3, 2, 2, 2])
            with cols[0]:
                st.image(game["image_url"], width=120)
            with cols[1]:
                st.subheader(game["title"])
                st.caption(game["genre"])
                st.caption(game.get("description", "No description"))
            with cols[2]:
                st.markdown(f"💰 **Price:** ${game['price']}")
            with cols[3]:
                st.markdown(f"🎮 Platform: {game['platform']}")
            with cols[4]:
                if st.button("🛒 Add to Cart", key=f"add_{game['id']}"):
                    if add_to_cart(active_cart_id, game["id"]):
                        st.success(f"✅ Added {game['title']} to cart!")
                    else:
                        st.error(f"❌ Failed to add {game['title']}.")