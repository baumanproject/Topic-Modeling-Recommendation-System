import spacy
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import json
import logging

logger = logging.getLogger("data_transform")
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
path = "./configuration/input.json"


with open(path, 'r') as f:
    config_input = json.load(f)

data_folder = config_input["data_folder"]


nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
tokenizer=RegexpTokenizer(r'[a-zA-Zα-ωΑ-Ω]+\-?[a-zA-Zα-ωΑ-Ω]+')
stopwords_en = stopwords.words('english') + ['arxiv']


