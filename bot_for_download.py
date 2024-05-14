import logging
import re
import os
import psycopg2
import paramiko
from dotenv import load_dotenv
from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


load_dotenv()

client = paramiko.SSHClient()

def connect_to_machine():
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv("RM_PASSWORD")
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)

userDB=os.getenv('DB_USER')
passwordDB=os.getenv('DB_PASSWORD')
hostDB=os.getenv('DB_HOST')
portDB=os.getenv('DB_PORT')
databaseDB=os.getenv('DB_DATABASE')

connection = psycopg2.connect(
        user=userDB,
        password=passwordDB,
        host=hostDB,
        port=portDB,
        database=databaseDB
)
cursor = connection.cursor()

TOKEN = os.getenv('TOKEN')

count1 = 2
count2 = 2

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет, {user.full_name}!')

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email: ')
    return 'find_email'

def findPhoneNumberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль: ')
    return 'verify_password'

def aptListCommand(update: Update, context):
    update.message.reply_text('all - посмотреть все пакеты,\
                               \n\'Название пакета\' - посмотреть информацию о пакете')
    return 'get_apt_list'

def find_email(update: Update, context):
    user_input = update.message.text
    emailNumRegex =re.compile(r"\b[a-zA-Z0-9]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b")
    emailNumList = emailNumRegex.findall(user_input)
    context.user_data['email'] = emailNumList
    if not emailNumList:
        update.message.reply_text('Email не были найдены')
        return ConversationHandler.END 
    emailNum = ''
    for i in range(len(emailNumList)):
        emailNum += f'{i+1}. {emailNumList[i]}\n'
    update.message.reply_text('Были найдены следующие email: '\
                              +'\n'+emailNum+'\n'\
                                +'Записать их в базу данных? (Y\\N)') 
    return 'SAVE EMAIL'

def save_email(update: Update,context):
    email = context.user_data['email']
    if(update.message.text == 'Y'):
        try:
            for x in email:
                cursor.execute("INSERT INTO email(id, email) VALUES (count1, '"+str(x)+"');")
            connection.commit()
	    count1+=1
            update.message.reply_text("Добавление выполнено успешно!")
        except (Exception, Error) as error:
            update.message.reply_text("ERROR WITH DATABASE!")
            return ConversationHandler.END 
    else:
        update.message.reply_text("Хорошо, двигаемся дальше")
        return ConversationHandler.END 

def find_phone_number(update: Update, context):
    user_input = update.message.text 
    phoneNumRegex = re.compile(r'\+?7[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|\+?7[ -]?\d{10}|\+?7[ -]?\d{3}[ -]?\d{3}[ -]?\d{4}|8[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}|8[ -]?\d{10}|8[ -]?\d{3}[ -]?\d{3}[ -]?\d{4}') 
    phoneNumberList = phoneNumRegex.findall(user_input) 
    context.user_data['phone_numbers'] = phoneNumberList
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END 
    phoneNumbers = ''
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' 
    update.message.reply_text('Были найдены следующие номера: '\
                              +'\n'+phoneNumbers+'\n'\
                                +'Записать их в базу данных? (Y\\N)') 
    return 'SAVE PHONE NUMBERS'

def save_phone_numbers(update: Update,context):
    phoneNumberList = context.user_data['phone_numbers']
    if(update.message.text == 'Y'):
        try:
            for x in phoneNumberList:
                cursor.execute("INSERT INTO phone_number(id,phone_number) VALUES (count2, '"+str(x)+"');")
            connection.commit()
            count2+=1		
            update.message.reply_text("Добавление выполнено успешно!")
        except (Exception, Error) as error:
            update.message.reply_text("ERROR WITH DATABASE!")
            return ConversationHandler.END 
    else:
        update.message.reply_text("Хорошо, двигаемся дальше")
        return ConversationHandler.END 

