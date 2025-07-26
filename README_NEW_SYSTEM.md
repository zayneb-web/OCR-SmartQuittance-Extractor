# Quittance Extractor - New Smart System

This new system provides intelligent quittance processing with automatic format detection and improved box picking capabilities.

## 🚀 Quick Start

Run the launcher to access all features:

```bash
python launcher.py
```

## 📋 System Overview

### Key Features

1. **Automatic Format Detection**: The system automatically detects which quittance format to use
2. **Smart Box Picker**: Create box configurations on preprocessed images
3. **Multiple Format Support**: Support for different quittance types
4. **Easy Configuration Management**: Save and load box configurations
5. **Visual Feedback**: Preview boxes and processing results

### Supported Quittance Formats

1. **format_1**: Original quittance format
2. **carte_assurances**: CARTE ASSURANCES format
3. **format_3**: Third format (customizable)

## 🛠️ Available Operations

### 1. Process All Quittances (Auto-detect)

- Automatically detects the format of each quittance
- Processes all images in the `./images` directory
- Saves results to `extracted_quittances.json`

### 2. Process All Quittances (Manual Selection)

- Manually select which format to use for all quittances
- Useful when you know all quittances are the same type

### 3. Process Single Quittance

- Process one specific quittance
- Shows detected format and results

### 4. Create New Box Configuration

- Use the Smart Box Picker to create new field configurations
- Works with preprocessed images
- Saves configurations for reuse

### 5. Visualize Existing Configuration

- Load and visualize existing box configurations
- Useful for verification and debugging

### 6. Run Original Box Picker

- Access the original box picker tool

### 7. Run Original OCR Extractor

- Access the original OCR extraction tool

## 📁 File Structure

```
quittance extractor/
├── launcher.py                 # Main launcher script
├── quittance_processor.py      # New smart processor
├── smart_box_picker.py         # Improved box picker
├── TableExtractor.py           # Image preprocessing
├── images/                     # Input images
│   ├── HP0006.jpg
│   └── HP0012.jpg
├── box_configurations/         # Saved box configurations
│   ├── format_1_config.json
│   ├── carte_assurances_config.json
│   └── format_3_config.json
├── debug_crops/                # Debug cropped images
├── process_images/             # Processing steps
└── extracted_quittances.json   # Output results
```

## 🔧 How to Use

### Step 1: Prepare Images

Place your quittance images in the `./images` directory.

### Step 2: Run the System

```bash
python launcher.py
```

### Step 3: Choose Operation

Select from the available operations (1-8).

### Step 4: For New Quittance Types

If you have a new quittance type:

1. **Create Box Configuration**:

   - Choose option 4 (Smart Box Picker)
   - Load and preprocess your image
   - Define field names
   - Click to create boxes for each field
   - Save the configuration

2. **Add to Processor**:
   - Edit `quittance_processor.py`
   - Add your new format to `FIELD_BOXES_CONFIGS`
   - Update the `detect_quittance_format` method if needed

## 🎯 Smart Box Picker Features

### Loading Options

1. **Original Image**: Load and preprocess automatically
2. **Preprocessed Image**: Load already processed image
3. **Existing Configuration**: Load and visualize saved config

### Saving Options

- **JSON Format**: For programmatic use
- **Python Format**: For easy copy-paste into code

### Usage Tips

- Click top-left corner, then bottom-right corner for each field
- Press 's' to save, 'q' to quit without saving
- Use ESC key to cancel

## 🔍 Format Detection Logic

The system detects quittance formats by:

1. **OCR Analysis**: Extracts text from the image
2. **Keyword Matching**: Looks for specific keywords
3. **Format Classification**:
   - "carte assurances" or "agence" → `carte_assurances`
   - "assurance" and "contrat" → `format_1`
   - Default → `format_1`

## 📊 Output Format

Results are saved in JSON format with the following structure:

### For CARTE ASSURANCES format:

```json
{
  "assurance": "...",
  "numero_quittance": "...",
  "agence": "...",
  "souscripteur": "...",
  "adresse": "...",
  "ville": "...",
  "assure": "...",
  "num_contrat": "...",
  "fractionnement": "...",
  "numero_aliment": "...",
  "periode_assurance": {
    "date_debut": "...",
    "date_fin": "..."
  },
  "prime_base": "...",
  "prime_annexe": "...",
  "frais": "...",
  "taxe_base": "...",
  "taxes_annexes": "...",
  "fpcsr": "...",
  "fpac": "...",
  "fga": "...",
  "prime_totale": "...",
  "categorie_risque": "...",
  "immatriculation": "...",
  "marque": "...",
  "type_vehicule": "...",
  "date_emission": "...",
  "commission": "...",
  "source_file": "filename.jpg",
  "detected_format": "carte_assurances"
}
```

### For Original format:

```json
{
  "assurance": "...",
  "num_contrat": "...",
  "Periode d'assurance": {
    "date_debut": "...",
    "date_fin": "..."
  },
  "numero quittance": "...",
  "risque": "...",
  "prime": "...",
  "code": "...",
  "COUT DE CONTRAT": "...",
  "assure": {
    "nom et prenom": "...",
    "adresse": "...",
    "code postal": "..."
  },
  "PER": "...",
  "taxe": {
    "taxe": "...",
    "fg": "..."
  },
  "somme a payer": "...",
  "total": "...",
  "source_file": "filename.jpg",
  "detected_format": "format_1"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **No images found**:

   - Make sure images are in `./images` directory
   - Check file extensions (.jpg, .jpeg, .png, .tiff, .bmp)

2. **Format detection fails**:

   - Use manual format selection
   - Check image quality and preprocessing

3. **Box coordinates wrong**:

   - Use Smart Box Picker on preprocessed images
   - Verify image dimensions match expected format

4. **OCR errors**:
   - Check image quality
   - Ensure proper preprocessing
   - Verify PaddleOCR installation

### Debug Features

- **Debug Crops**: Individual field crops saved in `debug_crops/`
- **Box Visualizations**: Preview images with boxes drawn
- **Processing Steps**: Intermediate images saved in `process_images/`

## 🔄 Migration from Old System

The new system is backward compatible:

- Original `box_picker.py` still available (option 6)
- Original `ocr_llm_extractor.py` still available (option 7)
- Existing configurations can be loaded and used

## 📝 Adding New Formats

1. Create box configuration using Smart Box Picker
2. Add format to `FIELD_BOXES_CONFIGS` in `quittance_processor.py`
3. Update `detect_quittance_format` method if needed
4. Update `format_output_data` method for proper JSON structure

## 🎉 Benefits of New System

- **Automatic**: No need to manually select formats
- **Flexible**: Easy to add new quittance types
- **Visual**: Better feedback and debugging
- **Organized**: Proper configuration management
- **User-friendly**: Simple launcher interface
