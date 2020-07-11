import re
import pickle
import requests

LOGIN_URL = 'https://futurebroadband.com.au/wp-login.php'
PORTAL_URL = 'https://futurebroadband.com.au/portal/'

COOKIES_PICKLE_PATH = 'cookies.pickle'


def save_to_file(text, file):
    with open(file, 'w') as output:
        output.write(text)


def get_usage_from_html(html):
    # Search the text for the broadband data usage
    match = re.search(r'usage[^\d]*(\d+(\s*\.\s*\d+)?)\s*GB', html, re.I)
    if not match:
        raise Exception("Can't find usage on webpage")

    return match[1]


def load_portal_using_cookies(session):
    """ Throws an exception if no saved cookies or can't access website """
    print("Trying to login using existing cookies...")
    with open(COOKIES_PICKLE_PATH, 'rb') as cookies_file_w:
        session.cookies.update(pickle.load(cookies_file_w))

    return session.get(PORTAL_URL)


def load_portal_fresh_login(session):
    """ Throws an exception if can't access website
    TODO: throw exception if login failed
    """
    email = input("Please enter the email you used with future broadband\n>")
    password = input("Please enter the password you used with future broadband\n>")

    payload = {
        'log': email,
        'pwd': password,
        'redirect_to': '/portal/',
        'wp-submit': 'login',
    }

    # Post the payload to the site to log in
    return session.post(LOGIN_URL, data=payload)


def get_usage(session):
    # TODO: differentiate between not being able to find usage in html/other errors, and invalid username/password err
    try:
        response = load_portal_using_cookies(session)
        return get_usage_from_html(response.text)
    except:
        response = load_portal_fresh_login(session)
        print("Couldn't use cookies to get usage - Please login again:\n")
        return get_usage_from_html(response.text)


def main():
    session = requests.Session()

    usage_gb = get_usage(session)

    print(f"You have used {usage_gb} GB of data.")

    # Save cookies to file for next time
    with open(COOKIES_PICKLE_PATH, 'wb') as cookies_file_r:
        pickle.dump(session.cookies, cookies_file_r)


if __name__ == '__main__':
    main()
