import sys

import argparse

from docsim.generator import Generator

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--template', type=str, help='template config file', default="templates/PAN-HI/Latest/template.json")
    parser.add_argument('--samples', type=int, help='number of documents to generate',
                        default="2")
    parser.add_argument('--output_folder', type=str, help='output folder',
                        default="output")

    opt = parser.parse_args()
    Generator(opt.template).generate(opt.samples, opt.output_folder)
