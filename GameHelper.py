import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import json
import os
import requests
import re
from bs4 import BeautifulSoup

MEMORY_FILE = "memory.json"
GAMES_FILE = "games.json"
LLAMA_API_URL = "http://localhost:1234/v1/responses"
DUCKDUCKGO_SEARCH = "https://html.duckduckgo.com/html/"

def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def clean_memory(memory):
    cleaned = {}
    for game, messages in memory.items():
        cleaned[game] = [
            m for m in messages
            if isinstance(m, dict) and "user" in m and "nyra" in m
        ]
    return cleaned

def save_games():
    save_json(GAMES_FILE, list(games_listbox.get(0, tk.END)))

def game_adden():
    game_name = simpledialog.askstring("Add Game", "Which Game?")
    if game_name:
        games = games_listbox.get(0, tk.END)
        if game_name not in games:
            games_listbox.insert(tk.END, game_name)
            memory.setdefault(game_name, [])
            save_games()
            save_json(MEMORY_FILE, memory)

def remove_game():
    selected = games_listbox.curselection()
    if not selected:
        messagebox.showwarning("Remove Game", "Please select a game to remove")
        return

    for i in reversed(selected):
        g = games_listbox.get(i)
        games_listbox.delete(i)
        memory.pop(g, None)

    save_games()
    save_json(MEMORY_FILE, memory)

def exited():
    messagebox.showinfo("Exiting", "Good Bye")
    root.destroy()

def search_duckduckgo_facts(query):
    facts = {}
    try:
        r = requests.post(DUCKDUCKGO_SEARCH, data={"q": query}, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        results = soup.find_all("a", {"class": "result__a"})

        for a in results:
            href = a.get("href", "")
            if "fandom.com" in href or "wiki" in href:
                page = requests.get(href, timeout=20)
                psoup = BeautifulSoup(page.text, "html.parser")

                paragraphs = psoup.find_all("p")
                text = "\n".join(p.get_text() for p in paragraphs[:10])

                pattern = r"([A-Za-z ]+)[\s:]+([\d]+) ([A-Za-z ]+)"
                matches = re.findall(pattern, text)

                for item, qty, subitem in matches:
                    facts[item.strip()] = {subitem.strip(): int(qty)}

                if facts:
                    return facts

    except:
        return {}

    return facts

def is_suspicious(text):
    suspicious_words = ["maybe", "probably", "I think", "could be", "custom", "fan-made"]
    return any(w.lower() in text.lower() for w in suspicious_words)

def open_chat():
    selected_idx = games_listbox.curselection()
    if not selected_idx:
        messagebox.showwarning("Chat", "Please select a game first!")
        return

    game_name = games_listbox.get(selected_idx[0])
    memory.setdefault(game_name, [])

    chat_window = tk.Toplevel()
    chat_window.title(f"Chat - {game_name}")
    chat_window.geometry("500x550")

    chat_box = scrolledtext.ScrolledText(chat_window, width=60, height=25, state=tk.DISABLED)
    chat_box.pack(pady=10)

    chat_box.tag_config("user", foreground="red")
    chat_box.tag_config("nyra", foreground="blue")

    entry = tk.Entry(chat_window, width=40)
    entry.pack(side=tk.LEFT, padx=5, pady=5)

    def send_message():
        user_text = entry.get().strip()
        if not user_text:
            return

        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"You: {user_text}\n", "user")
        entry.delete(0, tk.END)

        history = memory.get(game_name, [])
        conversation = ""

        for msg in history[-5:]:
            conversation += f"User: {msg.get('user','')}\nAI: {msg.get('nyra','')}\n"

        facts = search_duckduckgo_facts(f"{game_name} {user_text}")

        if not facts:
            facts_prompt = "No verified facts found. Answer 'I don't know'."
        else:
            facts_prompt = "Facts:\n" + json.dumps(facts, indent=2)

        system_prompt = f"""
You are an expert for the game '{game_name}'.
Use ONLY verified facts. If unsure say 'I don't know'.

{facts_prompt}
"""

        payload = {
            "model": "Meta Llama 3.1 8B Instruct",
            "temperature": 0.0,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation + f"User: {user_text}"}
            ]
        }

        try:
            r = requests.post(LLAMA_API_URL, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()

            assistant_text = "I don't know"

            if "output" in data and data["output"]:
                assistant_text = data["output"][0]["content"][0].get("text", "I don't know")

        except Exception as e:
            assistant_text = f"Error: {e}"

        if is_suspicious(assistant_text):
            assistant_text = "I don't know"

        chat_box.insert(tk.END, f"Nyra: {assistant_text}\n\n", "nyra")
        chat_box.config(state=tk.DISABLED)
        chat_box.see(tk.END)

        memory.setdefault(game_name, []).append(
            {"user": user_text, "nyra": assistant_text}
        )

        save_json(MEMORY_FILE, memory)

    entry.bind("<Return>", lambda e: send_message())

    tk.Button(chat_window, text="Send", command=send_message).pack(side=tk.LEFT, padx=5, pady=5)

root = tk.Tk()
root.configure(bg="black")
root.title("Game Helper")
root.geometry("400x500")

games = load_json(GAMES_FILE, [])
memory = clean_memory(load_json(MEMORY_FILE, {}))

games_listbox = tk.Listbox(root, width=30, height=10, bg="red", fg="black")
games_listbox.pack(pady=10)

for game in games:
    games_listbox.insert(tk.END, game)

tk.Button(root, text="Open Chat", command=open_chat, bg="red", fg="black").pack(pady=5)
tk.Button(root, text="Add Game", command=game_adden, bg="red", fg="black").pack(pady=5)
tk.Button(root, text="Remove Game", command=remove_game, bg="red", fg="black").pack(pady=5)
tk.Button(root, text="Exit", command=exited, bg="red", fg="black").pack(pady=10)

root.mainloop()