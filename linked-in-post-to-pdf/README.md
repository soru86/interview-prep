# LinkedIn Carousel → PDF Converter

Convert LinkedIn post carousel/document slides into a high-quality downloadable PDF.

## Architecture

- **Frontend**: React + Vite — premium dark-theme UI with glassmorphism
- **Backend**: Python FastAPI + Playwright — browser automation for slide capture

## Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.11
- **A LinkedIn account** (the tool needs browser login to access post content)

## Setup & Run

### 1. Backend

```bash
cd backend

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Start the server
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

## Usage

1. Open `http://localhost:5173` in your browser
2. **First time only**: A Chromium window will open — log into LinkedIn. The session is saved for future runs.
3. Paste a LinkedIn post URL (e.g., `https://www.linkedin.com/posts/...`)
4. Click **Convert to PDF**
5. Download your PDF when ready!

## How It Works

1. **Playwright** opens the LinkedIn post in a real browser
2. Detects the document/carousel viewer
3. Screenshots each slide at 2× retina resolution
4. **ReportLab** generates a PDF with pages sized to match each slide
5. Temporary image files are automatically cleaned up

## Project Structure

```
├── backend/
│   ├── main.py             # FastAPI server
│   ├── scraper.py          # Playwright slide capture
│   ├── pdf_generator.py    # Image → PDF conversion
│   ├── requirements.txt    # Python dependencies
│   ├── output/             # Generated PDFs (auto-created)
│   └── .browser-data/      # Persistent browser cookies (auto-created)
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Component styles
│   │   ├── index.css       # Global design system
│   │   └── main.jsx        # Entry point
│   ├── index.html
│   └── package.json
└── README.md
```

## ⚠️ Important Notes

- This tool is for **personal use only**
- LinkedIn may update its DOM structure — selectors in `scraper.py` may need updating
- Automated scraping may violate LinkedIn's Terms of Service — use responsibly
- Session cookies are stored locally in `backend/.browser-data/`
