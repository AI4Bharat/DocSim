import sys
from docsim.augmentor import Augmentor

if __name__ == '__main__':
    config_json, input_folder = sys.argv[1:3]
    epochs = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    output_folder = sys.argv[4] if len(sys.argv) > 4 else None
    num_workers = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    
    a = Augmentor(config_json)
    a(input_folder, epochs, output_folder, num_workers)
