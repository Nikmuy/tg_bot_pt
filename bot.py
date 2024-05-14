import logging
import re
import psycopg2
from psycopg2 import Error
from telegram import Update, ForceReply, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY= os.getenv('SECRET_KEY')
DATABASE_URL= os.getenv('DATABASE_URL')


TOKEN = os.getenv('TOKEN')

logging.basicConfig(filename='myProgramLog.txt', level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s', encoding="utf-8")

logging.debug('Отладочная информация.')
logging.info('Работает модуль logging.')
logging.warning('Риск получения сообщения об ошибке.')
logging.error('Произошла ошибка.')
logging.critical('Программа не может выполняться.')

logger = logging.getLogger(__name__)

logging.debug("error")
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

def findEmailCommand(update: Update, context):
    update.message.reply_text("Введите текст для поиска email'ов: ")

    return 'find_email'

def verifypasswordCommand(update: Update, context):
    update.message.reply_text("Введите пароль для его проверки: ")

    return 'verify_password'

def get_apt_listCommand(update: Update, context):
    update.message.reply_text("Введите название пакета для получения информации по нему или all для получения информации о всех пакетах: ")
    return 'get_apt_list'


def cancel(update, _):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал о том, что пользователь не разговорчивый
    # Отвечаем на отказ поговорить
    update.message.reply_text(
        'Действия отменены',
        reply_markup=ReplyKeyboardRemove()
    )
    # Заканчиваем разговор.
    return ConversationHandler.END

def get_repl_logs (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=username, password=password, port=port)
    except (Exception, Error) as error:
        update.message.reply_text(str(error))
    try:
        stdin, stdout, stderr = client.exec_command("cat /tmp/pg.log | grep 'replica' | tail -n 20")
    except (Exception, Error) as error:
         update.message.reply_text(str(error))
    try:
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data) # Отправляем сообщение пользователю
    except (Exception, Error) as error:
        update.message.reply_text(str(error))
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_phone_numbers(update: Update, context):
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database=os.getenv('DB_DATABASE')
    try:
        connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port, 
                                  database=database)

        cursor = connection.cursor()
        cursor.execute("select * from numbers;")
        info = cursor.fetchall()
        data= ''
        for row in info:
            data+=f"{row[0]}. {row[1]} \n"
        update.message.reply_text(data)
    except (Exception, Error) as error:
        update.message.reply_text(str(error))
        logging.debug(error)
    finally:
            if connection:
                cursor.close()
                connection.close()
                update.message.reply_text("Соединение с PostgreSQL закрыто")
            else:
                update.message.reply_text("Соединения не было, смотри ошибки")
    return ConversationHandler.END
