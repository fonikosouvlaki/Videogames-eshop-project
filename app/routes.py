import datetime
from flask import request
from flask import Flask, send_file
from app import server
from app.model.games import Game, db
from app.model.cart import Cart, CartItem
from app.model.cart import PurchasedCart, PurchasedCartItem
from app.model.scraper import scrape_price_from_consoleclub,scrape_price_from_gamestory
from app.groq import groq_generate_summary
from app.groq import get_game_suggestions
import subprocess
from app.model.analysis import run_analysis
import os

# Game Routes

@server.route("/games", methods=["GET"])  # Αναζήτηση όλων των παιχνιδιών
def games():
    game_id = request.args.get("id")
    
    if game_id:
        game = Game.query.get(game_id)
        return (game.to_dict(), 200) if game else ("Game not found", 404)
    
    else:
        games = Game.query.all()

        # Ομαδοποίηση κατά platform
        grouped = {}
        for game in games:
            platform = game.platform or "Unknown"
            if platform not in grouped:
                grouped[platform] = []
            grouped.setdefault(platform,[]).append(game.to_dict())

        return grouped, 200


@server.route("/games", methods=["POST"]) #Προσθήκη νέου παιχνιδιού
def add_game():
    data = request.get_json()
    if not data:
        return "Missing parameters", 400
    if not all(data.get(k) for k in ["title", "platform", "price", "genre"]):
        return "Missing parameters", 400

    game = Game(
        title=data.get("title"),
        platform=data.get("platform"),
        genre=data.get("genre"),
        price=data.get("price"),
        description=data.get("description"),
        image_url=data.get("image_url")
    )

    db.session.add(game)
    db.session.commit()
    return "CREATED", 201


@server.route("/games/<id>", methods=["DELETE"]) #Διαγραφή παιχνιδιού με ID
def delete_game(id):
    game = Game.query.get(id)
    if not game:
        return "Game not found", 404
    db.session.delete(game)
    db.session.commit()
    return "OK", 200


@server.route("/games/<id>", methods=["PUT"]) #Ενημέρωση παιχνδιού
def update_game(id):
    title = request.args.get("title")
    platform = request.args.get("platform")
    genre = request.args.get("genre")
    price=request.args.get("price")
    description=request.args.get("description")
    image_url=request.args.get("image_url")


    game = Game.query.get(id)
    if not game:
        return "Game not found", 404

    # update ΜΟΝΟ σε οτι δωσαμε
    if title:
        game.title = title
    if platform:
        game.platform = platform
    if genre:
        game.genre = genre
    if description:
        game.description = description
    if image_url:
        game.image_url = image_url
    if price:
        try:
            game.price = float(price)
        except ValueError:
            return "Invalid price value", 400

    db.session.commit()
    return "OK", 200


@server.route("/games/search", methods=["GET"])
def search_games():
    title = request.args.get("title")
    genre = request.args.get("genre")
    platform = request.args.get("platform")
    price = request.args.get("price", type=float)
    description = request.args.get("description")
    sort_by = request.args.get("sort_by", default="title")
    order = request.args.get("order", default="asc")

    query = Game.query

    if title:
        query = query.filter(Game.title.ilike(f"%{title}%"))
    if genre:
        query = query.filter(Game.genre.ilike(f"%{genre}%"))
    if platform:
        query = query.filter(Game.platform.ilike(f"%{platform}%"))
    if price is not None:
        query = query.filter(Game.price <= price)
    if description:
        query = query.filter(Game.description.ilike(f"%{description}%"))

    sort_fields = {
        "title": Game.title,
        "price": Game.price,
        "platform": Game.platform,
        "genre": Game.genre
    }

    sort_column = sort_fields.get(sort_by, Game.title)
    if order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = query.order_by(sort_column)
    games = query.all()

    # ✅ Group games by platform
    grouped = {}
    for game in games:
        g = game.platform or "Unknown"
        grouped.setdefault(g, []).append(game.to_dict())

    return grouped, 200

# Available Καλαθια

@server.route("/cart", methods=["POST"]) #Δημιουργία Νέου Άδειου Καλαθιού
def create_cart():
    cart = Cart()
    db.session.add(cart)
    db.session.commit()
    return {
        "cart_id": cart.id,
        "created_at": cart.created_at.isoformat()
    }, 201


@server.route("/cart/<cart_id>/add", methods=["POST"]) #Προσθήκη παιχνιδιού σε συγκεκριμένο καλάθι
def add_to_cart(cart_id):
    data = request.get_json()
    game_id = data.get("game_id")
    if not game_id:
        return "Missing game_id", 400

    cart = Cart.query.get(cart_id)
    game = Game.query.get(game_id)
    if not cart or not game:
        return "Cart or Game not found", 404

    item = CartItem(cart_id=cart.id, game_id=game.id)
    db.session.add(item)
    db.session.commit()
    return "Game added to cart", 200


@server.route("/cart/<cart_id>/remove", methods=["POST"]) #Αφαίρεση παιχνδιού απο συγκεκριμένο καλάθι
def remove_from_cart(cart_id):
    data = request.get_json()
    game_id = data.get("game_id")
    if not game_id:
        return "Missing game_id", 400

    item = CartItem.query.filter_by(cart_id=cart_id, game_id=game_id).first()
    if not item:
        return "Item not found in cart", 404

    db.session.delete(item)
    db.session.commit()
    return "Game removed from cart", 200


