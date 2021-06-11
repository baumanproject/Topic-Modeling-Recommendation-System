from google_drive_api.run import GDriveDownloadInfo, download_file

from postgres_api.run import insert_into_DOCUMENT, insert_into_DOC_PROCESSING, \
    insert_into_DOC_SIMILARITY, logs_insert, get_last_update, existance_in_document_table, \
    close_postgres_connection, insert_into_TM_CURRENT \
    , clear_TM_CURRENT, existance_in_tm_current_table,clear_DOC_SIMILARITY

from data_transform.run import lemmatizer, preprocessor, get_text

from tm_model.run import add_to_temp_vw_file, inference_for_file, clear_log_directory, vw_files_concat, train, model

from execute import logger


def inference():
    logger.info("--INFERENCE ITERATION--")
    if model == None:
        logger.critical("During training critical error occured | Model in inference mode does not exist")
        raise BrokenPipeError
    last_update_time = get_last_update("Topic_modeling_inference")
    info_drive_array = GDriveDownloadInfo(red_time=last_update_time)

    for i in info_drive_array:
        logger.info("Input: {} document".format(i["name"]))
        if existance_in_document_table(i["name"]) != []:
            continue

        download_file(i)
        insert_into_DOCUMENT(i["name"], i["createdTime"])
        if existance_in_tm_current_table(i["name"]) != []:
            insert_into_DOC_PROCESSING(i["name"], "TM", "Success")
            continue
        string_repr = preprocessor(lemmatizer(get_text(i["name"])))
        if len(string_repr) == 0:
            logger.warning("Document {} was crached during preprocessing".format(i["name"]))
            insert_into_DOC_PROCESSING(i["name"], "TM", "Failed")
        else:
            logger.info("Document successfully prepared".format(i["name"]))
            insert_into_DOC_PROCESSING(i["name"], "TM", "Success")
            add_to_temp_vw_file(string_repr, i["name"])
            arr = inference_for_file(i["name"])
            for elem in arr:
                insert_into_DOC_SIMILARITY("TM", i["name"], elem[1], elem[0])
                insert_into_DOC_SIMILARITY("TM", elem[1], i["name"], elem[0])
            logger.info("For document {0} was added {1} similarities".format(i["name"], len(arr)))
    logs_insert("Topic_modeling_inference")
    clear_log_directory()
    close_postgres_connection()


def synchronize(test=False):
    logger.info("-- Synchronization phase --")
    if model == None:
        logger.critical("During training critical error occured | Model in inference mode does not exist")
        raise BrokenPipeError
    # will make checks for dataset1.vw and tm_curr table
    lines = tuple(open("./opt/vw/prod/dataset.vw", 'r'))
    clear_TM_CURRENT()
    for line in lines:
        file_id = line.split('|')[0].strip()
        insert_into_TM_CURRENT(file_id)
        # uncomment for PROD!!!!
        if not test:
            arr = inference_for_file(file_id, init=1)
            for elem in arr:
                insert_into_DOC_SIMILARITY("TM", file_id, elem[1], elem[0])
    logger.info("Data was synchronized")
    close_postgres_connection()


def retrain():
    logger.info("--RETRAIN ITERATION--")
    vw_files_concat()
    train()
    clear_DOC_SIMILARITY()
    synchronize()



