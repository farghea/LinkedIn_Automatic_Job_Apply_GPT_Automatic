#%% 

import time 
import random
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules import linkedin2 as ln
from modules import utils as ut 


class EasyApplyNavigator:
    def __init__(self, driver):
        self.driver = driver
        self.modal = None
        self.form_container = None
        
    def initialize_form_container(self):
        """Initialize the form container"""
        try:
            self.modal = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-easy-apply-modal"))
            )
            self.form_container = self.modal.find_element(By.CSS_SELECTOR, "div.jobs-easy-apply-content")
            return True
        except Exception as e:
            print(f"Error initializing form container: {str(e)}")
            return False


    def get_buttons(self):
        """Get all button elements"""
        if not self.form_container:
            if not self.initialize_form_container():
                return []
                
        try:
            all_buttons = []
            seen_elements = set()
            
            button_selectors = [
                ("button", By.CSS_SELECTOR, "button.artdeco-button:not(.hidden)"),
                ("upload", By.CSS_SELECTOR, "span[role='button'][aria-label*='Upload resume']"),
                ("file", By.CSS_SELECTOR, "input[type='file']"),
                ("button", By.CSS_SELECTOR, ".artdeco-button--primary"),
                ("button", By.CSS_SELECTOR, ".artdeco-button--tertiary"),
                ("button", By.CSS_SELECTOR, ".jobs-document-upload__replace-button")
            ]

            for button_type, by, selector in button_selectors:
                try:
                    elements = self.form_container.find_elements(by, selector)
                    for element in elements:
                        clickable_element = element
                        if not element.is_enabled():
                            try:
                                clickable_element = element.find_element(By.XPATH, "./ancestor::button")
                            except:
                                try:
                                    clickable_element = element.find_element(By.XPATH, "..")
                                except:
                                    continue

                        element_id = clickable_element.get_attribute('id') or clickable_element.get_attribute('class')
                        if element_id not in seen_elements:
                            seen_elements.add(element_id)
                            all_buttons.append({
                                'type': button_type,
                                'element': clickable_element,
                                'text': clickable_element.text,
                                'html_type': clickable_element.get_attribute('type'),
                                'aria_label': clickable_element.get_attribute('aria-label'),
                                'class': clickable_element.get_attribute('class'),
                                'is_enabled': clickable_element.is_enabled(),
                                'is_displayed': clickable_element.is_displayed()
                            })
                except:
                    continue

            return all_buttons
            
        except Exception as e:
            print(f"Error getting buttons: {str(e)}")
            return []
    

    def get_input_fields(self):
        """Get all input fields with their labels using multiple selector strategies"""
        if not self.form_container:
            if not self.initialize_form_container():
                return []
                
        try:
            input_fields = []
            seen_inputs = set()  # Track seen input IDs
            
            # Strategy 1: Direct label-input pairs
            label_selectors = [
                "label.artdeco-text-input--label",
                "label.fb-dash-form-element__label",
                "label[data-test-single-typeahead-entity-form-title]",
                "label.fb-form-element__label"
            ]
            
            for selector in label_selectors:
                labels = self.form_container.find_elements(By.CSS_SELECTOR, selector)
                
                for label in labels:
                    try:
                        # Get the 'for' attribute of the label
                        input_id = label.get_attribute('for')
                        
                        if not input_id or input_id in seen_inputs:
                            continue
                            
                        seen_inputs.add(input_id)
                        
                        # Find the corresponding input using the ID
                        input_field = self.form_container.find_element(By.ID, input_id)
                        
                        # Get label text
                        label_text = ""
                        span_elements = label.find_elements(By.CSS_SELECTOR, "span")
                        for span in span_elements:
                            if not span.get_attribute('class') or 'visually-hidden' not in span.get_attribute('class'):
                                span_text = span.text.strip()
                                if span_text:
                                    label_text = span_text
                                    break
                        
                        if not label_text:
                            label_text = label.text.strip()
                        
                        # Store input field information
                        input_fields.append({
                            'label_text': label_text,
                            'label_element': label,
                            'input_element': input_field,
                            'input_type': input_field.get_attribute('type'),
                            'required': input_field.get_attribute('required'),
                            'current_value': input_field.get_attribute('value'),
                            'class': input_field.get_attribute('class'),
                            'id': input_id
                        })
                        
                    except Exception as e:
                        print(f"Error processing input field: {str(e)}")
                        continue
            
            # Strategy 2: Find inputs directly and look for associated labels
            input_selectors = [
                "input[type='text']",
                "input[type='email']",
                "input[type='tel']",
                "input[type='number']",
                "input[role='combobox']",
                "input[required]"
            ]
            
            for selector in input_selectors:
                inputs = self.form_container.find_elements(By.CSS_SELECTOR, selector)
                
                for input_field in inputs:
                    try:
                        input_id = input_field.get_attribute('id')
                        
                        if not input_id or input_id in seen_inputs:
                            continue
                            
                        seen_inputs.add(input_id)
                        
                        # Try to find associated label
                        label_element = None
                        label_text = ""
                        
                        try:
                            # Look for label with matching 'for' attribute
                            label_element = self.form_container.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                            # Extract text from span elements inside label
                            span_elements = label_element.find_elements(By.CSS_SELECTOR, "span")
                            for span in span_elements:
                                if not span.get_attribute('class') or 'visually-hidden' not in span.get_attribute('class'):
                                    span_text = span.text.strip()
                                    if span_text:
                                        label_text = span_text
                                        break
                                        
                            if not label_text:
                                label_text = label_element.text.strip()
                                
                        except:
                            # If no label found, try to find nearby text
                            try:
                                parent = input_field.find_element(By.XPATH, "./..")
                                siblings = parent.find_elements(By.XPATH, ".//*")
                                for sibling in siblings:
                                    if sibling.tag_name in ['span', 'div'] and sibling.text.strip():
                                        label_text = sibling.text.strip()
                                        break
                            except:
                                pass
                        
                        input_fields.append({
                            'label_text': label_text,
                            'label_element': label_element,
                            'input_element': input_field,
                            'input_type': input_field.get_attribute('type'),
                            'required': input_field.get_attribute('required'),
                            'current_value': input_field.get_attribute('value'),
                            'class': input_field.get_attribute('class'),
                            'id': input_id
                        })
                        
                    except Exception as e:
                        print(f"Error processing direct input field: {str(e)}")
                        continue
            
            # Remove any potential duplicates based on input ID
            seen = set()
            unique_input_fields = []
            for field in input_fields:
                if field['id'] not in seen:
                    seen.add(field['id'])
                    unique_input_fields.append(field)
                    
            return unique_input_fields
            
        except Exception as e:
            print(f"Error getting input fields: {str(e)}")
            return []
    
    # =======================================
    def get_selection_elements(self):
        """Get all selection elements (radio buttons/yes-no questions)"""
        if not self.form_container:
            if not self.initialize_form_container():
                return []
                
        try:
            selection_elements = []
            seen_questions = set()
            
            # Find all potential selection groups
            selectors = [
                "fieldset.fb-dash-form-element",
                ".jobs-easy-apply-form-section__input",
                ".fb-form-element__question-options",
                ".jobs-easy-apply-form-element",
                ".fb-dash-form-element"
            ]

            # Get all elements matching selectors
            elements = []
            for selector in selectors:
                elements.extend(self.form_container.find_elements(By.CSS_SELECTOR, selector))

            # Filter for valid selection elements with questions
            question_selectors = [
                "span[aria-hidden='true']",
                ".fb-form-element-label",
                ".jobs-easy-apply-form-element__label",
                ".fb-dash-form-element__label"
            ]
            
            for element in elements:
                try:
                    # Get question text
                    question_text = None
                    for q_selector in question_selectors:
                        try:
                            question = element.find_element(By.CSS_SELECTOR, q_selector)
                            question_text = question.text
                            if question_text:
                                break
                        except:
                            continue

                    # Skip duplicates and empty questions
                    if not question_text or question_text in seen_questions:
                        continue
                        
                    seen_questions.add(question_text)
                    
                    # Get options
                    options = element.find_elements(By.CSS_SELECTOR, "label.t-14") or \
                                element.find_elements(By.CSS_SELECTOR, "label[data-test-text-selectable-option__label]")
                    
                    if options:  # Only add if it has options
                        selection_elements.append({
                            'element': element,
                            'question': question_text,
                            'options': [{
                                'text': opt.text,
                                'label': opt,
                                'for': opt.get_attribute('for')
                            } for opt in options]
                        })
                        
                except Exception as e:
                    continue

            return selection_elements
            
        except Exception as e:
            print(f"Error getting selection elements: {str(e)}")
            return []
    
    def select_option(self, selection_element_dict, answer_text):
        """
        Select an option for a selection element
        Args:
            selection_element_dict: Dictionary from get_selection_elements containing element info
            answer_text: Text of the option to select ("Yes"/"No")
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            element = selection_element_dict['element']
            labels = element.find_elements(
                By.CSS_SELECTOR,
                f"label[data-test-text-selectable-option__label='{answer_text}']"
            )
            
            if labels:
                for label in labels:
                    try:
                        input_id = label.get_attribute('for')
                        input_element = self.driver.find_element(By.ID, input_id)
                        self.driver.execute_script("arguments[0].click();", input_element)
                        print(f"Selected '{answer_text}' for question: {selection_element_dict['question']}")
                        return True
                    except Exception as e:
                        print(f"Failed to click option: {str(e)}")
                        continue
                        
            print(f"No matching option found for: {answer_text}")
            print(f"Available options: {[opt['text'] for opt in selection_element_dict['options']]}")
            return False
            
        except Exception as e:
            print(f"Error selecting option: {str(e)}")
            return False

    
    def get_dropdowns(self):
        """Get all dropdown elements and their options"""
        if not self.form_container:
            if not self.initialize_form_container():
                return []
                
        try:
            dropdowns = []
            dropdown_selectors = [
                "select[data-test-text-entity-list-form-select]",  # LinkedIn specific selector
                "select[aria-required='true']",  # Required dropdowns
                "select"  # Fallback for any other dropdowns
            ]
            
            for selector in dropdown_selectors:
                dropdown_elements = self.form_container.find_elements(By.CSS_SELECTOR, selector)
                
                for dropdown in dropdown_elements:
                    try:
                        dropdown_id = dropdown.get_attribute('id')
                        
                        label_text = None
                        
                        try:
                            label_span = dropdown.find_element(By.XPATH, 
                                "./preceding-sibling::span[@aria-hidden='true'][1]")
                            label_text = label_span.text.strip()
                        except:
                            pass
                        
                        if not label_text:
                            try:
                                parent_div = dropdown.find_element(By.XPATH, "./ancestor::div[contains(@class, 'jobs-easy-apply-form-element')]")
                                label_elements = parent_div.find_elements(By.CSS_SELECTOR, 
                                    "span[aria-hidden='true'], legend, label")
                                if label_elements:
                                    label_text = label_elements[0].text.strip()
                            except:
                                pass
                        
                        options = dropdown.find_elements(By.TAG_NAME, "option")
                        option_texts = [opt.get_attribute('value') for opt in options]
                        
                        if not any(d['element'] == dropdown for d in dropdowns):
                            dropdowns.append({
                                'element': dropdown,
                                'name': dropdown_id,
                                'label': label_text,
                                'current_value': dropdown.get_attribute('value'),
                                'options': option_texts,
                                'option_elements': options,
                                'required': dropdown.get_attribute('required') == 'true'
                            })
                            
                    except Exception as e:
                        print(f"Error processing dropdown: {str(e)}")
                        continue
                
            return dropdowns
            
        except Exception as e:
            print(f"Error getting dropdowns: {str(e)}")
            return []
    

    def apply_job(self, cv_path, upload_cv=False):
        """
        Attempts to complete a job application form
        Args:
            cv_path (str): Path to CV file
        Returns:
            bool: True if application was submitted, False otherwise
        """
        try:
            # Initialize chatbot
            chatbot = ut.OpenAIChatBot(
                api_key_path='user_profile.json', 
                model="gpt-3.5-turbo", 
                use_history=True)
            chatbot.send_message(chatbot.read_applicant_info())
            chatbot.send_message("Throughout this application, please be very short, specific, and straightforward. Answer the questions as briefly as possible, with no extra information.")
            
            no_apply_page_index = 6
            for apply_page_index in range(no_apply_page_index):
                time.sleep(0.5)

                # Handle CV upload
                buttons = self.get_buttons()
                upload_cv_bool = False
                try:
                    for button in buttons:
                        if ('upload' in button['text'].lower()) & upload_cv:
                            upload_cv_bool = True
                            button['element'].click()
                            time.sleep(random.uniform(2, 3))
                            pyautogui.typewrite(cv_path, interval=0.04)
                            time.sleep(random.uniform(0, 1))
                            pyautogui.press('enter')

                    if upload_cv_bool:
                        buttons = self.get_buttons()
                except Exception as e:
                    print(f"Error uploading CV: {str(e)}")

                # Handle dropdowns
                try:
                    dropdowns = self.get_dropdowns()
                    for dropdown in dropdowns:
                        if (dropdown['current_value'] == '') or dropdown['current_value'] == dropdown['options'][0]:
                            gpt_prompt = f"""this is a drop down menu selection for a job application for {dropdown['label']}. and the current value is {dropdown['current_value']}. and available options are {dropdown['options']}. so based on this which element should be select. please give me that answer only please. do not change only that option. the answer is NOT 'Select an option'. DO NOT selection 'select an option'. maximize my chance to get the job please; i want this job."""
                            response = chatbot.send_message(gpt_prompt)
                            
                            most_similar_choice, _ = ut.most_similar_string(
                                response, dropdown['options'])
                            
                            index = dropdown['options'].index(most_similar_choice)
                            dropdown['element'].click()
                            time.sleep(random.uniform(0.2, 0.4))
                            for _ in range(index):
                                pyautogui.press('down')
                                time.sleep(random.uniform(0.10, 0.2))
                            
                            pyautogui.press('enter')
                except Exception as e:
                    print(f"Error handling dropdowns: {str(e)}")

                # Handle input fields
                try:
                    input_fields = self.get_input_fields()
                    for input_field in input_fields:
                        if input_field['current_value'] == '':
                            gpt_prompt = f"""For a job application form input field:
                                Question: {input_field['label_text']}
                                Guideline: Please provide only the exact value that should be entered in this field. Give just the value with no explanation. also if they ask for a numerical value please provide that number alone."""
                            
                            response = chatbot.send_message(gpt_prompt)
                            response = ut.get_after_colon(response)

                            # ======================
                            words = response.split()
                            should_extract_number = (
                                (':' in response and len(words) < 6) or     # Contains colon and less than 6 words
                                len(words) < 3                              # Less than 3 words total
                            ) and any(char.isdigit() for char in response)  # Contains at least one number
                            
                            if should_extract_number:
                                response = ut.simple_extract_number(response)
                            #=======================

                            input_field['input_element'].click()
                            time.sleep(random.uniform(0.7, 1.2))
                            pyautogui.typewrite(response, interval=0.123)
                except Exception as e:
                    print(f"Error handling input fields: {str(e)}")

                # Handle selection elements
                try:
                    selection_elements = self.get_selection_elements()
                    for selection in selection_elements:
                        gpt_prompt = f"""For a job application form selection question:
                            Question: {selection['question']}
                            Available options: {[opt['text'] for opt in selection['options']]}
                            Please provide ONLY one of the available options as your answer. Give just the option with no explanation."""
                            
                        response = chatbot.send_message(gpt_prompt)
                    
                        for option in selection['options']:
                            if option['text'].lower() == response.lower():
                                time.sleep(random.uniform(0.5, 1.2))
                                option['label'].click()
                                time.sleep(random.uniform(0.5, 1))
                                break
                except Exception as e:
                    print(f"Error handling selection elements: {str(e)}")

                # Handle submit/next buttons
                try:
                    terminate_loop = False
                    for button in buttons:
                        button_text = button['text'].lower()
                        if any(text in button_text for text in ['next', 'submit', 'continue', 'review', 'apply', 'send', 'done']):
                            time.sleep(random.uniform(1, 2))
                            button['element'].click()
                            time.sleep(random.uniform(1, 2))
                        if any(text in button_text for text in ['submit', 'apply', 'send']):
                            terminate_loop = True
                    
                    if terminate_loop:
                        time.sleep(random.uniform(1, 2))
                        pyautogui.press('esc')
                        return True
                        
                except Exception as e:
                    print(f"Error handling buttons: {str(e)}")

                if apply_page_index == (no_apply_page_index-1):
                    try:
                        ut.click_discard_button(self.driver)
                        pyautogui.press('esc')
                        ut.click_discard_button(self.driver)
                        pyautogui.press('esc')
                        pyautogui.press('esc')
                        ut.click_discard_button(self.driver)
                    except:
                        pass


                    
            return False
            
        except Exception as e:
            print(f"Error in apply_job method: {str(e)}")
            return False


if __name__ == "__main__":
    pass
