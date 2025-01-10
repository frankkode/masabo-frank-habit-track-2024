from django.core.management.base import BaseCommand
import cloudinary.uploader
import os
from django.conf import settings

class Command(BaseCommand):  # Make sure it's named exactly 'Command'
    help = 'Upload images from media/docs/images to Cloudinary'

    def handle(self, *args, **options):  # Use **options instead of **kwargs
        # Get the absolute path of the project
        BASE_DIR = settings.BASE_DIR
        
        # Print paths for debugging
        image_dir = os.path.join(BASE_DIR, 'habits', 'static', 'docs', 'images')
        self.stdout.write(f"Looking for images in: {image_dir}")
        
        # Check if directory exists
        if not os.path.exists(image_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {image_dir}'))
            return

        # List all files in directory
        for filename in os.listdir(image_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_path = os.path.join(image_dir, filename)
                
                try:
                    result = cloudinary.uploader.upload(
                        file_path,
                        folder='docs/images',
                        use_filename=True,
                        unique_filename=False
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully uploaded {filename} to Cloudinary')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to upload {filename}: {str(e)}')
                    )