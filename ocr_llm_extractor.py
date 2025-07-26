import os
import json
import cv2
from TableExtractor import TableExtractor
from paddleocr import PaddleOCR

IMAGE_DIR = './images'
OUTPUT_FILE = 'extracted_quittances.json'
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']

# Box coordinates measured on this image size:
EXPECTED_IMAGE_SHAPE = (768, 1137, 3)  # (height, width, channels) - update to match your box picking image

# Multiple box configurations for different quittance formats
FIELD_BOXES_CONFIGS = {
    'format_1': {  # Original format
        'assurance': (193, 171, 331, 33),
        'num_contrat': (203, 268, 112, 42),
        "Periode d'assurance_date_debut": (268, 412, 112, 25),
        "Periode d'assurance_date_fin": (480, 406, 117, 31),
        'numero quittance': (575, 174, 126, 31),
        'risque': (356, 266, 122, 31),
        'prime': (588, 265, 89, 36),
        'code': (693, 410, 84, 22),
        'COUT DE CONTRAT': (748, 270, 93, 32),
        'assure_nom et prenom': (701, 575, 222, 34),
        'assure_adresse': (704, 609, 198, 52),
        'assure_code postal': (699, 663, 78, 33),
        'PER': (853, 407, 79, 30),
        'taxe_taxe': (967, 267, 111, 29),
        'taxe_fg': (991, 319, 93, 34),
        'somme a payer': (1206, 405, 101, 48),
        'total': (1197, 308, 109, 49),
    },
   
    'carte_assurances': {  # CARTE ASSURANCES format
        'assurance': (109, 70, 130, 85),
        'numero_quittance': (681, 234, 156, 31),
        'agence': (278, 286, 62, 54),
        'souscripteur': (277, 343, 339, 41),
        'adresse': (269, 376, 272, 43),
        'ville': (276, 412, 246, 36),
        'assure': (272, 448, 335, 43),
        'num_contrat': (263, 486, 149, 39),
        'fractionnement': (677, 476, 152, 54),
        'numero_aliment': (255, 522, 214, 37),
        'date_effet_debut': (253, 556, 145, 46),
        'date_effet_fin': (627, 549, 143, 54),
        'prime_base': (96, 644, 125, 56),
        'prime_annexe': (253, 636, 109, 61),
        'frais': (388, 631, 92, 69),
        'taxe_base': (498, 646, 112, 64),
        'taxes_annexes': (626, 641, 132, 72),
        'fpcsr': (760, 644, 91, 64),
        'fpac': (855, 657, 91, 49),
        'fga': (948, 656, 85, 62),
        'prime_totale': (1040, 656, 121, 67),
        'categorie_risque': (284, 706, 162, 45),
        'immatriculation': (293, 754, 155, 29),
        'marque': (284, 778, 167, 38),
        'type_vehicule': (280, 811, 161, 49),
        'date_emission': (1036, 1385, 145, 49),
        'commission': (1028, 1385, 155, 59),
    }
}

# Default to format_1
FIELD_BOXES = FIELD_BOXES_CONFIGS['format_1']

def preprocess_image(image_path):
    table_extractor = TableExtractor(image_path)
    processed_img = table_extractor.execute()  # This is your 11_perspective_corrected_with_padding.jpg
    return processed_img

def extract_field_from_box(image, box, ocr, field):
    x, y, w, h = box
    crop = image[y:y+h, x:x+w]
    cv2.imwrite(f"debug_crop_{field}.jpg", crop)
    print(f"Cropping field at ({x}, {y}, {w}, {h}), crop shape: {crop.shape}")
    result = ocr.ocr(crop, cls=True)
    text = ''
    if not result:
        print(f"No OCR result for field at ({x}, {y}, {w}, {h})")
        return text
    for line in result:
        if not line:
            continue
        for word_info in line:
            text += word_info[1][0] + ' '
    return text.strip()

