import cv2

coords = []
field_names = []

print("Enter field names in order (one per line, empty line to finish):")
while True:
    name = input()
    if not name.strip():
        break
    field_names.append(name.strip())

print("Now click top-left and bottom-right corners for each field in the image window.")

img = cv2.imread('preprocess/table_extractor/11_perspective_corrected_with_padding.jpg')
img_copy = img.copy()

current_field = 0
points = []

# Mouse callback function
def click_event(event, x, y, flags, param):
    global current_field, points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(img_copy, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow('image', img_copy)
        if len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
            x, y = min(x1, x2), min(y1, y2)
            w, h = abs(x2 - x1), abs(y2 - y1)
            print(f"{field_names[current_field]}: (x={x}, y={y}, w={w}, h={h})")
            coords.append((field_names[current_field], (x, y, w, h)))
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow('image', img_copy)
            points = []
            current_field += 1
            if current_field >= len(field_names):
                print("All fields done. Close the window.")
                cv2.imwrite('boxes_drawn.jpg', img_copy)
                cv2.destroyAllWindows()

cv2.imshow('image', img_copy)
cv2.setMouseCallback('image', click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()

print("Final box coordinates:")
for name, box in coords:
    print(f"'{name}': {box},") 