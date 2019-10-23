import re
import string

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def check_contains(input, letters):
    return any(char in letters for char in input)


def validate_password(input):
    try:
        return all([
            check_contains(input, string.ascii_uppercase),
            check_contains(input, string.ascii_lowercase),
            check_contains(input, string.digits),
            check_contains(input, string.punctuation + '#'),
            len(input) >= 8
        ])
    except:
        return False


def validateEmail(address):
    EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    if not EMAIL_REGEX.match(address):
        return False
    else:
        return True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
