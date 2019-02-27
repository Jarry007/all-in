from PIL import Image
"""
def compression_img(data):
    size= (120,120)
    im = Image.open(data)
    im.thumbnail(size)
    print(im.format)
    im.save('out.png', 'PNG')
    print(im.format)

if __name__ =="__main__":
    img = 'D://flask1/apps/static/img/ad.jpg'
    compression_img(img)
"""
from qqwry import QQwry
def query(ip):
    q = QQwry()
    q.load_file('D://flask1/apps/static/qqwry.dat',loadindex=False)
    result = q.lookup(ip)
    print(result)
if __name__ == '__main__':
    while True:
        ip = input(':')
        query(ip)


