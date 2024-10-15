import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import dotenv
import paramiko
import re
import subprocess

# Загрузка переменных из .env файла
dotenv.load_dotenv()

# Присваиваем значение токена из переменной окружения
TOKEN = os.getenv("TOKEN")

# Настройки SSH подключения
RM_HOST = os.getenv("RM_HOST")
RM_PORT = os.getenv("RM_PORT")
RM_USER = os.getenv("RM_USER")
RM_PASSWORD = os.getenv("RM_PASSWORD")

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start_command(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def help_command(update: Update, context):
    update.message.reply_text('Help!')

# 1. Поиск информации в тексте и вывод ее. а) Email-адреса.
def find_email_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов:')
    return 'find_email'

def find_email(update: Update, context):
    user_input = update.message.text
    email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    emails = email_regex.findall(user_input)

    if not emails:
        update.message.reply_text('Email-адреса не найдены')
    else:
        update.message.reply_text('\n'.join(emails))

    return ConversationHandler.END

# 1. Поиск информации в тексте и вывод ее. б) Номера телефонов.
def find_phone_number_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров:')
    return 'find_phone_number'

def find_phone_number(update: Update, context):
    user_input = update.message.text  # Получаем текст, введенный пользователем

    # Список регулярных выражений для различных форматов номеров телефонов
    phone_patterns = [
        r'8\d{10}',                         # 8XXXXXXXXXX
        r'8\(\d{3}\)\d{7}',                 # 8(XXX)XXXXXXX
        r'8 \d{3} \d{3} \d{2} \d{2}',       # 8 XXX XXX XX XX
        r'8 \(\d{3}\) \d{3} \d{2} \d{2}',   # 8 (XXX) XXX XX XX
        r'8-\d{3}-\d{3}-\d{2}-\d{2}'        # 8-XXX-XXX-XX-XX
        r'\+7\d{10}',                       # +7XXXXXXXXXX
        r'\+7\(\d{3}\)\d{7}',               # +7(XXX)XXXXXXX
        r'\+7 \d{3} \d{3} \d{2} \d{2}',     # +7 XXX XXX XX XX
        r'\+7 \(\d{3}\) \d{3} \d{2} \d{2}', # +7 (XXX) XXX XX XX
        r'\+7-\d{3}-\d{3}-\d{2}-\d{2}'      # +7-XXX-XXX-XX-XX
    ]

    # Перебираем все регулярные выражения и ищем совпадения
    phone_number_list = []
    for pattern in phone_patterns:
        phone_number_list.extend(re.findall(pattern, user_input))  # Находим все совпадения и добавляем их в список

    if not phone_number_list:  # Если нет совпадений
        update.message.reply_text('Телефонные номера не найдены')
    else:
        phone_numbers = '\n'.join([f'{i + 1}) {num}' for i, num in enumerate(phone_number_list)])  # Формируем список номеров
        update.message.reply_text(f'Найденные номера телефонов:\n{phone_numbers}')

    return ConversationHandler.END  # Завершаем диалог

# 2. Проверка сложности пароля регулярным выражением.
def verify_password_command(update: Update, context):
    update.message.reply_text('Введите пароль для проверки его сложности:')
    return 'find_verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text
    password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

    if password_regex.match(user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')

    return ConversationHandler.END

# 3. Мониторинг Linux-системы.
def ssh_exec(command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD)

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8')
        ssh.close()
        return output
    except Exception as e:
        return f"[x] Ошибка подключения по SSH: {e}!"

# Команды мониторинга
def get_release_command(update: Update, context):
    result = ssh_exec('lsb_release -a')
    update.message.reply_text(result)

def get_uname_command(update: Update, context):
    result = ssh_exec('uname -a')
    update.message.reply_text(result)

def get_uptime_command(update: Update, context):
    result = ssh_exec('uptime')
    update.message.reply_text(result)

def get_df_command(update: Update, context):
    result = ssh_exec('df -h')
    update.message.reply_text(result)

def get_free_command(update: Update, context):
    result = ssh_exec('free -m')
    update.message.reply_text(result)

def get_mpstat_command(update: Update, context):
    result = ssh_exec('mpstat')
    update.message.reply_text(result)

def get_w_command(update: Update, context):
    result = ssh_exec('w')
    update.message.reply_text(result)

def get_auths_command(update: Update, context):
    result = ssh_exec('last -n 10')
    update.message.reply_text(result)

def get_critical_command(update: Update, context):
    result = ssh_exec('journalctl -p crit -n 5')
    update.message.reply_text(result)

def get_ps_command(update: Update, context):
    # Выполняем команду, сортируя процессы по использованию CPU, и берем только первые 5 строк с заголовком
    result = ssh_exec('ps aux --sort=-%cpu | head -n 6')

    # Проверяем, чтобы результат не был слишком длинным для одного сообщения в Telegram
    if len(result) > 4096:
        result = result[:4096]

    update.message.reply_text(result)

def get_ss_command(update: Update, context):
    result = ssh_exec('ss -tuln')
    update.message.reply_text(result)

def get_apt_list_command(update: Update, context):
    # Если пользователь не передал никаких аргументов, выводим список всех пакетов
    if len(context.args) == 0:
        result = ssh_exec('apt list --installed')

        # Проверяем, чтобы результат не был слишком длинным для одного сообщения в Telegram
        if len(result) > 4096:
            result = result[:4096]
            update.message.reply_text(result)
        else:
            update.message.reply_text(result)
    else:
        # Если передано имя пакета, ищем информацию о конкретном пакете
        package_name = context.args[0]
        result = ssh_exec(f'apt list --installed | grep {package_name}')

        # Проверяем, что есть результат
        if result.strip():
            update.message.reply_text(result)
        else:
            update.message.reply_text(f'Пакет "{package_name}" не найден среди установленных.')

def get_services_command(update: Update, context):
    result = ssh_exec('systemctl list-units --type=service')

    if len(result) > 4096:
        result = result[:4096]

    update.message.reply_text(result)

# Основной блок
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчики диалога
    conv_handler_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_command)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
        },
        fallbacks=[]
    )

    conv_handler_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_number_command)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
        },
        fallbacks=[]
    )

    conv_handler_verify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_command)],
        states={
            'find_verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    # Команды для мониторинга
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(conv_handler_email)
    dp.add_handler(conv_handler_phone_number)
    dp.add_handler(conv_handler_verify_password)
    dp.add_handler(CommandHandler('get_release', get_release_command))
    dp.add_handler(CommandHandler('get_uname', get_uname_command))
    dp.add_handler(CommandHandler('get_uptime', get_uptime_command))
    dp.add_handler(CommandHandler('get_df', get_df_command))
    dp.add_handler(CommandHandler('get_free', get_free_command))
    dp.add_handler(CommandHandler('get_mpstat', get_mpstat_command))
    dp.add_handler(CommandHandler('get_w', get_w_command))
    dp.add_handler(CommandHandler('get_auths', get_auths_command))
    dp.add_handler(CommandHandler('get_critical', get_critical_command))
    dp.add_handler(CommandHandler('get_ps', get_ps_command))
    dp.add_handler(CommandHandler('get_ss', get_ss_command))
    dp.add_handler(CommandHandler('get_apt_list', get_apt_list_command))
    dp.add_handler(CommandHandler('get_services', get_services_command))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

# Запускаем нашу программу, если делаем это напрямую.
if __name__ == '__main__':
    main()
