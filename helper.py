import toml

days_of_week = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def read_toml(file):
    return toml.load(file)


def read_vs_day_toml(file="vs_day_reminders.toml"):
    return read_toml(file)


def read_server_info(file="server_info.toml"):
    return read_toml(file)


def read_token(file=".secret"):
    with open(file=file) as f:
        token = f.read()
        return token


def combine_vs_messages(tasks):
    message = ""
    for index, task in enumerate(tasks):
        message += f"{index+1}. {task}\n"

    return message

emoji_to_language = {
    '🇺🇸': 'en',  # English
    '🇪🇸': 'es',  # Spanish
    '🇫🇷': 'fr',  # French
    '🇲🇽': 'es',  # Spanish (for Mexico)
    '🇰🇷': 'ko',  # Korean
    '🇧🇷': 'pt',  # Portuguese (Brazil)
}