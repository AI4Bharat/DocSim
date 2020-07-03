import qrcode
import random

def get_qr_img(min_v=3, max_v=7, data=None):
    version = random.randint(min_v, max_v)
    qr = qrcode.QRCode(version=version, border=0)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img
