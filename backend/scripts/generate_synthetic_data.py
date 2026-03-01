"""Simple synthetic dataset generator for MVP training.

Creates a specified number of 640x640 PNG images with randomly placed
colored rectangles representing different component classes. The
corresponding YOLO label files are generated in the same directory.

Usage:
    python backend/scripts/generate_synthetic_data.py --output data/train/images --count 100
    python backend/scripts/generate_synthetic_data.py --output data/val/images --count 20

The script writes .png images and .txt label files; each label line is
"<class> <x_center> <y_center> <width> <height>" in normalized coordinates.

This is only for demonstration – replace with real photos for production.
"""
import os
import random
import argparse
from PIL import Image, ImageDraw

CLASSES = [
    'IC', 'Capacitor', 'Resistor', 'Transistor',
    'Connector', 'PCB_Trace', 'Heat_Sink', 'Crystal'
]


def make_image(path, num_boxes=5):
    size = 640
    img = Image.new('RGB', (size, size), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    boxes = []
    for _ in range(num_boxes):
        w = random.randint(50, 200)
        h = random.randint(20, 150)
        x = random.randint(0, size - w)
        y = random.randint(0, size - h)
        class_id = random.randrange(len(CLASSES))
        # random color
        color = tuple(random.randint(100, 255) for _ in range(3))
        draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
        # normalized YOLO coordinates
        x_center = (x + w / 2) / size
        y_center = (y + h / 2) / size
        boxes.append((class_id, x_center, y_center, w / size, h / size))
    img.save(path)
    # write label file alongside in a 'labels' subdirectory as expected by YOLO
    label_dir = os.path.join(os.path.dirname(path), '..', 'labels')
    os.makedirs(label_dir, exist_ok=True)
    label_path = os.path.join(label_dir, os.path.basename(path).replace('.png', '.txt'))
    with open(label_path, 'w') as f:
        for box in boxes:
            f.write(' '.join(str(x) for x in box) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True,
                        help='output directory (must exist)')
    parser.add_argument('--count', type=int, default=100,
                        help='number of images to generate')
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    for i in range(args.count):
        filename = f'synth_{i:04d}.png'
        make_image(os.path.join(args.output, filename))
    print(f'Generated {args.count} images in {args.output}')


if __name__ == '__main__':
    main()
