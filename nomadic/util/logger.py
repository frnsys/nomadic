import sys
import logging


log = logging.getLogger('nomadic_daemon')
log.setLevel( logging.DEBUG )
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

sh = logging.StreamHandler(sys.stdout)
fh = logging.FileHandler('/tmp/nomadic.log')

sh.setFormatter(formatter)
fh.setFormatter(formatter)

log.addHandler(sh)
log.addHandler(fh)

debug = log.debug
exception = log.exception
