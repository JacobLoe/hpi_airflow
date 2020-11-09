import requests


def get_videos(**context):

    # get the videoid given with trigger from the config
    # FIXME get rid of video_id in favor of videoid
    # FIXME rename ids more consistently
    videoid = context['dag_run'].conf['videoid']
    video_id = "294704e"
    media_base_url = "http://ada.filmontology.org/api_dev/media/"

    try:
        r = requests.get(media_base_url + video_id)
        if r.status_code == 200:
            # OK. We should have some server options available as json
            data = r.json()
            video_url = data.get('videourl')
            video_sha256sum = data.get('sha256sum')
            print(video_url, video_sha256sum)
        else:
            pass
            # # FIXME: error handling - z.B.:
            # # Not OK result. Display error message.
            # msg = ("Server error: %s") % output.get('message', ("Server transmission error."))
            # logger.error(msg)
            # return
    except requests.exceptions.RequestException:
        # FIXME: exception handling - cannot connect to server/wrong url etc.
        pass

    # check for checksum in file_mappings.tsv #FIXME pull file_mappings path from xcom
    # in case it doesn't exist download the movie, compute checksum and compare it with previous checksum
    # add checksum and video path to file_mappings.tsv
    # push checksum to xcom
    context['ti'].xcom_push(key='videoid', value=videoid)

    # Beispiel und Daten per REST an einen Server zu schicken - nicht lauffähig, da unsere REST API das bisher noch nicht implementiert hat

    # # Use a requests.session to use a KeepAlive connection to the server
    # session = requests.session()
    # # content-type heißt, du shickst dem server json, accept heißt, du erwartest json als Antwort
    # headers = {"Content-Type": "application/json", "Accept": "application/json"}
    #
    # response = session.post(url, headers=headers, json={
    #         "bla": 1,
    #         "blubb": True,
    #         'annotations': [
    #             {
    #             }
    #         ]
    #     })
    #
    # # Antwort wie oben entpacken:
    # output = response.json()
    # if output.get('status') == 200:
    #     data = output.get('key')
    # else:
    #     # FIXME: s.o.
    #     pass


if __name__ == '__main__':
    get_videos()
