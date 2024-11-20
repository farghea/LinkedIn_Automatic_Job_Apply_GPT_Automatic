#%% 
import time
import random
import json
from datetime import datetime
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules import linkedin2 as ln
from modules import utils as ut 
from modules import easyapplynav as ezappnav


class LinkedInJobNavigator:
    def __init__(self, driver):
        self.driver = driver
        self.current_job_index = 0
        self.jobs_list = []
        
    def scroll_to_element(self, element, behavior="smooth"):
        """Scroll element into view smoothly"""
        self.driver.execute_script(
            'arguments[0].scrollIntoView({block: "center", behavior: "' + behavior + '"});',
            element
        )
        time.sleep(random.uniform(0.5, 1))  # Random delay to mimic human behavior

    def get_job_cards(self):
        """Find all job cards in the current view"""
        try:
            # Wait for job cards to be present
            job_cards = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".job-card-container")
                )
            )
            return job_cards
        except TimeoutException:
            print("Timeout waiting for job cards to load")
            return []

    def click_job_card(self, job_card):
        """Click on a job card and wait for details to load"""
        try:
            # Scroll the job card into view
            self.scroll_to_element(job_card)
            
            # Click the job card
            job_card.click()
            
            # Wait for job details to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "jobs-search__job-details")
                )
            )
            
            # Add small random delay to mimic human behavior
            time.sleep(random.uniform(1, 2))
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error clicking job card: {str(e)}")
            return False

    def initial_setup(self):
        """Click first job and scroll to load content"""
        try:
            # Find and click the first job
            first_job = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-card-container"))
            )
            self.scroll_to_element(first_job)
            first_job.click()
            print("Clicked first job")
            
            # Wait for job details to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__job-details"))
            )
            
            # Scroll through the jobs list to load more content
            jobs_list = self.driver.find_element(By.CLASS_NAME, "jobs-search-results-list")
            
            # Slower, incremental scrolling
            total_height = self.driver.execute_script("return arguments[0].scrollHeight", jobs_list)
            current_position = 0
            step = 300  # Scroll 300 pixels at a time
            
            while current_position < total_height:
                current_position += step
                self.driver.execute_script(
                    f"arguments[0].scrollTop = {current_position};", 
                    jobs_list
                )
                time.sleep(random.uniform(0.8, 1.2))  # Random delay between scrolls
            
            # Scroll back to top smoothly
            current_position = total_height
            while current_position > 0:
                current_position -= step
                self.driver.execute_script(
                    f"arguments[0].scrollTop = {current_position};", 
                    jobs_list
                )
                time.sleep(random.uniform(0.5, 0.7))
                
            print("Initial setup completed")
            return True
            
        except Exception as e:
            print(f"Error in initial setup: {str(e)}")
            return False
    
    def navigate_jobs(self, driver, tailor_cv = False, max_jobs=None):
        """
        Navigate through job listings one by one
        Args:
            max_jobs: Maximum number of jobs to process (None for all jobs)
        """
        # self.easy_apply_filter(driver)
        
        processed_jobs = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # self.initial_setup()

        while True:
            # Get current job cards
            job_cards = self.get_job_cards()
            
            # Process each job card
            for job_index, job_card in enumerate(job_cards[self.current_job_index:]):
                if max_jobs and processed_jobs >= max_jobs:
                    print(f"Reached maximum number of jobs to process ({max_jobs})")
                    return
                
                if self.click_job_card(job_card):
                    processed_jobs += 1
                    self.current_job_index += 1
                    print(f"Processed job {processed_jobs}")
                    
                    # **************** here is the main part where magic happens ***************
                    # Check if job has Easy Apply button
                    if "easy apply" not in job_card.text.lower():
                        continue
                    
                    # Get job description and process CV
                    job_description_text = ut.find_job_description(driver)
                    
                    # Load CV name from user profile
                    with open('user_profile.json') as file:
                        cv_name = json.load(file).get("CV_file_name")
                    
                    if tailor_cv:
                        # Create CVAdjuster instance and process CV
                        cv_adjuster = CVAdjuster(
                            job_description=job_description_text,
                            cv_tex_path=f'CV/{cv_name}'
                        )
                        
                        # Process the CV (modifies, saves, and generates PDF)
                        cv_adjuster.process_cv()
                        cv_path = os.path.join(os.getcwd(), 'CV', cv_adjuster.new_filename)
                        print(f'Adjusted CV is saved as {cv_adjuster.new_filename}')
                    else:
                        cv_path = os.path.join(os.getcwd(), 'CV', cv_name.split('.')[0]+'.pdf')
                        print(f'CV is NOT tailored: {cv_name}')

                    # Click Easy Apply and handle the application
                    self.click_easy_apply()
                    print('clicked on "easy apply"')


                    # this is to exit the cases where linkedin warns about the 
                    # vailidty of the job 
                    time.sleep(0.5)
                    self.click_continue_applying()

                    # Applying for the job (move on after 90 sec)
                    # with ThreadPoolExecutor(max_workers=1) as executor:
                    #     future = executor.submit(lambda: ezappnav.EasyApplyNavigator(driver).apply_job(cv_path))
                    #     try:
                    #         # Set timeout duration in seconds
                    #         result = future.result(timeout = 5)
                    #     except TimeoutError:
                    #         ut.click_discard_button(driver)
                    #         continue
                    
                    ez_nav = ezappnav.EasyApplyNavigator(driver)
                    if tailor_cv or (job_index <=5):
                        upload_cv = True
                    else:
                        upload_cv = False

                    ez_nav.apply_job(cv_path, upload_cv)
                    
                    # ******************************************************************************
                
                # Add random delay between jobs
                time.sleep(random.uniform(1.5, 3))
            
            # Scroll down to load more jobs
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new content to load
            
            # Check if we've reached the bottom of the page
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached end of job listings")
                break
            last_height = new_height
    
    def click_easy_apply(self):
        """Click the Easy Apply button and wait for the modal to load"""
        try:
            # Try multiple selectors for the Easy Apply button
            easy_apply_selectors = [
                ".jobs-apply-button",
                "button[aria-label='Easy Apply']",
                ".jobs-s-apply button",
                ".jobs-apply-button--top-card"
            ]
            
            for selector in easy_apply_selectors:
                try:
                    # Wait for button to be present and clickable
                    easy_apply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    # Check if it's an Easy Apply button
                    if "Easy Apply" in easy_apply_button.text:
                        # Scroll to button and click
                        self.scroll_to_element(easy_apply_button)
                        time.sleep(random.uniform(0.5, 1))
                        easy_apply_button.click()
                        
                        # Wait for application modal to appear
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "jobs-easy-apply-modal"))
                        )
                        print("Clicked Easy Apply and modal opened")
                        return True
                        
                except (TimeoutException, NoSuchElementException):
                    continue
                    
            print("Could not find Easy Apply button")
            return False
            
        except Exception as e:
            print(f"Error clicking Easy Apply: {str(e)}")
            return False
    
    def easy_apply_filter(self, driver):
        easy_apply_filter = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Easy Apply filter.']"))
        )
        easy_apply_filter.click()
        time.sleep(random.uniform(1, 2))

        return None
    
    def click_continue_applying(self, timeout=3, max_retries=1):
        """Click the 'Continue applying' button if it appears"""
        for attempt in range(max_retries):
            try:
                continue_button = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((
                        By.XPATH, 
                        "//span[contains(@class, 'artdeco-button__text') and text()='Continue applying']"
                    ))
                )
                continue_button.click()
                print("Clicked 'Continue applying' button")
                return True
            except TimeoutException:
                if attempt == max_retries - 1:
                    print("No 'Continue applying' button found")
                    return False
                time.sleep(0.2)
        return False



