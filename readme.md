# Flask + React CSV Brand Onboarding Tool

A lightweight Flask API + React UI for bulk-creating brand profile pages from a CSV upload. The React frontend provides a simple upload interface, while the Flask backend validates each row and calls an upstream onboarding API to create each brand, returning per-row success/error results.

#### App can be previewed at: fliptools.vercel.app

---

## What this app does

- **Upload a CSV** from the UI
- Backend validates required columns and required values per row
- For each row, backend calls `create_brands(...)` to POST the brand data payload to the endpoint 
- Returns a JSON array of results: `[{ brand, result }]` or `[{ brand, error }]`

---

## Architecture

- **Backend (Flask)**
  - Serves the compiled React app from `frontend/build`
  - Provides a single API endpoint: `POST /upload` that processes the CSV

- **Frontend (React)**
  - Compiled into `frontend/build` and served by Flask in production mode 
  - Repo assumes a standard React app inside `frontend/`

---

## CSV format
### Required columns

Your CSV **must include** these headers (exact names, whitespace is tolerated in headers):

- `brand_name`
- `companyName`
- `mainContactName`
- `vendorMainContactEmail`
- `websiteUrl`

### Optional columns

If present, these are passed through to the onboarding API: 

- `description`
- `foundedInYear`
- `countryOfOrigin`
- `instagramUrl`
- `mainContactPhone`

### Notes

- Rows missing required values are skipped and returned with an error message.
- Phone numbers are normalized into a `+<countrycode><digits>` format, with a default if missing. 
- API errors are parsed into a more user-friendly message when possible.

---

## Environment variables

Backend reads configuration from environment variables / `.env`.

### Required
- `BASE_URL` — base URL used to build the onboarding endpoint. 

### Auth
`new_brand.py` retrieves a Bearer token via `get_flip_access_token()` from an `access_token` module. 