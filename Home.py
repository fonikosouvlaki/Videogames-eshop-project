import streamlit as st

st.set_page_config(page_title="Home | Game Store", layout="wide")

# === CSS για background + white text + horizontal scroll container ===
st.markdown(
    """
    <style>
    ::-webkit-scrollbar {
    height: 8px;
    background: transparent;
 }

    ::-webkit-scrollbar-thumb {
    background-color: white;
    border-radius: 4px;
    border: none;
 }
    .stApp {
        background-image: url("https://www.pixelstalk.net/wp-content/uploads/2016/05/Download-Gaming-Wallpaper-images-full.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }
    .block-container {
        background-color: rgba(0, 0, 0, 0.65);
        padding: 2rem;
        border-radius: 12px;
    }
    .testimonial-slider {
        display: flex;
        overflow-x: auto;
        gap: 1rem;
        padding: 1rem;
    }
    .testimonial {
        min-width: 300px;
        flex: 0 0 auto;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        font-size: 0.95rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === Τίτλος και κείμενο καλωσορίσματος ===
st.title("🎮 Game Store Κωνσταντίνος & Δημήτρης")

st.markdown("""
## 🛍️ Το απόλυτο κατάστημα για gamers!
Καλωσορίσατε στο **Game Store ΚώσταςΜΕ2458 & ΔημήτριοςΜΕ2457**, το σημείο συνάντησης κάθε gamer που σέβεται τον εαυτό του!  
Ανακαλύψτε κορυφαίους τίτλους, απίστευτες προσφορές και μοναδικές εμπειρίες αγοράς.

🎯 **Γιατί εμάς;**
- ✔️ Μεγάλη ποικιλία παιχνιδιών για όλες τις πλατφόρμες  
- 🚀 Σούπερ γρήγορες αγορές και αποστολές  
- ❤️ Πιστοί πελάτες που μας λατρεύουν
""")

# === Testimonials ===
st.markdown("## 💬 Τι λένε οι χρήστες μας")

# Testimonials μέσα σε οριζόντια κύλιση
st.markdown("""
<div class="testimonial-slider">
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Απλά τέλειοι. Βρήκα το παιχνίδι που έψαχνα μήνες!”<br><br>— Γιάννης</div>
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Άμεση εξυπηρέτηση και τέλειες τιμές. Συνιστώ ανεπιφύλακτα!”<br><br>— Νίκη</div>
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Το UI της σελίδας είναι πανεύκολο. Αγόρασα χωρίς άγχος.”<br><br>— Τάσος</div>
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Πρώτη φορά αγοράζω online παιχνίδι τόσο εύκολα.”<br><br>— Δήμητρα</div>
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Πραγματικά εξαιρετική εμπειρία. Μπράβο παιδιά!”<br><br>— Κώστας</div>
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Πολύ οργανωμένο eshop. Εύκολο checkout!”<br><br>— Μαρία</div>
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Ταχύτατη αποστολή. Θα αγοράσω ξανά!”<br><br>— Βασίλης</div>
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Μοναδική ποικιλία παιχνιδιών σε προσφορές.”<br><br>— Ελένη</div>
  <div class="testimonial">⭐️⭐️⭐️⭐️⭐️<br><br>“Η καλύτερη εξυπηρέτηση που έχω δει.”<br><br>— Ανδρέας</div>
</div>
""", unsafe_allow_html=True)

# === Τελικό μήνυμα ===
st.markdown("""
---

🔗 **Μπες σήμερα στον κόσμο του gaming.**  
Φτιάξε το καλάθι σου και ετοιμάσου για ατελείωτες ώρες διασκέδασης!

📞 Επικοινωνία: support@gamestoretest.gr | ☎️ 210-1234567  
""")