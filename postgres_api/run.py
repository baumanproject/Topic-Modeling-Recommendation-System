from postgres_api import conn, cur, logger
from psycopg2 import Error
from datetime import datetime


def get_last_update(project_type):
    try:
        select_query = "SELECT timestamp from run_logs WHERE process_type = %s ORDER BY timestamp  DESC LIMIT 1"
        cur.execute(select_query, (project_type,))
        mobile_records = cur.fetchall()
        # print(mobile_records)
        logger.info("Data was successfully selected from Logs Table")
        return mobile_records
    except (Exception, Error) as error:
        logger.error("Error while selecting from Logs Table", error)
        conn.rollback()
        return None


def existance_in_document_table(file_id):
    try:
        select_query = "SELECT doc_id from document WHERE doc_id = %s and doc_src = %s"
        cur.execute(select_query, (file_id, "GDrive"))
        mobile_records = cur.fetchall()
        logger.info("Data was successfully selected from Document Table")
        if mobile_records != []:
            logger.warn("Document {0} is already exists in Documents Table".format(file_id))
        return mobile_records
    except (Exception, Error) as error:
        logger.error("Error while selecting from Document Table", error)
        conn.rollback()
        return []


def existance_in_tm_current_table(file_id):
    try:
        select_query = "SELECT doc_id from tm_current WHERE doc_id = %s"
        cur.execute(select_query, (file_id,))
        mobile_records = cur.fetchall()
        logger.info("Data was successfully selected from tm_current Table")
        if mobile_records != []:
            logger.warning("Document {0} is already exists in tm_current Table".format(file_id))
        return mobile_records
    except (Exception, Error) as error:
        logger.error("Error while selecting from tm_current Table", error)
        conn.rollback()
        return []


def logs_insert(project_type):
    try:
        insert_query = "INSERT INTO run_logs (process_type, timestamp) VALUES (%s,%s)"
        cur.execute(insert_query, (project_type, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        logger.info("Data was successfully inserted into Logs Table")
        return True
    except (Exception, Error) as error:
        logger.error("Error while inserting into Logs Table", error)
        conn.rollback()
        return False


def insert_into_DOCUMENT(doc_name, timestamp):
    try:
        insert_query = "INSERT INTO document (doc_src, doc_id, timestamp) VALUES (%s,%s,%s)"
        cur.execute(insert_query, ("GDrive", doc_name, timestamp))
        conn.commit()
        logger.info("Data was successfully inserted into Document Table")
        # return True
    except (Exception, Error) as error:
        logger.error("Error while inserting into Documents", error)
        conn.rollback()


def insert_into_TM_CURRENT(doc_name):
    try:
        insert_query = "INSERT INTO TM_CURRENT (doc_id, timestamp) VALUES (%s,%s)"
        cur.execute(insert_query, (doc_name, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        # logger.info("Data was successfully  insert into TM_CURRENT")
        # return True
    except (Exception, Error) as error:
        logger.error("Error while inserting into TM_CURRENT", error)
        conn.rollback()


def clear_TM_CURRENT():
    try:
        insert_query = "TRUNCATE tm_current"
        cur.execute(insert_query)
        conn.commit()
        logger.info("Table TM_CURRENT was successfully cleared")
        # return True
    except (Exception, Error) as error:
        logger.error("Error while clearing TM_CURRENT", error)
        conn.rollback()


def clear_DOC_SIMILARITY():
    try:
        insert_query = "TRUNCATE doc_similarity"
        cur.execute(insert_query)
        conn.commit()
        logger.info("Table DOC_SIMILARITY was successfully cleared")
        # return True
    except (Exception, Error) as error:
        logger.error("Error while clearing DOC_SIMILARITY", error)
        conn.rollback()


def insert_into_DOC_PROCESSING(proc_id, doc_id, status):
    try:
        insert_query = "INSERT INTO doc_processing (doc_id, process_id, status) VALUES ('{0}', '{1}', '{2}')" \
            .format(doc_id, proc_id, status)
        cur.execute(insert_query)
        conn.commit()
        logger.info("Data was successfully inserted into DOC_PROCESSING Table")
    except (Exception, Error) as error:
        logger.error("Error while inserting into DOC_PROCESSING", error)
        conn.rollback()


def insert_into_DOC_SIMILARITY(algo, d_1, d_2, similarity):
    try:

        insert_query = "INSERT INTO doc_similarity (algo_type, doc_id_1, doc_id_2, similarity) VALUES ('{0}', '{1}', '{2}', {3})" \
            .format(algo, d_1, d_2, similarity)

        cur.execute(insert_query)
        conn.commit()
        # print("Data was successfully inserted into DOC_SIMILARITY Table")
    except (Exception, Error) as error:
        logger.error("Error while inserting into DOC_SIMILARITY", error)
        conn.rollback()


def close_postgres_connection():
    cur.close()
    conn.close()
    logger.warning("Connection to PostgreSql is closed")
