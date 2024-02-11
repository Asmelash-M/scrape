import requests
import sys
from bs4 import BeautifulSoup
from telegram import Bot
import time
import telebot
from io import BytesIO

# Telegram bot token
TOKEN = '6948815289:AAHO5TRZJ4zCyVob9bm-3PdGdXOHVC4MdUA'
# Telegram channel ID or username
telegram_channel_username = '@composure0947'


def send_photo_to_telegram(chat_id, photo, caption, token):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        'chat_id': chat_id,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    files = {
        'photo': photo.getvalue()
    }
    response = requests.post(url, data=payload, files=files)
    return response.json()


urls = {
    'ነፃ አስተያየቶች': 'https://amharic.zehabesha.com/%E1%88%AD%E1%8B%95%E1%88%B5/%e1%8a%90%e1%8d%83-%e1%8a%a0%e1%88%b5%e1%89%b0%e1%8b%ab%e1%8b%a8%e1%89%b6%e1%89%bd',
    'ሰብአዊ መብት': 'https://amharic.zehabesha.com/%E1%88%AD%E1%8B%95%E1%88%B5/%e1%88%b0%e1%89%a5%e1%8a%a0%e1%8b%8a-%e1%88%98%e1%89%a5%e1%89%b5',
    'ከታሪክ ማህደር': 'https://amharic.zehabesha.com/%E1%88%AD%E1%8B%95%E1%88%B5/%e1%8a%a8%e1%89%b3%e1%88%aa%e1%8a%ad-%e1%88%9b%e1%88%85%e1%8b%b0%e1%88%ad',
    'የህይወት ታሪክ': 'https://amharic.zehabesha.com/%E1%88%AD%E1%8B%95%E1%88%B5/%e1%8b%a8%e1%88%85%e1%8b%ad%e1%8b%88%e1%89%b5-%e1%89%b3%e1%88%aa%e1%8a%ad',
    'ኢኮኖሚ': 'https://amharic.zehabesha.com/%E1%88%AD%E1%8B%95%E1%88%B5/%e1%8a%a2%e1%8a%ae%e1%8a%96%e1%88%9a',
    'ኪነ ጥበብ':'https://amharic.zehabesha.com/%E1%88%AD%E1%8B%95%E1%88%B5/%e1%8a%aa%e1%8a%90-%e1%8c%a5%e1%89%a0%e1%89%a5',
    'ጤና': 'https://amharic.zehabesha.com/%E1%88%AD%E1%8B%95%E1%88%B5/%e1%8c%a4%e1%8a%93',
    'ፖለቲካ': 'https://amharic.zehabesha.com/%E1%88%AD%E1%8B%95%E1%88%B5/%e1%8d%96%e1%88%88%e1%89%b2%e1%8a%ab'
}
categories = urls.keys()


def scrape(category):
    if category in categories:
        response = requests.get(urls[category], timeout=30)

        s = BeautifulSoup(response.text, 'html.parser')
        posts = s.find_all(lambda tag: tag.name == 'article' and 'post' in tag.get('class', []))


        for post in posts:
            try:
                title = post.find('a', {'rel': 'bookmark'}).text.strip()
                link = post.find('a', {'rel': 'bookmark'})['href'].strip()
                image_element = post.find('img')
                image = image_element['data-src'] if image_element else ''
                photo = BytesIO(requests.get(image, timeout=30).content)
                date = post.find('time').text.strip()
                content = post.find('p').text.strip()
                # storing the categories in a list
                categories_div = post.find('div', class_='entry-categories')
                categories_list = []
                if categories_div:
                    category_tags = categories_div.find_all('a')
                    for category_tag in category_tags:
                        categories_list.append(category_tag.text.strip().replace("'", ''))
                        post_tags = '   '.join([f'#{tag.replace(' ', '_')}' for tag in categories_list])

                # Format the message to be sent to the Telegram channel
                message = f'<b>{title}</b>\n\n{date}\n\n{content}\n<a href="{link}">Read More</a>\n\n{post_tags}'
                # print(message)

                # Send the message to the Telegram channel
                send_photo_to_telegram(chat_id=telegram_channel_username ,photo=photo, caption=message, token=TOKEN)

                # to stop for some time between posts
                time.sleep(7)
            except UnicodeEncodeError:
                print(post.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))


""" bot commands """
                
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    # Check if category is provided in the command
    words = message.text.split()
    if len(words) > 1:
        # Extract the category from the command
        category = ' '.join(words[1:])
        bot.send_message(message.chat.id, f"Started posting items in {category}\n")
        send_updates(message.chat.id, category)
    else:
        # Provide instructions to the user if no category is provided
        bot.send_message(message.chat.id, f"Welcome to the Bot!\n"
                                          f"Send /start followed by category to start posting\n\n"
                                          f"send one of the following commands, <u>click to copy</u>:\n\n"
                                          f"{''.join([f'<code>/start {category}</code>\n' for category in categories])}"
                         , parse_mode='HTML')


def send_updates(chat_id, category=None):
    if category:
        # Scrape data for the specified category
        scrape(category)

    # Sleep for a short time before sending the next update
    time.sleep(6000)


# Start polling for messages
bot.polling(non_stop=True)