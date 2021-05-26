import sublime
import sublime_plugin


class RestRequestCommand(sublime_plugin.WindowCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        print("Hi, I'm Sublime REST")
