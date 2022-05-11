import os
import queue
import logging
from logging.handlers import QueueHandler, QueueListener
import sys
        
def logging_file(log_file_dir: str):
    
    if not os.path.exists("./log"):
        os.mkdir("./log")
        
    # if not os.path.isfile(log_file_dir):
    #     f= open('app.log', 'w+')
    #     f.close()
        
def getLogger(fname:str, run_id:str):
    # reset default serverity from warning to debug
    logging.basicConfig(level=logging.NOTSET)
    logger = logging.getLogger(fname)

    s_handler = logging.StreamHandler()
    # client_id = os.environ["client_id"]
    log_file_dir = f'./log/{run_id}.log'
    logging_file(log_file_dir)
    f_handler = logging.FileHandler(log_file_dir)

    try:
        if sys.argv[3] == "debug":
            f_handler.setLevel(logging.DEBUG)
            logger.info(f"[app] logging in Debug mode!")
        else:
            f_handler.setLevel(logging.INFO)
            logger.info(f"[app] logging in Productive mode!")
    except Exception as e:
            f_handler.setLevel(logging.INFO)
            logger.info(f"[app] logging in Productive mode!")

    s_handler.setLevel(logging.DEBUG)
   
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