def num_to_db(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'отмена':
        update.message.reply_text("Что ж, не будем так не будем")
    else:
        update.message.reply_text("Плохой выбор")
        num_list=context.user_data.get('phone_numbers')
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database=os.getenv('DB_DATABASE')
        try:
            connection = psycopg2.connect(user=user,
                                    password=password,
                                    host=host,
                                    port=port, 
                                    database=database)

            cursor = connection.cursor()
            for num in num_list:
                cursor.execute(f"INSERT INTO numbers (number) VALUES ('{num[0]}');")
            connection.commit()
        except (Exception, Error) as error:
            update.message.reply_text(str(error))
            logging.debug(error)
        finally:
                if connection:
                    cursor.close()
                    connection.close()
                    update.message.reply_text("Поздравляю, данные успешно внесены")
    return ConversationHandler.END

def email_to_db(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'отмена':
        update.message.reply_text("Что ж, не будем так не будем")
    else:
        update.message.reply_text("Плохой выбор")
        email_list=context.user_data.get('emails')
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        database=os.getenv('DB_DATABASE')
        try:
            connection = psycopg2.connect(user=user,
                                    password=password,
                                    host=host,
                                    port=port, 
                                    database=database)

            cursor = connection.cursor()
            for email in email_list:
                cursor.execute(f"INSERT INTO emails (email) VALUES ('{email}');")
            connection.commit()
        except (Exception, Error) as error:
            update.message.reply_text(str(error))
            logging.debug(error)
        finally:
                if connection:
                    cursor.close()
                    connection.close()
                    update.message.reply_text("Поздравляю, данные успешно внесены")
    return ConversationHandler.END

def get_emails(update: Update, context):
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database=os.getenv('DB_DATABASE')
    try:
        connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port, 
                                  database=database)

        cursor = connection.cursor()
        cursor.execute("select * from emails;")
        info = cursor.fetchall()
        data= ''
        for row in info:
            data+=f"{row[0]}. {row[1]} \n"
        update.message.reply_text(data)
    except (Exception, Error) as error:
        update.message.reply_text(str(error))
        logging.debug(error)
    finally:
            if connection:
                cursor.close()
                connection.close()
                update.message.reply_text("Соединение с PostgreSQL закрыто")
            else:
                update.message.reply_text("Соединения не было, смотри ошибки")

def get_release (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('hostnamectl')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_uname (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uname -nvp')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_uptime (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_df (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_free (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_w (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_mpstat (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_auth (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('last -10')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_critical (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('grep "CRITICAL" /var/log/syslog | tail -n 5')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_ps (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_ss (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ss -tulpn')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_services (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('systemctl')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_apt_list (update: Update, context):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    user_input = update.message.text
    if user_input=="all":
        stdin, stdout, stderr = client.exec_command(f'apt list --installed')
    else:
        stdin, stdout, stderr = client.exec_command(f'apt show {user_input}')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    if len(data)>=4096:
        mass=[data[i:i+4096] for i in range(0, len(data), 4096)]
        for i in mass:
            update.message.reply_text(i)
    else:
        update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def find_email (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) почту
    emailRegex = re.compile(r'\b[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+)*' \
                r'@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b') # формат (что-то)@(что-то).(что-то)

    emailList = emailRegex.findall(user_input) # Ищем почты
    if not emailList: # Обрабатываем случай, когда почт нет
        update.message.reply_text('Почты не найдены')
        return # Завершаем выполнение функции
    
    emails = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n' # Записываем очередной номер
        
    update.message.reply_text(emails) # Отправляем сообщение пользователю
    context.user_data['emails'] = emailList
    update.message.reply_text("Напиши 'отмена', если не хочешь, чтоб твои почты были внесены в таблицу")
    return 'email_to_db'

def find_phone_number (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    phoneNumRegex = re.compile(r'((8|\+7) \(\d{3}\) \d{3}-\d{2}-\d{2}|(8|\+7)\d{10}|(8|\+7)\(\d{3}\)\d{7}|(8|\+7) \d{3} \d{3} \d{2} \d{2}|(8|\+7) \(\d{3}\) \d{3} \d{2} \d{2}|(8|\+7)-\d{3}-\d{3}-\d{2}-\d{2})')
    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов
    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i][0]}\n' # Записываем очередной номер
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    context.user_data['phone_numbers'] = phoneNumberList
    update.message.reply_text("Напиши 'отмена', если не хочешь, чтоб твои номера были внесены в таблицу")
    return 'num_to_db'

def verify_password (update: Update, context):
    user_input = update.message.text # Получаем текст для проверки пароля
    passwordRegex = re.compile(r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*()]{8,}$')
    passwordCheck = passwordRegex.match(user_input) # проверка пароля

    if  passwordCheck: # Обрабатываем случай, когда пароль прошёл проверку
        update.message.reply_text(f"Поздравляю, твой пароль '{user_input}' прошёл проверку и является сложным")
        return # Завершаем выполнение функции
    else:
        update.message.reply_text('Простой пароль') # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher


    conv_handler_phone = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)
        ],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command,find_phone_number)],
            'num_to_db': [MessageHandler(Filters.text & ~Filters.command, num_to_db)], 
        },
         fallbacks=[CommandHandler('cancel', cancel)],
    )

    conv_handler_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)
        ],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command,find_email)],
            'email_to_db': [MessageHandler(Filters.text & ~Filters.command, email_to_db)], 
        },
         fallbacks=[CommandHandler('cancel', cancel)],
    )

    conv_handler_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifypasswordCommand)
        ],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command,verify_password)],
        },
         fallbacks=[CommandHandler('cancel', cancel)],
    )
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(conv_handler_phone)
    dp.add_handler(conv_handler_email)
    dp.add_handler(conv_handler_password)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auth))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
