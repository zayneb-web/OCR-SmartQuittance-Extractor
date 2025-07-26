# Backend Integration Examples

## Simple Approach: Store Only Essential Data

Since you have different quittances from different companies, we'll store only:

- **ID** (unique identifier)
- **Company Name** (from extracted data)
- **Image URL** (Cloudinary URL)
- **User ID** (who uploaded it)
- **Upload Date**

## Integration Examples

### 1. Node.js/Express Backend Integration (CORRECTED)

```javascript
// In your existing Express backend
const express = require("express");
const multer = require("multer");
const FormData = require("form-data"); // IMPORTANT: Use form-data package
const axios = require("axios");
const app = express();

// OCR API endpoint (updated port)
const OCR_API_URL = "http://localhost:8001/extract_quittance/";

// Upload middleware
const upload = multer({ storage: multer.memoryStorage() });

// Your existing route that uses OCR
app.post("/api/quittances/upload", upload.single("file"), async (req, res) => {
  try {
    // 1. Send image to OCR API (CORRECTED)
    const formData = new FormData();
    formData.append("file", req.file.buffer, {
      filename: req.file.originalname,
      contentType: req.file.mimetype,
    });

    const ocrResponse = await axios.post(OCR_API_URL, formData, {
      headers: {
        ...formData.getHeaders(), // IMPORTANT: Include form-data headers
      },
      timeout: 30000, // 30 second timeout
    });

    const { cloudinary_url, extracted_data } = ocrResponse.data;

    // 2. Save only essential data to your existing database
    const quittance = new Quittance({
      userId: req.user.id,
      companyName: extracted_data.assurance || "Unknown Company",
      imageUrl: cloudinary_url,
      uploadedAt: new Date(),
      // Optional: store the full extracted data if you want to access it later
      extractedData: extracted_data,
    });

    await quittance.save();

    res.json({
      success: true,
      quittance: {
        id: quittance._id,
        companyName: quittance.companyName,
        imageUrl: quittance.imageUrl,
        uploadedAt: quittance.uploadedAt,
      },
      // Return full extracted data for immediate use
      extractedData: extracted_data,
    });
  } catch (error) {
    console.error("OCR processing failed:", error);
    res.status(500).json({ error: "Failed to process quittance" });
  }
});

// Get user's quittances (simplified)
app.get("/api/quittances", async (req, res) => {
  const quittances = await Quittance.find({ userId: req.user.id })
    .select("companyName imageUrl uploadedAt")
    .sort({ uploadedAt: -1 });
  res.json(quittances);
});

// Get specific quittance with full data
app.get("/api/quittances/:id", async (req, res) => {
  const quittance = await Quittance.findById(req.params.id);
  if (!quittance || quittance.userId.toString() !== req.user.id) {
    return res.status(404).json({ error: "Quittance not found" });
  }
  res.json(quittance);
});
```

### 2. CORRECTED Version for Your Code

Here's the corrected version of your upload route:

```javascript
import express from "express";
import multer from "multer";
import FormData from "form-data"; // ADD THIS IMPORT
import axios from "axios"; // Use axios instead of fetch for better FormData support
import Quittance from "../models/Quittance.js";
import { authenticateToken } from "../middleware/authentification.js";

const router = express.Router();

// Configure multer for memory storage
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Accept only images
    if (file.mimetype.startsWith("image/")) {
      cb(null, true);
    } else {
      cb(new Error("Only image files are allowed"), false);
    }
  },
});

// OCR API endpoint
const OCR_API_URL = process.env.OCR_SERVICE_URL + "/extract_quittance/";

// Upload quittance with OCR processing (CORRECTED)
router.post(
  "/upload",
  authenticateToken,
  upload.single("file"),
  async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
      }

      // Create initial quittance record
      const quittance = new Quittance({
        userId: req.user.id,
        companyName: "Processing...",
        imageUrl: "",
        cloudinaryPublicId: "",
        status: "processing",
      });

      await quittance.save();

      try {
        // Send image to OCR API (CORRECTED)
        const formData = new FormData();
        formData.append("file", req.file.buffer, {
          filename: req.file.originalname,
          contentType: req.file.mimetype,
        });

        const ocrResponse = await axios.post(OCR_API_URL, formData, {
          headers: {
            ...formData.getHeaders(), // IMPORTANT: Include form-data headers
          },
          timeout: 30000, // 30 second timeout
        });

        const { cloudinary_url, cloudinary_public_id, extracted_data } =
          ocrResponse.data;

        // Update quittance with extracted data
        quittance.companyName = extracted_data.assurance || "Unknown Company";
        quittance.imageUrl = cloudinary_url;
        quittance.cloudinaryPublicId = cloudinary_public_id;
        quittance.extractedData = extracted_data;
        quittance.status = "completed";

        await quittance.save();

        res.json({
          success: true,
          quittance: {
            id: quittance._id,
            companyName: quittance.companyName,
            imageUrl: quittance.imageUrl,
            uploadedAt: quittance.uploadedAt,
            status: quittance.status,
          },
          extractedData: extracted_data,
        });
      } catch (ocrError) {
        // Update quittance with error status
        quittance.status = "failed";
        quittance.errorMessage = ocrError.message || "OCR processing failed";
        await quittance.save();

        console.error("OCR processing failed:", ocrError);
        res.status(500).json({
          error: "Failed to process quittance",
          quittanceId: quittance._id,
          details: ocrError.message,
        });
      }
    } catch (error) {
      console.error("Upload error:", error);
      res.status(500).json({ error: "Failed to upload quittance" });
    }
  }
);

// ... rest of your routes remain the same
```

### 3. Required Dependencies

Add these to your `package.json`:

```json
{
  "dependencies": {
    "form-data": "^4.0.0",
    "axios": "^1.6.0"
  }
}
```

Install them:

```bash
npm install form-data axios
```

### 4. Alternative: Using fetch with proper FormData

If you prefer to keep using fetch:

```javascript
// Alternative approach using fetch
const formData = new FormData();
formData.append(
  "file",
  new Blob([req.file.buffer], { type: req.file.mimetype }),
  req.file.originalname
);

const ocrResponse = await fetch(OCR_API_URL, {
  method: "POST",
  body: formData,
  // Don't set Content-Type header - let the browser set it with boundary
});
```

## The Main Issues with Your Original Code:

1. **❌ Missing FormData import** - Node.js doesn't have built-in FormData
2. **❌ Missing form-data headers** - Need `formData.getHeaders()`
3. **❌ Using fetch with FormData** - Better to use axios for this
4. **❌ Incorrect Content-Type** - Should let form-data set it automatically

## ✅ The Fixes:

1. **✅ Import FormData package**
2. **✅ Use axios instead of fetch**
3. **✅ Include form-data headers**
4. **✅ Proper timeout handling**

Your backend structure is actually very good! Just needed these small fixes for the FormData handling. 🎯
