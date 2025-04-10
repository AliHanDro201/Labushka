import os

client_id = os.getenv('SPOTIPY_CLIENT_ID')
if client_id:
    print("SPOTIPY_CLIENT_ID =", client_id)
else:
    print("Переменная SPOTIPY_CLIENT_ID не установлена.")
