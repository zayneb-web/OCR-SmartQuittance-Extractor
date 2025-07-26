# Integration Guide - Automatic Company Format Detection

## 🎯 How It Works

When you choose a company in your frontend, the system automatically knows which quittance format to use!

### 1. **Frontend** → **Backend** → **OCR API**

```
Frontend (Company Selection)
    ↓
Backend (Sends company_name)
    ↓
OCR API (Auto-detects format)
    ↓
Returns extracted data with format_used
```

## 🔧 Backend Integration

### Update your Express.js route:

```javascript
// In your upload route, send company_name to OCR API
const formData = new FormData();
formData.append("file", blob, req.file.originalname);
formData.append("company_name", companyName); // ← Add this line

const response = await axios.post(OCR_API_URL, formData, {
  headers: { "Content-Type": "multipart/form-data" },
  timeout: 60000,
});

const { cloudinary_url, cloudinary_public_id, extracted_data, format_used } =
  response.data;
console.log(`Format used: ${format_used}`); // Shows which format was detected
```

## 🏢 Company Mappings

### Current Mappings (in `company_mappings.py`):

| Company Name        | Format Used        | Description                    |
| ------------------- | ------------------ | ------------------------------ |
| `ipteur`            | `hp0012_custom`    | IPTEUR company - custom format |
| `carte assurances`  | `carte_assurances` | CARTE ASSURANCES format        |
| `assurance tunisie` | `format_1`         | Default insurance format       |

### Add New Companies:

Edit `company_mappings.py`:

```python
COMPANY_FORMAT_MAPPING = {
    # Existing mappings...
    "ipteur": "hp0012_custom",
    "carte assurances": "carte_assurances",

    # Add your new company here
    "your_company_name": "format_1",  # or "hp0012_custom", "carte_assurances"
}
```

## 📊 Response Format

The OCR API now returns:

```json
{
  "cloudinary_url": "https://...",
  "cloudinary_public_id": "...",
  "extracted_data": {
    "assurance": "...",
    "numero_quittance": "...",
    "agence": "..."
    // ... all extracted fields
  },
  "format_used": "hp0012_custom", // ← Shows which format was used
  "status": "success",
  "message": "Quittance processed successfully"
}
```

## 🎯 Benefits

1. **✅ Automatic Detection**: No manual format selection needed
2. **✅ Company-Based**: Each company uses its specific format
3. **✅ Easy to Add**: Just add company name to mappings
4. **✅ Fallback**: Unknown companies use `format_1` by default
5. **✅ Transparent**: You know which format was used

## 🔍 Testing

### Test Company Mappings:

```bash
python company_mappings.py
```

### Test OCR API:

```bash
# Start the OCR service
python main_simple.py

# Test with curl (replace with your actual company name)
curl -X POST "http://localhost:8001/extract_quittance/" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_image.jpg" \
     -F "company_name=ipteur"
```

## 🚀 Quick Start

1. **Add your companies** to `company_mappings.py`
2. **Update your backend** to send `company_name`
3. **Test the integration** with your frontend
4. **Monitor the logs** to see which format is used

That's it! Your system now automatically detects the correct format based on the company! 🎉
