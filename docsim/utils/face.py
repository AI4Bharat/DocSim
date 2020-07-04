import requests
import PIL
from PIL import Image
import io

def get_random_face(shape=(400,400)):
    url = 'https://thispersondoesnotexist.com/image'
    r = requests.get(url).content
    image = Image.open(io.BytesIO(r))
    image = image.resize(shape)
    return image