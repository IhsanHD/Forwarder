import re
import telebot
import git
import os
import base64
import json

# Ganti dengan token bot Telegram Anda
BOT_TOKEN = "7013294958:AAGFR7tjZgsyRjfS5kRgy8cd-HsH5qCZWsI"
GITHUB_REPO_PATH = "/root/python/Forwarder/repo/ConfigOC/"  # Path ke repo lokal
GITHUB_COMMIT_MESSAGE = "Auto update vmess output"

bot = telebot.TeleBot(BOT_TOKEN)

counter = 1  # Auto-increment counter


def decode_vmess(vmess_encoded):
    try:
        vmess_data = base64.b64decode(vmess_encoded.replace("vmess://", "")).decode(
            "utf-8"
        )
        return json.loads(vmess_data)
    except Exception as e:
        return None


def convert_vmess_format(vmess_url):
    global counter
    vmess_data = decode_vmess(vmess_url)
    if not vmess_data:
        return "Invalid VMess URL format"

    # Ambil data yang benar dari VMess
    name = vmess_data.get(
        "ps", f"Vmess WS (SNI) {counter}"
    )  # Gunakan nama dari VMess jika ada
    server = vmess_data.get("add", "104.17.3.81")  # Gunakan alamat asli jika ada
    port = vmess_data.get("port", "443")
    uuid = vmess_data.get("id", "UUID")
    path = vmess_data.get("path", "/vmess")
    sni = vmess_data.get("sni", server)  # Jika SNI tidak ada, gunakan server
    host = vmess_data.get("host", server)  # Gunakan host dari VMess jika ada

    converted_format = (
        f"proxies:\n"
        f"- name: Vmess WS (SNI) {counter}\n"
        f"  type: vmess\n"
        f"  server: 104.17.3.81\n"
        f"  port: 443\n"
        f"  uuid: {uuid}\n"
        f"  alterId: 0\n"
        f"  cipher: auto\n"
        f"  udp: true\n"
        f"  tls: true\n"
        f"  skip-cert-verify: true\n"
        f"  servername: {sni}\n"
        f"  network: ws\n"
        f"  ws-opts:\n"
        f"    path: {path}\n"
        f"    headers:\n"
        f"      Host: {sni}\n"
        f"- name: Vmess WS (SNI) {counter + 1}\n"
        f"  type: vmess\n"
        f"  server: {sni}\n"
        f"  port: 443\n"
        f"  uuid: {uuid}\n"
        f"  alterId: 0\n"
        f"  cipher: auto\n"
        f"  udp: true\n"
        f"  tls: true\n"
        f"  skip-cert-verify: true\n"
        f"  servername: meetings.googleapis.com\n"
        f"  network: ws\n"
        f"  ws-opts:\n"
        f"    path: {path}\n"
        f"    headers:\n"
        f"      Host: meetings.googleapis.com\n"
    )
    counter += 1  # Increment untuk sesi berikutnya
    return converted_format.strip()


def save_and_push_to_github(data):
    file_path = os.path.join(GITHUB_REPO_PATH, "vmess_output.yaml")

    # Pastikan direktori ada
    if not os.path.exists(GITHUB_REPO_PATH):
        os.makedirs(GITHUB_REPO_PATH)

    # Simpan ke file
    with open(file_path, "w") as file:
        file.write(data)

    # Push ke GitHub secara otomatis
    try:
        repo = git.Repo(GITHUB_REPO_PATH)
        repo.git.add(file_path)
        repo.index.commit(GITHUB_COMMIT_MESSAGE)
        origin = repo.remote(name="origin")
        origin.pull()  # Pull sebelum push untuk menghindari konflik
        origin.push()
    except Exception as e:
        print(f"Git push error: {e}")


@bot.message_handler(func=lambda message: message.text.startswith("vmess://"))
def handle_vmess_link(message):
    vmess_url = message.text
    converted_text = convert_vmess_format(vmess_url)

    # Simpan output dan push ke GitHub
    save_and_push_to_github(converted_text)

    bot.reply_to(message, f"```\n{converted_text}\n```", parse_mode="Markdown")


print("Bot is running...")
bot.polling()
