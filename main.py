import telebot
import psutil
import platform
import subprocess
import os



bot = telebot.TeleBot('API')

# Разрешённые пользователи
allowedAccounts = []
blockedUsers = []

# Хранение состояния пользователей, которым разрешено
user_allowed_state = {}

def get_ram_info():
    mem = psutil.virtual_memory()
    return {
        "total": f"{mem.total / (1024**3):.2f} GB",
        "used": f"{mem.used / (1024**3):.2f} GB",
        "free": f"{mem.available / (1024**3):.2f} GB",
        "percent": f"{mem.percent} %"
    }

def get_cpu_info():
    load1, load5, load15 = os.getloadavg()
    cpu_count = psutil.cpu_count()
    return {
        "load_avg": f"{load1:.2f}, {load5:.2f}, {load15:.2f}",
        "cores": cpu_count,
        "usage_per_core": [f"{x}%" for x in psutil.cpu_percent(percpu=True, interval=1)],
        "total_usage": f"{psutil.cpu_percent()} %"
    }

def get_disk_info():
    disk = psutil.disk_usage('/')
    return {
        "total": f"{disk.total / (1024**3):.2f} GB",
        "used": f"{disk.used / (1024**3):.2f} GB",
        "free": f"{disk.free / (1024**3):.2f} GB",
        "percent": f"{disk.percent} %"
    }

def get_system_info():
    uname = platform.uname()
    return {
        "system": uname.system,
        "node": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor
    }

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    if user_id in allowedAccounts:
        user_allowed_state[user_id] = True
        bot.reply_to(message, "✅ Доступ разрешён. Используй команды /ram /cpu /disk /sysinfo")
    else:
        if user_id in blockedUsers:
            return
        else:
            blockedUsers.append(user_id)
            bot.reply_to(message, "⛔ Доступ запрещён")
            # Уведомить администратора
            #bot.send_message(message.chat.id администратора, f"Запрос от неизвестного пользователя: {user_id}")

@bot.message_handler(commands=['ram'])
def ram_info(message):
    if user_allowed_state.get(message.chat.id):
        ram = get_ram_info()
        text = "\n".join([f"{k.capitalize()}: {v}" for k, v in ram.items()])
        bot.reply_to(message, f"💾 ОЗУ:\n{text}")

@bot.message_handler(commands=['cpu'])
def cpu_info(message):
    if user_allowed_state.get(message.chat.id):
        cpu = get_cpu_info()
        text = f"Загрузка: {cpu['load_avg']}\nЯдер: {cpu['cores']}\nОбщая нагрузка: {cpu['total_usage']}\n"
        per_core = "\n".join([f"Ядро {i+1}: {x}" for i, x in enumerate(cpu['usage_per_core'])])
        bot.reply_to(message, f"🖥️ CPU:\n{text}\n{per_core}")

@bot.message_handler(commands=['disk'])
def disk_info(message):
    if user_allowed_state.get(message.chat.id):
        disk = get_disk_info()
        text = "\n".join([f"{k.capitalize()}: {v}" for k, v in disk.items()])
        bot.reply_to(message, f"📦 Диск:\n{text}")

@bot.message_handler(commands=['sysinfo'])
def sysinfo(message):
    if user_allowed_state.get(message.chat.id):
        sysinfo = get_system_info()
        text = "\n".join([f"{k.capitalize()}: {v}" for k, v in sysinfo.items()])
        bot.reply_to(message, f"🧰 Система:\n{text}")

mem = psutil.virtual_memory()
cpu = get_cpu_info()
if mem.percent > 86.0:
    for n,account in enumerate(allowedAccounts):
        bot.send_message(account, f"озу заполнена на {cpu['total_usage']}% критично")
if psutil.cpu_percent() > 92.0:
    for n,account in enumerate(allowedAccounts):
        bot.send_message(account, f"нагрузка на процессор критична: {cpu['total_usage']}%")


bot.infinity_polling() 
