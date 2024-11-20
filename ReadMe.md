# LinkedIn Easy Apply Bot Using GPT 

A Python-based automation tool that helps you automatically apply for jobs on LinkedIn using the "Easy Apply" feature. The bot uses GPT-3.5-turbo to answer application questions and GPT-4 to optimize your CV for specific job postings (optional feature). It uses Edge and needs no web driver. 


Average OpenAI API costs:
- Basic application: ~$0.002 (0.2 cents) per job
- With CV customization: Varies based on CV length

## Project Structure
```
├── CV/                     # Directory for your CV files
├── modules/
│   ├── pycache/
│   ├── easyapplynav.py    # Handles job application form navigation
│   ├── jobnavigator.py    # Manages job listing navigation
│   ├── linkedin2.py       # Core LinkedIn automation
│   └── utils.py           # Utility functions
├── environment.yml        # Conda environment configuration
├── main.py               # Main script to run the bot
├── requirements.txt      # Python dependencies
└── user_profile.json     # User information and API keys
```

## Prerequisites
- Microsoft Edge browser
- Python 3.8+
- OpenAI API key (GPT-3.5 and GPT-4 access)
- LinkedIn account

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `user_profile.json`:
```json
{
    "openai_api_key": "your-api-key",
    "CV_file_name": "your-cv.pdf",
    "name": "Your Name",
    "email": "your.email@example.com",
    "phone": "1234567890"
    // Add other profile information
}
```

## CV Setup

1. Place your CV in the `CV` directory:

For basic usage (`tailor_cv=False`):
- Add your CV as a PDF file
- Update `user_profile.json` with the filename
```json
{
    "CV_file_name": "your_cv.pdf"
}
```

For CV tailoring (`tailor_cv=True`):
- Add your CV's LaTeX source file (.tex)
- Ensure you have a LaTeX distribution installed (e.g., MiKTeX for Windows)
- The bot will:
  - Generate tailored versions of your CV for each application
  - Automatically compile new PDFs using pdflatex
  - Name files with timestamps (e.g., `cv_modified_20240318_152342.pdf`)
- Update `user_profile.json` with the LaTeX filename
```json
{
    "CV_file_name": "your_cv.tex"
}
```

LaTeX Requirements (if you do not want to adjust CV this is NOT required):
```bash
# Windows
# Install MiKTeX from: https://miktex.org/download

# Linux
sudo apt-get install texlive-full

# Mac
brew install --cask mactex
```


## Usage

1. Update the parameters in `main.py`:
```python
run_this(
    job_title='Mechanical Engineer',
    location='Canada',
    past_week_jobs=False,
    tailor_cv=False
)
```

2. Run the script:
```bash
python main.py
```

## Features
- Automated login and job search
- Filters for Easy Apply jobs
- Smart form filling using GPT-3.5
- CV tailoring option using GPT-4
- Handles multiple job application pages
- Random delays to mimic human behavior

## AI Integration
- Uses GPT-3.5-turbo for answering application questions
- Uses GPT-4 for CV customization when `tailor_cv=True`

## Notes
- Make sure you're logged into LinkedIn in Edge before running
- The bot uses Microsoft Edge in debug mode
- Applications are processed with random delays to avoid detection
- Set `tailor_cv=True` to customize CV for each job (higher cost but potentially better results)
- Set `past_week_jobs=True` to filter for recent postings only

## Limitations
- Only works with Edge browser
- Requires manual LinkedIn login
- Limited to Easy Apply jobs
- May need adjustments based on LinkedIn's UI changes
- Requires OpenAI API key with access to both GPT-3.5 and GPT-4
