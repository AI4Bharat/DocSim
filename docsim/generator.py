import os
import json
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from docsim.utils.random import random_id
from docsim.text_generators import *
from docsim.image_generators import *

class Generator:
    def __init__(self, template_json):
        
        if type(template_json) == dict:
            template = template_json
        else:
            with open(template_json, encoding='utf-8') as f:
                template = json.load(f)
        
        self.doc_name = template['doc_name']
        self.bg_img = template['background_img']
        self.DEBUG = template['debug_mode'] if 'debug_mode' in template else False
    
        self.set_defaults(template)
        self.process_components(template)
    
    def set_defaults(self, template):
        self.default_config = template['defaults']
        
        if 'font_color' not in self.default_config:
            self.default_config['font_color'] = 'rgb(0,0,0)'
        if 'font_files' not in self.default_config:
            self.default_config['font_files']['en'] = None
        if 'font_size' not in self.default_config:
            self.default_config['font_size'] = 12
        
        if 'lang' not in self.default_config:
            self.default_config['lang'] = 'en'
        
        if 'multiline' not in self.default_config:
            self.default_config['multiline'] = True
        
        if 'split_words' not in self.default_config:
            self.default_config['split_words'] = False
        
        self.default_fonts = {lang: ImageFont.truetype(self.default_config['font_files'][lang], size=self.default_config['font_size']) for lang in self.default_config['font_files']}
        
        if 'upper_case' not in self.default_config:
            # Do Not Force Upper-casing
            self.default_config['upper_case'] = False
        
        self.default_config['post_processor'] = TextPostProcessor(upper_case=self.default_config['upper_case'], multiline=self.default_config['multiline'])
        
        return
         
    def process_components(self, template):
        '''
        Assign generators to each component in the template
        '''
        self.components = template['components']
        for component_name, component in self.components.items():
            
            component['id'], component['already_printed'] = component_name, False
            if 'filler_source' in component:
                component['data_source'] = self.components[component['filler_source']]
            
            if component['type'] == 'text':
                
                # Setup fonts
                if 'lang' not in component:
                    component['lang'] = self.default_config['lang']
                if 'multiline' not in component:
                    component['multiline'] = self.default_config['multiline']
                if 'upper_case' not in component:
                    component['upper_case'] = self.default_config['upper_case']
                if 'font_color' not in component:
                    component['font_color'] = self.default_config['font_color']
                if 'font_file' not in component:
                    component['font_file'] = self.default_config['font_files'][component['lang']]
                if 'font_size' not in component:
                    component['font_size'] = self.default_config['font_size']
                component['font'] = ImageFont.truetype(component['font_file'], size=component['font_size'])
                
                if 'split_words' not in component:
                    component['split_words'] = self.default_config['split_words']
                if 'entity' not in component:
                    component['entity'] = None
                
                # Setup the filling method                
                if component['filler_mode'] == 'random':
                    if component['filler_type'] == 'full_name':
                        component['generator'] = FullNameGenerator(component['lang'])
                    elif component['filler_type'] == 'multiline_full_name':
                        component['generator'] = MultilineFullNameGenerator(component['lang'])
                    elif component['filler_type'] == 'child_name':
                        component['generator'] = ChildNameFromParentGenerator(component['lang'], component['data_source'])
                    elif component['filler_type'] == 'address':
                        component['generator'] = AddressGenerator(
                            language = component['lang'], type = component['address_type'])
                    else:
                        raise NotImplementedError
                elif component['filler_mode'] == 'regex':
                    component['generator'] = TextFromRegexGenerator(component['filler_regex'])
                elif component['filler_mode'] == 'array':
                    component['generator'] = TextFromArrayGenerator(component['filler_options'])
                elif component['filler_mode'] == 'fixed':
                    component['generator'] = TextFromArrayGenerator([component['filler_text']])
                elif component['filler_mode'] == 'reference':
                    component['generator'] = ReferentialTextGenerator(component['data_source'])
                elif component['filler_mode'] == 'transliteration':
                    component['generator'] = ReferentialTextTransliterator(component['data_source']['lang'], component['lang'], component['data_source'])
                else:
                    raise NotImplementedError
                
                # Setup post-processing. TODO: Optimize? (Too many same objects)
                component['post_processor'] = TextPostProcessor(upper_case=component['upper_case'], multiline=component['multiline'])
            
            elif component['type'] == 'image':
                if component['filler_mode'] == 'random':
                    component['generator'] = ImageGenerator(component['image_folder'], component['dims'])
                elif component['filler_mode'] == 'static':
                    component['generator'] = ImageRetriever(component['image_file'], component['dims'])
                elif component['filler_mode'] == 'random_face_online':
                    component['generator'] = OnlineFaceGenerator(component['dims'])
                elif component['filler_mode'] == 'qr':
                    component['generator'] = QRCodeGenerator(component)
                elif component['filler_mode'] == 'barcode':
                    component['generator'] = BarCodeGenerator(component)
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        
        if 'printed_fields' in template:
            for component_name, component in template['printed_fields'].items():
                if component_name in self.components:
                    exit('Component name %s already taken' % component_name)
                component['id'], component['already_printed'] = component_name, True
                
                if component['type'] == 'text':
                    if 'lang' not in component:
                        component['lang'] = self.default_config['lang']
                    if 'split_words' not in component:
                        component['split_words'] = False #self.default_config['split_words']
                    if 'entity' not in component:
                        component['entity'] = None
                
                self.components[component_name] = component
        return
    
    def generate(self, num_samples, output_folder=None):
        if not output_folder:
            output_folder = os.path.join('output', self.doc_name)
        os.makedirs(output_folder, exist_ok=True)
        output_files = []
        
        for i in tqdm(range(num_samples)):
            image = Image.open(self.bg_img)
            img_draw = ImageDraw.Draw(image)
            ground_truth = []
            for component_name, component in self.components.items():
                if component['type'] == 'text':
                    if component['split_words']:
                        metadata = self.draw_words(img_draw, component)
                    else:
                        metadata = [self.draw_text(img_draw, component)]
                    ground_truth.extend(metadata)
                elif component['type'] == 'image':
                    metadata = self.draw_img(image, component)
                    ground_truth.append(metadata)
                else:
                    raise NotImplementedError
            
            output_file = os.path.join(output_folder, random_id())
            image.save(output_file+'.jpg')
            gt = {'doc_name': self.doc_name, 'data': ground_truth}
            with open(output_file+'.json', 'w', encoding='utf-8') as f:
                json.dump(gt, f, ensure_ascii=False, indent=4)
            
            output_files.append(output_file)
        
        return output_files
    
    def draw_text(self, img_draw, component):
        x, y = component['location']['x_left'], component['location']['y_top']
        if component['already_printed']:
            width, height = component['dims']['width'], component['dims']['height']
            text = component['text']
        else:
            align = component["align"] if "align" in component else "left"
            spacing = component["spacing"] if "spacing" in component else 4
            text = component['generator'].generate()
            component['last_generated'] = text
            text = component['post_processor'].process(text)
            img_draw.text((x, y), text, fill=component['font_color'], font=component['font'], align=align, spacing=spacing)
            width, height = img_draw.textsize(text, font=component['font'])
        self.DEBUG and img_draw.rectangle([(x,y), (x+width+1, y+height+1)], outline='rgb(255,0,0)')
        return {
            'type': component['type'],
            'label': component['id'],
            'entity': component['entity'],
            'points': [ # Clock-wise
                [x+1, y+1], # Left Top
                [x+width+1, y+1], # Right Top
                [x+width+1, y+height+1], # Right Bottom
                [x+1, y+height+1] # Left bottom
            ],
            'width': width,
            'height': height,
            'text': text,
            'lang': component['lang']
        }
        
    def draw_words(self, img_draw, component):
        x_left, y = component['location']['x_left'], component['location']['y_top']
        bboxes = []
        if component['already_printed']:
            raise NotImplementedError
            # Experimental Implementation:
            width, height = component['dims']['width'], component['dims']['height']
            text = component['text']
            lines = text.split('\n')
            h = height // len(lines)
            # font = ImageFont.truetype(self.default_fonts[component['lang']].path, h)
            # space_width, h = img_draw.textsize(' ', font=font)
            for row_num, line in enumerate(lines):
                x, char_index = x_left, 0
                # Assumes an equal width font for all characters. What else can I do
                unit_width = width / float(line.count(' ')/2 + len(line.replace(' ', '')))
                space_width = int(unit_width/2)
                for col_num, word in enumerate(line.split()):
                    w = int(unit_width * len(word) + 0.99)
                    # w, h = img_draw.textsize(word, font=font)
                    self.DEBUG and img_draw.rectangle([(x,y), (x+w+1, y+h+1)], outline='rgb(255,0,0)')
                    bboxes.append({
                        'type': component['type'],
                        'label': '%s--%d_%d' % (component['id'], row_num, col_num),
                        'entity': component['entity'],
                        'points': [ # Clock-wise
                            [x+1, y+1], # Left Top
                            [x+w+1, y+1], # Right Top
                            [x+w+1, y+h+1], # Right Bottom
                            [x+1, y+h+1] # Left bottom
                        ],
                        'width': w,
                        'height': h,
                        'text': word,
                        'lang': component['lang']
                    })
                    
                    char_index += len(word)
                    x += w
                    while char_index < len(line) and line[char_index] == ' ':
                        x += space_width
                        char_index += 1
                y += height
                x = x_left
            
        else:
            align = component["align"] if "align" in component else "left"
            spacing = component["spacing"] if "spacing" in component else 4
            text = component['generator'].generate()
            component['last_generated'] = text
            text = component['post_processor'].process(text)
            space_width, height  = img_draw.textsize(' ', font=component['font'])
            for row_num, line in enumerate(text.split('\n')):
                x, char_index = x_left, 0
                for col_num, word in enumerate(line.split()):
                    img_draw.text((x, y), word, fill=component['font_color'], font=component['font'], align=align, spacing=spacing)
                    w, h  = img_draw.textsize(word, font=component['font'])
                    self.DEBUG and img_draw.rectangle([(x,y), (x+w+1, y+h+1)], outline='rgb(255,0,0)')
                    if h > height: # Variable-height fonts
                        height = h
                    bboxes.append({
                        'type': component['type'],
                        'label': '%s--%d_%d' % (component['id'], row_num, col_num),
                        'entity': component['entity'],
                        'points': [ # Clock-wise
                            [x+1, y+1], # Left Top
                            [x+w+1, y+1], # Right Top
                            [x+w+1, y+h+1], # Right Bottom
                            [x+1, y+h+1] # Left bottom
                        ],
                        'width': w,
                        'height': h,
                        'text': word,
                        'lang': component['lang']
                    })
                    
                    char_index += len(word)
                    x += w
                    while char_index < len(line) and line[char_index] == ' ':
                        x += space_width
                        char_index += 1
                
                y += height
                x = x_left
        
        return bboxes
    
    def draw_img(self, background, component):
        x, y = component['location']['x_left'], component['location']['y_top']
        width, height = component['dims']['width'], component['dims']['height']
        if not component['already_printed']:
            img, details = component['generator'].generate()
            background.paste(img, (x, y))
        
        return {
            'type': component['type'],
            'label': component['id'],
            'mode': component['filler_mode'],
            'details': details,
            'points': [ # Clock-wise
                [x+1, y+1], # Left Top
                [x+width+1, y+1], # Right Top
                [x+width+1, y+height+1], # Right Bottom
                [x+1, y+height+1] # Left bottom
            ],
            'width': width,
            'height': height,
        }
    
