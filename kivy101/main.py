import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivyforms import FormCanvas


screen = Builder.load_string('''
BoxLayout:
    orientation: 'horizontal'
    FormCanvas:
        id: form_canvas
    BoxLayout:
        size_hint: 0.2, 1
        orientation: 'vertical'
        Button:
            text: 'Add button'
            on_press: app.add_button()
        Button:
            text: 'Add checkbox'
            on_press: app.add_checkbox()
        Button:
            text: 'Add label'
            on_press: app.add_label()
        Button:
            text: 'Add text input'
            on_press: app.add_textinput()
        Button:
            text: 'Add toggle button'
            on_press: app.add_togglebutton()
        Button:
            text: 'Export to Kv'
            on_press: app.export_to_kv()
''')


class DesignerApp(App):
    button_id = 0
    label_id = 0
    togglebutton_id = 0

    def on_start(self):
        self.form_canvas = self.root.ids.form_canvas

    def add_button(self):
        self.button_id += 1
        self.form_canvas.add_widget(Button(text='Button ' + str(self.button_id)))

    def add_checkbox(self):
        self.form_canvas.add_widget(CheckBox())

    def add_label(self):
        self.label_id += 1
        self.form_canvas.add_widget(Label(text='Label ' + str(self.label_id)))

    def add_textinput(self):
        self.form_canvas.add_widget(TextInput())

    def add_togglebutton(self):
        self.togglebutton_id += 1
        self.form_canvas.add_widget(ToggleButton(text='Toggle Button ' + str(self.togglebutton_id)))

    def export_to_kv(self):
        print(self.form_canvas.export_to_kv())

    def build(self):
        return screen


if __name__ == '__main__':
    app = DesignerApp()
    app.run()

