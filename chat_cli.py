# chat_cli.py
import requests, json

URL = "http://127.0.0.1:8000/chat"
messages = []

def send(user_text):
    messages.append({"role":"user","content":user_text})
    r = requests.post(URL, json={"messages": messages})
    data = r.json()
    if "tool_result" in data:
        bot_text = json.dumps(data["tool_result"], ensure_ascii=False)
    else:
        bot_text = data.get("reply", "")
    print("Bot:", bot_text)
    messages.append({"role":"assistant","content":bot_text})

def main():
    print("Çıkmak için 'exit' yazın.\n")
    while True:
        u = input("Sen: ")
        if u.lower() in {"exit","quit"}:
            break
        send(u)

if __name__ == "__main__":
    main()
