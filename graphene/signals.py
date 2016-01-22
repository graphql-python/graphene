try:
    from blinker import Signal
except ImportError:
    class Signal(object):

        def send(self, *args, **kwargs):
            pass

init_schema = Signal()
class_prepared = Signal()
pre_init = Signal()
post_init = Signal()
