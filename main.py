import webbrowser

import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import time


BASE_URL = 'https://www.jobs.ge/?page=1&q=&cid=6&lid=&jid='
token = ""

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('საიტზე გადასვლა')
    markup.row(btn1)
    bot.send_message(message.chat.id, f'გამარჯობა, {message.from_user.first_name} მე დაგეხმარები სასურველი სამუშაოს'
                                      f' მოძებნაში IT სფეროში, დაწერე საძიებო სიტყვა და მე ვიპოვი ყველა ვაკანსიას'
                                      f' შენს მაგივრად 😉', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text == 'საიტზე გადასვლა':
        webbrowser.open(url='https://www.jobs.ge/')


@bot.message_handler(commands=['find'])
def find(message):
    bot.send_message(message.chat.id, f'ჩაწერე საძიებო სიტყვა და ვაკანსიას    მე ვიპოვი 🧐')
    bot.register_next_step_handler(message, message_info)


def message_info(message):
    num = 0
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    jobs = soup.find_all('a', class_='vip')
    for job in jobs:
        if message.text in job.text:
            href = job['href']
            job_url = f'https://www.jobs.ge{href}'
            response_job = requests.get(job_url)
            job_soup = BeautifulSoup(response_job.content, 'html.parser')
            english = job_soup.find('a', href=f"/en/{href[4:]}").find_next('a', string='ინგლისურ ენაზე')
            if english:
                eng_url = f"https://www.jobs.ge{english['href']}"
                eng_response = requests.get(eng_url)
                text_soup = BeautifulSoup(eng_response.content, "html.parser")
                en_texts = text_soup.find('td', style="padding-top:30px; padding-bottom:40px;").text
                bot.send_message(message.chat.id, f"🟢 {job.text} 🟢")
                if len(en_texts) > 4096:
                    for x in range(0, len(en_texts), 4096):
                        bot.send_message(message.chat.id, en_texts[x:x + 4096])
                else:
                    bot.send_message(message.chat.id, f"{en_texts}")
            else:
                bot.send_message(message.chat.id, f"🟢 {job.text} 🟢")
                job_text = job_soup.find('td', style="padding-top:30px; padding-bottom:40px;").text
                if len(job_text) > 4096:
                    for x in range(0, len(job_text), 4096):
                        bot.send_message(message.chat.id, job_text[x:x + 4096])
                else:
                    bot.send_message(message.chat.id, job_text)
            time.sleep(1.5)
            num += 1
    if num:
        bot.send_message(message.chat.id, f"✅  '{message.text}' ამ პოზიციაზე მოიძებნა {num} ვაკანსია  ✅")
    else:
        bot.send_message(message.chat.id, f"❌  '{message.text}' ამ მოთხოვნაზე ვაკანსია ვერ მოიძებნა 😕 გადაამოწმეთ "
                                          f"ტექსტი სწორია თუ არა ის 👀  ❌")
    num = 0


@bot.message_handler(commands=['exit'])
def close(message):
    bot.send_message(message.chat.id, "კარგათ იმედია შევძელი შენი დახმარება წარმატებები 😄")


@bot.message_handler()
def non_message(message):
    bot.send_message(message.chat.id, "თუ გსურთ ვაკანსიის მოძებნა დაწერეთ '/find'")


bot.infinity_polling()
