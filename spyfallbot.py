import random
import telebot

bot = telebot.TeleBot('597504356:AAHJAVOybNjqysf9OoLTo32NTT75SWyCmEU')
gamedict = dict()


@bot.message_handler(commands=['start'])
def handle_start(message):
    text1 = 'Register all the participants. To participate print "/participate". '
    text2 = 'To start the game print "/startgame". To reset print "/reset".'
    text3 = 'Before the game starts every participant need to write something to bot in private messages'
    bot.send_message(message.chat.id, text1)
    bot.send_message(message.chat.id, text2)
    bot.send_message(message.chat.id, text3)
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('/participate', '/gamestart')
    markup.row('/list', '/help', '/reset')
    bot.send_message(message.chat.id, "Choose one:", reply_markup=markup)


@bot.message_handler(commands=['participate', 'particulate'])
def handle_participate(message):
    if gamedict.get(message.chat.id, 0) == 0:
        gamedict[message.chat.id] = []
    flag = 0
    for user in gamedict[message.chat.id]:
        if user.username == message.from_user.username:
            flag = 1
            break
    if flag:
        bot.send_message(message.chat.id, '@' + message.from_user.username + ' is already participating in this chat game!')
    else:
        gamedict[message.chat.id].append(message.from_user)
        bot.send_message(message.chat.id, 'Ok, @' + message.from_user.username + ' is now participating!')
        text = 'Current participants:'
        for user in gamedict[message.chat.id]:
            text += ' @' + user.username


@bot.message_handler(commands=['list'])
def handle_participate(message):
    if gamedict.get(message.chat.id, 0) == 0:
        bot.send_message(message.chat.id, 'No participants')
    elif gamedict[message.chat.id] == set():
        bot.send_message(message.chat.id, 'No participants')
    else:
        text = 'Current participants:'
        for user in gamedict[message.chat.id]:
            text += ' @' + user.username
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['reset'])
def handle_reset(message):
    if gamedict.get(message.chat.id, 0) != 0:
        del gamedict[message.chat.id]
    bot.send_message(message.chat.id, 'The game has been reset!')


@bot.message_handler(commands=['startgame', 'gamestart'])
def handle_startgame(message):
    location = get_location()
    if gamedict.get(message.chat.id, 0) == 0:
        bot.send_message(message.chat.id, 'Can not start with no participants')
    elif gamedict[message.chat.id] == []:
        bot.send_message(message.chat.id, 'Can not start with no participants')
    else:
        try:
            bot.send_message(message.chat.id, 'The game has started!')
            spynum = len(gamedict[message.chat.id]) // 5 + 1
            spyset = random.sample(gamedict[message.chat.id], spynum)
            bot.send_message(message.chat.id, 'The number of participants: ' + str(len(gamedict[message.chat.id])))
            bot.send_message(message.chat.id, 'The number of spies: ' + str(len(spyset)))
            for user in gamedict[message.chat.id]:
                if user in spyset:
                    bot.send_message(user.id, 'Your current game in ' + str(message.chat.title))
                    bot.send_message(user.id, 'You are a spy')
                else:
                    bot.send_message(user.id, 'Your current game in ' + str(message.chat.title))
                    bot.send_message(user.id, location)
            bot.send_message(message.chat.id, 'The locations have been sent')
            bot.send_message(message.chat.id, 'The game will now reset in 3.. 2.. 1...')
            handle_reset(message)
        except:
            bot.send_message(message.chat.id, 'The has been an error!')
            bot.send_message(message.chat.id, 'Perhaps, somebody has forgot to write to bot before the game')


def get_location():
    InFile = open('spyfalllocations.txt', 'r', encoding='utf8')
    locationset = []
    for line in InFile.readlines():
        locationset.append(line)
    return random.choice(locationset)


@bot.message_handler(commands=['help'])
def handle_help(message):
    import random
    bot.send_message(message.chat.id, str(random.randint(10, 20)) + ' minute break, come later')


if __name__ == '__main__':
    bot.polling(none_stop=True)
