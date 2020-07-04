import os, sys
import json
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from docsim.utils.random import random_id
from docsim.text_generators import TextFromRegexGenerator, TextFromArrayGenerator, FullNameGenerator, ReferntialTextTransliterator
from docsim.utils.qr import get_qr_img, get_rand_string
from docsim.utils.barcode import get_barcode
from docsim.utils.face import get_random_face

class Generator:
    def __init__(self, template_json):
        
        with open(template_json, encoding='utf-8') as f:
            template = json.load(f)
        
        self.doc_name = template['doc_name']
        self.bg_img = template['background_img']
        
        self.components = template['components']
        self.default_config = template['defaults']
        self.set_defaults()
        self.process_components()
    
    def set_defaults(self):
        if 'font_color' not in self.default_config:
            self.default_config['font_color'] = 'rgb(0,0,0)'
        if 'font_file' not in self.default_config:
            self.default_config['font_file'] = None
        if 'font_size' not in self.default_config:
            self.default_config['font_size'] = 12
        
        if 'lang' not in self.default_config:
            self.default_config['lang'] = 'en'
        
        self.default_font = ImageFont.truetype(self.default_config['font_file'], size=self.default_config['font_size'])
        
    def process_components(self):
        for component_name, component in self.components.items():
            if component['type'] == 'text':
                
                # Setup fonts
                if 'font_color' not in component:
                    component['font_color'] = self.default_config['font_color']
                if 'font_file' not in component:
                    component['font_file'] = self.default_config['font_file']
                if 'font_size' not in component:
                    component['font_size'] = self.default_config['font_size']
                component['font'] = ImageFont.truetype(component['font_file'], size=component['font_size'])
                
                # Setup the filling method
                if 'lang' not in component:
                    component['lang'] = self.default_config['lang']
                
                if component['filler_mode'] == 'random':
                    if component['filler_type'] == 'full_name':
                        component['generator'] = FullNameGenerator(component['lang'])
                    else:
                        raise NotImplementedError
                elif component['filler_mode'] == 'regex':
                    component['generator'] = TextFromRegexGenerator(component['filler_regex'])
                elif component['filler_mode'] == 'array':
                    component['generator'] = TextFromArrayGenerator(component['filler_options'])
                elif component['filler_mode'] == 'transliteration':
                    src_component = self.components[component['filler_source']]
                    component['generator'] = ReferntialTextTransliterator(src_component['lang'], component['lang'], src_component)
                else:
                    raise NotImplementedError
            elif component['type'] == 'qr':
                pass
            elif component['type'] == 'barcode':
                pass
            elif component['type'] == 'face-image':
                pass
            else:
                raise NotImplementedError
        return
    
    def generate(self, num_samples, output_folder=None):
        if not output_folder:
            output_folder = os.path.join('output', self.doc_name)
        os.makedirs(output_folder, exist_ok=True)
        
        for i in tqdm(range(num_samples)):
            image = Image.open(self.bg_img)
            img_draw = ImageDraw.Draw(image)
            ground_truth = []
            for component_name, component in self.components.items():
                if component['type'] == 'text':
                    metadata = self.draw_text(img_draw, component)
                    ground_truth.append(metadata)
                if component['type'] == 'qr':
                    metadata = self.draw_qr(image, component)
                    ground_truth.append(metadata)
                if component['type'] == 'barcode':
                    metadata = self.draw_barcode(image, component)
                    ground_truth.append(metadata)
                if component['type'] == 'face-image':
                    metadata = self.draw_face(image, component)
                    ground_truth.append(metadata)
                    
            output_file = os.path.join(output_folder, random_id())
            image.save(output_file+'.png')
            with open(output_file+'.json', 'w', encoding='utf-8') as f:
                json.dump(ground_truth, f, ensure_ascii=False, indent=4)
    
    def draw_text(self, img_draw, component):
        x, y = component['location']['x_left'], component['location']['y_top']
        text = component['generator'].generate()
        component['last_generated'] = text
        img_draw.text((x, y), text, fill=component['font_color'], font=component['font'])
        width, height = img_draw.textsize(text, font=component['font'])
        # img_draw.rectangle([(x,y), (x+width+1, y+height+1)], outline='rgb(255,0,0)')
        return {
            'x_left': x,
            'y_top': y,
            'x_right': x+width+1,
            'y_bottom': y+height+1,
            'width': width,
            'height': height,
            'type': 'text',
            'text': text
        }
    
    def draw_qr(self, image, component):
        x, y = component['location']['x_left'], component['location']['y_top']
        width, height = component['dims']['width'], component['dims']['height']
        version_min, version_max = component['version_min'], component['version_max']
        string_min, string_max = component['string_len_min'], component['string_len_max']
        string = get_rand_string(min_l=string_min, max_l=string_max)
        qr_img = get_qr_img(min_v=version_min, max_v=version_max, data=string)
        qr_img = qr_img.resize((width, height))
        image.paste(qr_img,(x,y))
        
        return {
            'type': 'qr-code',
            'x_left': x,
            'y_top': y,
            'x_right': x+width+1,
            'y_bottom': y+height+1,
            'width': width,
            'height': height,
            'qr_text': string
        }
    def draw_barcode(self, image, component):
        x, y = component['location']['x_left'], component['location']['y_top']
        width, height = component['dims']['width'], component['dims']['height']
        bar_image = get_barcode(new_shape=(width,height))
        image.paste(bar_image,(x,y))
        
        return {
            'type': 'barcode',
            'x_left': x,
            'y_top': y,
            'x_right': x+width+1,
            'y_bottom': y+height+1,
            'width': width,
            'height': height,
        }
    def draw_face(self, image, component):
        x, y = component['location']['x_left'], component['location']['y_top']
        width, height = component['dims']['width'], component['dims']['height']
        face_image = get_random_face(shape=(width,height))
        image.paste(face_image,(x,y))
        
        return {
            'type': 'face',
            'x_left': x,
            'y_top': y,
            'x_right': x+width+1,
            'y_bottom': y+height+1,
            'width': width,
            'height': height,
        }
if __name__ == '__main__':
    template_json, output_folder = sys.argv[1:]
    Generator(template_json).generate(1, output_folder)
