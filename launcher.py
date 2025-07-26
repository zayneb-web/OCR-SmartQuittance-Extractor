#!/usr/bin/env python3
"""
Quittance Extractor Launcher
This script provides an easy way to access different tools in the quittance extraction system.
"""

import os
import sys

def print_banner():
    print("=" * 60)
    print("           QUITTANCE EXTRACTOR SYSTEM")
    print("=" * 60)
    print()

def print_menu():
    print("Available Operations:")
    print("1. Process all quittances (auto-detect format)")
    print("2. Process all quittances (manual format selection)")
    print("3. Process single quittance")
    print("4. Create new box configuration (Smart Box Picker)")
    print("5. Visualize existing box configuration")
    print("6. Run original box picker")
    print("7. Run original OCR extractor")
    print("8. Exit")
    print()

def check_images():
    """Check if images exist in the images directory"""
    image_dir = './images'
    if not os.path.exists(image_dir):
        print(f"❌ Images directory '{image_dir}' not found!")
        return False
    
    image_files = []
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
            image_files.append(filename)
    
    if not image_files:
        print(f"❌ No image files found in '{image_dir}'!")
        return False
    
    print(f"✅ Found {len(image_files)} image(s): {image_files}")
    return True

def run_quittance_processor(auto_detect=True):
    """Run the quittance processor"""
    try:
        from quittance_processor import QuittanceProcessor
        
        processor = QuittanceProcessor()
        
        if auto_detect:
            print("🔄 Processing with auto-detection...")
            results = processor.process_all_images()
        else:
            print("🔄 Processing with manual format selection...")
            print("Available formats:")
            for i, format_name in enumerate(processor.FIELD_BOXES_CONFIGS.keys(), 1):
                print(f"{i}. {format_name}")
            
            choice = input("\nSelect format: ").strip()
            format_names = list(processor.FIELD_BOXES_CONFIGS.keys())
            try:
                format_index = int(choice) - 1
                if 0 <= format_index < len(format_names):
                    manual_format = format_names[format_index]
                    print(f"Using format: {manual_format}")
                    results = processor.process_all_images(manual_format)
                else:
                    print("Invalid choice, using auto-detect")
                    results = processor.process_all_images()
            except ValueError:
                print("Invalid input, using auto-detect")
                results = processor.process_all_images()
        
        print("✅ Processing complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Error importing quittance_processor: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False

def run_single_quittance():
    """Process a single quittance"""
    try:
        from quittance_processor import QuittanceProcessor
        
        processor = QuittanceProcessor()
        
        # List available images
        image_files = []
        for filename in os.listdir(processor.IMAGE_DIR):
            if any(filename.lower().endswith(ext) for ext in processor.IMAGE_EXTENSIONS):
                image_files.append(filename)
        
        if not image_files:
            print("❌ No image files found!")
            return False
        
        print("Available images:")
        for i, filename in enumerate(image_files, 1):
            print(f"{i}. {filename}")
        
        choice = input("\nSelect image (number): ").strip()
        try:
            image_index = int(choice) - 1
            if 0 <= image_index < len(image_files):
                selected_image = image_files[image_index]
                image_path = os.path.join(processor.IMAGE_DIR, selected_image)
                
                print(f"🔄 Processing: {selected_image}")
                fields = processor.process_single_image(image_path)
                
                print("✅ Processing complete!")
                print(f"Detected format: {fields.get('detected_format', 'Unknown')}")
                return True
            else:
                print("❌ Invalid image selection")
                return False
        except ValueError:
            print("❌ Invalid input")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_smart_box_picker():
    """Run the smart box picker"""
    try:
        from smart_box_picker import SmartBoxPicker
        
        picker = SmartBoxPicker()
        picker.run()
        return True
        
    except ImportError as e:
        print(f"❌ Error importing smart_box_picker: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running box picker: {e}")
        return False

def visualize_configuration():
    """Visualize existing configuration"""
    try:
        from smart_box_picker import SmartBoxPicker
        
        # List available configurations
        config_dir = "box_configurations"
        if not os.path.exists(config_dir):
            print(f"❌ Configuration directory '{config_dir}' not found!")
            return False
        
        config_files = []
        for filename in os.listdir(config_dir):
            if filename.endswith('_config.json'):
                config_files.append(filename)
        
        if not config_files:
            print(f"❌ No configuration files found in '{config_dir}'!")
            return False
        
        print("Available configurations:")
        for i, filename in enumerate(config_files, 1):
            print(f"{i}. {filename}")
        
        choice = input("\nSelect configuration (number): ").strip()
        try:
            config_index = int(choice) - 1
            if 0 <= config_index < len(config_files):
                config_file = os.path.join(config_dir, config_files[config_index])
                
                picker = SmartBoxPicker()
                if picker.load_existing_configuration(config_file):
                    # Ask for preprocessed image
                    preprocessed_path = input("Enter preprocessed image path: ").strip()
                    if os.path.exists(preprocessed_path):
                        picker.load_preprocessed_image(preprocessed_path)
                        picker.visualize_existing_config()
                        return True
                    else:
                        print("❌ Preprocessed image not found!")
                        return False
                else:
                    print("❌ Failed to load configuration")
                    return False
            else:
                print("❌ Invalid configuration selection")
                return False
        except ValueError:
            print("❌ Invalid input")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_original_box_picker():
    """Run the original box picker"""
    try:
        import subprocess
        print("🔄 Running original box picker...")
        subprocess.run([sys.executable, "box_picker.py"])
        return True
    except Exception as e:
        print(f"❌ Error running original box picker: {e}")
        return False

def run_original_ocr_extractor():
    """Run the original OCR extractor"""
    try:
        import subprocess
        print("🔄 Running original OCR extractor...")
        subprocess.run([sys.executable, "ocr_llm_extractor.py"])
        return True
    except Exception as e:
        print(f"❌ Error running original OCR extractor: {e}")
        return False

def main():
    print_banner()
    
    # Check if images exist
    if not check_images():
        print("Please make sure you have images in the './images' directory.")
        print()
    
    while True:
        print_menu()
        choice = input("Select operation (1-8): ").strip()
        
        if choice == "1":
            print("\n" + "="*40)
            run_quittance_processor(auto_detect=True)
            print("="*40 + "\n")
            
        elif choice == "2":
            print("\n" + "="*40)
            run_quittance_processor(auto_detect=False)
            print("="*40 + "\n")
            
        elif choice == "3":
            print("\n" + "="*40)
            run_single_quittance()
            print("="*40 + "\n")
            
        elif choice == "4":
            print("\n" + "="*40)
            run_smart_box_picker()
            print("="*40 + "\n")
            
        elif choice == "5":
            print("\n" + "="*40)
            visualize_configuration()
            print("="*40 + "\n")
            
        elif choice == "6":
            print("\n" + "="*40)
            run_original_box_picker()
            print("="*40 + "\n")
            
        elif choice == "7":
            print("\n" + "="*40)
            run_original_ocr_extractor()
            print("="*40 + "\n")
            
        elif choice == "8":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-8.")
            print()

if __name__ == "__main__":
    main() 