class CVAdjuster:
    def __init__(self, job_description, cv_tex_path):
        try:
            self.job_description = job_description
            self.cv_tex_path = cv_tex_path
            self.original_dir = os.getcwd()
            
            try:
                with open(cv_tex_path, 'r', encoding='utf-8') as file:
                    self.cv_content = file.read()
                print(f"Successfully loaded CV from {cv_tex_path}")
            except Exception as e:
                print(f"Error reading CV file: {str(e)}")
                self.cv_content = None
            
            self.modified_content = None
            self.keywords = set()
            self.missing_skills = set()
            
            # Initialize OpenAI chatbot
            self.chatbot = ut.OpenAIChatBot(
                api_key_path='user_profile.json', 
                # model="gpt-4", 
                model = "gpt-3.5-turbo",
                use_history=True
            )
            
        except Exception as e:
            print(f"Error initializing CVAdjuster: {str(e)}")
            raise

    def modify_cv(self):
        """Modify CV content using GPT to tailor it for the job description"""
        try:
            # First review of job description
            initial_review = self.chatbot.send_message(
                f"Here is a job description that I am interested in applying for:\n\n"
                f"{self.job_description}\n\n"
                f"Please review it, as I'll be sending my CV next, and I'd like your help in tailoring it to align with this job."
            )

            # CV modification request
            modified_cv = self.chatbot.send_message(
                f"Please review and tailor the content of my CV (provided below in LaTeX format) "
                f"specifically for the job description. Keep these guidelines in mind:\n"
                f"1. Do NOT change or modify the LaTeX formatting or structure in any way.\n"
                f"2. ONLY adjust the text content within the CV to make it more relevant and tailored for the job.\n"
                f"3. Keep it concise and professional. Avoid verbosity or unrealistic phrasing.\n"
                f"4. In your response, include ONLY the modified LaTeX code, starting directly with it "
                f"without any introduction or extra commentary.\n\n"
                f"Here is my CV in LaTeX format:\n\n"
                f"{self.cv_content}"
            )

            # Final verification and cleanup
            final_cv = self.chatbot.send_message(
                f"1. please make sure the latex format is correct and can be compibled without an issue.\n"
                f"2. In your response, include ONLY the modified LaTeX code, starting directly with it "
                f"without any introduction or extra commentary.\n\n"
                f"Here is your previous response:\n\n"
                f"{modified_cv}"
            )

            self.modified_content = final_cv
            return final_cv

        except Exception as e:
            print(f"Error in modify_cv: {str(e)}")
            return None

    def save_modified_cv(self):
        """Save the modified CV content to a new file"""
        try:
            if not self.modified_content:
                print("No modified content to save")
                return None

            new_filename = f'cv_modified_{datetime.now().strftime("%Y%m%d_%H%M%S")}.tex'
            new_cv_path = os.path.join('CV', new_filename)
            self.new_filename = new_filename

            # Ensure CV directory exists
            os.makedirs('CV', exist_ok=True)

            with open(new_cv_path, 'w', encoding='utf-8') as file:
                file.write(self.modified_content)
            print(f"Modified CV saved to: {new_cv_path}")
            
            return new_cv_path

        except Exception as e:
            print(f"Error saving modified CV: {str(e)}")
            return None

    def generate_pdf(self):
        """Generate PDF from the modified LaTeX file"""
        try:
            if not self.modified_content:
                print("No modified content to generate PDF from")
                return None

            save_and_generate_pdf(self.modified_content, self.original_dir)
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")

    def process_cv(self):
        """Complete CV processing pipeline"""
        try:
            # Modify CV content
            self.modify_cv()
            
            # Save modified CV
            self.save_modified_cv()
            
            # Generate PDF
            self.generate_pdf()
            
        except Exception as e:
            print(f"Error in CV processing pipeline: {str(e)}")

    



