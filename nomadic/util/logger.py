import sys
import logging


log = logging.getLogger('nomadic_daemon')
log.setLevel( logging.DEBUG )
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

sh = logging.StreamHandler(sys.stdout)
fh = logging.FileHandler('/tmp/nomadic.log')

for h in [sh, fh]:
    h.setFormatter(formatter)
    log.addHandler(h)

debug = log.debug
exception = log.exception
