from PIL import Image, ImageDraw

class Image:
    def __init__(self, width, height, brightness, imgPath):
        self.brightness = 1
        self.width = width
        self.height = height
        self.imgPath = imgPath
    
    def updateBrightness(self, brightness):
        enhancer = ImageEnhance.Brightness(self.imageObject)
        im = enhancer.enhance(self.brightness)
        self.imageObject = im
        return im

    def draw(self):
        imgObject = Image.open(self.imgPath)
        img = ImageDraw.Draw(imgObject)

        enhancer = ImageEnhance.Brightness(img)
        im = enhancer.enhance(self.brightness)
        self.imageObject = im
        return im
