import tkinter as tk
from tkinter import messagebox
import requests  # pip install requests
import asyncio
import threading
import websockets
import json
import ssl

WS_BASE_URI = "wss://stream.binance.com:9443/ws/{}@trade"
LOGIN_API_URL = "http://localhost:8000/api/login"  # приклад API логіну

class CryptoClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Updates Client")
        self.root.geometry("400x500")

        self.text = tk.Text(root)
        self.text.pack(pady=10, padx=10, expand=True)

        self.symbols = ["btcusdt", "ethusdt", "bnbusdt", "xrpusdt"]
        self.selected_symbol = tk.StringVar(value=self.symbols[0])
        self.dropdown = tk.OptionMenu(root, self.selected_symbol, *self.symbols)
        self.dropdown.pack(pady=5)

        # Поля для логіна і пароля
        self.login_entry = tk.Entry(root)
        self.login_entry.pack(pady=2)
        self.login_entry.insert(0, "Username")

        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=2)
        self.password_entry.insert(0, "Password")

        tk.Button(root, text="Login", command=self.login).pack(pady=5)
        tk.Button(root, text="Get User Info", command=self.user_info).pack(pady=5)
        tk.Button(root, text="Subscribe to Updates", command=self.start_ws).pack(pady=10)

        self.ssl_context = ssl._create_unverified_context()

        self.token = None  # Токен після логіну

    def login(self):
        username = self.login_entry.get()
        password = self.password_entry.get()
        try:
            response = requests.post(LOGIN_API_URL, json={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                messagebox.showinfo("Login", "Login successful!")
            else:
                messagebox.showerror("Login Failed", f"Error: {response.text}")
        except Exception as e:
            messagebox.showerror("Login Failed", str(e))

    def user_info(self):
        if not self.token:
            messagebox.showwarning("Warning", "Please login first!")
            return
        # Тут можна зробити запит з токеном, наприклад, отримати інфо про користувача
        messagebox.showinfo("User", f"User info request (token: {self.token})")

    def start_ws(self):
        # Логін тепер необов’язковий, просто попередження
        if not self.token:
            messagebox.showinfo("Info", "You are not logged in. You can still view currency updates.")

        self.text.delete("1.0", tk.END)
        threading.Thread(target=self.run_ws, daemon=True).start()

    def run_ws(self):
        asyncio.run(self.ws_handler())

    async def ws_handler(self):
        symbol = self.selected_symbol.get()
        uri = WS_BASE_URI.format(symbol)
        try:
            async with websockets.connect(uri, ssl=self.ssl_context) as ws:
                self.update_ui(f"Subscribed to {symbol.upper()} updates...\n")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    price = float(data['p'])
                    self.update_ui(f"{symbol.upper()}: ${price:.2f}")
        except Exception as e:
            self.update_ui(f"[Error] {e}\n")

    def update_ui(self, text):
        self.text.insert("1.0", text + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoClient(root)
    root.mainloop()
