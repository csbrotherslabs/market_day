from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand

FOLDERS=[
'buyers/profile_images','buyers/review_images','sellers/profile_images','sellers/store_images','sellers/product_images','sellers/review_images','drivers/profile_images','drivers/delivery_proofs','qa/profile_images','qa/inspection_images','admin/profile_images','admin/action_images','reviews/buyer_reviews','reviews/seller_reviews','reviews/driver_reviews','system/placeholders']

class Command(BaseCommand):
    help='Create local media folder structure.'
    def handle(self,*args,**kwargs):
        for rel in FOLDERS:
            path=Path(settings.MEDIA_ROOT)/rel
            path.mkdir(parents=True, exist_ok=True)
            (path/'.gitkeep').touch(exist_ok=True)
        self.stdout.write(self.style.SUCCESS('Media folders created.'))
