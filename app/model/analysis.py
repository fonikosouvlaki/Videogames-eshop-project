import matplotlib
matplotlib.use('Agg') #Για απεικονηση στο ποστμαν αναγκαστικά
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from app.model.cart import PurchasedCart
from app.model.games import Game, db
import io

# --- Γράφημα Παλινδρόμησης (Linear Regression) ---
def run_analysis(): 
    carts = PurchasedCart.query.all() #Δες όλα τα αγορασμένα καλάθια

    if not carts:
        print("No purchased carts found.")
        return None, None

    # Προετοιμασια Δεδομενων
    cart_dates = []
    total_cart_prices = []

    for cart in carts:
        if cart.purchased_at:
            cart_total = sum( #Σύνολο καλαθιού
                item.game.price for item in cart.items if item.game and item.game.price is not None
            )
            cart_dates.append(cart.purchased_at)
            total_cart_prices.append(cart_total)

    if not cart_dates:
        print("No valid cart data with dates and prices.")
        return None, None

    # Regression γραφημα
    dates_ordinal = [d.toordinal() for d in cart_dates]
    coeffs = np.polyfit(dates_ordinal, total_cart_prices, 1) #Χρησιμοποιεί γραμμική παλινδρόμηση (linear regression) για να βρει τη γραμμή που προσεγγίζει τα δεδομένα.
    trend = np.poly1d(coeffs) #Η trend(x) είναι μια εξίσωση που προβλέπει την αξία καλαθιού για κάποια ημερομηνία x.
    future_x = np.linspace(min(dates_ordinal), max(dates_ordinal) + 30, 100) #Η Python μετατρέπει τις ημερομηνίες σε ακέραιους αριθμούς (π.χ. 2025-05-24 → 738300), γιατί για την εξίσωση της γραμμής (regression) χρειαζόμαστε αριθμούς.
    future_y = trend(future_x) #Φτιάχνει 100 σημεία μελλοντικού χρόνου (μέχρι 30 μέρες μπροστά).Υπολογίζει την προβλεπόμενη αξία για κάθε μελλοντική ημερομηνία.

    plt.figure(figsize=(10, 6))
    plt.scatter(cart_dates, total_cart_prices, label="Historical Carts", color="blue")
    plt.plot([datetime.fromordinal(int(x)) for x in future_x], future_y, label="Estimated Trend", color="red")
    plt.xlabel("Date")
    plt.ylabel("Total Cart Value (€)")
    plt.title("Cart Value Over Time")
    plt.legend()
    plt.tight_layout()

    # Αποθηκευση σε buffer
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    plt.close()

# --- Γράφημα Πίτα: Top 5 Game Sales as Percentages ---

    game_frequency = {}
    for cart in carts:
        for item in cart.items:
            if item.game:
                title = item.game.title
                game_frequency[title] = game_frequency.get(title, 0) + 1

    # Ταξινόμησε βάση συχνότητας
    sorted_games = sorted(game_frequency.items(), key=lambda x: x[1], reverse=True)
    total_sales = sum(count for _, count in sorted_games)

    # Top 5 + Υπόλοιπα(Other)
    top_games = sorted_games[:5]
    other_games = sorted_games[5:]

    top_labels = [title for title, _ in top_games]
    top_counts = [count for _, count in top_games]

    # Άθροισμα "Other" sales
    other_count = sum(count for _, count in other_games)
    if other_count > 0:
        top_labels.append("Other")
        top_counts.append(other_count)

    # Plot pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(
    top_counts,
    labels=top_labels,
    autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
    startangle=140
    )
    plt.title("Top 5 Game Sales (as % of Total Sales)")
    plt.tight_layout()

    # Save to buffer
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    plt.close()

    return buf1, buf2