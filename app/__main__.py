from app.common.rq import main
from app.common.log import config_logging


config_logging()

# production mode, rq entrypoint
if __name__ == '__main__':
    main()
