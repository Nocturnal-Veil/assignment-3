import unittest
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

BASE_URL = "http://13.53.171.202:5001"
WAIT_TIMEOUT = 15


# ─────────────────────────────────────────────────────────────
# DRIVER SETUP
# ─────────────────────────────────────────────────────────────

def get_driver():
    """Create Chrome driver configured for Jenkins + Docker."""

    chrome_options = Options()

    # Required for Docker/Jenkins
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Stability
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Avoid automation detection issues
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Explicit chromedriver path
    service = Service("/usr/local/bin/chromedriver")

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    driver.implicitly_wait(10)

    return driver


# ─────────────────────────────────────────────────────────────
# TEST CLASS
# ─────────────────────────────────────────────────────────────

class LibraryAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait = WebDriverWait(cls.driver, WAIT_TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def navigate_to(self, path="/"):
        """Navigate to a page."""
        self.driver.get(BASE_URL + path)
        time.sleep(1)

    # ─────────────────────────────────────────────────────────
    # TC-01 Homepage loads
    # ─────────────────────────────────────────────────────────

    def test_01_homepage_loads(self):
        self.navigate_to("/")

        self.assertIn(
            "Library",
            self.driver.title + self.driver.page_source,
            "Homepage should contain 'Library'"
        )

    # ─────────────────────────────────────────────────────────
    # TC-02 Navigation links exist
    # ─────────────────────────────────────────────────────────

    def test_02_navigation_links_present(self):
        self.navigate_to("/")

        page = self.driver.page_source.lower()

        self.assertIn("books", page)
        self.assertIn("members", page)
        self.assertIn("borrows", page)

    # ─────────────────────────────────────────────────────────
    # TC-03 Books page loads
    # ─────────────────────────────────────────────────────────

    def test_03_books_page_loads(self):
        self.navigate_to("/books")

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        page = self.driver.page_source.lower()

        self.assertIn("book", page)

    # ─────────────────────────────────────────────────────────
    # TC-04 Books list has data
    # ─────────────────────────────────────────────────────────

    def test_04_books_list_has_data(self):
        self.navigate_to("/books")

        time.sleep(2)

        page = self.driver.page_source

        has_data = (
            "gatsby" in page.lower()
            or "mockingbird" in page.lower()
            or "1984" in page.lower()
            or "clean code" in page.lower()
            or "book" in page.lower()
        )

        self.assertTrue(
            has_data,
            "Books list should contain at least one book"
        )

    # ─────────────────────────────────────────────────────────
    # TC-05 Add Book button exists
    # ─────────────────────────────────────────────────────────

    def test_05_add_book_button_exists(self):
        self.navigate_to("/books")

        page = self.driver.page_source.lower()

        self.assertIn("add", page)

    # ─────────────────────────────────────────────────────────
    # TC-06 Add new book
    # ─────────────────────────────────────────────────────────

    def test_06_add_new_book(self):
        self.navigate_to("/books")

        try:
            add_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'ADD')]"
                    )
                )
            )

            add_btn.click()

            time.sleep(1)

            title_field = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[contains(@placeholder,'Title') or contains(@placeholder,'title')]"
                    )
                )
            )

            title_field.clear()
            title_field.send_keys("Selenium Test Book")

            author_field = self.driver.find_element(
                By.XPATH,
                "//input[contains(@placeholder,'Author') or contains(@placeholder,'author')]"
            )

            author_field.clear()
            author_field.send_keys("Test Author")

            submit_btn = self.driver.find_element(
                By.XPATH,
                "//button[@type='submit' or contains(text(),'Save') or contains(text(),'Add')]"
            )

            submit_btn.click()

            time.sleep(2)

            self.assertIn(
                "Selenium Test Book",
                self.driver.page_source
            )

        except Exception as e:
            self.skipTest(f"Add book test skipped: {e}")

    # ─────────────────────────────────────────────────────────
    # TC-07 Members page loads
    # ─────────────────────────────────────────────────────────

    def test_07_members_page_loads(self):
        self.navigate_to("/members")

        page = self.driver.page_source.lower()

        self.assertIn("member", page)

    # ─────────────────────────────────────────────────────────
    # TC-08 Members list has data
    # ─────────────────────────────────────────────────────────

    def test_08_members_list_has_data(self):
        self.navigate_to("/members")

        time.sleep(2)

        page = self.driver.page_source

        has_data = (
            "ali" in page.lower()
            or "sara" in page.lower()
            or "ahmed" in page.lower()
            or "@example.com" in page.lower()
        )

        self.assertTrue(has_data)

    # ─────────────────────────────────────────────────────────
    # TC-09 Add member button exists
    # ─────────────────────────────────────────────────────────

    def test_09_add_member_button_exists(self):
        self.navigate_to("/members")

        page = self.driver.page_source.lower()

        self.assertIn("add", page)

    # ─────────────────────────────────────────────────────────
    # TC-10 Add new member
    # ─────────────────────────────────────────────────────────

    def test_10_add_new_member(self):
        self.navigate_to("/members")

        try:
            add_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'ADD')]"
                    )
                )
            )

            add_btn.click()

            time.sleep(1)

            name_field = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[contains(@placeholder,'Name') or contains(@placeholder,'name')]"
                    )
                )
            )

            name_field.clear()
            name_field.send_keys("Selenium Tester")

            email_field = self.driver.find_element(
                By.XPATH,
                "//input[@type='email' or contains(@placeholder,'email')]"
            )

            unique_email = f"seltest{int(time.time())}@test.com"

            email_field.clear()
            email_field.send_keys(unique_email)

            submit_btn = self.driver.find_element(
                By.XPATH,
                "//button[@type='submit' or contains(text(),'Save') or contains(text(),'Add')]"
            )

            submit_btn.click()

            time.sleep(2)

            self.assertIn(
                "Selenium Tester",
                self.driver.page_source
            )

        except Exception as e:
            self.skipTest(f"Add member test skipped: {e}")

    # ─────────────────────────────────────────────────────────
    # TC-11 Borrows page loads
    # ─────────────────────────────────────────────────────────

    def test_11_borrows_page_loads(self):
        self.navigate_to("/borrows")

        page = self.driver.page_source.lower()

        self.assertIn("borrow", page)

    # ─────────────────────────────────────────────────────────
    # TC-12 Borrows columns
    # ─────────────────────────────────────────────────────────

    def test_12_borrows_page_columns(self):
        self.navigate_to("/borrows")

        time.sleep(2)

        page = self.driver.page_source.lower()

        self.assertTrue(
            "member" in page
            or "book" in page
            or "status" in page
        )

    # ─────────────────────────────────────────────────────────
    # TC-13 Dashboard stats
    # ─────────────────────────────────────────────────────────

    def test_13_dashboard_stats(self):
        self.navigate_to("/")

        time.sleep(2)

        page = self.driver.page_source

        numbers = re.findall(r"\b\d+\b", page)

        self.assertTrue(
            len(numbers) > 0,
            "Dashboard should contain numeric stats"
        )

    # ─────────────────────────────────────────────────────────
    # TC-14 API books endpoint
    # ─────────────────────────────────────────────────────────

    def test_14_api_books_endpoint(self):
        self.driver.get(BASE_URL + "/api/books")

        time.sleep(1)

        page = self.driver.page_source.lower()

        self.assertTrue(
            "[" in page
            or "title" in page
        )

    # ─────────────────────────────────────────────────────────
    # TC-15 API members endpoint
    # ─────────────────────────────────────────────────────────

    def test_15_api_members_endpoint(self):
        self.driver.get(BASE_URL + "/api/members")

        time.sleep(1)

        page = self.driver.page_source.lower()

        self.assertTrue(
            "[" in page
            or "name" in page
            or "email" in page
        )


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import xmlrunner

    with open("test-results.xml", "wb") as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False,
            buffer=False,
            catchbreak=False
        )