@server.route("/cart/<cart_id>", methods=["GET"]) #Προβολή συγκεκριμένου καλαθιού
def view_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return "Cart not found", 404

    return {
        "cart_id": cart.id,
        "created_at": cart.created_at.isoformat(),
        "items": [
            {
                "game_id": item.game.id,
                "title": item.game.title,
                "price": item.game.price,
                "platform": item.game.platform,
                "genre": item.game.genre,
                "description": item.game.description,
                "image_url": item.game.image_url    
            }
            for item in cart.items
        ]
    }, 200

@server.route("/carts", methods=["GET"]) #Προβολή όλων των Διαθέσιμων/Active καλαθιών
def list_carts():
    carts = Cart.query.all()
    return [
        {
            "cart_id": cart.id,
            "created_at": cart.created_at.isoformat(),
            "items_count": len(cart.items)
        }
        for cart in carts
    ]

# Αγορασμένα Καλαθια

@server.route("/cart/<cart_id>/purchase", methods=["POST"]) #Αγορά ενός Διαθέσιμου/Active Καλαθιού
def purchase_cart(cart_id):
    data = request.get_json()
    if not data or "purchased_at" not in data:
        return {"error": "Date and time are required"}, 400

    try:
        purchased_at = datetime.datetime.fromisoformat(data["purchased_at"]) #isoformat για συγκεκριμένο τρόπο υποβολής ημερομηνίας αγοράς
    except ValueError:
        return {"error": "Invalid datetime format. Use ISO format (e.g., 2025-05-08T15:30:00)"}, 400

    cart = Cart.query.get(cart_id)
    if not cart:
        return {"error": "Cart not found"}, 404

    purchased_cart = PurchasedCart(id=cart.id, purchased_at=purchased_at) #Δημιουργία Αγορασμένου Καλαθιού
    db.session.add(purchased_cart)

    for item in cart.items:
        purchased_item = PurchasedCartItem(
            purchased_cart_id=cart.id,
            game_id=item.game_id
        )
        db.session.add(purchased_item)

    db.session.delete(cart)#Διαγραφή Διαθέσιμου Καλαθιού
    db.session.commit()

    return {
        "message": "Cart purchased successfully",
        "purchased_cart_id": purchased_cart.id,
        "purchased_at": purchased_cart.purchased_at.isoformat()
    }, 200

@server.route("/purchases", methods=["GET"]) #Προβολή όλων των Αγορασμένων Καλαθιών
def view_purchased_carts():
    purchased_carts = PurchasedCart.query.all()

    result = []
    for cart in purchased_carts:
        items = []
        for item in cart.items:
            if item.game:  # Ελέγχουμε αν υπάρχει το παιχνίδι πλέον στη ΒΔ μας
                items.append({
                    "game_id": item.game_id,
                    "game_title": item.game.title
                })
            else:
                items.append({
                    "game_id": item.game_id,
                    "game_title": "Unknown Game (Deleted or Missing)"
                })

        result.append({
            "purchased_cart_id": cart.id,
            "purchased_at": cart.purchased_at.isoformat(),
            "items": items
        })

    return {"purchased_carts": result}, 200

# Scraper 1

@server.route("/scrape", methods=["GET"])
def scrape_game_price():
    game_id = request.args.get("id")
    game = Game.query.get(game_id)

    if not game:
        return "Game not found", 404

    title, price, image_url = scrape_price_from_consoleclub(game.title, game.platform)

    return (
        f"Title: {title}\n"
        f"Price: {price}\n"
        f"Image URL: {image_url}\n"
        f"Scraping complete", 
        200
    )

# Scraper 2

@server.route("/scrape/gamestory", methods=["GET"])
def scrape_game_price_gamestory():
    game_id = request.args.get("id")
    game = Game.query.get(game_id)

    if not game:
        return "Game not found", 404

    title, price, image_url = scrape_price_from_gamestory(game.title, game.platform)

    return (
        f"Title: {title}\n"
        f"Price: {price}\n"
        f"Image URL: {image_url}\n"
        f"Scraping complete from Gamestory", 
        200
    )

#Analysis

@server.route('/analysis/plot1')
def analysis_plot1():
    buf1, buf2 = run_analysis()
    if not buf1:
        return "No data available", 400
    return send_file(buf1, mimetype='image/png')

@server.route('/analysis/plot2')
def analysis_plot2():
    buf1, buf2 = run_analysis()
    if not buf2:
        return "No data available", 400
    return send_file(buf2, mimetype='image/png')

#Groq_Summary
@server.route("/games/summary", methods=["GET"])
def get_game_summary():
    title = request.args.get("title")
    game = Game.query.filter(Game.title.ilike(f"%{title}%")).first()

    if not game:
        return {"error": "Game not found in database"}, 404

    prompt = f"Write a short, informative summary of the video game '{game.title}'. Include its genre, story, and why people enjoy it."
    summary = groq_generate_summary(prompt)
    
    return {
        "game": game.title,
        "summary": summary
    }, 200

#Groq_cart_suggestion 
@server.route("/suggest/<cart_id>", methods=["GET"])
def suggest_games(cart_id):
    return get_game_suggestions(cart_id)