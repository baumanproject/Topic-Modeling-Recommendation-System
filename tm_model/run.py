from tm_model import model, MIN_SCORE, CLEAR_LOG_MODE, logger, THREADS, NUM_TOPICS, SIM_NUM
import os
from sklearn.feature_extraction.text import CountVectorizer
import artm
import pandas as pd
from scipy import spatial
import warnings
from operator import itemgetter
import glob
import shutil

warnings.filterwarnings("ignore", category=RuntimeWarning)


# light version of upload
def make_vw_bow_n_wd_batch(file_string):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(file_string)
    return vectorizer.get_feature_names(), X.toarray()


# send file to temp vw file, that union theta from model and theta from temp folder.
def add_to_temp_vw_file(file_string, file_name):
    f_output = open("./opt/vw/temp/temp.vw", "a+")
    new_document = '{} |@modal {} '.format(file_name, file_string)
    f_output.write(new_document + '\n')
    f_output.close()


def find_top_documents(file_name, file_name_array, embeddings_array):
    index_of_file = file_name_array.index(file_name)
    input_emb = embeddings_array[index_of_file]
    measure_array = []
    for name, emb in zip(file_name_array, embeddings_array):
        if name == file_name:
            continue
        else:
            cosine_distance = 1 - spatial.distance.cosine(input_emb, emb)
            if cosine_distance > MIN_SCORE:
                measure_array.append((cosine_distance, name))

    if measure_array == []:
        logger.warning("Unfortunately no similarity documents for {}".format(file_name))
        return measure_array
    sorted_measure_array = sorted(measure_array, key=itemgetter(0))
    if len(sorted_measure_array) > SIM_NUM:
        sorted_measure_array = sorted_measure_array[:SIM_NUM]
    return sorted_measure_array


def inference_for_file(file_name, init=0):
    theta_base = model.get_theta()
    # amount = os.stat("./opt/vw/temp/temp.vw").st_size
    if os.stat("./opt/vw/temp/temp.vw").st_size != 0 and init != 1:

        batch_vectorizer = artm.BatchVectorizer(data_path="./opt/vw/temp/temp.vw",
                                                data_format='vowpal_wabbit',
                                                target_folder="./opt/vw/temp/temp_batch")

        temp_theta = model.transform(batch_vectorizer=batch_vectorizer, theta_matrix_type='dense_theta')

        union_theta = pd.concat([temp_theta.T, theta_base.T])
    else:
        union_theta = theta_base.T

    union_theta.reset_index(level=0, inplace=True)
    file_name_array = union_theta["index"].tolist()
    embeddings_array = union_theta.drop(["index"], axis=1).values.tolist()
    del union_theta
    del theta_base

    return find_top_documents(file_name, file_name_array, embeddings_array)


def train():
    try:
        logger.info("TRAINIG BEGIN")
        batch_vectorizer_mono = artm.BatchVectorizer(data_path="./opt/vw/prod/dataset1.vw",
                                                     data_format='vowpal_wabbit',
                                                     target_folder="./opt/vw/prod/dataset_batch")
        logger.info("Batches stage completed")
        model_artm = artm.ARTM(num_topics=NUM_TOPICS,
                               num_processors=THREADS,
                               theta_columns_naming='title',
                               # show_progress_bars=True,
                               theta_name="prod_theta",
                               class_ids={'@modal': 1},
                               cache_theta=True
                               )
        dictionary = artm.Dictionary()
        dictionary.gather(data_path=batch_vectorizer_mono.data_path)
        dictionary.filter(min_df_rate=0.01, min_tf=10, inplace=True)
        model_artm.initialize(dictionary=dictionary)
        logger.info("Dictionary stage completed")
        model_artm.scores.add(artm.SparsityPhiScore(name='sparsity_phi_score', class_id='@modal'))
        model_artm.scores.add(artm.SparsityThetaScore(name='sparsity_theta_score'))
        model_artm.scores.add(artm.TopTokensScore(name='top_tokens_score', class_id="@modal"))
        model_artm.scores.add(artm.PerplexityScore(name='perplexity_score', class_ids={'@modal': 1}))
        model_artm.regularizers.add(
            artm.DecorrelatorPhiRegularizer(name='decorrelator_phi_lab', tau=1.0e+5, class_ids=['@modal']))

        model_artm.num_document_passes = 1
        ITERATIONS = [8, 8, 8]
        logger.info("Model initialization stage completed")
        model_artm.fit_offline(batch_vectorizer=batch_vectorizer_mono, num_collection_passes=ITERATIONS[0])
        logger.info("1/3 trainig stage")
        model_artm.regularizers.add(artm.SmoothSparseThetaRegularizer(name='sparse_theta_regularizer', tau=-1.5))
        model_artm.fit_offline(batch_vectorizer=batch_vectorizer_mono, num_collection_passes=ITERATIONS[1])
        logger.info("2/3 trainig stage")
        model_artm.fit_offline(batch_vectorizer=batch_vectorizer_mono, num_collection_passes=ITERATIONS[2])
        logger.info("3/3 trainig stage")
        logger.info("Training is completed")

        # logger.info("Sparsity_phi_score: {}".format(model_artm.score_tracker['sparsity_phi_score'].value))
        # logger.info("Sparsity_theta_score".format(model_artm.score_tracker['sparsity_theta_score'].value))
        logger.info("Perplexity_score".format(model_artm.score_tracker['perplexity_score'].value[-1]))
        # delete tm_model_sources folder

        if os.path.isdir('./opt/tm_model/tm_model_sources'):
            shutil.rmtree("./opt/tm_model/tm_model_sources")
        logger.warning("Tm_model folder was deleted")

        model_artm.dump_artm_model("./opt/tm_model/tm_model_sources")
        logger.info("TM model is saved")

    except Exception as error:
        logger.critical("During training critical error occured | {0}".format(error))


def vw_files_concat():
    # Concat vw files
    with open("./opt/vw/prod/dataset1.vw", 'a+') as outfile:
        with open("./opt/vw/temp/temp.vw", 'r') as fd:
            for line in fd:
                outfile.write(line)

    logger.info("Vw files are unioned")
    # clear temp.vw file
    f = open("./opt/vw/temp/temp.vw", 'w')
    f.close()
    logger.warning("temp.vw file was cleared")

    # clear batch directory
    files = glob.glob('./opt/vw/temp/temp_batch/*')
    for f in files:
        os.remove(f)
    logger.warning("Temp Batch directory was cleared")


    # delete tm_model batch
    files = glob.glob('./opt/vw/prod/dataset_batch/*')
    for f in files:
        os.remove(f)
    logger.warning("Tm_model_batches directory was cleared")

    # learning phase


def clear_log_directory():
    if CLEAR_LOG_MODE:
        files = glob.glob('./logs/artm_logs/*')
        for f in files:
            os.remove(f)
        logger.warning("Log directory was cleared")
    else:
        pass
# return pairs for similarity table
