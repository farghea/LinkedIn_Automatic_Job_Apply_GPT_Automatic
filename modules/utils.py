#%% 

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sentence_transformers import SentenceTransformer, util
import json
from openai import OpenAI

class OpenAIChatBot:
    def __init__(self, api_key_path, model="gpt-3.5-turbo", use_history=True):
        """Initialize the chatbot with API key, model, and history settings."""
        self.api_key_path = api_key_path
        self.api_key = self.read_api_key()
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.use_history = use_history
        # Initialize conversation history if using history
        self.conversation_history = [{"role": "system", "content": "You are a helpful assistant."}] if use_history else []

    def read_api_key(self):
        """Read the OpenAI API key from a JSON file."""
        try:
            with open(self.api_key_path, 'r') as file:  # Corrected variable name here
                data = json.load(file)
                return data.get("openai_api_key")
        except Exception as e:
            print("Failed to load API key:", e)
            return None

    def send_message(self, message):
        """Send a message to the chatbot and get a response."""
        if self.use_history:
            self.conversation_history.append({"role": "user", "content": message})
        else:
            self.conversation_history = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history
            )
            assistant_message = response.choices[0].message.content

            if self.use_history:
                self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            print("Error communicating with OpenAI:", e)
            return None

    def read_applicant_info(self):
        """Reads the JSON file content and formats it for a job application, excluding the API key."""
        try:
            with open(self.api_key_path, 'r') as file:  # Assumes applicant info is in the same JSON file
                data = json.load(file)
            
            message = "The following information will be used in a job application please have them and use them later on as required:\n"
            for key, value in data.items():
                if key != "openai_api_key":  # Skip the API key
                    message += f"{key}: {value}\n"
            
            return message

        except Exception as e:
            print("Failed to load applicant information:", e)
            return None


def most_similar_string(input_string, string_list):
    # finds rthe most similar text in a list for a given "input_string"
    
    model = SentenceTransformer('all-MiniLM-L6-v2') 

    input_embedding = model.encode(input_string, convert_to_tensor=True)
    list_embeddings = model.encode(string_list, convert_to_tensor=True)

    similarities = util.cos_sim(input_embedding, list_embeddings)[0]

    highest_index = similarities.argmax().item()
    highest_similarity = similarities[highest_index].item()
    
    most_similar = string_list[highest_index]
    
    return most_similar, highest_similarity


def get_after_colon(text):
    if ": " in text:
        return text.split(": ", 1)[1]
    return text


def click_discard_button(driver):
    """
    Optimized function to find and click the discard button on LinkedIn job application modal.
    Returns True if successfully discarded, False otherwise.
    """
    try:
        # Combined XPath selector for all possible discard buttons
        combined_xpath = """
        //button[
            contains(@aria-label, 'Dismiss') or 
            contains(@aria-label, 'Discard') or 
            contains(text(), 'Discard') or 
            contains(text(), 'Cancel application') or 
            contains(text(), 'Dismiss')
        ] | 
        //*[contains(@class, 'artdeco-modal__dismiss') or 
            contains(@class, 'jobs-easy-apply-modal__discard-button')]
        """
        
        # Wait for any matching button with reduced timeout
        discard_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, combined_xpath.replace('\n', '')))
        )
        discard_button.click()
        
        # Quick check for confirmation dialog with reduced timeout
        try:
            confirm_xpath = """
            //button[
                contains(@class, 'artdeco-modal__confirm-dialog-btn') or
                contains(text(), 'Discard') or
                contains(text(), 'Confirm')
            ]
            """
            confirm_button = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, confirm_xpath.replace('\n', '')))
            )
            confirm_button.click()
        except:
            # No confirmation needed
            pass
            
        return True
        
    except Exception as e:
        print(f"Error attempting to discard application: {str(e)}")
        return False

def find_job_description(driver):
    # this function get job description function 
    description_text = None
    selectors = [
        "job-details-about-the-job-module__description",
        "jobs-description__content",
        "jobs-description",
        "jobs-description-content__text",
        "description__text",
        "job-view-layout jobs-details",
        "job-view-layout"
    ]

    for selector in selectors:
        try:
            print(f"Trying selector: {selector}")
            description = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, selector))
            )
            if description:
                description_text = description.text.strip()
                print("Found description:", description_text[:100])
                break
        except Exception as e:
            print(f"Selector {selector} failed: {str(e)}")
    
    if description_text is None:
        print("Could not find description with any known selector")
        print("\nPage source:")
        print(driver.page_source[:500])

    return description_text


def simple_extract_number(text):
    """Extract the first number from a string."""
    return ''.join(char for char in text if char.isdigit())



if __name__ == '__main__':
    pass
    # chatbot = OpenAIChatBot(api_key_path='user_profile.json', model="gpt-3.5-turbo", use_history=True)
    
    # response = chatbot.send_message(chatbot.read_applicant_info())
    # print("Assistant:", response)



