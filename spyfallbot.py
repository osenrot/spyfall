# Made by ***

# Import statements
import telebot
import numpy as np
import pandas as pd
from datetime import datetime
import time
# REST API library to access Yandex Disk
import yadisk
import sys

# Import my data analysis package
sys.path.append('..')

bot = telebot.TeleBot('597504356:AAHJAVOybNjqysf9OoLTo32NTT75SWyCmEU')

# Declare the logging dictionaries
participants_dict = dict()
location_dict = dict()
spy_set_dict = dict()

# Declare global ctime variable
ctime = datetime.now()

# Declare YaDisk connection
y = yadisk.YaDisk("5c4bff878884430d9814c1a1922e55b5",
                  "4a9cc6ad35dd4f4ca8ba1d26c51d9225",
                  "AQAAAAAzlyZ6AAWdXWc6f_yE9EHUv4xX3KETv5Q")


# Synchronize files with Ya Disk
def upload_to_yadisk():
    y.upload("game_stats.csv", "/game_stats.csv")
    y.upload("spyfalllocations.txt", "/spyfalllocations.txt")


def download_from_yadisk():
    y.download("/game_stats.csv", "game_stats.csv")
    y.download("/spyfalllocations.txt", "spyfalllocations.txt")


game_stats = pd.read_csv('game_stats.csv', sep=';', index_col=0, parse_dates=True)


# Declare the default location set
with open('spyfalllocations.txt', 'r', encoding='utf8') as f:
    location_set = f.read().splitlines()
location_set_name = '/def'


# Handle the /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Send the intro message
    intro_message_text = ''' 
Register all the participants. To participate print "/participate".
To start the game print "/startgame". To reset print "/reset".
Before the game starts every participant needs to write something to the bot in private messages.
'''
    bot.send_message(message.chat.id, intro_message_text)

    # Create the markup and send it with the message
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/participate', '/gamestart')
    markup.row('/list', '/help', '/reset')
    bot.send_message(message.chat.id, "Choose one:", reply_markup=markup)


# Handle the /participate command
@bot.message_handler(commands=['participate', 'particulate'])
def handle_participate(message):
    # Check if the participant dictionary is empty
    if participants_dict.get(message.chat.id, 0) == 0:
        participants_dict[message.chat.id] = []

    # Check if the person is already participating
    participating_flag = 0
    for user in participants_dict[message.chat.id]:
        if user.username == message.from_user.username:
            participating_flag = 1
            break

    # If already participating, notify
    if participating_flag:
        bot.send_message(message.chat.id, f'@{message.from_user.username} is already participating in this chat game!')

    # If not participating, add to participants and notify
    else:
        participants_dict[message.chat.id].append(message.from_user)
        bot.send_message(message.chat.id, f'Ok, @{message.from_user.username} is now participating!')

        # Print the current list of participants
        text = 'Current participants:'
        for user in participants_dict[message.chat.id]:
            text += ' @' + user.username


# Handle the /list command
@bot.message_handler(commands=['list'])
def handle_list(message):
    # If the list of participants is empty, say 'No participants'
    if participants_dict.get(message.chat.id, 0) == 0:
        bot.send_message(message.chat.id, 'No participants')
    elif participants_dict[message.chat.id] == set():
        bot.send_message(message.chat.id, 'No participants')

    # If the list of participants is not empty, say the list
    else:
        message_text = 'Current participants:'
        for user in participants_dict[message.chat.id]:
            message_text += f' @{user.username}'
        bot.send_message(message.chat.id, message_text)


# Handle the /reset command
@bot.message_handler(commands=['reset'])
def handle_reset(message):
    # Delete all the logging dictionaries
    if participants_dict.get(message.chat.id, 0) != 0:
        del participants_dict[message.chat.id]
    if location_dict.get(message.chat.id, 0) != 0:
        del location_dict[message.chat.id]
    if spy_set_dict.get(message.chat.id, 0) != 0:
        del spy_set_dict[message.chat.id]

    # Say a successful message
    bot.send_message(message.chat.id, 'The game has been reset!')

    # Create and say the markup
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/participate', '/gamestart')
    markup.row('/list', '/help', '/reset')
    bot.send_message(message.chat.id, "Choose one:", reply_markup=markup)


