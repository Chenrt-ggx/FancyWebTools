import io
from PIL import Image
from ddddocr import DdddOcr


def matrix_for_each(x, y):
    result = []
    for i in x:
        for j in y:
            result.append((i, j))
    return result


def de_noise(img, white, limit=0.75, total=5):
    for _ in range(total):
        for i, j in matrix_for_each(range(img.width), range(img.height)):
            px = img.getpixel((i, j))
            if px == white:
                continue
            count, select = 0, 0
            for x, y in matrix_for_each([-1, 0, 1], [-1, 0, 1]):
                ni, nj = i + x, j + y
                if 0 <= ni < img.width and 0 <= nj < img.height:
                    count += 1
                    if img.getpixel((ni, nj)) == white:
                        select += 1
            if select / count > limit:
                img.putpixel((i, j), white)
    return img


def do_ocr(data):
    buf = io.BytesIO()
    de_noise(Image.open(io.BytesIO(data)), (250, 250, 250)).save(buf, format='PNG')
    return DdddOcr().classification(buf.getvalue())
