import sys
from gt_can.tg_message import messager_channel as mc

mc.bootstrap(sys.argv[1] if len(sys.argv) > 1 else
             "tg_cfg.json")