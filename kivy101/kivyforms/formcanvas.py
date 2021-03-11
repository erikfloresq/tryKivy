from kivy.graphics import Color, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout


"""
Some common methods
"""
def get_form_canvas(widget):
    parent = widget.parent
    while parent and not isinstance(parent, FormCanvas):
        if parent is parent.parent:
            raise Exception("Infinite loop when searching FormCanvas")
        parent = parent.parent
    return parent

def get_index(widget):
    for idx in range(len(widget.parent.children)):
        if widget.parent.children[idx] is widget:
            return idx
    return None

def get_zone(widget, x, y):
    side = widget.x + widget.width / 4
    if x > side * 3:
        return 'right'
    elif x < side:
        return 'left'
    elif y > widget.y + widget.height / 2:
        return 'top'
    else:
        return 'bottom'


class Destination(Label):
    def __init__(self, **kwargs):
        super(Destination, self).__init__(**kwargs)
        self.text = 'Widget goes here'
        self.color = [1, 1, 0, 1]
        with self.canvas.after:
            Color(1, 1, 0, 1)
            self.box = Line(dash_length=8, dash_offset=4)

    def update_box(self):
        self.box.points = [
            self.x, self.y,
            self.x, self.y + self.height,
            self.x + self.width, self.y + self.height,
            self.x + self.width, self.y,
            self.x, self.y
        ]

    def on_pos(self, instance, value):
        self.update_box()

    def on_size(self, instance, value):
        self.update_box()


class Grabbable(BoxLayout):
    def __init__(self, **kwargs):
        super(Grabbable, self).__init__(**kwargs)
        self.detached = False

    def point(self, touch):
        get_form_canvas(self).point_widget(self, touch.pos)

    def detach(self):
        self.detached = True
        get_form_canvas(self).detach_widget(self)

    def attach(self, touch):
        if self.detached:
            form_canvas = None
            for widget in self.get_root_window().children[1].walk():
                if isinstance(widget, FormCanvas) and widget.collide_point(*touch.pos):
                    form_canvas = widget
                    break
            else:
                raise Exception("FormCanvas not found")
            form_canvas.attach_widget(self)
            self.detached = False

    def move(self, x, y):
        self.pos = [x - self.width / 2, y - self.height / 2]
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.grab_current is None:
                touch.grab(self)
                self.detach()
                self.move(*touch.pos)
                return True
        return super(Grabbable, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.move(*touch.pos)
        else:
            if self.parent and self.parent != self.get_root_window():
                if self.collide_point(touch.x, touch.y):
                    self.point(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.attach(touch)
            

class FormCanvas(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(FormCanvas, self).__init__(*args, **kwargs)

        self._canvas = StackLayout(
            orientation='lr-tb',
            padding=[10, 10, 10, 10],
            spacing=[10, 10]
        )
        super(FormCanvas, self).add_widget(self._canvas)

        self.widgets_height = 40
        self.widgets_size_hint = (1, None)

    def add_widget(self, widget):
        g = Grabbable(
            height=self.widgets_height,
            size_hint=self.widgets_size_hint
        )
        widget.height = self.widgets_height
        widget.size_hint = self.widgets_size_hint
        g.add_widget(widget)
        self._canvas.add_widget(g)

    def detach_widget(self, widget):
        "Detach grabbable widget from canvas and show widget destination"

        # Show widget destination
        self.destination = Destination()
        self.destination.height = self.widgets_height
        self.destination.size_hint = self.widgets_size_hint
        widget.parent.add_widget(self.destination, index=get_index(widget))

        # Place widget in the root window
        widget.parent.remove_widget(widget)
        widget.size_hint = (None, None)
        widget.width = 150
        widget.height = 50
        self.get_root_window().add_widget(widget)

    def point_widget(self, widget, position):
        if not self.destination:
            raise Exception("Wrong status: destination point not specified")

        # Widget info about destination
        widget_idx = get_index(widget)
        zone = get_zone(widget, *position)

        # Remove destination
        box = self.destination.parent
        box.remove_widget(self.destination)

        # Put destination in the right place
        if zone in ('left', 'right') and widget.parent.orientation != 'horizontal':
            parent = widget.parent
            box = self.create_box()
            parent.add_widget(box, index=widget_idx)
            parent.remove_widget(widget)
            box.add_widget(widget)
            if zone == 'left':
                box.add_widget(self.destination, index=1)
            else:
                box.add_widget(self.destination, index=0)
        else:
            widget.parent.add_widget(self.destination, index=widget_idx)

        # Remove useless boxes
        if isinstance(box, BoxLayout) and len(box.children) == 1:
            child = box.children[0]
            box.remove_widget(child)
            box.parent.add_widget(child, index=get_index(box))
            box.parent.remove_widget(box)

    def attach_widget(self, widget):
        """
        Attach grabbable widget to the destination
        """
        widget.parent.remove_widget(widget)
        widget.height = self.widgets_height
        widget.size_hint = self.widgets_size_hint

        dest_idx = get_index(self.destination)
        self.destination.parent.add_widget(widget, index=dest_idx)
        self.destination.parent.remove_widget(self.destination)
        self.destination = None

    def create_box(self):
        return BoxLayout(
            orientation='horizontal',
            height=self.widgets_height,
            size_hint=self.widgets_size_hint,
            spacing=self._canvas.spacing[0]
        )

    def export_to_kv(self):
        kv = """StackLayout:
    orientation: '{orientation}'
    padding: {padding}
    spacing: {spacing}
""".format(orientation=self._canvas.orientation, padding=self._canvas.padding, spacing=self._canvas.spacing)

        indent = '    '
        stack = [self._canvas]

        widgets = self.walk(restrict=True)
        next(widgets)    # the first widget is the FormCanvas
        next(widgets)    # and the second is the inner StackLayout
        for widget in widgets:
            if not isinstance(widget, Grabbable):
                # Look for the widget position inside the tree
                parent = widget.parent
                if isinstance(parent, Grabbable):
                    parent = parent.parent
                while not parent is stack[-1]:
                    stack.pop()

                # Widget header
                kv += '{indent}{widget}:\n'.format(indent=indent*len(stack), widget=type(widget).__name__)

                stack.append(widget)

                # Widget attributes
                for attr in ('height', 'size_hint', 'text', 'spacing'):
                    if hasattr(widget, attr):
                        value = getattr(widget, attr)
                        if type(value) is str:
                            value = "'" + value + "'"
                        kv += "{indent}{attr}: {value}\n".format(
                            indent=indent*len(stack),
                            attr=attr,
                            value=value
                        )

        return kv
