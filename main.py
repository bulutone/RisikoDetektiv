import mysql.connector
import requests
from datetime import date

db_host = ""
db_username = ""
db_password = ""
db_database = ""

try:
    db_connection = mysql.connector.connect(
        host=db_host,
        user=db_username,
        password=db_password,
        database=db_database
    )
    db_cursor = db_connection.cursor()
except mysql.connector.Error as err:
    print("Veritabanı hatası: {}".format(err))
    exit()

api_key = ""
channel_id = ""

def send_http_get(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as err:
        print("HTTP isteği hatası: {}".format(err))
        return None

def get_data_from_secretsite_muster(url):
    data = send_http_get(url)
    if data:
        return data.split('|---|---|---|---|---|')[1].split('> [!TIP]')[0]
    return None

def send_telegram_message(chat_id, msg):
    url = "https://api.telegram.org/bot{}/sendMessage".format(api_key)
    params = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "html",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("Telegram mesajı gönderme hatası: {}".format(err))

def process_data(data, channel_id, is_recent_victims=True):
    items = data.split('|---|---|---|---|---|')[1].split('> [!TIP]')
    
    for item in items[1:20]:
        item_parts = item.split('|')
        date = "{}{}".format(str(date.today().year), item_parts[0].strip())
        victim = item_parts[1].split('`')[1].strip()
        country = item_parts[2].split('[')[1].split(']')[0].strip() if '[' in item_parts[2] else ''
        ransom = item_parts[3].split('[')[1].split(']')[0].strip()
        img = item_parts[4].split('href="')[1].split('"')[0].strip() if 'href="' in item_parts[4] else ''

        if country == 'DE':
            check_query = "SELECT 1 FROM `recentvictims` WHERE `date` = %s AND `ransom` = %s AND `victim` = %s AND `img` = %s"
            check_values = (date, ransom, victim, img)
            db_cursor.execute(check_query, check_values)
            if db_cursor.rowcount <= 0:
                msg = "🇩🇪 Country: Deutschland\n\n📆 Attack Date: {}\n\n🥷 Ransomware Group: {}\n\n📌 Victim: {}\n\n🔗 @RisikoDetektiv".format(date, ransom, victim)
                print(msg)
                if img:
                    send_telegram_message(channel_id, msg)
                else:
                    send_telegram_message(channel_id, msg)
                insert_query = "INSERT INTO `recentvictims` (`id`, `date`, `ransom`, `victim`, `img`) VALUES (NULL, %s, %s, %s, %s)"
                insert_values = (date, ransom, victim, img)
                db_cursor.execute(insert_query, insert_values)
                db_connection.commit()

if __name__ == "__main__":
    # Recent Victims
    victims_url = "https://secretsite.muster"
    victims_data = get_data_from_secretsite_muster(victims_url)
    if recent_victims_data:
        process_data(victims_data, channel_id)

    # Recent Cyber Attacks
    cyber_attacks_url = "https://secretsite.muster/recentcyberattacks.md"
    cyber_attacks_data = get_data_from_secretsite_muster(cyber_attacks_url)
    if cyber_attacks_data:
        process_data(cyber_attacks_data, channel_id, is_victims=False)

    db_cursor.close()
    db_connection.close()
