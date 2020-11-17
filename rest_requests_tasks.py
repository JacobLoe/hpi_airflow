import requests
import hashlib
import shutil
import urllib
import os


def get_video(**context):

    # get the id of the current dag that is used
    # dag_id = 'shotdetection'
    dag_id = context['dag_run'].conf['dag_id']

    #
    features_root = os.path.split(context['ti'].xcom_pull(key='volumes_features_path', dag_id=dag_id))[0][:-1]
    print('features_root: ', features_root)
    # features_root = '/home/jacob/Downloads/hpi/videos'

    # get the videoid given with trigger from the config
    videoid = context['ti'].xcom_pull(key='videoid', dag_id=dag_id)
    # videoid = "6ffaf51" #Occupy Wallstreet
    media_base_url = "http://ada.filmontology.org/api_dev/media/"

    try:
        r = requests.get(media_base_url + videoid)
        if r.status_code == 200:
            data = r.json()
            video_url = data.get('videourl')
            video_checksum = data.get('sha256sum')
            print(video_url, video_checksum)
        else:
            pass
            # # FIXME: error handling - z.B.:
            # # Not OK result. Display error message.
            # msg = ("Server error: %s") % output.get('message', ("Server transmission error."))
            # logger.error(msg)
            # r
    except requests.exceptions.RequestException:
        # FIXME: exception handling - cannot connect to server/wrong url etc.
        raise Exception('Something went wrong')

    # create the folder to save the video to
    video_cache = os.path.join(features_root, video_checksum, 'media')
    print('video_cache', video_cache)
    done_file = os.path.join(video_cache, '.done')
    # download only if the .done-file doesn't exist. or the .done-file reads a different checksum
    if not os.path.isfile(done_file) or not open(done_file, 'r').read() == video_checksum:
        # create the video_cache folder, delete the old one if needed
        if not os.path.isdir(video_cache):
            os.makedirs(video_cache)
        else:
            shutil.rmtree(video_cache)
            os.makedirs(video_cache)
        # the video is saved as "checksum.mp4"
        video_file = os.path.join(video_cache, video_checksum + '.mp4')

        urllib.request.urlretrieve(video_url, video_file)

        # compute the checksum for the downloaded video
        movie_bytes = open(video_file, 'rb').read()
        video_new_checksum = hashlib.sha256(movie_bytes).hexdigest()
        print('checksum: ', video_checksum, '\n', 'downloaded checksum: ', video_new_checksum)
        print('new, old:', type(video_new_checksum), type(video_checksum))
        # if the checksums are equal write the checksum in a .done-file
        # and set the checksum as the id for the video
        if video_new_checksum == video_checksum:
            with open(done_file) as f:
                f.write(str(video_new_checksum))
            videoid = video_new_checksum
        else:
            raise Exception('Something went wrong with the download for the id: "{video_checksum}"\n.'
                            ' The checksum for the downloaded file does not match the checksum from the server'.format(video_checksum=video_checksum))
    else:
        # if the checksums are the same, assume that the video was
        # previously downloaded correctly
        pass

    # push checksum to xcom
    context['ti'].xcom_push(key='videoid', value=videoid)


if __name__ == '__main__':
    get_video()
