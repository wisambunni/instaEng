from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import sys

CHROME_OPTIONS = webdriver.ChromeOptions()

CHROME_OPTIONS.add_argument('--headless')

# Set your own webdriver
browser = webdriver.Chrome(executable_path='C:/chromedriver.exe', chrome_options=CHROME_OPTIONS)

#browser.set_window_size(1920, 1600)

def to_int(string):
    """
    Converts a string to integer.
    While the return type is float. It's the reason so because it's necessary to
    convert strings with decimal places (i.e, 75.5). The output should be
    treated as an integer.

    :param string: String value (can contain decimals, k and m holders,
                                 for thousands and millions)
    :type string: str

    :return: string integer converted to float
    :rtype: float
    """
    string = string.replace(',', '')
    num = 0

    if string[-1] == 'k':
        num = float(string[:-1]) * 1000
    elif string[-1] == 'm':
        num = float(string[:-1]) * 1000000
    else:
        num = float(string)

    return num


def calc_engagement_rate(total_engagement, followers):
    """
    Calculates the enegagement rate.

    :param total_engagement: The total engagement value for the page.
    :type total_engagement: float

    :param followers: The number of followers of the page.
    :type followers: int

    :return: The engagement %.
    :rtype: float
    """
    return (total_engagement / followers) * 100


def get_followers():
    """
    Gets the number of followers for a specific page.

    :return: Number of followers.
    :rtype: selenium.WebElement
    """
    followers = browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span')
    print(type(followers))


    return followers


def get_posts():
    """
    Gets the 12 most recent posts of a page.

    :return: the 12 most recent posts.
    :rtype: list
    """
    posts = browser.find_elements_by_xpath("//*[@class='v1Nh3 kIKUG  _bz0w']")

    return posts


def get_engagement(hover):
    """
    Gets the engagement of a post (likes and comments). Note that instagram
    website doesn't show the post interaction unless a mouse is hovering over
    the post.

    :param hover: element used to hover over a post.
    :type hover: ActionChains

    :return: The likes and comments of a certain post.
    :rtype: tuple
    """
    # Continue scrolling until the designated post is found
    while True:
        try:
            hover.perform()
            #browser.implicitly_wait(0.5)
            engagement = browser.find_element_by_class_name('qn-0x')
            break
        except:
            browser.execute_script('window.scrollBy(0, 50)')


    likes, comments = tuple(engagement.text.split('\n'))

    likes = to_int(likes)
    comments = to_int(comments)

    return likes, comments


def load_users(FILE_PATH):
    """
    Loads a file containing instagram users. Each user should be on a separate
    line. You need valid instagram names for this script to work properly.

    :param FILE_PATH: The path to the user file.
    :type FILE_PATH: str

    :return: A list of users.
    :rtype: list
    """
    # Load a list of users
    infile = open(FILE_PATH, 'r').read().split('\n')
    if infile[-1] == '':
        infile.pop()

    return infile


def main():
    if len(sys.argv) < 2:
        print("ERR: Please specify user file")
        sys.exit()
    else:
        FILE_PATH = sys.argv[1]

    users = load_users(FILE_PATH)

    outfile = open('engagement.csv', 'w')
    outfile.write('username, followers, URL, engagement rate\n')

    for user in users:
        print(user)
        insta_url = 'https://instagram.com/'+user
        browser.get(insta_url)

        total_likes = 0
        total_comments = 0

        followers = get_followers()
        followers = to_int(followers.text)

        posts = get_posts()
        browser.execute_script('window.scrollTo(0, 150)')

        for post in posts:
            hover = ActionChains(browser).move_to_element(post)

            likes, comments = get_engagement(hover)

            total_likes += likes
            total_comments += comments

        engagement_rate = calc_engagement_rate((total_likes+comments)/len(posts), followers)
        engagement_rate = format(engagement_rate, '.2f')

        print(user, followers, insta_url, engagement_rate)
        outfile.write(user + ', ' + str(followers) + ', ' + insta_url + ', ' + str(engagement_rate) + '%\n')

    browser.close()
    outfile.close()


if __name__ == '__main__':
    main()

