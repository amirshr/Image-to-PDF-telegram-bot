class ImageToPdf:
    def __init__(self, imgs, path):
        self.images = []
        self.path = path

        for im in imgs:
            try:
                im = im.convert('RBG')
            except:
                pass
            self.images.append(im)

    def convert(self):
        self.images[0].save(self.path +'/converted.pdf', save_all=True, append_images=self.images[1:])
