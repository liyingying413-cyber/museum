# Open Museum Explorer (Streamlit + Art Institute of Chicago API)

A GitHub-ready Streamlit app that searches artworks using the **Art Institute of Chicago (AIC)** open API—no API key required.

## Features
- Keyword search with pagination
- Image grid, titles, artist, date & medium
- Detail panel with larger image and metadata
- External link to the artwork’s page on artic.edu
- Toggle to show only results with images

## Local Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a new GitHub repo.
2. In Streamlit Cloud, select the repo and set **Main file path** to `app.py`.
3. Deploy.

## Data Source
Art Institute of Chicago API: https://api.artic.edu/docs/