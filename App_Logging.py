import os
import queue
import logging
from logging.handlers import QueueHandler, QueueListener
import sys
from tkinter.messagebox import NO
        
def logging_file(log_file_dir: str):
    
    if not os.path.exists("./log"):
        os.mkdir("./log")
        
    # if not os.path.isfile(log_file_dir):
    #     f= open('app.log', 'w+')
    #     f.close()
        
def getLogger(fname:str, run_id:str):
    # reset default serverity from warning to debug
    logging.basicConfig(level=logging.NOTSET)
    output_format = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    format = logging.Formatter(output_format)

    if fname == "err":
        logger = logging.getLogger("err")
        logger.propagate = False
        log_error_dir = f'./log/error_{run_id}.log'
        logging_file(log_error_dir)
        e_handler = logging.FileHandler(log_error_dir)
        e_handler.setLevel(logging.ERROR)
        e_handler.setFormatter(format)
        logger.addHandler(e_handler)

        return logger

    logger = logging.getLogger(fname)
    logger.propagate = False
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

    s_handler.setFormatter(format)
    f_handler.setFormatter(format)
    
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    

    return logger

