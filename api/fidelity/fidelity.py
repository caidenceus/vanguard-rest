from browser import Browser
import path
from selenium.webdriver.common.by import By

import time

class Fidelity:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.logged_in = False

        self.browser = Browser(chromium=False)
        # TODO: Temporary work around
        self.wait = 1500

    def start(self):
        self.browser.start()
    
    def teardown(self):
        self.browser.teardown()

    def login(self):
        self.browser.get(path.LOGIN_PATH)
        username_input = self.browser.find_element(By.ID, 'userId-input')
        password_input = self.browser.find_element(By.ID, 'password')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        self.browser.find_element(By.XPATH, '//button[normalize-space()="Log In"]').click()

        # Wait for landing page to load
        time.sleep(self.wait)
        self.logged_in = True
    
    def ensure_logged_in(self):
        if not self.logged_in:
            raise RuntimeError('Must be logged in')
    
    def go_to_home(self):
        self.ensure_logged_in()
        self.browser.get(path.HOME_PATH)
        time.sleep(self.wait)

    def go_to_balances(self):
        self.ensure_logged_in()
        # BUG: selenium will not load headless pages with chromium
        # self.browser.get(path.HOLDINGS_PATH)
        # HACK: manually click the holdings page link instead
        self.browser.find_element(By.XPATH, '//a[normalize-space()="Balances"]').click()
        time.sleep(self.wait)

    def get_total_assets(self):
        self.go_to_balances()
        total_assets_str = self.browser.find_element(By.CLASS_NAME, 'balances--value-total')

        # $xx,xxx.xx
        total_assets_str.text.split(' ')

        # Remove '$' and commas
        return float(total_assets_str[1:].replace(',', ''))

    def get_account_holdings(self):
        self.go_to_balances()
        accounts = []
        balances_table = self.browser.find_element(By.CLASS_NAME, 'balances--table')

        # For each table row, there are two cells. 'account name' and 'holdings'
        for row in balances_table.find_elements(By.CSS_SELECTOR, 'balances--table-content'):
            account = {}

            # Each row contains three cells (Name, Total Balance, Change)
            for index, cell in enumerate(row.find_elements(By.CLASS_NAME, '')):
                # First cell is account name
                if index == 0:
                    account.update({'account': cell.text.strip()})
                elif index == 1:
                    # Remove '$' and commas
                    amount = float(cell.text[1:].replace(',', ''))
                    account.update({'holdings': amount})
            accounts.append(account)
        del accounts['total']
        return accounts
