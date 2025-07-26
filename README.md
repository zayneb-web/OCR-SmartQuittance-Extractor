# Quittance Extractor - Smart System

A smart system for extracting data from different types of quittance documents with automatic format detection.

## 🚀 Quick Start

```bash
python launcher.py
```

## 📋 What It Does

- **Automatically detects** quittance format (format_1, carte_assurances, hp0012_custom)
- **Extracts text** from specific fields using OCR
- **Saves results** in JSON format
- **Works with preprocessed images** for accurate field extraction

## 🛠️ Supported Formats

1. **format_1** - Original quittance format
2. **carte_assurances** - CARTE ASSURANCES format
3. **hp0012_custom** - Custom format for HP0012 (automatically detected)

## 📁 File Structure

```
quittance extractor/
├── launcher.py                 # Main launcher
├── quittance_processor.py      # Smart processor
├── smart_box_picker.py         # Box picker tool
├── TableExtractor.py           # Image preprocessing
├── images/                     # Input images
│   ├── HP0006.jpg
│   └── HP0012.jpg
├── box_configurations/         # Saved box configurations
├── debug_crops/                # Debug field extractions
└── extracted_quittances.json   # Output results
```

## 🎯 How to Use

### 1. Prepare Images

Place your quittance images in the `./images` directory.

### 2. Run the System

```bash
python launcher.py
```

### 3. Choose Operation

- **Option 1**: Process all quittances (auto-detect) - **Recommended**
- **Option 2**: Process all quittances (manual format)
- **Option 3**: Process single quittance
- **Option 4**: Create new box configuration
- **Option 5**: Visualize existing configuration

### 4. Get Results

Results are saved in `extracted_quittances.json`

## 🔧 For New Quittance Types

### Create Box Configuration:

1. Choose **Option 4** in launcher
2. Load and preprocess your image
3. Define field names
4. Click to create boxes for each field
5. Save configuration

### Add to Processor:

1. Edit `quittance_processor.py`
2. Add new format to `FIELD_BOXES_CONFIGS`
3. Update `detect_quittance_format` method if needed

## 📊 Output Format

```json
{
  "assurance": "...",
  "numero_quittance": "...",
  "agence": "...",
  "souscripteur": "...",
  "adresse": "...",
  "ville": "...",
  "code_postal": "...",
  "assure": "...",
  "num_contrat": "...",
  "periode_assurance": {
    "date_debut": "...",
    "date_fin": "..."
  },
  "prime_base": "...",
  "prime_annexe": "...",
  "frais": "...",
  "taxe_base": "...",
  "prime_totale": "...",
  "categorie_risque": "...",
  "immatriculation": "...",
  "marque": "...",
  "type_vehicule": "...",
  "date_emission": "...",
  "source_file": "filename.jpg",
  "detected_format": "hp0012_custom"
}
```

## 🎉 Key Features

- ✅ **Automatic format detection**
- ✅ **Custom box configurations**
- ✅ **Preprocessed image support**
- ✅ **Visual feedback and debugging**
- ✅ **Multiple format support**
- ✅ **Easy configuration management**

## 🐛 Troubleshooting

### Common Issues:

1. **No images found** → Check `./images` directory
2. **Format detection fails** → Use manual format selection
3. **Box coordinates wrong** → Use Smart Box Picker on preprocessed images
4. **OCR errors** → Check image quality and preprocessing

### Debug Features:

- **Debug crops**: Individual field extractions in `debug_crops/`
- **Box visualizations**: Preview images with boxes drawn
- **Processing logs**: Detailed console output

## 📝 Requirements

```bash
pip install -r requirements.txt
```

## 🎯 Example Usage

```bash
# Process all quittances automatically
python launcher.py
# Choose Option 1

# Process single quittance
python launcher.py
# Choose Option 3, select image

# Create new box configuration
python launcher.py
# Choose Option 4
```

That's it! Your system is ready to extract quittance data automatically. 🚀
