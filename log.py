import logging

def initialize():
    logme = logging.getLogger('estimator')
    logme.setLevel(logging.DEBUG)

    logfile = logging.FileHandler('twolevelsketch.log')
    logfile.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    logfile.setFormatter(formatter)
    console.setFormatter(formatter)

    logme.addHandler(logfile)
    logme.addHandler(console)
