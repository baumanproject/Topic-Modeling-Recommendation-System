import io
from googleapiclient.http import MediaIoBaseDownload
import os
import shutil
import itertools
from google_drive_api import service, data_folder, api_folder_path, logger
from datetime import datetime, timedelta


def download_file(inputs):
    """Download a Drive file's content to the local filesystem.

        Args:
        service: Drive API Service instance.
        file_id: ID of the Drive file that will downloaded.
        file_name: used as name for to write content in.
    """
    file_id, file_name, _ = inputs.values()
    #print(file_id, file_name)
    fd = io.BytesIO()
    request = service.files().get_media(fileId=file_id)
    # fileDelete='1AKMgCR6v-6uc-JSvhsttBITJzf7k-pDg'
    # file = DRIVE.files().delete(fileId=fileDelete).execute()
    media_request = MediaIoBaseDownload(fd, request)
    flag = True
    while flag:

        download_progress, done = media_request.next_chunk()

        if download_progress:
            logger.info('Download Progress: %d%%' % int(download_progress.progress() * 100))
        if done:
            logger.info('Download Complete')
            # fd.close()
            flag = False

    fd.seek(0)
    #print(os.path.join(data_folder, file_name))
    with open(os.path.join(data_folder, file_name), "wb+") as f:
        shutil.copyfileobj(fd, f)


def GDriveDownloadInfo(red_time=[]):
    info = []
    page_token = None
    # a = datetime.strptime(red_time[0],)
    while True:
        response = service.files().list(q="'{}' in parents and name contains 'pdf'".format(api_folder_path),
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name, createdTime)',
                                        # fields = "*",
                                        pageToken=page_token).execute()
        # print(response.get('files'))
        info.append(response.get('files'))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    # print(info)
    info = list(itertools.chain.from_iterable(info))

    if red_time == []:
        pass
    else:
        #info = list(map(common_time_zone, info))
        info = list(filter(lambda x: datetime.fromisoformat(x["createdTime"][:-1]) > red_time[0][0], info))
    logger.info("Incoming documents amount: {0}".format(len(info)))
    return info
