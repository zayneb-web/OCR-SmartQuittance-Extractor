# Quittance Extractor

A FastAPI application for extracting information from insurance receipts (quittances) using OCR and LLM.

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Create a `.env` file in the root directory with your Cloudinary credentials:

   ```
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

   **⚠️ IMPORTANT:** Never commit your `.env` file to version control. It's already added to `.gitignore`.

3. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

## Security Notice

- API keys and secrets are now stored in environment variables
- The `.env` file is excluded from version control
- Never hardcode credentials in your source code

## API Endpoints

- `POST /extract_quittance/`: Upload and process insurance receipts
