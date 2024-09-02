from dataclasses import dataclass, field

import pygame
import pygame_gui
from typing import Union, Dict, Optional, Iterator
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface, IUIElementInterface
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIContainerInterface

from pygame_gui.core import UIElement, UIContainer
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape

from pygame_gui.core.gui_type_hints import Coordinate, RectLike
from parameters import Parameters

MARGIN = 4
ADJUSTMENT = 5
LABEL_HEIGHT = 35
SLIDER_HEIGHT = 35
VALUE_WIDTH = 50

@dataclass
class Entry:
  param_name: str
  param_type: str
  slider: UIElement
  label_textbox: UIElement
  value_textbox: UIElement

class SliderPanel(pygame_gui.elements.UIPanel):
  def __init__(
      self, 
      parameters: Parameters,
      relative_rect: RectLike,
      manager: Optional[IUIManagerInterface] = None,
      *,
      element_id: str = 'panel',
      container: Optional[IContainerLikeInterface] = None,
      parent_element: Optional[UIElement] = None,
      object_id: Optional[Union[ObjectID, str]] = None,
      anchors: Optional[Dict[str, Union[str, UIElement]]] = None,
      visible: int = 1
    ):
    super().__init__(
      relative_rect=relative_rect,
      manager=manager,
      container=container,
      anchors=anchors,
      visible=visible,
      parent_element=parent_element,
      object_id=object_id,
      element_id=element_id)
    self._parameters: Parameters = parameters
    self._param_name_to_entry: Dict[str, Entry] = {}
    self._ui_element_to_entry: Dict[UIElement, Entry] = {}
    self._curr_y = MARGIN
  
  def add_slider(self, param_name, param_type, label, value_range, click_increment):
    label_textbox = pygame_gui.elements.ui_text_box.UITextBox(
      label,
      container=self,
      relative_rect=pygame.Rect((MARGIN, self._curr_y), (self.relative_rect.width - MARGIN * 2 - 1, LABEL_HEIGHT)),
      #anchors={'left': 'left', 'right': 'right'},
      manager=self.ui_manager,
      plain_text_display_only=True,
      object_id=ObjectID(class_id='@label'),
    )
    slider = pygame_gui.elements.ui_horizontal_slider.UIHorizontalSlider(
      container=self,
      relative_rect=pygame.Rect((MARGIN, self._curr_y + LABEL_HEIGHT - ADJUSTMENT), (self.relative_rect.width - MARGIN * 2 - VALUE_WIDTH + ADJUSTMENT, SLIDER_HEIGHT)),
      start_value=self._parameters[param_name], value_range=value_range, click_increment=click_increment,
      manager=self.ui_manager)
    value_textbox = pygame_gui.elements.ui_text_box.UITextBox(
      self._format_value(self._parameters[param_name], param_type),
      container=self,
      relative_rect=pygame.Rect((self.relative_rect.width - MARGIN - VALUE_WIDTH - 1, self._curr_y + LABEL_HEIGHT - ADJUSTMENT), (VALUE_WIDTH, SLIDER_HEIGHT)),
      manager=self.ui_manager,
      plain_text_display_only=True,
      object_id=ObjectID(class_id='@value'),
    )

    entry = Entry(
      param_name=param_name,
      param_type=param_type,
      slider=slider,
      label_textbox=label_textbox,
      value_textbox=value_textbox)
    self._param_name_to_entry[param_name] = entry
    self._ui_element_to_entry[slider] = entry
    self._curr_y += LABEL_HEIGHT + SLIDER_HEIGHT - ADJUSTMENT

  def process_events(self, event:pygame.event.Event):
    if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
      entry: Entry = self._ui_element_to_entry[event.dict['ui_element']]
      if entry:
        value = entry.slider.get_current_value()
        self._parameters[entry.param_name] = value
        entry.value_textbox.set_text(self._format_value(value, entry.param_type))

  def _format_value(self, param_value, param_type):
    if param_type == 'float':
      return f"{param_value:.2f}"
    elif param_type == 'int':
      return f"{param_value}"
    return ""