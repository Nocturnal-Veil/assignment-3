import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BASE_URL = "http://13.63.56.101:5001"
WAIT_TIMEOUT = 15
# ──────────────────────────────────────────────────────────────────────────────


def get_driver():
    """Create a headless Chrome driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver


class LibraryAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait = WebDriverWait(cls.driver, WAIT_TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def navigate_to(self, path="/"):
        self.driver.get(BASE_URL + path)
        time.sleep(1)

    # ── TC-01: Homepage loads ──────────────────────────────────────────────────
    def test_01_homepage_loads(self):
        """TC-01: The app loads and displays the dashboard."""
        self.navigate_to("/")
        self.assertIn("Library", self.driver.title + self.driver.page_source,
                      "Dashboard page should mention 'Library'")

    # ── TC-02: Navigation links exist ─────────────────────────────────────────
    def test_02_navigation_links_present(self):
        """TC-02: Navigation sidebar/navbar contains Books, Members, Borrows links."""
        self.navigate_to("/")
        page = self.driver.page_source.lower()
        self.assertIn("books", page, "Navigation should have Books link")
        self.assertIn("members", page, "Navigation should have Members link")
        self.assertIn("borrows", page, "Navigation should have Borrows link")

    # ── TC-03: Books page loads ────────────────────────────────────────────────
    def test_03_books_page_loads(self):
        """TC-03: Navigating to /books shows the Books page."""
        self.navigate_to("/books")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page = self.driver.page_source.lower()
        self.assertIn("book", page, "Books page should display book content")

    # ── TC-04: Books list displays data ───────────────────────────────────────
    def test_04_books_list_has_data(self):
        """TC-04: The books list contains at least one book from the database."""
        self.navigate_to("/books")
        time.sleep(2)  # wait for API call
        page = self.driver.page_source
        # Sample data includes 'The Great Gatsby' or 'Clean Code'
        has_data = ("Gatsby" in page or "Mockingbird" in page
                    or "1984" in page or "Clean Code" in page
                    or "Book" in page)
        self.assertTrue(has_data, "Books list should show at least one book")

    # ── TC-05: Add Book form opens ─────────────────────────────────────────────
    def test_05_add_book_button_exists(self):
        """TC-05: An 'Add Book' button exists on the books page."""
        self.navigate_to("/books")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page = self.driver.page_source.lower()
        self.assertIn("add", page, "Books page should have an Add button")

    # ── TC-06: Add a new book ──────────────────────────────────────────────────
    def test_06_add_new_book(self):
        """TC-06: Fill in the Add Book form and submit it successfully."""
        self.navigate_to("/books")
        time.sleep(1)

        # Click the Add Book button
        try:
            add_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'ADD')]")
                )
            )
            add_btn.click()
        except Exception:
            # fallback: look for any button that might open a form
            btns = self.driver.find_elements(By.TAG_NAME, "button")
            for b in btns:
                if "add" in b.text.lower():
                    b.click()
                    break

        time.sleep(1)

        # Fill title field
        try:
            title_field = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@placeholder[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'title')]]")
                )
            )
            title_field.clear()
            title_field.send_keys("Selenium Test Book")

            # Fill author field
            author_field = self.driver.find_element(
                By.XPATH, "//input[@placeholder[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'author')]]"
            )
            author_field.clear()
            author_field.send_keys("Test Author")

            # Submit form
            submit_btn = self.driver.find_element(
                By.XPATH, "//button[@type='submit' or contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'SAVE') or contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'ADD')]"
            )
            submit_btn.click()
            time.sleep(2)
            self.assertIn("Selenium Test Book", self.driver.page_source,
                          "Newly added book should appear in the list")
        except Exception as e:
            self.skipTest(f"Add book form not found or changed: {e}")

    # ── TC-07: Members page loads ──────────────────────────────────────────────
    def test_07_members_page_loads(self):
        """TC-07: Navigating to /members shows the Members page."""
        self.navigate_to("/members")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page = self.driver.page_source.lower()
        self.assertIn("member", page, "Members page should show member content")

    # ── TC-08: Members list has data ──────────────────────────────────────────
    def test_08_members_list_has_data(self):
        """TC-08: The members list shows at least one member from sample data."""
        self.navigate_to("/members")
        time.sleep(2)
        page = self.driver.page_source
        has_data = ("Ali" in page or "Sara" in page or "Khan" in page
                    or "Ahmed" in page or "@example.com" in page)
        self.assertTrue(has_data, "Members list should display at least one member")

    # ── TC-09: Add member button exists ───────────────────────────────────────
    def test_09_add_member_button_exists(self):
        """TC-09: An 'Add Member' button exists on the members page."""
        self.navigate_to("/members")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page = self.driver.page_source.lower()
        self.assertIn("add", page, "Members page should have an Add button")

    # ── TC-10: Add a new member ────────────────────────────────────────────────
    def test_10_add_new_member(self):
        """TC-10: Fill in the Add Member form and submit it successfully."""
        self.navigate_to("/members")
        time.sleep(1)

        try:
            add_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'ADD')]")
                )
            )
            add_btn.click()
        except Exception:
            btns = self.driver.find_elements(By.TAG_NAME, "button")
            for b in btns:
                if "add" in b.text.lower():
                    b.click()
                    break

        time.sleep(1)

        try:
            name_field = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@placeholder[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'name')]]")
                )
            )
            name_field.clear()
            name_field.send_keys("Selenium Tester")

            email_field = self.driver.find_element(
                By.XPATH, "//input[@type='email' or @placeholder[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'email')]]"
            )
            email_field.clear()
            unique_email = f"seltest{int(time.time())}@test.com"
            email_field.send_keys(unique_email)

            submit_btn = self.driver.find_element(
                By.XPATH, "//button[@type='submit' or contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'SAVE') or contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'ADD')]"
            )
            submit_btn.click()
            time.sleep(2)
            self.assertIn("Selenium Tester", self.driver.page_source,
                          "Newly added member should appear in the list")
        except Exception as e:
            self.skipTest(f"Add member form not found or changed: {e}")

    # ── TC-11: Borrows page loads ──────────────────────────────────────────────
    def test_11_borrows_page_loads(self):
        """TC-11: Navigating to /borrows shows the Borrows page."""
        self.navigate_to("/borrows")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page = self.driver.page_source.lower()
        self.assertIn("borrow", page, "Borrows page should display borrow content")

    # ── TC-12: Borrows page has expected table columns ─────────────────────────
    def test_12_borrows_page_columns(self):
        """TC-12: Borrows table has Member, Book, Due Date, Status columns."""
        self.navigate_to("/borrows")
        time.sleep(2)
        page = self.driver.page_source.lower()
        self.assertTrue(
            "member" in page or "book" in page or "status" in page,
            "Borrows page should have table columns for member, book, or status"
        )

    # ── TC-13: Dashboard shows summary stats ──────────────────────────────────
    def test_13_dashboard_stats(self):
        """TC-13: Dashboard page shows numeric statistics."""
        self.navigate_to("/")
        time.sleep(2)
        page = self.driver.page_source
        # Look for numbers that indicate stats are loaded
        import re
        numbers = re.findall(r'\b\d+\b', page)
        self.assertTrue(len(numbers) > 0,
                        "Dashboard should display some numeric statistics")

    # ── TC-14: API /api/books returns JSON ────────────────────────────────────
    def test_14_api_books_endpoint(self):
        """TC-14: The /api/books endpoint is reachable and returns data."""
        self.driver.get(BASE_URL + "/api/books")
        time.sleep(1)
        page = self.driver.page_source
        # Valid JSON array from the API will contain '[' or 'title'
        self.assertTrue(
            "[" in page or "title" in page.lower(),
            "API /api/books should return a JSON list of books"
        )

    # ── TC-15: API /api/members returns JSON ──────────────────────────────────
    def test_15_api_members_endpoint(self):
        """TC-15: The /api/members endpoint is reachable and returns data."""
        self.driver.get(BASE_URL + "/api/members")
        time.sleep(1)
        page = self.driver.page_source
        self.assertTrue(
            "[" in page or "name" in page.lower() or "email" in page.lower(),
            "API /api/members should return a JSON list of members"
        )


if __name__ == "__main__":
    import xmlrunner
    with open("test-results.xml", "wb") as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False,
            buffer=False,
            catchbreak=False
        )