"""
10-19-15
"""


from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty
from kivy.lang import Builder


class Arrow(Widget):
    start = ObjectProperty(None)
    end = ObjectProperty(None, allownone=True)

    start_pos = ListProperty([0, 0])
    end_pos = ListProperty([0, 0])

    color = ListProperty([1, 1, 1, 1])
    end_color = ListProperty([1, 1, 1, 1])
    start_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kw):
        super(Arrow, self).__init__(**kw)

        self.make_rebinder(
            'start',
            {'pos': self._update_start,
             'size': self._update_start})
        self.make_rebinder(
            'end',
            {'pos': self._update_end,
             'size': self._update_end})

    # name of object (target) -> create prev (_prev_target)
    # dict of bindings:
    #   {
    #       'pos': method,
    #       ...
    #   }
    def make_rebinder(self, propname, bindings):
        """
        This method generates a method that will unbind/rebind the given
        bindings to the given property's properties when the property changes.

        Example:
            self is some kind of Widget
            propname is the name of an ObjectProperty pointing to an instance
                of a Label
        """
        # Create the previous property.
        setattr(self, '_prev_' + propname, None)

        def rebinder(self, *ar):
            # Get property and previous property.
            prop = getattr(self, propname)
            prev_prop = getattr(self, '_prev_' + propname)

            # Unbind from previous prop, if we had one.
            if prev_prop is not None:
                prev_prop.unbind(**bindings)

                # Call all the bindings, to make sure things are updated.
                for binding in bindings.values():
                    binding()

            # Bind to new property's properties, if we have a new property.
            if prop is not None:
                prop.bind(**bindings)

                # Call all the bindings, to make sure things are updated.
                for binding in bindings.values():
                    binding()

            # Set the previous property.
            setattr(self, '_prev_' + propname, prop)

        rebinder(self)
        self.bind(**{propname: rebinder})

    def _update_start(self, *ar):
        start = self.start

        if start is None:
            self.start_pos = [0, 0]
        else:
            self.start_pos[0] = start.right
            self.start_pos[1] = start.y + start.height / 2

    def _update_end(self, *ar):
        end = self.end

        if end is None:
            self.end_pos = [0, 0]
        else:
            x, y = self.end.to_window(*self.end.pos)
            # print('window', x, y)
            x, y = self.to_widget(x, y)

            self.end_pos[0] = x
            self.end_pos[1] = y + end.height / 2


Builder.load_string("""
<Arrow>:
    canvas:
        Color:
            rgba: self.color if self.end is not None else (1, 1, 1, 0)
        Line:
            points: self.start_pos[0], self.start_pos[1], self.end_pos[0], self.end_pos[1]
            width: 2
        Color:
            rgba: self.start_color if self.end is not None else (1, 1, 1, 0)
        Line:
            circle: self.start_pos[0], self.start_pos[1], 3
            width: 2
        Color:
            rgba: self.end_color if self.end is not None else (1, 1, 1, 0)
        Line:
            circle: self.end_pos[0], self.end_pos[1], 5
            width: 2

""")


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.widget import Widget
    from kivy.uix.label import Label

    b = BoxLayout(orientation='horizontal')

    w1 = Label(text='start')
    w2 = Widget()
    w3 = Label(text='end')

    a = Arrow(
        start=w1,
        end=w3
    )

    w1.add_widget(a)

    b.add_widget(w1)
    b.add_widget(w2)
    b.add_widget(w3)

    runTouchApp(b)
