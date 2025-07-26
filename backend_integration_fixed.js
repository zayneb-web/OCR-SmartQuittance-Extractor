// Fixed Express.js backend integration for hp0012_custom format
// This properly maps all the fields from your successful Python extraction

import express from "express";
import multer from "multer";
import axios from "axios";
import FormData from "form-data";
import Quittance from "../models/Quittance.js";
import Company from "../models/Company.js";
import { verifyToken } from "../middleware/authentification.js";

const router = express.Router();

// OCR API endpoint
const OCR_API_URL = "http://localhost:8001/extract_quittance/";

// Configure multer for memory storage
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith("image/")) {
      cb(null, true);
    } else {
      cb(new Error("Only image files are allowed"), false);
    }
  },
});

// Upload quittance with proper field mapping
router.post("/upload", verifyToken, upload.single("file"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "No file uploaded" });
    }

    const { companyName } = req.body;
    if (!companyName) {
      return res.status(400).json({ error: "Company name is required" });
    }

    // Validate that the company exists by name
    const company = await Company.findOne({ nom: companyName });
    if (!company) {
      return res.status(400).json({ error: "Company not found" });
    }

    // Create initial quittance record
    const timestamp = Date.now();
    const quittance = new Quittance({
      userId: req.user.id,
      companyId: company._id,
      imageUrl: "",
      cloudinaryPublicId: "",
      status: "processing",
      code_quittance: `temp_${timestamp}`,
      numero_contrat: "",
      beneficiaire: "",
      agence: "",
      assurance: "",
      souscripteur: "",
      devise: "dinar",
      prime_totale: 0,
    });

    await quittance.save();

    try {
      // Send image to OCR API with company name
      const formData = new FormData();
      formData.append("file", req.file.buffer, {
        filename: req.file.originalname,
        contentType: req.file.mimetype,
      });
      formData.append("company_name", companyName);

      console.log(
        `Sending quittance for company: ${companyName} - Automatic format detection enabled`
      );

      const response = await axios.post(OCR_API_URL, formData, {
        headers: {
          ...formData.getHeaders(),
        },
        timeout: 60000,
      });

      const {
        cloudinary_url,
        cloudinary_public_id,
        extracted_data,
        format_used,
      } = response.data;

      console.log(`OCR processing completed. Format used: ${format_used}`);

      // Map extracted data to our schema
      quittance.imageUrl = cloudinary_url;
      quittance.cloudinaryPublicId = cloudinary_public_id;

      // Handle different formats with proper field mapping
      if (format_used === "hp0012_custom") {
        // HP0012 custom format - map all fields correctly
        quittance.code_quittance =
          extracted_data.numero_quittance || `temp_${Date.now()}`;
        quittance.numero_contrat = extracted_data.num_contrat || "";
        quittance.beneficiaire = extracted_data.assure || "";
        quittance.agence = extracted_data.agence || "";
        quittance.assurance = extracted_data.assurance || "";
        quittance.souscripteur = extracted_data.souscripteur || "";
        quittance.devise = "dinar";

        // Parse prime_totale correctly (remove "DT" and convert to number)
        const primeTotalStr = extracted_data.prime_totale || "0";
        const primeTotalClean = primeTotalStr
          .replace(/[^\d.,]/g, "")
          .replace(",", ".");
        quittance.prime_totale = parseFloat(primeTotalClean) || 0;

        // Store ALL extracted data for reference
        quittance.extractedData = {
          // Core fields
          assurance: extracted_data.assurance || "",
          numero_quittance: extracted_data.numero_quittance || "",
          agence: extracted_data.agence || "",
          souscripteur: extracted_data.souscripteur || "",
          adresse: extracted_data.adresse || "",
          ville: extracted_data.ville || "",
          code_postal: extracted_data.code_postal || "",
          assure: extracted_data.assure || "",
          num_contrat: extracted_data.num_contrat || "",
          fractionnement: extracted_data.fractionnement || "",
          numero_aliment: extracted_data.numero_aliment || "",

          // Period
          periode_assurance: {
            date_debut: extracted_data.periode_assurance?.date_debut || "",
            date_fin: extracted_data.periode_assurance?.date_fin || "",
          },

          // Financial fields
          prime_base: extracted_data.prime_base || "",
          prime_annexe: extracted_data.prime_annexe || "",
          frais: extracted_data.frais || "",
          taxe_base: extracted_data.taxe_base || "",
          taxes_annexes: extracted_data.taxes_annexes || "",
          fpcsr: extracted_data.fpcsr || "",
          fpac: extracted_data.fpac || "",
          fga: extracted_data.fga || "",
          prime_totale: extracted_data.prime_totale || "",

          // Vehicle fields
          categorie_risque: extracted_data.categorie_risque || "",
          immatriculation: extracted_data.immatriculation || "",
          marque: extracted_data.marque || "",
          type_vehicule: extracted_data.type_vehicule || "",
          date_emission: extracted_data.date_emission || "",

          // Metadata
          format_used: format_used,
          source_file: extracted_data.source_file || "",
        };
      } else if (format_used === "carte_assurances") {
        // CARTE ASSURANCES format mapping
        quittance.code_quittance =
          extracted_data.numero_quittance || `temp_${Date.now()}`;
        quittance.numero_contrat = extracted_data.num_contrat || "";
        quittance.beneficiaire = extracted_data.assure || "";
        quittance.agence = extracted_data.agence || "";
        quittance.assurance = extracted_data.assurance || "";
        quittance.souscripteur = extracted_data.souscripteur || "";
        quittance.devise = "dinar";

        const primeTotalStr = extracted_data.prime_totale || "0";
        const primeTotalClean = primeTotalStr
          .replace(/[^\d.,]/g, "")
          .replace(",", ".");
        quittance.prime_totale = parseFloat(primeTotalClean) || 0;

        quittance.extractedData = {
          ...extracted_data,
          format_used: format_used,
        };
      } else {
        // Default format_1 mapping
        quittance.code_quittance = extracted_data.code || `temp_${Date.now()}`;
        quittance.numero_contrat = extracted_data.num_contrat || "";
        quittance.beneficiaire = extracted_data.assure?.["nom et prenom"] || "";
        quittance.agence = extracted_data.agence || "";
        quittance.assurance = extracted_data.assurance || "";
        quittance.souscripteur = extracted_data.souscripteur || "";
        quittance.devise = extracted_data.devise || "dinar";
        quittance.prime_totale = parseFloat(extracted_data.prime) || 0;

        quittance.extractedData = {
          num_contrat: extracted_data.num_contrat || "",
          periode_assurance: {
            date_debut: extracted_data["Periode d'assurance"]?.date_debut || "",
            date_fin: extracted_data["Periode d'assurance"]?.date_fin || "",
          },
          numero_quittance: extracted_data["numero quittance"] || "",
          risque: extracted_data.risque || "",
          prime: extracted_data.prime || "",
          code: extracted_data.code || "",
          cout_contrat: extracted_data["COUT DE CONTRAT"] || "",
          assure: {
            nom_et_prenom: extracted_data.assure?.["nom et prenom"] || "",
            adresse: extracted_data.assure?.adresse || "",
            code_postal: extracted_data.assure?.["code postal"] || "",
          },
          per: extracted_data.PER || "",
          taxe: {
            taxe: extracted_data.taxe?.taxe || "",
            fg: extracted_data.taxe?.fg || "",
          },
          somme_a_payer: extracted_data["somme a payer"] || "",
          total: extracted_data.total || "",
          format_used: format_used,
        };
      }

      quittance.status = "completed";
      await quittance.save();

      // Return response with all extracted data
      res.json({
        success: true,
        quittance: {
          id: quittance._id,
          companyId: quittance.companyId,
          company: company,
          code_quittance: quittance.code_quittance,
          numero_contrat: quittance.numero_contrat,
          beneficiaire: quittance.beneficiaire,
          agence: quittance.agence,
          assurance: quittance.assurance,
          souscripteur: quittance.souscripteur,
          devise: quittance.devise,
          prime_totale: quittance.prime_totale,
          nature: quittance.nature,
          imageUrl: quittance.imageUrl,
          uploadedAt: quittance.uploadedAt,
          status: quittance.status,
        },
        extractedData: quittance.extractedData, // Return ALL extracted data
        formatUsed: format_used,
        message: `Quittance processed successfully using ${format_used} format`,
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
    res.status(500).json({
      error: "Failed to upload quittance",
      success: false,
      details: error.message,
    });
  }
});

export default router;
