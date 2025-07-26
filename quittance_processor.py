import os
import json
import cv2
import numpy as np
from TableExtractor import TableExtractor
from paddleocr import PaddleOCR

class QuittanceProcessor:
    def __init__(self):
        self.IMAGE_DIR = './images'
        self.OUTPUT_FILE = 'extracted_quittances.json'
        self.IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        
        # Format configurations for different quittance types
        self.FIELD_BOXES_CONFIGS = {
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
                'date_emission': (1036, 958, 145, 49),  # Fixed: was 1385, now 958
                'commission': (1028, 948, 155, 59),     # Fixed: was 1385, now 948
            },
            
            'format_3': {  # Third format (you can customize this)
                # Add your third format field boxes here
                'example_field': (100, 100, 200, 50),
            },
            
            'hp0012_custom': {  # HP0012 custom format
                'assurance': (541, 188, 234, 35),
                'numero_quittance': (789, 189, 153, 32),
                'agence': (362, 263, 90, 28),
                'souscripteur': (361, 314, 354, 27),
                'adresse': (362, 353, 297, 19),
                'ville': (468, 379, 145, 30),
                'code_postal': (364, 386, 81, 25),
                'assure': (364, 419, 351, 32),
                'num_contrat': (361, 461, 141, 28),
                'fractionnement': (784, 455, 154, 32),
                'numero_aliment': (361, 495, 183, 30),
                'date_effet_debut': (358, 528, 134, 35),
                'date_effet_fin': (746, 526, 138, 37),
                'prime_base': (194, 620, 125, 56),
                'prime_annexe': (337, 623, 135, 51),
                'frais': (494, 623, 100, 57),
                'taxe_base': (608, 624, 122, 53),
                'taxes_annexes': (736, 620, 146, 59),
                'fpcsr': (885, 622, 91, 55),
                'fpac': (980, 625, 87, 47),
                'fga': (1077, 629, 76, 41),
                'prime_totale': (1187, 621, 106, 56),
                'categorie_risque': (382, 689, 168, 31),
                'immatriculation': (382, 726, 136, 29),
                'marque': (381, 763, 129, 30),
                'type_vehicule': (380, 798, 150, 35),
                'date_emission': (1089, 733, 150, 44),
            }
        }
        
        self.ocr = PaddleOCR(use_angle_cls=True, lang='fr')
    
    def detect_quittance_format(self, image):
        """
        Automatically detect quittance format based on image characteristics
        Returns: 'format_1', 'carte_assurances', 'hp0012_custom', or 'format_3'
        """
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Extract some text from the image to help with format detection
        result = self.ocr.ocr(image, cls=True)
        text_content = ""
        if result:
            for line in result:
                if line:
                    for word_info in line:
                        text_content += word_info[1][0] + " "
        
        text_content = text_content.lower()
        
        # Format detection logic
        if "carte assurances" in text_content or "agence" in text_content:
            # Check if it's the specific HP0012 format by looking for unique characteristics
            if "ipteur" in text_content or "benammaref" in text_content:
                return 'hp0012_custom'
            else:
                return 'carte_assurances'
        elif "assurance" in text_content and "contrat" in text_content:
            return 'format_1'
        else:
            # Default to format_1 if unsure, or you can add more detection logic
            return 'format_1'
    
    def preprocess_image(self, image_path):
        """Preprocess image using TableExtractor"""
        table_extractor = TableExtractor(image_path)
        processed_img = table_extractor.execute()
        return processed_img
    
    def extract_field_from_box(self, image, box, field):
        """Extract text from a specific box in the image"""
        x, y, w, h = box
        
        # Check if coordinates are within image bounds
        img_height, img_width = image.shape[:2]
        if x < 0 or y < 0 or x + w > img_width or y + h > img_height:
            print(f"Warning: Box coordinates out of bounds for field '{field}' at ({x}, {y}, {w}, {h}). Image size: {img_width}x{img_height}")
            return ''
        
        crop = image[y:y+h, x:x+w]
        
        # Check if crop is valid
        if crop is None or crop.size == 0:
            print(f"Warning: Invalid crop for field '{field}' at ({x}, {y}, {w}, {h})")
            return ''
        
        # Save debug crop only if crop is valid
        try:
            debug_dir = "debug_crops"
            os.makedirs(debug_dir, exist_ok=True)
            cv2.imwrite(f"{debug_dir}/crop_{field}.jpg", crop)
        except Exception as e:
            print(f"Warning: Could not save debug crop for field '{field}': {e}")
        
        print(f"Cropping field '{field}' at ({x}, {y}, {w}, {h}), crop shape: {crop.shape}")
        
        result = self.ocr.ocr(crop, cls=True)
        text = ''
        
        if not result:
            print(f"No OCR result for field '{field}' at ({x}, {y}, {w}, {h})")
            return text
            
        for line in result:
            if not line:
                continue
            for word_info in line:
                text += word_info[1][0] + ' '
        
        return text.strip()
    
    def extract_all_fields(self, image, format_name):
        """Extract all fields using the specified format"""
        if format_name not in self.FIELD_BOXES_CONFIGS:
            raise ValueError(f"Unknown format: {format_name}. Available formats: {list(self.FIELD_BOXES_CONFIGS.keys())}")
        
        field_boxes = self.FIELD_BOXES_CONFIGS[format_name]
        data = {}
        
        for field, box in field_boxes.items():
            data[field] = self.extract_field_from_box(image, box, field)
        
        return self.format_output_data(data, format_name)
    
    def format_output_data(self, data, format_name):
        """Format the extracted data based on the quittance type"""
        if format_name == 'carte_assurances':
            return {
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
        elif format_name == 'hp0012_custom':
            return {
                'assurance': data.get('assurance', ''),
                'numero_quittance': data.get('numero_quittance', ''),
                'agence': data.get('agence', ''),
                'souscripteur': data.get('souscripteur', ''),
                'adresse': data.get('adresse', ''),
                'ville': data.get('ville', ''),
                'code_postal': data.get('code_postal', ''),
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
            }
        else:  # format_1 and format_3
            return {
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
    
    def visualize_boxes(self, image, format_name, output_path='boxes_preview.jpg'):
        """Visualize the boxes for the specified format"""
        if format_name not in self.FIELD_BOXES_CONFIGS:
            raise ValueError(f"Unknown format: {format_name}")
        
        field_boxes = self.FIELD_BOXES_CONFIGS[format_name]
        img_copy = image.copy()
        
        for field, (x, y, w, h) in field_boxes.items():
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img_copy, field, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imwrite(output_path, img_copy)
        print(f"Box visualization saved to {output_path}")
    
    def process_single_image(self, image_path, format_name=None):
        """Process a single image with automatic or manual format detection"""
        print(f"Processing: {image_path}")
        
        try:
            # Preprocess the image
            processed_img = self.preprocess_image(image_path)
            print(f"Preprocessed image shape: {processed_img.shape}")
            
            # Detect format if not specified
            if format_name is None:
                format_name = self.detect_quittance_format(processed_img)
                print(f"Detected format: {format_name}")
            
            # Visualize boxes
            try:
                self.visualize_boxes(processed_img, format_name, f"boxes_preview_{os.path.basename(image_path)}.jpg")
            except Exception as e:
                print(f"Warning: Could not save box visualization: {e}")
            
            # Extract fields
            fields = self.extract_all_fields(processed_img, format_name)
            fields['source_file'] = os.path.basename(image_path)
            fields['detected_format'] = format_name
            
            return fields
            
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            # Return a basic result with error information
            return {
                'source_file': os.path.basename(image_path),
                'detected_format': format_name or 'unknown',
                'error': str(e)
            }
    
    def process_all_images(self, manual_format=None):
        """Process all images in the images directory"""
        results = []
        
        # Get list of image files
        image_files = []
        for filename in os.listdir(self.IMAGE_DIR):
            if any(filename.lower().endswith(ext) for ext in self.IMAGE_EXTENSIONS):
                image_files.append(filename)
        
        if not image_files:
            print(f"No image files found in {self.IMAGE_DIR}")
            return results
        
        print(f"Found {len(image_files)} image(s): {image_files}")
        
        # Process each image
        for filename in image_files:
            image_path = os.path.join(self.IMAGE_DIR, filename)
            try:
                fields = self.process_single_image(image_path, manual_format)
                results.append(fields)
                print(f"Successfully processed {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
        
        # Save results
        with open(self.OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Extraction complete. Results saved to {self.OUTPUT_FILE}")
        return results

def main():
    processor = QuittanceProcessor()
    
    print("=== Quittance Processor ===")
    print("Available formats:")
    for i, format_name in enumerate(processor.FIELD_BOXES_CONFIGS.keys(), 1):
        print(f"{i}. {format_name}")
    print("0. Auto-detect (recommended)")
    
    choice = input("\nSelect format (0 for auto-detect): ").strip()
    
    manual_format = None
    if choice != "0":
        format_names = list(processor.FIELD_BOXES_CONFIGS.keys())
        try:
            format_index = int(choice) - 1
            if 0 <= format_index < len(format_names):
                manual_format = format_names[format_index]
                print(f"Using manual format: {manual_format}")
            else:
                print("Invalid choice, using auto-detect")
        except ValueError:
            print("Invalid input, using auto-detect")
    
    # Process all images
    results = processor.process_all_images(manual_format)
    
    # Display summary
    print(f"\n=== Processing Summary ===")
    print(f"Total images processed: {len(results)}")
    for result in results:
        print(f"- {result['source_file']}: {result['detected_format']}")

if __name__ == "__main__":
    main() 