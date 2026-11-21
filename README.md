# Viva Question Generator

`Viva Question Generator` is a beginner-friendly Python project that helps students prepare for viva examinations. It lets you upload a project report PDF, extracts the text, sends it to Google Gemini AI, and generates `15 likely viva questions with short answers`.

## Features

- Upload a project report in PDF format
- Extract text from the PDF using `PyPDF2`
- Generate exactly `15 viva questions`
- Divide output into:
  - `Easy` - 5 questions
  - `Medium` - 5 questions
  - `Hard` - 5 questions
- Display questions in an attractive `Streamlit` interface
- Show proper error messages for invalid or unreadable PDFs
- Show a loading spinner while questions are being generated
- Download the generated questions as a PDF

## Project files

Create or keep these files in the same project folder:

- `app.py`
- `requirements.txt`
- `.env`
- `.gitignore`
- `README.md`

## Step 1: Open the project in VS Code

1. Open `VS Code`.
2. Click `File` -> `Open Folder`.
3. Select the project folder that contains:
   - `app.py`
   - `requirements.txt`
   - `.env`
4. Open the VS Code terminal:
   - Click `Terminal` -> `New Terminal`

## Step 2: Create a virtual environment

Run this command in the terminal:

```powershell
python -m venv venv
```

Now activate it:

```powershell
venv\Scripts\activate
```

If activation works, you will usually see `(venv)` at the beginning of the terminal line.

## Step 3: Install the required packages

Run:

```powershell
pip install -r requirements.txt
```

This installs:

- `streamlit`
- `PyPDF2`
- `google-generativeai`
- `python-dotenv`
- `reportlab`

`reportlab` is used only for the PDF download feature.

## Step 4: Add your Gemini API key

Open the `.env` file.

You will see a line like this:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

If you want to add or replace the key, paste your Gemini API key after the `=` sign like this:

```env
GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
```

Important:

- Do not add quotes unless your key actually needs them
- Do not paste the key inside `app.py`
- Keep the `.env` file private
- `.gitignore` already prevents the `.env` file from being uploaded to GitHub

## Step 5: Run the project

In the same terminal, run:

```powershell
streamlit run app.py
```

After that:

1. Streamlit will start a local server
2. A browser tab should open automatically
3. If it does not open automatically, copy the local URL from the terminal and open it in your browser

## Step 6: How to use the app

1. Open the app in your browser
2. Upload your project report PDF
3. Click `Generate Viva Questions`
4. Wait for the loading spinner
5. Review the generated:
   - Easy questions
   - Medium questions
   - Hard questions
6. Click `Download Questions as PDF` if you want to save the output

## How the code works

### `app.py`

This is the main Streamlit application.

It does these jobs:

1. Loads the Gemini API key from `.env`
2. Accepts a PDF upload from the user
3. Reads the PDF text using `PyPDF2`
4. Sends the extracted content to Gemini
5. Requests exactly 15 viva questions in JSON format
6. Displays the results in expandable sections
7. Creates a downloadable PDF file from the generated questions

### `requirements.txt`

Contains all required Python packages.

### `.env`

Stores your Gemini API key securely.

### `.gitignore`

Prevents secret files and cache files from being uploaded.

## Common errors and solutions

### 1. `ModuleNotFoundError`

Problem:

You may see an error like:

```text
ModuleNotFoundError: No module named 'streamlit'
```

Solution:

Install the packages again:

```powershell
pip install -r requirements.txt
```

Make sure your virtual environment is activated first.

### 2. `Gemini API key not found`

Problem:

The app shows that the API key is missing.

Solution:

Open `.env` and make sure it contains:

```env
GEMINI_API_KEY=YOUR_REAL_API_KEY
```

Then stop the app and run it again:

```powershell
streamlit run app.py
```

### 3. `The PDF could not be read`

Problem:

The uploaded PDF may be damaged, scanned as an image, or encrypted.

Solution:

- Try another PDF
- Use a text-based PDF instead of an image-only scanned PDF
- Remove password protection if the PDF is locked

### 4. Streamlit command not working

Problem:

You may get:

```text
'streamlit' is not recognized
```

Solution:

Run this instead:

```powershell
python -m streamlit run app.py
```

### 5. Gemini request failed

Problem:

The app may fail because of:

- invalid API key
- no internet connection
- API quota exceeded
- temporary Gemini service issue

Solution:

- check the API key
- confirm internet is working
- wait a few minutes and try again
- make sure you are using a Gemini API key that supports the free tier

## Free tier note

This project uses `Google Gemini` and is designed to work with the free tier where available. It does not use OpenAI or any paid API by default.

## How to explain this project to your college examiner

You can demonstrate the project like this:

1. Start the app using:

```powershell
streamlit run app.py
```

2. Explain the purpose:
   - "This project helps students prepare for viva questions by analyzing their project report automatically."

3. Upload a real project PDF

4. Click `Generate Viva Questions`

5. Explain the flow:
   - "The app extracts text from the PDF using PyPDF2."
   - "Then it sends the extracted content to Google Gemini."
   - "Gemini generates 15 likely viva questions with short answers."
   - "The questions are organized into Easy, Medium, and Hard levels."

6. Open a few expandable question cards

7. Download the PDF report and show that the output can be saved

## Short viva explanation you can say

You can say:

> "My project is a Viva Question Generator built with Python and Streamlit. It takes a student project report in PDF format, extracts the text using PyPDF2, and uses the Gemini API to generate likely viva questions with short answers. The output is grouped into Easy, Medium, and Hard levels, which helps students prepare better for oral examination."

## Extra improvement ideas

If you want to improve it later, you can add:

- question count customization
- export to Word file
- support for scanned PDFs using OCR
- project summary generation
- keyword extraction

## Final command summary

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
