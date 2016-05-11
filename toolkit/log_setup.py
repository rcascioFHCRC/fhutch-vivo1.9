import logging
import logging.handlers

def get_logger():
    # For console logging.
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    )
    # File handler and formatting. 
    handler = logging.handlers.RotatingFileHandler(
        "logs/harvest.log",
        maxBytes=10*1024*1024,
        backupCount=5,
    )
    lformat = logging.Formatter("%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler.setFormatter(lformat)

    # Module logging
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Converis client
    client_logger = logging.getLogger("converis_client")
    client_logger.setLevel(logging.WARNING)
    client_logger.addHandler(handler)

    # Harvest scripts logging
    logger = logging.getLogger('harvest')
    logger.setLevel(logging.INFO)       
    logger.addHandler(handler)  
    return logger