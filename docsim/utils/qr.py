import qrcode
import random
import string 

def get_qr_img(min_v=3, max_v=7, data=None):
    version = random.randint(min_v, max_v)
    qr = qrcode.QRCode(version=version, border=0)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def get_rand_string(min_l=10, max_l=20):
    length = random.randint(min_l, max_l)
    return ''.join(random.choice(string.ascii_lowercase +string.ascii_uppercase + string.digits)
                         for i in range(length))
