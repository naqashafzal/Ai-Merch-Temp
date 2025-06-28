# AI-Powered Merchandise Template Generator

This project is a proof-of-concept Python script that automatically generates branded merchandise templates by analyzing client websites.

## Project Overview

The application takes a website URL, analyzes it to extract branding elements (logo, colors, screenshot), and then generates a sample coffee mug design and a print-ready PDF.

## Example Video
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/sKKT-4N3hPU/0.jpg)](https://www.youtube.com/watch?v=sKKT-4N3hPU)

## Core Features

-   **Website Analysis**: Parses a website to extract its logo, dominant colors, and a full-page screenshot.
-   **Mock AI Integration**: Simulates AI analysis to provide style descriptions and design recommendations.
-   **Template Generation**: Programmatically creates a coffee mug design using the extracted brand assets.
-   **Print-Ready Output**: Generates both a PNG image and a PDF of the final design.
-   **Web Interface**: A simple Flask-based front end to interact with the tool.

## Technical Stack

-   **Backend**: Python 3.8+, Flask
-   **Web Scraping**: BeautifulSoup, Selenium
-   **Image Processing**: Pillow (PIL), colorgram.py
-   **Design Generation**: Pillow, CairoSVG, reportlab
-   **Frontend**: HTML, CSS, JavaScript

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd merchandise_generator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    This project uses `webdriver-manager` to automatically handle the Chrome driver required by Selenium. Ensure you have Google Chrome installed.
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  **Start the Flask server:**
    ```bash
    python app.py
    ```

2.  **Open your web browser** and navigate to:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

3.  **Enter a website URL** (e.g., `notion.so`, `stripe.com`) into the input field and click "Generate".

4.  Wait for the process to complete. The results, including the generated design, will be displayed on the page.