def save_and_generate_pdf(response, original_dir):
    try:
        # Define file paths and directory
        new_filename = f'cv_modified_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        cv_folder = os.path.join(original_dir, 'CV')
        
        # Ensure directory exists
        os.makedirs(cv_folder, exist_ok=True)
        
        # Save LaTeX content to file
        tex_path = os.path.join(cv_folder, f'{new_filename}.tex')
        with open(tex_path, 'w', encoding='utf-8') as file:
            file.write(response)
        print(f"Modified CV saved to: {tex_path}")
        
        # Run pdflatex command within the cv_folder directory
        result = subprocess.run(
            ['pdflatex', new_filename + '.tex'],
            cwd=cv_folder,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            print(f"PDF generated at: {os.path.join(cv_folder, f'{new_filename}.pdf')}")
        else:
            print(f"PDF generation failed: {result.stderr.decode()}")

    except Exception as e:
        print(f"Error in CV generation: {str(e)}")



if __name__ == "__main__":
    edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    linkedin_bot = ln.LinkedInAutomation(edge_path)
    
    linkedin_bot.start_edge_with_debugging()
    linkedin_bot.connect_to_existing_session()
    linkedin_bot.open_linkedin()
    
    linkedin_bot.activate_linkedin_window()
    linkedin_bot.search(query_job_title="manager", location='London')
    linkedin_bot.set_date_posted_to_past_week()
    linkedin_bot.click_show_results_button()
    
    time.sleep(0.64)
    linkedin_bot.activate_linkedin_window()
    navigator = LinkedInJobNavigator(linkedin_bot.driver)
    navigator.easy_apply_filter(linkedin_bot.driver)
    navigator.initial_setup()
    pages = linkedin_bot.get_pagination_info()

    navigator.navigate_jobs(linkedin_bot.driver, tailor_cv = False)


    
    
    
    








