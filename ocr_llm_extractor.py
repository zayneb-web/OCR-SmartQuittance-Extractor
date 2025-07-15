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

FIELD_BOXES = {
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
}

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

def extract_all_fields(image, field_boxes):
    ocr = PaddleOCR(use_angle_cls=True, lang='fr')
    data = {}
    for field, box in field_boxes.items():
        data[field] = extract_field_from_box(image, box, ocr, field)
    # Post-process for nested fields
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