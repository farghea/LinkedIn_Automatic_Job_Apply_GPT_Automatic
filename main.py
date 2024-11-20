#%%
 
import time
import random

from modules import linkedin2 as ln
from modules import utils as ut 
from modules import jobnavigator as jnav



def run_this(job_title, location, past_week_jobs, tailor_cv):
    edge_path = EDGE_PATH
    linkedin_bot = ln.LinkedInAutomation(edge_path)
    
    linkedin_bot.start_edge_with_debugging()
    linkedin_bot.connect_to_existing_session()
    linkedin_bot.open_linkedin()
    

    linkedin_bot.activate_linkedin_window()
    linkedin_bot.search(query_job_title=job_title, location=location)
    if past_week_jobs:
        linkedin_bot.set_date_posted_to_past_week()
    linkedin_bot.click_show_results_button()

    
    time.sleep(0.64)
    linkedin_bot.activate_linkedin_window()
    navigator = jnav.LinkedInJobNavigator(linkedin_bot.driver)
    navigator.easy_apply_filter(linkedin_bot.driver)
    navigator.initial_setup()
    pages = linkedin_bot.get_pagination_info()
    
    for page_index in range(len(pages)-1):
        time.sleep(random.uniform(1, 1.5))
        pages = linkedin_bot.get_pagination_info()
        navigator.navigate_jobs(linkedin_bot.driver, tailor_cv = tailor_cv, 
                                max_jobs=None)
        
        pages[page_index+1]['element'].click()
        navigator = jnav.LinkedInJobNavigator(linkedin_bot.driver)
        navigator.initial_setup()
        time.sleep(random.uniform(3, 3.5))
    

if __name__ == '__main__':
    EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    
    run_this(
        job_title = 'Mechanical Engineer',
        location = 'Canada',
        past_week_jobs = False,
        tailor_cv = False)
    
    
    



