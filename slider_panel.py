from dataclasses import dataclass
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.core.interfaces import IContainerLikeInterface
from pygame_gui.core import UIElement
from pygame_gui.core.gui_type_hints import RectLike
from typing import Union, Dict, Optional

from param_def import ParamDef
from param_set import ParamSet

MARGIN = 4
ADJUSTMENT = 5
LABEL_HEIGHT = 35
SLIDER_HEIGHT = 35
VALUE_WIDTH = 80

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
      parameters: ParamSet,
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
    self._parameters: ParamSet = parameters
    self._param_name_to_entry: Dict[str, Entry] = {}
    self._ui_element_to_entry: Dict[UIElement, Entry] = {}
    self._curr_y = MARGIN
  
  def set_parameters(self, params:ParamSet):
    self._parameters = params
    for _, entry in self._param_name_to_entry.items():
      value = self._parameters[entry.param_name]
      entry.slider.set_current_value(value)
      entry.value_textbox.set_text(self._format_value(value, entry.param_type))
  
  def add_slider(self, param_def:ParamDef):
    value = self._parameters[param_def.name]
    # UI Horizontal Slider uses the datatype of start_value to determine type so
    # ensure it matches the specified type.
    if param_def.type == 'int':
      value = int(value)
    elif param_def.type == 'float':
      value = float(value)

    label_textbox = pygame_gui.elements.ui_text_box.UITextBox(
      param_def.name,
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
      start_value=value, value_range=param_def.range, click_increment=param_def.step,
      manager=self.ui_manager)
    value_textbox = pygame_gui.elements.ui_text_box.UITextBox(
      self._format_value(value, param_def.type),
      container=self,
      relative_rect=pygame.Rect((self.relative_rect.width - MARGIN - VALUE_WIDTH - 1, self._curr_y + LABEL_HEIGHT - ADJUSTMENT), (VALUE_WIDTH, SLIDER_HEIGHT)),
      manager=self.ui_manager,
      plain_text_display_only=True,
      object_id=ObjectID(class_id='@value'),
    )

    entry = Entry(
      param_name=param_def.name,
      param_type=param_def.type,
      slider=slider,
      label_textbox=label_textbox,
      value_textbox=value_textbox)
    self._param_name_to_entry[param_def.name] = entry
    self._ui_element_to_entry[slider] = entry
    self._curr_y += LABEL_HEIGHT + SLIDER_HEIGHT - ADJUSTMENT

  def process_events(self, event:pygame.event.Event, parameters_changed_callback):
    invalid = False
    if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
      entry: Entry = self._ui_element_to_entry[event.dict['ui_element']]
      if entry:
        value = entry.slider.get_current_value()
        self._parameters[entry.param_name] = value
        entry.value_textbox.set_text(self._format_value(value, entry.param_type))
        invalid = True

    if invalid:
      parameters_changed_callback()

  def _format_value(self, param_value: Union[int, float], param_type: str):
    if param_type == 'float':
      return f"{param_value:.4f}"
    elif param_type == 'int':
      return f"{param_value}"
    return ""