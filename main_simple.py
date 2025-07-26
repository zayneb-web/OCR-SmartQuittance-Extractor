from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION CLOUDINARY ===
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

from quittance_processor import QuittanceProcessor

app = FastAPI(
    title="Quittance OCR Extractor",
    description="Pure OCR service for extracting data from insurance quittances",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract_quittance/")
async def extract_quittance(
    file: UploadFile = File(...),
    company_name: str = Form(None),  # Company name for format detection
    format_name: str = Form(None)    # Optional manual format override
):
    """
    Extract quittance data from uploaded image.
    Automatically detects format based on company name or image content.
    Returns only the extracted data and Cloudinary URL.
    Your existing backend can consume this and save to your database.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary first
        result = cloudinary.uploader.upload(contents, resource_type="image")
        image_url = result['secure_url']
        public_id = result.get('public_id')
        
        # Process image directly from memory
        import tempfile
        
        # Create a temporary file that auto-deletes
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name
        
        try:
            # Initialize the smart processor
            processor = QuittanceProcessor()
            
            # Determine format to use
            detected_format = None
            if format_name:
                # Use manual format if provided
                detected_format = format_name
            elif company_name:
                # Map company name to format
                detected_format = map_company_to_format(company_name)
            
            # Process with OCR using smart processor
            fields = processor.process_single_image(temp_path, detected_format)
            
            # Extract the actual data (remove metadata)
            extracted_data = {k: v for k, v in fields.items() 
                            if k not in ['source_file', 'detected_format']}
            
        finally:
            # Always clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return {
            "cloudinary_url": image_url,
            "cloudinary_public_id": public_id,
            "extracted_data": extracted_data,
            "format_used": fields.get('detected_format', 'auto_detected'),
            "status": "success",
            "message": "Quittance processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing quittance: {str(e)}"
        )

from company_mappings import get_format_for_company

def map_company_to_format(company_name):
    """
    Map company names to quittance formats using the configuration file.
    """
    return get_format_for_company(company_name)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Quittance OCR Extractor is running"}

@app.get("/formats")
async def get_available_formats():
    """Get list of available quittance formats"""
    processor = QuittanceProcessor()
    return {
        "available_formats": list(processor.FIELD_BOXES_CONFIGS.keys()),
        "default_format": "format_1"
    }

@app.get("/company-mappings")
async def get_company_mappings():
    """Get company to format mappings"""
    from company_mappings import COMPANY_FORMAT_MAPPING
    return {
        "company_mappings": COMPANY_FORMAT_MAPPING,
        "note": "Add more mappings in company_mappings.py file"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port) 