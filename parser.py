import argparse
from execute.run import retrain, inference,synchronize
from execute import logger
import os

if __name__ == "__main__":
    try:

        parser = argparse.ArgumentParser(description = 'TM_rec_backend')
        parser.add_argument('-m','--module',type = str, choices=["inf", "rt", "sync"],default="inf",
                            help='inference module [inf],retrain module [rt] or synchronize module[sync]')


        #parser.add_argument('-d','--direcory',type = str,
         #                   help='current working directory',required=True)

        args = parser.parse_args()
        arg_choice = args.module
        if(arg_choice == "sync"):
            synchronize()
        elif(arg_choice == "inf"):
            inference()
        elif( arg_choice == "rt"):
            retrain()
        else:
            print("error")
            raise Exception


    except Exception as e:
        logger.error("Unexpected error or illegal parametres", exc_info=True)