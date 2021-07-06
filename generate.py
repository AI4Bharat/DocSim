import sys
from docsim.generator import Generator

if __name__ == '__main__':
    # TODO: Use argparse
    #template_json = sys.argv[1]
    #samples = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    #output_folder = sys.argv[3] if len(sys.argv) > 3 else None

    #TODO uncomment above code remove below code
    template_json = "templates/PAN-HI/Latest/template.json"
    samples= 10
    output_folder = "output"
    Generator(template_json).generate(samples, output_folder)
