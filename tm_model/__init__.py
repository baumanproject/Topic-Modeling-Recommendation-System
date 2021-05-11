import artm
import json
import logging

logger = logging.getLogger("topic_modeling")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.FileHandler('./logs/app_logs/app.log')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

path = "./configuration/tm_config.json"

with open(path, 'r') as f:
    config_input = json.load(f)

MIN_SCORE = config_input["inference"]["min_similarity_score"]
SIM_NUM = config_input["similarity_number"]
THREADS = config_input["train"]["threads"]
NUM_TOPICS = config_input["train"]["num_topics"]

CLEAR_LOG_MODE = config_input["inference"]["clear_log_dir"]
lc = artm.messages.ConfigureLoggingArgs()
lc.log_dir = "./logs/artm_logs"
lib = artm.wrapper.LibArtm(logging_config=lc)

# Change any other logging parameters at runtime (except logging folder)
lc.minloglevel = 3  # 0 = INFO, 1 = WARNING, 2 = ERROR, 3 = FATAL
lib.ArtmConfigureLogging(lc)
'''lc = artm.messages.ConfigureLoggingArgs()
artm_log_dir = "./logs/artm_logs"
lc.log_dir = artm_log_dir
lib = artm.wrapper.LibArtm(logging_config=lc)
lib.ArtmConfigureLogging(lc)'''
try:
    model = artm.load_artm_model("./opt/tm_model/tm_model_sources")
except Exception as error:
    model = None
    logger.warning("Model is not initialize. Normal for retrain mode. Otherwise - pay attention!")