# Handle the /startgame command
@bot.message_handler(commands=['startgame', 'gamestart'])
def handle_startgame(message):
    # Say the no participants message if the list of participants is empty
    if participants_dict.get(message.chat.id, 0) == 0:
        bot.send_message(message.chat.id, 'Can not start with no participants')

    # Else try to start the game
    else:
        try:
            # Declare ctime as gloval to be able to change it
            global ctime

            # Say the starting message
            bot.send_message(message.chat.id, f'The game is starting, wait a bit...')

            # Choose the location and log it
            location = np.random.choice(location_set, 1).tolist()[0]
            if location_dict.get(message.chat.id, 0) == 0:
                location_dict[message.chat.id] = location

            # Create the images url and print them to bugfix
            spy_image_url = str(get_image_url('spy').tolist()[0]).strip()
            print(spy_image_url)
            location_image_url = str(get_image_url(location).tolist()[0]).strip()
            print(location_image_url)

            # Say the starting game message
            bot.send_message(message.chat.id, 'The game has started!')

            # Set the spy number and choose from the participants accordingly
            spy_num = len(participants_dict[message.chat.id]) // 5 + 1
            spy_set = np.random.choice(participants_dict[message.chat.id], spy_num, replace=False)

            # Log the spies
            if spy_set_dict.get(message.chat.id, 0) == 0:
                spy_set_dict[message.chat.id] = spy_set

            # Say the intro game information
            bot.send_message(message.chat.id, f'The number of participants: {len(participants_dict[message.chat.id])}')
            bot.send_message(message.chat.id, f'The number of spies: {spy_num}')

            # Go to each participant and send the locations/spy notification with images
            for user in participants_dict[message.chat.id]:
                if user in spy_set:
                    bot.send_message(user.id, f'Your current game in {message.chat.title}\n** You are a spy **')
                    bot.send_message(user.id, spy_image_url)
                else:
                    bot.send_message(user.id, f'Your current game in {message.chat.title}\n** {location} **')
                    bot.send_message(user.id, location_image_url)

            # Say that the locations were sent
            bot.send_message(message.chat.id, 'The locations have been sent.')

            # Start the time count
            ctime = datetime.now()
            bot.send_message(message.chat.id, 'Now you have 15 minutes for this game!')

            # Show the winner-choosing markup and say "Choose the winner"
            markup = telebot.types.ReplyKeyboardMarkup()
            markup.row('/spy', '/people', '/draw')
            bot.send_message(message.chat.id,
                             "Choose who won, the /spy, the /people or it was a /draw",
                             reply_markup=markup)

            # Go to the winner choosing step
            bot.register_next_step_handler(message, process_choose_winner_step)

        # If exception say the exception message
        except Exception as e:
            bot.send_message(message.chat.id, f'There has been an error! {e}')
            handle_reset(message)


# Handle the winner choosing
def process_choose_winner_step(message):
    # If the answer message is not in the proper text set, retry
    if message.text not in ('/spy', '/people', '/draw'):
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.row('/spy', '/people', '/draw')
        process_choose_winner_step(message)
    # If the answer message is in the proper text set, do the logging and restart the game
    else:
        spy_set = spy_set_dict[message.chat.id]
        location = location_dict[message.chat.id]
        ftime = datetime.now()
        time = (ftime - ctime)

        current_game_stats = pd.DataFrame({'ctime': ctime,
                                           'ftime': ftime,
                                           'time': time,
                                           'chat_id': message.chat.id,
                                           'participants': [user.username for user in participants_dict[message.chat.id]],
                                           'spies': [spy.username for spy in spy_set],
                                           'participants_num': len(participants_dict[message.chat.id]),
                                           'spies_num': len(spy_set),
                                           'winner': message.text,
                                           'location': location,
                                           'location_set_name': location_set_name})
        global game_stats
        game_stats = pd.concat([game_stats, current_game_stats], ignore_index=True, sort=False)

        game_stats.to_csv('game_stats.csv', sep=';')
        current_game_stats.to_csv('current_game_stats.csv', sep=';')

        bot.send_message(message.chat.id, f'The game has finished !')
        bot.send_message(message.chat.id, f'The spies were {["@" + str(spy.username) for spy in spy_set]}')
        bot.send_message(message.chat.id, f'The location was {location} from set {location_set_name}')
        bot.send_message(message.chat.id, f'This game was of {time} length')
        bot.send_message(message.chat.id, f'Resetting the game in 3, 2, 1...')
        handle_reset(message)
        upload_to_yadisk()