def extract_all_fields(image, field_boxes=None):
    if field_boxes is None:
        field_boxes = FIELD_BOXES
    
    ocr = PaddleOCR(use_angle_cls=True, lang='fr')
    data = {}
    for field, box in field_boxes.items():
        data[field] = extract_field_from_box(image, box, ocr, field)
    
    # Determine format based on field names
    if 'agence' in field_boxes:
        # CARTE ASSURANCES format
        final_json = {
            'assurance': data.get('assurance', ''),
            'numero_quittance': data.get('numero_quittance', ''),
            'agence': data.get('agence', ''),
            'souscripteur': data.get('souscripteur', ''),
            'adresse': data.get('adresse', ''),
            'ville': data.get('ville', ''),
            'assure': data.get('assure', ''),
            'num_contrat': data.get('num_contrat', ''),
            'fractionnement': data.get('fractionnement', ''),
            'numero_aliment': data.get('numero_aliment', ''),
            'periode_assurance': {
                'date_debut': data.get('date_effet_debut', ''),
                'date_fin': data.get('date_effet_fin', ''),
            },
            'prime_base': data.get('prime_base', ''),
            'prime_annexe': data.get('prime_annexe', ''),
            'frais': data.get('frais', ''),
            'taxe_base': data.get('taxe_base', ''),
            'taxes_annexes': data.get('taxes_annexes', ''),
            'fpcsr': data.get('fpcsr', ''),
            'fpac': data.get('fpac', ''),
            'fga': data.get('fga', ''),
            'prime_totale': data.get('prime_totale', ''),
            'categorie_risque': data.get('categorie_risque', ''),
            'immatriculation': data.get('immatriculation', ''),
            'marque': data.get('marque', ''),
            'type_vehicule': data.get('type_vehicule', ''),
            'date_emission': data.get('date_emission', ''),
            'commission': data.get('commission', ''),
        }
    else:
        # Original format
        final_json = {
            'assurance': data.get('assurance', ''),
            'num_contrat': data.get('num_contrat', ''),
            "Periode d'assurance": {
                'date_debut': data.get("Periode d'assurance_date_debut", ''),
                'date_fin': data.get("Periode d'assurance_date_fin", ''),
            },
            'numero quittance': data.get('numero quittance', ''),
            'risque': data.get('risque', ''),
            'prime': data.get('prime', ''),
            'code': data.get('code', ''),
            'COUT DE CONTRAT': data.get('COUT DE CONTRAT', ''),
            'assure': {
                'nom et prenom': data.get('assure_nom et prenom', ''),
                'adresse': data.get('assure_adresse', ''),
                'code postal': data.get('assure_code postal', ''),
            },
            'PER': data.get('PER', ''),
            'taxe': {
                'taxe': data.get('taxe_taxe', ''),
                'fg': data.get('taxe_fg', ''),
            },
            'somme a payer': data.get('somme a payer', ''),
            'total': data.get('total', ''),
        }
    
    return final_json

def extract_all_fields_with_format(image, format_name='format_1'):
    """Extract fields using a specific format configuration"""
    if format_name not in FIELD_BOXES_CONFIGS:
        raise ValueError(f"Unknown format: {format_name}. Available formats: {list(FIELD_BOXES_CONFIGS.keys())}")
    
    field_boxes = FIELD_BOXES_CONFIGS[format_name]
    return extract_all_fields(image, field_boxes)

def visualize_boxes(image, field_boxes, output_path='boxes_preview.jpg'):
    img_copy = image.copy()
    for field, (x, y, w, h) in field_boxes.items():
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img_copy, field, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.imwrite(output_path, img_copy)

def main():
    results = []
    for filename in os.listdir(IMAGE_DIR):
        if any(filename.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
            print(f"Processing {filename}...")
            processed_img = preprocess_image(os.path.join(IMAGE_DIR, filename))
            print(f"Processed image shape: {processed_img.shape}")
            if processed_img.shape != EXPECTED_IMAGE_SHAPE:
                print(f"WARNING: Processed image shape {processed_img.shape} does not match expected {EXPECTED_IMAGE_SHAPE}. Box coordinates may be invalid!")
            visualize_boxes(processed_img, FIELD_BOXES)
            fields = extract_all_fields(processed_img, FIELD_BOXES)
            fields['source_file'] = filename
            results.append(fields)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Extraction complete. Results saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main() 