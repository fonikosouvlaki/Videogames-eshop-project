import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Ρύθμιση σελίδας με τίτλο και διάταξη
st.set_page_config(page_title="Game Store Analysis", layout="wide")
st.title("📊 Game Store Analysis")

# URL του backend API
API_URL = "http://localhost:5000"

# Συνάρτηση για λήψη και απόδοση γραφημάτων από το backend
@st.cache_data
def fetch_plot(endpoint):
    try:
        res = requests.get(f"{API_URL}{endpoint}")  # Αίτημα στο backend
        if res.status_code == 200:
            return Image.open(BytesIO(res.content))  # Επιστροφή της εικόνας ως PIL object
        else:
            return None
    except Exception as e:
        st.error(f"Error downloading chart: {e}")
        return None

# Μήνυμα καλωσορίσματος
st.markdown("Welcome to the analytics dashboard! Here we present trends and statistics based on game sales, popularity, and prices.")

# Χωρισμός της σελίδας σε δύο στήλες για παράλληλη εμφάνιση γραφημάτων
col1, col2 = st.columns(2)

# Πρώτο γράφημα: Engagement vs Τιμή
with col1:
    st.markdown("#### 📈 Player Participation in Relation to Price")
    plot1 = fetch_plot("/analysis/plot1")
    if plot1:
        st.image(plot1, caption="Participation vs Price", use_container_width=True)
    else:
        st.warning("Chart 1 not loaded.")

# Δεύτερο γράφημα: Τάσεις ανά Πλατφόρμα και Είδος
with col2:
    st.markdown("#### 🧮 Platform and Genre Trends")
    plot2 = fetch_plot("/analysis/plot2")
    if plot2:
        st.image(plot2)
    else:
        st.warning("Chart 2 not loaded.")