def verify_password(update: Update, context):
    user_input=update.message.text
    if (
        len(str(user_input))>=8 and
        re.search(r'[A-Z]', user_input)
        and re.search(r'[a-z]', user_input)
        and re.search(r'\d', user_input)
        and re.search(r'[!@#$%^&*()]', user_input)):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
        return
    return ConversationHandler.END 

def print_info(stdout, stderr):
    data = stdout.read() + stderr.read()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return(data)

def get_release(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('cat /etc/os-release')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_uname(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('uname -a')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_uptime(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('uptime')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_df(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('df')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_free(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('free')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_mpstat(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('mpstat')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_w(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('w')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_auth(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('cat /var/log/auth.log | head -10')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_critical(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('cat /var/log/syslog | head -5')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_ps(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('ps')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_ss(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('ss -tulpn')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_apt_list(update: Update, context):
    connect_to_machine()
    user_input=str(update.message.text)
    if user_input=='all':
        stdin, stdout, stderr = client.exec_command('apt list | head -15')
        update.message.reply_text(print_info(stdout,stderr))
    else:
        user_input_apt=update.message.text
        stdin, stdout, stderr = client.exec_command('apt show '+str(user_input_apt))
        update.message.reply_text(print_info(stdout,stderr))
    connection.close()
    return ConversationHandler.END 

def get_services(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('systemctl status | head -20')
    connection.close()
    update.message.reply_text(print_info(stdout,stderr))

def get_repl_logs(update: Update, context):
    connect_to_machine()
    stdin, stdout, stderr = client.exec_command('cat /var/log/postgresql/postgresql-15-main.log | grep replication | head -10')
    update.message.reply_text(print_info(stdout,stderr))

def get_emails(update: Update, context):
    cursor.execute("SELECT * FROM email;")
    data = cursor.fetchall()
    output=''
    for x in data:
        output+=str(x[0])+'. '+x[1]+'\n'
    update.message.reply_text(output)

def get_phone_numbers(update: Update, context):
    cursor.execute("SELECT * FROM phone_number;")
    data = cursor.fetchall()
    output=''
    for x in data:
        output+=str(x[0])+'. '+str(x[1])+'\n'
    update.message.reply_text(output)

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email',findEmailCommand)],
        states={
            'find_email':[MessageHandler(Filters.text & ~Filters.command, find_email)],
            'SAVE EMAIL': [MessageHandler(Filters.text & ~Filters.command, save_email)],
        },
        fallbacks=[]
    )

    convHandlerFindPhoneNumber = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'SAVE PHONE NUMBERS': [MessageHandler(Filters.text & ~Filters.command, save_phone_numbers)],
        },
        fallbacks=[]
    )
		
    convHandlerverifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password',verifyPasswordCommand)],
        states={
            'verify_password':[MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )


    convHandleraptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list',aptListCommand)],
        states={
            'get_apt_list':[MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerFindPhoneNumber)
    dp.add_handler(convHandlerverifyPassword)
    dp.add_handler(convHandleraptList)

    dp.add_handler(CommandHandler('get_release', get_release))
    dp.add_handler(CommandHandler('get_uname', get_uname))
    dp.add_handler(CommandHandler('get_uptime', get_uptime))
    dp.add_handler(CommandHandler('get_df', get_df))
    dp.add_handler(CommandHandler('get_free', get_free))
    dp.add_handler(CommandHandler('get_mpstat', get_mpstat))
    dp.add_handler(CommandHandler('get_w', get_w))
    dp.add_handler(CommandHandler('get_auth', get_auth))
    dp.add_handler(CommandHandler('get_critical', get_critical))
    dp.add_handler(CommandHandler('get_ps', get_ps))
    dp.add_handler(CommandHandler('get_ss', get_ss))
    dp.add_handler(CommandHandler('get_services', get_services))

    dp.add_handler(CommandHandler('get_repl_logs',get_repl_logs))	
    dp.add_handler(CommandHandler('get_emails',get_emails))
    dp.add_handler(CommandHandler('get_phone_numbers',get_phone_numbers))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
