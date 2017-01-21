from media import Media, MediaObject

'''
https://wiki.gnome.org/Projects/gexiv2
'''

class ImageManager(object):
    def __init__(self, *args, **kwargs):
        self.media = None
        return super(ImageManager, self).__init__(*args, **kwargs)
        
    def start(self):
        if self.media:
            return

        self.media = Media(self.path, "image")
        self.media.start_cron(callback=self.scan_callback)

    def stop(self):
        if not self.media:
            return

        self.media.stop_cron()
        self.media = None

    def scan_callback(self, imagelist):
        newimages = self.get_newimages(imagelist)

        for image in newimages:
            prop = get_image_property(image)
            self.update_imagedb(image, prop)

    def get_newimages(self):
        pass

    def update_imagedb(self, image, prop):
        pass
