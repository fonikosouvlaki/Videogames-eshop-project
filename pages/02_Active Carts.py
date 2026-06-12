import streamlit as st
import requests
import datetime

# Ρυθμίσεις της σελίδας με τίτλο και διάταξη
st.set_page_config(page_title="Manage Carts", layout="wide")
st.title("🗒️ View & Manage Carts")

# Διεύθυνση του API backend
API_URL = "http://localhost:5000"

# Λήψη όλων των carts
@st.cache_data
def get_carts():
    res = requests.get(f"{API_URL}/carts")
    return res.json() if res.status_code == 200 else []

# Επιστροφή δεδομένων για συγκεκριμένο cart
@st.cache_data
def view_cart(cart_id):
    res = requests.get(f"{API_URL}/cart/{cart_id}")
    return res.json() if res.status_code == 200 else None

# Αφαίρεση παιχνιδιού από διαθέσιμο cart
@st.cache_data
def remove_from_cart(cart_id, game_id):
    res = requests.post(f"{API_URL}/cart/{cart_id}/remove", json={"game_id": game_id})
    return res.status_code == 200

# Ολοκλήρωση αγοράς διαθέσιμου cart
@st.cache_data
def purchase_cart(cart_id, purchased_at):
    payload = {"purchased_at": purchased_at}
    res = requests.post(f"{API_URL}/cart/{cart_id}/purchase", json=payload)
    return res.status_code == 200

# Παίρνουμε όλα τα διαθέσιμα carts
carts = get_carts()

# Κουμπί ανανέωσης των αγορασμένων carts
if st.button("🔄 Reload Active Carts"):
    st.cache_data.clear()  # καθαρίζει τα αποθηκευμένα δεδομένα
    st.rerun()  # επανεκκινεί την εφαρμογή

if not carts:
    st.info("No carts available.")
    st.stop()

# Εμφάνιση κάθε διαθέσιμου cart
for cart in carts:
    with st.expander(f"Cart #{cart['cart_id'][:8]} (Items: {cart['items_count']})"):
        cart_data = view_cart(cart["cart_id"])
        if not cart_data:
            st.warning("This cart is no longer available.")
            continue

        total_price = 0.0  # μεταβλητή για υπολογισμό του συνολικού κόστους

        # Εμφάνιση των παιχνιδιών του cart
        for item in cart_data["items"]:
            st.image(item["image_url"], width=80)
            st.markdown(f"**{item['title']}** | {item['platform']} | ${item['price']}")
            total_price += item['price']

            # Κουμπί για αφαίρεση παιχνιδιού από cart
            if st.button("❌ Remove from Cart", key=f"remove_{cart['cart_id']}_{item['game_id']}"):
                if remove_from_cart(cart["cart_id"], item["game_id"]):
                    st.success("Removed from cart.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Failed to remove item.")

        # Εμφάνιση συνολικού κόστους
        st.markdown(f"### 🧾 Total: ${total_price:.2f}")

        # Φόρμα για την αγορά του cart
        with st.form(f"purchase_form_{cart['cart_id']}"):
            st.markdown("**Purchase this cart:**")
            date_input = st.date_input("Purchase Date", value=datetime.date.today(), key=f"date_{cart['cart_id']}")
            time_input = st.text_input("Time (HH:MM)", value="12:00", key=f"time_{cart['cart_id']}")
            submit = st.form_submit_button("Purchase")

            # Αν ο χρήστης πατήσει "Purchase"
            if submit:
                try:
                    # Συνένωση ημερομηνίας και ώρας για σωστή μορφή ISO
                    full_dt = f"{date_input}T{time_input}:00"
                    datetime.datetime.fromisoformat(full_dt)  # έλεγχος εγκυρότητας

                    # Απόπειρα αγοράς
                    if purchase_cart(cart['cart_id'], full_dt):
                        st.success("✅ Purchased successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ Purchase failed.")
                except ValueError:
                    st.error("Invalid time format. Use HH:MM")
