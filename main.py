from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import instaloader
from instaloader.exceptions import TwoFactorAuthRequiredException


class InstaBot:
    def __init__(self, username, password):
        # Open Firefox
        options = Options()
        options.binary_location = r'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
        self.browser = webdriver.Firefox(options=options)
        # self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)

        loader = instaloader.Instaloader()
        number = -1
        try:
            loader.login(username, password)
        except TwoFactorAuthRequiredException:
            number = int(input("enter two factor authentication code: "))
            loader.two_factor_login(number)

        profile = instaloader.Profile.from_username(
            loader.context, username)

        # Login in to Instagram
        home_page = HomePage(self.browser)

        home_page.login(username, password, number)

        self.username = username
        self.profile = profile

    def unfollow(self):
        # Go to your Instagram profile page
        self.browser.get("https://www.instagram.com/{}/".format(self.username))
        sleep(2)

        # Get the usernames of all your followers
        followers, num_of_followers = self.get_followers()

        # Check to make sure that approximately all followers were scraped
        # (I say approximately because I've noticed I always have a few less followers than stated on Instagram)
        if len(followers) < num_of_followers * 0.99:
            print("There's been an error while scraping the usernames of your followers.")
            return

        # Unfollow accounts that aren't following you
        self.unfollow_helper(
            followers)
        # The number of accounts unfollowed is rounded if you have lots of followers
        # E.g., if you have 20,426 followers, Instagram will say you have 20.4K followers
        # and that's why the calculation will be rounded as well

        # Close browser
        self.browser.quit()
        return

    def get_followers(self):

        followers = self.profile.get_followers()

        usernames_of_followers = set()

        for follower in followers:
            usernames_of_followers.add(follower.username)

        return usernames_of_followers, followers.count

    def unfollow_helper(self, followers):
        # get followees
        followees = self.profile.get_followees()

        # declare a set  variable to keep followees username
        usernames_of_followees = set()

        for followee in followees:
            usernames_of_followees.add(followee.username)

        # followee - followers
        not_follows_back = usernames_of_followees.difference(followers)
        # Using readlines()
        ignored_accounts_from_file = set()
        file1 = open('ignored_accounts.txt', 'r')
        Lines = file1.readlines()
        for line in Lines:
            ignored_accounts_from_file.add(line.strip())
        not_follows_back = not_follows_back.difference(
            ignored_accounts_from_file)

        print("hit return if you want to unfollow the user or type '3' if you don't")
        for non_follower in not_follows_back:
            print(non_follower)
            value = input("unfollow?").capitalize().strip()

            if (value == "3"):
                f = open("ignored_accounts.txt", "a")
                f.write("{}\n".format(non_follower))
                continue

            self.browser.get(
                "https://www.instagram.com/{}/".format(non_follower))
            friendshipButton = self.browser.find_element(
                By.XPATH, "(//button[contains(@type,'button')])[2]")
            friendshipButton.click()
            sleep(1)

            unfollowButton = self.browser.find_element(
                By.XPATH, "//button[normalize-space()='Unfollow']")
            unfollowButton.click()


class HomePage:
    def __init__(self, browser):
        self.browser = browser
        self.browser.get("https://www.instagram.com/")

    def login(self, username, password, number):
        # Find the username and password inputs
        username_input = self.browser.find_element(
            By.CSS_SELECTOR, "input[name='username']")
        password_input = self.browser.find_element(
            By.CSS_SELECTOR, "input[name='password']")

        # Type your username and password in their respective inputs
        username_input.send_keys(username)
        password_input.send_keys(password)

        # Submit credentials and wait for page to load
        login_button = self.browser.find_element(
            By.XPATH, "//button[@type='submit']")
        # login_button = self.browser.find_element(By.XPATH,"//button[@type='submit']")
        # print(login_button)
        login_button.click()
        sleep(1)
        if (number > -1):
            verification_input = self.browser.find_element(
                By.XPATH, "//input[@name='verificationCode']")
            verification_input.send_keys(number)
            verification_button = self.browser.find_element(
                By.XPATH, "//button[normalize-space()='Confirm']")
            verification_button.click()

        sleep(5)


# Credentials to access Instagram account
username = ""
password = ""

my_insta_bot = InstaBot(username, password)
my_insta_bot.unfollow()
