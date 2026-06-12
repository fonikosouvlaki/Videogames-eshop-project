import requests
import json
from flask import request
from app import server
from app.model.games import Game
from app.model.cart import PurchasedCart

GROQ_API_KEY = "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"
url = "https://api.groq.com/openai/v1/chat/completions"

#Groq_Περίληψη Παιχνδιού
def groq_generate_summary(prompt):

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "temperature": 1,
        "max_completion_tokens": 1024,
        "top_p": 1,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Could not generate summary at the moment."

#Groq_Προτεινόμενα Βαση Αγορασμένου Καλαθιου
def get_game_suggestions(cart_id):
    cart = PurchasedCart.query.get(cart_id)
    if not cart:
        return {"error": "Cart not found"}, 404

    purchased_titles = [item.game.title for item in cart.items]

    all_games = Game.query.all()
    available_titles = [game.title for game in all_games if game.title not in purchased_titles]

    if not available_titles:
        return {"error": "No available games for suggestion"}, 400

    prompt = (
        f"A user purchased these games:\n"
        + "\n".join(f"- {title}" for title in purchased_titles)
        + "\n\nHere is the list of available games in stock:\n"
        + "\n".join(f"- {title}" for title in available_titles)
        + "\n\nBased on the user's purchase history, suggest 3 games that match their interests.\n"
        + "Only suggest from the available list."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "temperature": 1,
        "max_completion_tokens": 1024,
        "top_p": 1,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            return {"error": response.text}, response.status_code

        content = response.json()["choices"][0]["message"]["content"].strip()
        return {"suggestions": content}, 200
    except Exception as e:
        return {"error": str(e)}, 500