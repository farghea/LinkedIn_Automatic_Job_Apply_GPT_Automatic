#%% 
import subprocess
import time
import pygetwindow as gw
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
import pyautogui
import logging
from modules import jobnavigator as jnav

class LinkedInAutomation:
    def __init__(self, edge_path, remote_debugging_port=9222, user_data_dir="C:\\edge-debug"):
        self.edge_path = edge_path
        self.remote_debugging_port = remote_debugging_port
        self.user_data_dir = user_data_dir
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')

    def start_edge_with_debugging(self):
        try:
            subprocess.Popen([
                self.edge_path,
                f"--remote-debugging-port={self.remote_debugging_port}",
                f"--user-data-dir={self.user_data_dir}"
            ])
            time.sleep(3)  # Increased wait time
            self.logger.info("Edge browser started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Edge: {str(e)}")
            raise

    def connect_to_existing_session(self):
        try:
            edge_options = webdriver.EdgeOptions()
            edge_options.add_experimental_option("debuggerAddress", f"localhost:{self.remote_debugging_port}")
            self.driver = webdriver.Edge(options=edge_options)
            self.logger.info("Connected to existing Edge session")
        except Exception as e:
            self.logger.error(f"Failed to connect to Edge session: {str(e)}")
            raise

    def open_linkedin(self):
        try:
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)  # Increased wait time
            self.logger.info("Opened LinkedIn jobs page")
        except Exception as e:
            self.logger.error(f"Failed to open LinkedIn: {str(e)}")
            raise

    def activate_linkedin_window(self):
        try:
            windows = gw.getAllWindows()
            edge_window = None
            
            # Try different possible window titles
            for win in windows:
                if any(title in win.title for title in ["LinkedIn", "Jobs", "Edge"]):
                    edge_window = win
                    break

            if edge_window:
                edge_window.activate()
                edge_window.maximize()
                time.sleep(2)
                
                # Press Escape to close any potential popups
                pyautogui.press("esc")
                time.sleep(1)
                self.logger.info("LinkedIn window activated and maximized")
            else:
                raise Exception("Could not find LinkedIn window")
                
        except Exception as e:
            self.logger.error(f"Error activating window: {str(e)}")
            raise

    def wait_and_find_element(self, by, value, timeout=2, retries=3):
        """Helper method to find elements with retry logic"""
        for attempt in range(retries):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                )
            except TimeoutException:
                if attempt == retries - 1:
                    self.logger.error(f"Element not found after {retries} attempts: {value}")
                    raise
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)

    def find_search_bar(self):
        """Try multiple possible selectors for the search bar"""
        search_selectors = [
            # ("xpath", "//input[contains(@placeholder, 'Title')]"),
            # ("xpath", "//input[contains(@placeholder, 'Search')]"),
            ("xpath", "//input[contains(@class, 'jobs-search-box__text-input')]"),
            # ("xpath", "//input[contains(@aria-label, 'Search by title')]"),
            # ("xpath", "//input[contains(@id, 'jobs-search-box-keyword-id')]"),
            # ("css", "input.jobs-search-box__text-input"),
        ]

        for selector_type, selector in search_selectors:
            try:
                if selector_type == "xpath":
                    element = self.wait_and_find_element(By.XPATH, selector)
                else:
                    element = self.wait_and_find_element(By.CSS_SELECTOR, selector)
                if element:
                    self.logger.info(f"Found search bar using selector: {selector}")
                    return element
            except (TimeoutException, NoSuchElementException):
                continue

        raise Exception("Could not find search bar with any known selector")

    def search(self, query_job_title, location):
        try:
            # Find and click search bar
            search_bar = self.find_search_bar()
            search_bar.click()
            time.sleep(random.uniform(1, 2))

            # Clear existing text
            search_bar.clear()
            time.sleep(random.uniform(0.5, 1))

            # Type query with random delays
            for char in query_job_title:
                search_bar.send_keys(char)
                time.sleep(random.uniform(0.02, 0.06))

            # Press TAB twice to get to location field
            time.sleep(random.uniform(0.2, 0.5))
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('tab')
            time.sleep(0.2)

            # Type location
            pyautogui.write(location)
            time.sleep(0.2)
            
            # Press Enter to submit
            pyautogui.press('enter')
            time.sleep(1)  # Wait for search to complete
            
            self.logger.info(f"Successfully searched for: {query_job_title} in {location}")
            
        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            raise

    def take_screen_shot(self, screen_shot_name="temp.png"):
        try:
            time.sleep(2)
            self.driver.save_screenshot(screen_shot_name)
            self.logger.info(f"Screenshot saved as {screen_shot_name}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            raise

    def close(self):
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser session closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {str(e)}")

    def select_date_posted(self, option="Past Week"):
        """Select the 'Date Posted' filter option from the dropdown."""
        try:
            # Open the Date Posted dropdown
            date_posted_dropdown = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Date Posted')]"))
            )
            date_posted_dropdown.click()
            time.sleep(1)  # Short wait to allow options to load

            # Select the desired option (e.g., Past Week)
            option_element = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[text()='{option}']"))
            )
            option_element.click()
            time.sleep(2)  # Wait to allow the filter to apply

            self.logger.info(f"Selected '{option}' in Date Posted filter.")
            
        except TimeoutException:
            self.logger.error(f"Failed to find the '{option}' option in Date Posted filter.")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while selecting '{option}' in Date Posted filter: {str(e)}")
            raise
    
    def click_show_results(self):
        """Click the button containing 'Show' text, ignoring any other dynamic text."""
        try:
            # Locate a button containing 'Show' (case-insensitive)
            show_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, 
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show')]")
                )
            )
            show_button.click()
            time.sleep(random.uniform(2))  # Wait for the results to load
            
            self.logger.info("Clicked button containing 'Show'.")
        except TimeoutException:
            self.logger.error("Failed to find a button containing 'Show'.")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while clicking the 'Show' button: {str(e)}")
            raise
    
    def get_pagination_info(self):
        """
        Get information about all pagination elements.
        Returns a list of dictionaries containing page numbers and their elements.
        """
        try:
            # Wait for pagination container to be present
            pagination_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.artdeco-pagination__pages"))
            )
            
            # Find all pagination items
            pagination_items = pagination_container.find_elements(
                By.CSS_SELECTOR, 
                "li.artdeco-pagination__indicator--number"
            )
            
            pagination_info = []
            for item in pagination_items:
                try:
                    # Get the button element
                    button = item.find_element(By.TAG_NAME, "button")
                    span = button.find_element(By.TAG_NAME, "span")
                    
                    # Get page number or ellipsis
                    page_text = span.text.strip()
                    if page_text == "…":
                        page_number = -1  # Indicate ellipsis
                    else:
                        page_number = int(page_text)
                    
                    # Check if this is the active/current page
                    is_active = "active selected" in item.get_attribute("class")
                    
                    pagination_info.append({
                        'page_number': page_number,
                        'element': item,
                        'button': button,
                        'is_active': is_active,
                        'is_ellipsis': page_text == "…",
                        'aria_label': button.get_attribute('aria-label')
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing pagination item: {str(e)}")
                    continue
                    
            return pagination_info
            
        except Exception as e:
            self.logger.error(f"Error getting pagination info: {str(e)}")
            return []
    
    def wait_and_click(self, text, wait_time=1.46543, scroll=True):
        """
        Wait for an element containing specific text, scroll to it, and click.
        """
        try:
            # Wait for the element containing the text
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, f"//span[normalize-space()='{text}']"))
            )
            if scroll:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            
            # Click the element
            element.click()
            self.logger.info(f"Successfully clicked element with text: {text}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to find and click element with text '{text}': {e}")
            return False

    def set_date_posted_to_past_week(self):
        """
        Sets the 'Date Posted' filter to 'Past Week' on LinkedIn job search.
        """
        # Step 1: Open the "Date Posted" dropdown
        if self.wait_and_click("Date posted"):
            self.logger.info("Opened 'Date Posted' dropdown.")
            
            # Step 2: Select "Past Week" from the dropdown
            if self.wait_and_click("Past week"):
                self.logger.info("Selected 'Past Week' under 'Date Posted' filter.")
            else:
                self.logger.error("Failed to find 'Past Week' option in 'Date Posted' filter.")
        else:
            self.logger.error("Failed to open 'Date posted' dropdown.")

    def click_show_results_button(self, max_retries=3, timeout=5):
        """
        Click the 'Show results' button that contains a dynamic number.
        Uses multiple strategies and includes retry logic.
        """
        xpath_patterns = [
            # Pattern 1: Match any button containing both "Show" and "results" with any text between
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'results')]",
            
            # Pattern 2: Match button with specific class
            "//button[contains(@class, 'jobs-search-results__show-results-button')]",
            
            # Pattern 3: More specific pattern matching "Show X results" format
            "//button[matches(text(), '^Show [0-9,]+ results$')]",
            
            # Pattern 4: Looking for parent container that might have the button
            "//div[contains(@class, 'jobs-search-results')]//button[contains(., 'Show')]"
        ]
        
        for attempt in range(max_retries):
            try:
                # Try each XPath pattern until one works
                for xpath in xpath_patterns:
                    try:
                        self.logger.debug(f"Trying XPath pattern: {xpath}")
                        # Wait for element presence
                        button = WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        
                        # Scroll the button into view
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        
                        # Add a small wait to let the page settle
                        time.sleep(1)
                        
                        # Try multiple click methods
                        try:
                            # Method 1: Direct click
                            button.click()
                        except:
                            try:
                                # Method 2: JavaScript click
                                self.driver.execute_script("arguments[0].click();", button)
                            except:
                                # Method 3: Action chains
                                ActionChains(self.driver).move_to_element(button).click().perform()
                        
                        self.logger.info("Successfully clicked 'Show results' button")
                        return True
                        
                    except TimeoutException:
                        continue
                
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to click 'Show results' button after {max_retries} attempts")
                time.sleep(2)
        
        return False
    
    



if __name__ == "__main__":
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"

    linkedin_bot = LinkedInAutomation(edge_path)
    linkedin_bot.start_edge_with_debugging()
    linkedin_bot.connect_to_existing_session()
    linkedin_bot.open_linkedin()
    linkedin_bot.activate_linkedin_window()
    linkedin_bot.search(query_job_title="biomechanics", location='canada')
    linkedin_bot.set_date_posted_to_past_week()
    linkedin_bot.click_show_results_button()
    
    


