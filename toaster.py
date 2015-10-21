# 27/5/15


__all__ = ('toast', )


from kivy.core.window import Window
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.label import Label


Builder.load_string("""
<ToastWidget>:
    canvas.before:
        Color:
            rgba: .1,.1,.1,.92
        Rectangle:
            pos: self.pos
            size: self.size
""")


class ToastWidget(Label):
    def __init__(self, *ar, **kw):
        super(ToastWidget, self).__init__(*ar, **kw)

        Window.bind(size=self._update)
        self.size_hint = (None, None)
        self.height = '35dp'

    def start(self):
        self._update()
        Window.add_widget(self)

    def _update(self, *ar):
        self.center_x = Window.width / 2.
        self.y = '20dp'

        if self.width > Window.width:
            self.width = Window.width


def toast(message, duration=1.2, width='175dp', **kw):
    # TODO: if currently toasting, queue the toast
    # TODO: if the message is too wide, split it into multiple queued toasts

    toast_wid = ToastWidget(text=message,
                            opacity=0.0,
                            width=width,
                            **kw)

    anim = Animation(opacity=1.0,
                     duration=.3) + \
        Animation(opacity=1.0,
                  duration=duration) + \
        Animation(opacity=0.0,
                  duration=0.2)

    toast_wid.start()
    anim.start(toast_wid)


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.button import Button

    but = Button(text='toast!')
    but.bind(on_release=lambda *ar: toast("I'm toast!"))

    runTouchApp(but)
