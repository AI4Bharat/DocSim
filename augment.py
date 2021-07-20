import sys

import argparse

from docsim.augmentor import Augmentor

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', type=str, help='template config file',
                        default="templates/sample_augmentation/config.json")
    
    parser.add_argument('--src_folder', type=str, help='src_folder',
                        default="output")

    parser.add_argument('--dest_folder', type=str, help='destination folder',
                        default="output_augmented")

    parser.add_argument('--num_workers', type=int, help='number of threads',
                        default=4)

    parser.add_argument('--epochs', type=int, help='number of epochs',
                        default=1)

    
    opt = parser.parse_args()
    
    
    config_json  = opt.config
    input_folder = opt.src_folder
    
    epochs = opt.epochs
    output_folder = opt.dest_folder
    num_workers = opt.num_workers
    
    a = Augmentor(config_json)
    
    a(input_folder, epochs, output_folder, num_workers)
