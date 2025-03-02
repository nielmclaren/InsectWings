import glob

import pygame

class ScreenCapturer:
    def __init__(self, filename_prefix:str, filename_suffix:str):
        self._prefix:str = filename_prefix
        self._suffix:str = filename_suffix
        self._index:int = self._get_index()
    
    def capture(self, surf:pygame.Surface) -> str:
        index = self._index
        self._index += 1

        filename = self._get_filename(index)
        pygame.image.save(surf, filename)

        return filename

    def _get_index(self) -> int:
        existing = glob.glob(f"{self._prefix}*{self._suffix}")

        # Counting down handles case where a screenshot in the middle has been deleted.
        index = 999
        while index >= 0 and self._get_filename(index) not in existing:
            index -= 1
        return index + 1
    
    def _get_filename(self, index:int) -> str:
        return f"{self._prefix}{str(index).zfill(3)}{self._suffix}"
