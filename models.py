import os

from django.db import models

from wagtail.wagtailcore.models import Page
from django.core.files.images import ImageFile
from wagtail.wagtailimages.models import Image
from wagtail.wagtailcore.models import Collection, GroupCollectionPermission
from wagtail.wagtailadmin.edit_handlers import FieldPanel, DocumentChooserPanel


class GalleryPage(Page):
    # test
    root_coll = Collection.get_first_root_node()
    root_coll.add_child(name='testcoll')

    collection_name = models.CharField(max_length=250)
    image_dir = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )  # how to point to a directory?
    # how to include a button???

    content_panels = Page.content_panels + [
        FieldPanel('collection_name'),
        DocumentChooserPanel('image_dir'),
        Button(_on_button_press)  # ???
    ]

    def _on_button_press(self):
        self.imgs = self.get_image_files()
        self.create_collection()
        self.save_images_to_cms()

    def create_collection(self):
        root_coll = Collection.get_first_root_node()
        root_coll.add_child(name=self.collection_name)

    def get_image_files(self, exts=['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG']):
        '''Find images within the img_dir location.'''
        imgs = []
        if not os.isdir(self.img_dir):
            # raise exception ??
            return imgs
        for root, dirs, files in os.walk(self.img_dir):
            for fil in files:
                if os.path.splitext(fil)[1] in exts:
                    img_path = os.path.abspath(os.path.join(root, fil))
                    dir_name = os.path.split(os.path.dirname(img_path))[1]  # tag
                    img_name = os.path.splitext(os.path.basename(img_path))[0]  # title
                    imgs += [(img_path, dir_name, img_name)]
        return imgs

    def save_images_to_cms(self):
        '''Save images to the database with:
        - title: the file name
        - tags: the directory containing the image'''

        for img_path, dirname, img_name in self.imgs:
            image = Image(title=img_name,
                          file=ImageFile(open(img_path, "rb"), name=os.path.basename(img_path)),
                          tags=img_name)  # is this correct??
            image.save()
            # how to add image to collection??
