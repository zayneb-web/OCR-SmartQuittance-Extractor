import cv2
import json
import os
from TableExtractor import TableExtractor

class SmartBoxPicker:
    def __init__(self):
        self.coords = []
        self.field_names = []
        self.current_field = 0
        self.points = []
        self.image = None
        self.img_copy = None
        self.format_name = ""
        
    def load_image(self, image_path):
        """Load and preprocess image using TableExtractor"""
        print(f"Loading and preprocessing: {image_path}")
        table_extractor = TableExtractor(image_path)
        self.image = table_extractor.execute()
        self.img_copy = self.image.copy()
        print(f"Preprocessed image shape: {self.image.shape}")
        return self.image
    
    def load_preprocessed_image(self, preprocessed_image_path):
        """Load already preprocessed image"""
        print(f"Loading preprocessed image: {preprocessed_image_path}")
        self.image = cv2.imread(preprocessed_image_path)
        if self.image is None:
            raise ValueError(f"Could not load image: {preprocessed_image_path}")
        self.img_copy = self.image.copy()
        print(f"Image shape: {self.image.shape}")
        return self.image
    
    def get_field_names(self):
        """Get field names from user input"""
        print("Enter field names in order (one per line, empty line to finish):")
        self.field_names = []
        while True:
            name = input()
            if not name.strip():
                break
            self.field_names.append(name.strip())
        
        if not self.field_names:
            raise ValueError("No field names provided")
        
        print(f"Field names: {self.field_names}")
    
    def get_format_name(self):
        """Get format name from user"""
        self.format_name = input("Enter format name (e.g., 'format_1', 'carte_assurances', 'format_3'): ").strip()
        if not self.format_name:
            self.format_name = "new_format"
        print(f"Format name: {self.format_name}")
    
    def click_event(self, event, x, y, flags, param):
        """Mouse callback function for clicking"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            cv2.circle(self.img_copy, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow('Smart Box Picker', self.img_copy)
            
            if len(self.points) == 2:
                x1, y1 = self.points[0]
                x2, y2 = self.points[1]
                x, y = min(x1, x2), min(y1, y2)
                w, h = abs(x2 - x1), abs(y2 - y1)
                
                field_name = self.field_names[self.current_field]
                print(f"{field_name}: (x={x}, y={y}, w={w}, h={h})")
                self.coords.append((field_name, (x, y, w, h)))
                
                # Draw rectangle
                cv2.rectangle(self.img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(self.img_copy, field_name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.imshow('Smart Box Picker', self.img_copy)
                
                self.points = []
                self.current_field += 1
                
                if self.current_field >= len(self.field_names):
                    print("All fields done. Close the window or press 's' to save.")
                    cv2.imwrite('boxes_drawn.jpg', self.img_copy)
    
    def save_configuration(self):
        """Save the box configuration to a JSON file"""
        if not self.coords:
            print("No coordinates to save")
            return
        
        # Convert to dictionary format
        config = {}
        for field_name, (x, y, w, h) in self.coords:
            config[field_name] = (x, y, w, h)
        
        # Create output directory
        os.makedirs("box_configurations", exist_ok=True)
        
        # Save configuration
        output_file = f"box_configurations/{self.format_name}_config.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Configuration saved to: {output_file}")
        
        # Also save as Python dictionary format for easy copy-paste
        python_file = f"box_configurations/{self.format_name}_config.py"
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(f"# Configuration for {self.format_name}\n")
            f.write(f"{self.format_name} = {{\n")
            for field_name, (x, y, w, h) in self.coords:
                f.write(f"    '{field_name}': ({x}, {y}, {w}, {h}),\n")
            f.write("}\n")
        
        print(f"Python configuration saved to: {python_file}")
    
    def load_existing_configuration(self, config_file):
        """Load existing configuration from file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.coords = list(config.items())
            self.field_names = list(config.keys())
            print(f"Loaded configuration with {len(self.field_names)} fields")
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def run(self):
        """Main method to run the box picker"""
        print("=== Smart Box Picker ===")
        print("1. Load original image and preprocess")
        print("2. Load already preprocessed image")
        print("3. Load existing configuration")
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            # Load and preprocess original image
            image_path = input("Enter image path: ").strip()
            if not os.path.exists(image_path):
                print(f"Image not found: {image_path}")
                return
            self.load_image(image_path)
            
        elif choice == "2":
            # Load preprocessed image
            preprocessed_path = input("Enter preprocessed image path: ").strip()
            if not os.path.exists(preprocessed_path):
                print(f"Image not found: {preprocessed_path}")
                return
            self.load_preprocessed_image(preprocessed_path)
            
        elif choice == "3":
            # Load existing configuration
            config_file = input("Enter configuration file path: ").strip()
            if not os.path.exists(config_file):
                print(f"Configuration file not found: {config_file}")
                return
            if self.load_existing_configuration(config_file):
                # Load the corresponding preprocessed image
                preprocessed_path = input("Enter preprocessed image path to visualize: ").strip()
                if os.path.exists(preprocessed_path):
                    self.load_preprocessed_image(preprocessed_path)
                    self.visualize_existing_config()
                    return
            return
            
        else:
            print("Invalid choice")
            return
        
        # Get format name and field names
        self.get_format_name()
        self.get_field_names()
        
        # Setup window and mouse callback
        cv2.namedWindow('Smart Box Picker', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Smart Box Picker', self.click_event)
        
        # Show image
        cv2.imshow('Smart Box Picker', self.img_copy)
        print("Click top-left and bottom-right corners for each field.")
        print("Press 's' to save configuration, 'q' to quit without saving.")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                self.save_configuration()
                break
            elif key == ord('q'):
                print("Quitting without saving")
                break
            elif key == 27:  # ESC key
                print("Quitting without saving")
                break
        
        cv2.destroyAllWindows()
    
    def visualize_existing_config(self):
        """Visualize existing configuration on the image"""
        if not self.coords:
            print("No configuration to visualize")
            return
        
        # Draw all boxes
        for field_name, (x, y, w, h) in self.coords:
            cv2.rectangle(self.img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(self.img_copy, field_name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Save visualization
        output_file = f"boxes_visualization_{self.format_name}.jpg"
        cv2.imwrite(output_file, self.img_copy)
        print(f"Visualization saved to: {output_file}")
        
        # Show image
        cv2.namedWindow('Configuration Visualization', cv2.WINDOW_NORMAL)
        cv2.imshow('Configuration Visualization', self.img_copy)
        print("Press any key to close")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    picker = SmartBoxPicker()
    picker.run()

if __name__ == "__main__":
    main() 