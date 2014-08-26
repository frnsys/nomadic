import sys
import logging

log = logging.getLogger('nomadic_daemon')
log.setLevel( logging.DEBUG )
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
log.addHandler(sh)

debug = log.debug
exception = log.exception
