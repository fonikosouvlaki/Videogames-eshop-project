import streamlit as st
import requests

# Ρυθμίσεις της σελίδας με τίτλο και διάταξη
st.set_page_config(page_title="Manage Games", layout="wide")
st.title("🎮 Manage Games")

# URL του backend API
API_URL = "http://localhost:5000"

# Λήψη όλων των παιχνιδιών από το API (με caching)
@st.cache_data
def get_all_games():
    res = requests.get(f"{API_URL}/games")
    return res.json() if res.status_code == 200 else []

# Διαγραφή παιχνιδιού με ID
def delete_game(game_id):
    res = requests.delete(f"{API_URL}/games/{game_id}")
    return res.status_code == 200

# Ενημέρωση παιχνιδιού
def update_game(game_id, data):
    res = requests.put(f"{API_URL}/games/{game_id}", params=data)
    return res.status_code == 200

# Προσθήκη νέου παιχνιδιού
def add_game(data):
    res = requests.post(f"{API_URL}/games", json=data)
    return res.status_code == 201

# Φόρμα προσθήκης νέου παιχνιδιού
st.subheader("➕ Add New Game")
with st.form("add_game_form"):
    title = st.text_input("Title")
    platform = st.text_input("Platform")
    genre = st.text_input("Genre")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    description = st.text_area("Description")
    image_url = st.text_input("Image URL")
    submitted = st.form_submit_button("Add Game")

    # Αν πατήθηκε το κουμπί για προσθήκη
    if submitted:
        data = {
            "title": title,
            "platform": platform,
            "genre": genre,
            "price": price,
            "description": description,
            "image_url": image_url
        }
        # Προσπάθεια προσθήκης παιχνιδιού
        if add_game(data):
            st.success("✅ Game added successfully!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("❌ Failed to add game.")

# Διαχωριστική γραμμή
st.divider()

# Διαχείριση παιχνιδιών (επικαιροποίηση ή διαγραφή)
st.subheader("🛠️ Update or Delete Existing Games")

# Για κάθε παιχνίδι που έχει ανακτηθεί
all_games_by_platform = get_all_games()
for platform, games in all_games_by_platform.items():
 for game in games:
    with st.expander(f"{game['title']} | {game['platform']} (${game['price']})"):
        # Φόρμα για επικαιροποίηση στοιχείων
        with st.form(f"update_form_{game['id']}"):
            new_title = st.text_input("Title", value=game["title"])
            new_platform = st.text_input("Platform", value=game["platform"])
            new_genre = st.text_input("Genre", value=game["genre"])
            new_price = st.number_input("Price", value=float(game["price"]), format="%.2f")
            new_description = st.text_area("Description", value=game.get("description", ""))
            new_image_url = st.text_input("Image URL", value=game.get("image_url", ""))
            update = st.form_submit_button("✏️ Update Game")

            # Αν ο χρήστης πατήσει για ενημέρωση
            if update:
                updated_data = {
                    "title": new_title,
                    "platform": new_platform,
                    "genre": new_genre,
                    "price": new_price,
                    "description": new_description,
                    "image_url": new_image_url
                }
                # Αποστολή των νέων δεδομένων στο backend
                if update_game(game['id'], updated_data):
                    st.success("✅ Game updated.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Update failed.")

        # Κουμπί διαγραφής παιχνιδιού
        if st.button("🗑️ Delete Game", key=f"delete_{game['id']}"):
            if delete_game(game['id']):
                st.success("✅ Game deleted.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("❌ Failed to delete game.")