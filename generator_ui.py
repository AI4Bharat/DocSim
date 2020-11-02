import streamlit as st
import os
import json

TEMPLATES_FOLDER = 'templates'
TEMPLATE_FILE = 'template.json'
OUTPUT_FOLDER = 'output/server'

@st.cache
def get_template_names():
    from glob import glob
    TEMPLATES_PATTERN = os.path.join('**', TEMPLATE_FILE)
    templates = glob(TEMPLATES_PATTERN, recursive=True)
    return [template.replace('\\', '/').replace(TEMPLATE_FILE, '').replace(TEMPLATES_FOLDER, '').strip('/') for template in templates]

@st.cache
def read_template(template_name):
    template_path = os.path.join(TEMPLATES_FOLDER, template_name, TEMPLATE_FILE)
    with open(template_path, encoding='utf-8') as f:
        template_json = json.load(f)
    fields = [component_name for component_name, component in template_json['components'].items() if component['type']=='text']
    return template_json, fields

from docsim.generator import Generator
from copy import deepcopy
def generate_doc(template_json, field_values):
    template = deepcopy(template_json)
    for field, value in field_values.items():
        if not value:
            continue
        
        template['components'][field]['filler_mode'] = 'fixed'
        template['components'][field]['filler_text'] = value
    return Generator(template).generate_sample(OUTPUT_FOLDER)

import base64
def get_binary_file_downloader_html(bin_file, file_label='File'):
    '''Utility Function to generate HTML code
    for Downloader button'''
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    
    # Style courtesy: fabriziovanmarciano.com/button-styles/
    custom_css = f""" 
        <style>
        .dl_button_cont {{
        margin-top: 5px;
        margin-bottom: 5px;
        }}
        .dl_button {{
        color: #494949 !important;
        text-transform: uppercase;
        text-decoration: none;
        background: #ffffff;
        padding: 5px;
        border: 2px solid #494949 !important;
        display: inline-block;
        transition: all 0.4s ease 0s;
        }}
        .dl_button:hover {{
        color: #ffffff !important;
        background: #f6b93b;
        border-color: #f6b93b !important;
        transition: all 0.4s ease 0s;
        text-decoration: none;
        }}
        </style>
    """
    href = custom_css + f'''<div align="center" class="dl_button_cont">
    <a href="data:application/octet-stream;base64,{bin_str}" class="dl_button" download="{os.path.basename(bin_file)}">Download {file_label}</a>
    </div>'''
    return href

def show_ui():
    st.title('DocSim - Document Generator UI')
    
    st.sidebar.title('Settings')
    template_name = st.sidebar.selectbox('Select template:', get_template_names())

    template_json, fields = read_template(template_name)

    field_values = {}
    for field in fields:
        field_values[field] = st.text_input(field)

    st.markdown('**Note:**')
    st.text('Empty fields will be randomly filled during generation')

    start_generation = st.button('Generate!')
    if start_generation:
        output_file = generate_doc(template_json, field_values)
        st.image(output_file+'.jpg', use_column_width=True)
        st.markdown(get_binary_file_downloader_html(output_file+'.json', 'Output JSON'), unsafe_allow_html=True)
        st.markdown(get_binary_file_downloader_html(output_file+'.jpg', 'Output Image'), unsafe_allow_html=True)

show_ui()
