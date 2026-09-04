"""
Generate beautiful trial flowcharts for PsychoPy tasks.
"""

from dataclasses import dataclass
from collections.abc import Callable
import os
import math

from PIL import Image, ImageDraw, ImageFont

from .experiment import Base


@dataclass
class Scene:
    fnction:     Callable
    label:       str
    description: str


class Flowchart:

    SCENE_SIZE = (160, 120)

    def __init__(self, task: Base):
        """
        Initialize Flowchart object. Takes task argument.
        """
        self.task = task
        self.scenes: list[Scene] = []

    def add_scenes(self, scenes: list[Scene]):
        """
        Set list of scenes.
        """
        self.scenes = scenes

    def _generate_scene_images(self):
        """
        Run each scene, takes screenshot of the window.
        Return list of scenes as PIL images.
        Is not to be called directly, called in generate().
        """
        scene_images = []
        for scene in self.scenes:
            scene.fnction()
            self.task.win.getMovieFrame() 
            filename = f"{scene.label}.png"
            self.task.win.saveMovieFrames(filename)
            image = Image.open(filename)
            resized = image.resize(self.SCENE_SIZE, Image.Resampling.LANCZOS)
            scene_images.append(resized)
            os.remove(filename)
        return scene_images

    def generate(self, out_path: str):
        """
        Generate flowchart. Takes out_path argument.
        """
        images = self._generate_scene_images()
        len_images = len(images)
        if len_images < 1: return

        # parameters
        margin = 15
        overlap_left = 40
        overlap_top = 80
        img_w, img_h = self.SCENE_SIZE
        step_x = img_w - overlap_left
        step_y = img_h - overlap_top
        font_size = 16
        text_gap = 4

        # calculate output dimensions
        width = margin + (step_x * (len_images - 1)) + img_w + margin
        height = margin + (step_y * (len_images - 1)) + img_h + text_gap + font_size + margin

        # set up image
        canvas = Image.new("RGBA", (width, height), color="white")
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.load_default(size=font_size)
        except IOError:
            font = ImageFont.load_default(size=font_size)

        # draw each scene
        current_x = margin
        current_y = margin

        for i, img in enumerate(images):
            label_text = self.scenes[i].description
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                canvas.paste(img, (current_x, current_y), mask=img)
            else:
                canvas.paste(img, (current_x, current_y))
        
                text_bbox = draw.textbbox((0, 0), label_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                if i < len_images - 1:
                    text_x = (current_x + step_x) - text_width - text_gap
                else:
                    text_x = (current_x + img_w) - text_width
                text_x -= 5
                text_y = current_y + img_h + text_gap
    
                draw.text((text_x, text_y), label_text, fill="black", font=font)

            current_x += step_x
            current_y += step_y

        # draw arrow
        arrow_base_x = width*.15
        arrow_base_y = height*.7

        arrow_length = self.SCENE_SIZE[0]*.8
        arrow_slope = (height*.8)/width
        line_width = 2

        arrow_angle = math.atan(arrow_slope)

        arrow_end_x = arrow_base_x + (arrow_length * math.cos(arrow_angle))
        arrow_end_y = arrow_base_y + (arrow_length * math.sin(arrow_angle))

        draw.line([(arrow_base_x, arrow_base_y), (arrow_end_x, arrow_end_y)],
                   fill="black", width=line_width)

        head_wing_length = 10
        head_spread_angle = math.radians(20)

        left_wing_x = arrow_end_x - head_wing_length * math.cos(arrow_angle - head_spread_angle)
        left_wing_y = arrow_end_y - head_wing_length * math.sin(arrow_angle - head_spread_angle)

        right_wing_x = arrow_end_x - head_wing_length * math.cos(arrow_angle + head_spread_angle)
        right_wing_y = arrow_end_y - head_wing_length * math.sin(arrow_angle + head_spread_angle)

        draw.polygon([(arrow_end_x, arrow_end_y), (left_wing_x, left_wing_y),
             (right_wing_x, right_wing_y)], fill="black")

        # save flowchart image
        canvas.save(os.path.abspath(out_path))
