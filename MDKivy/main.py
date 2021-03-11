from kivy.lang import Builder

from kivymd.app import MDApp

KV = '''
MDBoxLayout:
    orientation: "vertical"

    MDToolbar:
        id: toolbar
        title: "Login"
        md_bg_color: 0, 0, 0, 1
    
    MDStackLayout:
        adaptive_height: False
        padding: [10, 10, 10, 10]

        MDTextField:
            id: text_field_user
            hint_text: "Username"
            helper_text: ""
            helper_text_mode: "persistent"
            pos_hint: {"center_y": .5}

        MDTextField:
            id: text_field_password
            hint_text: "Password"
            helper_text: ""
            helper_text_mode: "persistent"
            pos_hint: {"center_y": .5}

        MDFillRoundFlatButton:
            text: "Login"
'''


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)


Test().run()