import os.path
import queue
import logging
from logging.handlers import QueueHandler, QueueListener
        
def logging_file():
    
    if not os.path.isfile('app.log'):
        f= open('app.log', 'w+')
        f.close()
        
def getLogger(fname:str):
    # reset default serverity from warning to debug
    logging.basicConfig(level=logging.NOTSET)
    logger = logging.getLogger(fname)

    s_handler = logging.StreamHandler()
    logging_file()
    f_handler = logging.FileHandler('app.log')

    s_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.INFO)

    output_format = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    s_format = logging.Formatter(output_format)
    f_format = logging.Formatter(output_format)

    s_handler.setFormatter(s_format)
    f_handler.setFormatter(f_format)
    
    logger.propagate = False
    
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)

    return logger

def async_getLogger(fname:str):
    
    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)

    logging.basicConfig(level=logging.NOTSET)
    
    logger = logging.getLogger(fname)
    logger.propagate = False
    logger.addHandler(queue_handler)

    console_handler = logging.StreamHandler()
    formatter = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    listener = QueueListener(log_queue, console_handler, file_handler)
    listener.start()
    # listener.stop()

    return logger
