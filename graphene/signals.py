from blinker import Signal

init_schema = Signal()
class_prepared = Signal()
pre_init = Signal()
post_init = Signal()
