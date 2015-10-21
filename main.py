"""
10-15-15
"""


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.clock import Clock
from kivy.lang import Builder


from work import load_csv_as_dict, save_dict_as_csv
from toaster import toast
from arrow import Arrow


class ColoredLabel(Label):
    pass


class FieldWidget(Label):
    name = StringProperty()


Builder.load_string("""
<FieldWidget>:
    text: self.name

    size_hint_y: None
    height: '52sp'
    font_size: '14sp'

    text_size: self.size
    halign: 'left'
    valign: 'middle'
    padding_x: '5dp'

    color: .2, .2, .2, 1

    canvas.before:
        Color:
            rgba: 1, 1, 1, .86
        Rectangle:
            pos: self.x, self.y + 1
            size: self.width, self.height - 1
""")


class InField(FieldWidget):
    dest = ObjectProperty(None, allownone=True)

    arrow = ObjectProperty(None)

    in_idx = NumericProperty(0)

    def __init__(self, dest_manager, **kw):
        super(InField, self).__init__(**kw)

        self.dest_manager = dest_manager
        self.arrow = Arrow(start=self)
        self.add_widget(self.arrow)

    def on_dest(self, *ar):
        """
        Automatically update the arrow and other things...
        """
        self.arrow.end = self.dest

    def set_dest(self, dest_name):
        self.dest_manager.set_src(dest_name, self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            app = App.get_running_app()
            cmd_box = app.root.ids['cmd_box']\

            if cmd_box.text == '':
                cmd_box.text = 'h {}.{} -> '.format(self.in_idx, self.name)
                Clock.schedule_once(
                    lambda *ar: setattr(app.root.ids['cmd_box'], 'focus', True),
                    0.1)
            else:
                cmd_box.text += self.name
                cmd_box.dispatch('on_text_validate')


class OutField(FieldWidget):
    src = ObjectProperty(None)
    src_name = StringProperty()

    def __init__(self, dest_manager, **kw):
        super(OutField, self).__init__(**kw)

        self.dest_manager = dest_manager

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            app = App.get_running_app()
            cmd_box = app.root.ids['cmd_box']\

            if cmd_box.text == '':
                cmd_box.text = 'u {}'.format(self.src_name)
                cmd_box.dispatch('on_text_validate')
            else:
                cmd_box.text += self.src_name
                cmd_box.dispatch('on_text_validate')


class DestManager(GridLayout):
    def __init__(self, **kw):
        super(DestManager, self).__init__(**kw)
        self.cols = 1

        self.dests = {}

    def create_dest(self, name, src):
        # Delete dest if already have it.
        if src.name in self.dests:
            old_dest = self.dests[src.name]

            if old_dest.src is not None:
                old_dest.src.dest = None

            self.remove_widget(old_dest)
            del self.dests[src.name]

        new_dest = OutField(self, name=name, src=src)
        self.add_widget(new_dest)
        self.dests[src.name] = new_dest

        return new_dest

    def set_src(self, dest_name, src):
        if src is None:
            if dest_name in self.dests:
                dest = self.dests[dest_name]

                if dest.src is not None:
                    dest.src.dest = None

                self.remove_widget(dest)
                del self.dests[dest_name]
        else:
            dest = self.create_dest(dest_name, src)
            src.dest = dest

        self._sort()

    def _sort(self):
        children = self.children[:]
        children.sort(key=lambda a: (a.src.in_idx, a.src.name))
        self.clear_widgets()

        for c in children:
            self.add_widget(c)


Builder.load_string("""
<DestManager>:
    spacing: '5dp'
    padding: '5dp'
""")


class SrcManager(GridLayout):
    def __init__(self, **kw):
        super(SrcManager, self).__init__(**kw)
        self.cols = 1

    def find_src(self, src_name):
        for c in self.children:
            if hasattr(c, 'name') and c.name == src_name:
                return c

        return None


Builder.load_string("""
<SrcManager>:
    height: self.minimum_height
    size_hint_y: None
    spacing: '5dp'
    padding: '5dp'
""")


class AppRoot(BoxLayout):
    pass


class MergeCSVApp(App):
    in_files = ListProperty([])
    in_dicts = ListProperty([])

    def build(self):
        self.root = AppRoot()
        return self.root

    def set_files(self, *ar):
        self.in_files = ar

    def on_in_files(self, *ar):
        """
        Rebuild the inputs and the output.
        """
        self.in_dicts = [load_csv_as_dict(f) for f in self.in_files]

        self._build_inputs(self.in_dicts, self.in_files)
        self._auto_build_dests()

    def create_out_dict(self):
        pass

    def _build_inputs(self, in_dicts, fnames):
        self.root.ids['in_files'].clear_widgets()
        self.srcs = {}
        dm = self.root.ids['dest_fields']

        n = 0
        for in_d, fname in zip(in_dicts, fnames):
            l = SrcManager()

            text = '{} - {} ({} lines)'.format(n, fname, len(in_d.values()[0]))
            self.root.ids['in_files'].add_widget(
                ColoredLabel(
                    text=text,
                    size_hint_y=None,
                    height='20dp',
                    bold=True,
                    shorten=True,
                )
            )

            names = in_d.keys()
            names.sort()
            for name in names:
                l.add_widget(InField(dm, name=name, in_idx=n))

            self.root.ids['in_files'].add_widget(l)
            self.srcs[n] = l
            n += 1

    def _auto_build_dests(self):
        dm = self.root.ids['dest_fields']

        for src_man in self.root.ids['in_files'].children:
            for src in src_man.children[::-1]:
                src.set_dest(src.name)

    def do_command(self, cmd):
        if len(cmd) < 1:
            toast('empty command')
            return

        def sel_and_focus(*ar):
            self.root.ids.cmd_box.focus = True
            self.root.ids.cmd_box.select_all()

        def err(m='unknown command or invalid syntax'):
            toast(m, width='275dp')
            Clock.schedule_once(sel_and_focus, .1)

        if cmd[0] == 'h':
            # hook
            spl = cmd.split(' ')

            if len(spl) < 4:
                err()
                return

            src = spl[1]
            dest = spl[3]

            if len(src) < 3 or src[1] != '.':
                err()
                return

            fidx = int(src[0])
            sname = src[2:]

            src = self.srcs[fidx].find_src(sname)

            if src is None:
                err(m="input {} has no field {}".format(fidx, sname))
                return

            src.set_dest(dest)

        elif cmd[0] == 'u':
            # unhook
            spl = cmd.split(' ')

            if len(spl) < 2:
                err()
                return

            dest = spl[1]

            if dest not in self.root.ids['dest_fields'].dests:
                err()
                return

            self.root.ids['dest_fields'].set_src(dest, None)

        else:
            err()
            return

        if self.root.ids.record_cmds.active:
            self.root.ids.cmd_box.recorded += self.root.ids.cmd_box.text

        # Reset the text on a successful command.
        self.root.ids.cmd_box.text = ''
        Clock.schedule_once(
            lambda *ar: \
                setattr(self.root.ids.cmd_box, 'focus', True), .1)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('f1')
    parser.add_argument('f2')

    args = parser.parse_args()

    app = MergeCSVApp()
    Clock.schedule_once(lambda *ar: app.set_files(args.f1, args.f2), 1)
    app.run()
