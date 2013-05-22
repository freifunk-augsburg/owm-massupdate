import sys
sys.path.insert(1, "./")
import logging
import os
from logging.handlers import WatchedFileHandler
import config

def initialize_logging(name="unknown", quiet=False, verbose=False):
    """Initializes the logging module.

    This initializes pythons logging module:

        * set loglevel (from nodes config)
        * set log file
        * format log messages
        * log to file as well as stderr

    Kwargs:
        name (string): name of the module initializing the logger

    """
    if config.logLevel == 'DEBUG':
        logLevel = logging.DEBUG
    elif config.logLevel == 'INFO':
        logLevel = logging.INFO
    elif config.logLevel == 'WARN':
        logLevel = logging.WARN
    elif config.logLevel == 'ERROR':
        logLevel = logging.ERROR
    
    if not config.logFile:
        config.logFile = "/dev/null"

    logger = logging.getLogger(name)



    formatter = logging.Formatter('%(asctime)s - %(name)s\t%(levelname)s\t%(message)s')
    formatterstdout = logging.Formatter('%(asctime)s\t%(message)s')
    logger.setLevel(logLevel)
    if name == "owm-massupdate":
        try:
            log2file = WatchedFileHandler(config.logFile)
            log2file.setFormatter(formatter)
            log2file.setLevel(logLevel)
            logger.addHandler(log2file)
        except:
            print("--- WARNING --- config.logFile " + config.logFile + " IS EITHER NONEXISTENT OR NOT WRITABLE")
        if not quiet:
            log2stderr = logging.StreamHandler(sys.stderr)
            log2stderr.setFormatter(formatterstdout)
            log2stderr.setLevel(logging.INFO)
            logger.addHandler(log2stderr)
        if verbose:
            log2stderr.setLevel(logging.DEBUG)


    return logger