# Getting images from the Google Image Search from the query
def get_image_url(query):
    """Returns a random image url from Google Image Search via the query"""
    from selenium import webdriver

    # Connect the driver
    driver = webdriver.Chrome()
    driver.get('https://www.google.com/imghp?hl=en')

    # Get the resuts page from the query
    search_form = driver.find_element_by_id('tsf')
    image_query = search_form.find_element_by_name('q')
    image_query.clear()
    image_query.send_keys(query)
    search_form.submit()
    time.sleep(4)

    # Find all images
    images = driver.find_elements_by_tag_name('img')

    # Find all suitable urls
    results = []
    while results == []:
        # If not found scroll further
        driver.execute_script("window.scrollBy(0, 1000)")

        # Append suitable urls
        for image in images:
            src_str = str(image.get_attribute('src'))

            # Suitable means not base64, not empty and contains 'encrypted'
            if (not src_str.startswith('data:')) \
                    and (src_str != 'None') \
                    and (not src_str.find('encrypted') == -1):
                results.append(src_str)

    driver.close()
    return np.random.choice(results, 1)


# Say the oops message if trying to log the winner before the game
@bot.message_handler(commands=['spy', 'people', 'draw'])
def handle_winner(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    bot.send_message(message.chat.id, 'The games has not started yet, it is not the time to record winners!')
    markup.row('/participate', '/gamestart')
    markup.row('/list', '/help', '/reset')
    bot.send_message(message.chat.id, "Choose one:", reply_markup=markup)


# Handle the /help command
@bot.message_handler(commands=['help'])
def handle_help(message):
    help_message_text = ''' 
Register all the participants. To participate print "/participate".
To start the game print "/startgame". To reset print "/reset".
Before the game starts every participant needs to write something to the bot in private messages.
'''
    bot.send_message(message.chat.id, help_message_text)


# Handle the /stats command
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    import dataanalysis as dat
    print(game_stats)
    temp_data = game_stats.copy()
    temp_data['cdate'] = pd.to_datetime(temp_data['ctime'], format='%Y-%m-%d %H:%M:%S.%f').dt.date
    temp_data['count'] = 1
    games_by_day = temp_data[['cdate', 'count']].groupby('cdate')\
                                                .count()\
                                                .sort_values(by='cdate', ascending=True)\
                                                .reset_index(level=0, inplace=True)
    print(games_by_day)
    dat.plot_timeseries_graph(data=games_by_day,
                              dt='cdate',
                              cnt='count',
                              window=1,
                              first_day='2019-01-01',
                              last_day=datetime.today(),
                              graph_label='games_count',
                              )
    bot.send_photo(message.chat.id, 'games_by_day')


# Handle the /changeset command
@bot.message_handler(commands=['changeset'])
def handle_changeset(message):
    # Say the message with choices and proceed to the next step
    bot.send_message(message.chat.id,
                     "To change the location set choose from the list, to leave it be type anything not from the list:")
    bot.send_message(message.chat.id, '''
def - the default set
spb - Saint-P
msk - Moscow
nsk - Novosibirsk
ekb - Ekaterinburg
nnv - Nizhnii Novgorod
kzn - Kazan
vbg - Vyborg
smr - Samara
krd - Krasnodar
sochi - Sochi
ufa - Ufa
krasnoyarsk - Krasnoyarsk
kev - Kiyv
new-york - New-York    
''')
    bot.register_next_step_handler(message, process_change_location_set_step)


# Next step of changing location set
def process_change_location_set_step(message):
    # Change the global variable
    global location_set
    global location_set_name

    # If in the choices, change the set
    if message.text in ('def', 'spb', 'msk', 'nsk', 'ekb', 'nnv',
                        'kzn', 'vbg', 'smr', 'krd', 'sochi', 'ufa',
                        'krasnoyarsk', 'kev', 'new-york'):
        bot.send_message(message.chat.id, f"Changing to {message.text}...")
        location_set_name = message.text

        # If def, change to it
        if message.text == 'def':
            with open('spyfalllocations.txt', 'r', encoding='utf8') as f:
                location_set = f.read().splitlines()

        # Else connect to Kudago via REST API and get the location_set
        else:
            import requests
            url = f'https://kudago.com/public-api/v1.4/places/?lang=&fields=id,title&location={message.text}'
            r = requests.get(url)
            r = r.json()
            results = []
            for result in r['results']:
                results.append(result['title'])
            location_set = results
        bot.send_message(message.chat.id, f"Success!")

    # If not in the choices, the set remains the same
    else:
        bot.send_message(message.chat.id, f"The set remains the same")
        return


# Poll the bot none stop
if __name__ == '__main__':
    import requests
    try:
        bot.polling(none_stop=True)
    except requests.exceptions.ConnectTimeout as e:
        exit('<--- There was a timeout exception, maybe Telegram is blocked and you need to use VPN --->')
