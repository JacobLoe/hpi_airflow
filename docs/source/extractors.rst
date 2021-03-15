.. _extractors:

Extractors
==========

If needed all extractors can be started independently from airflow with the following commands.

Near duplicate detection
------------------------

ndd::

    docker run --rm -it -v airflow_cache:/data jacobloe/shotdetect:1.0 /data VIDEOID

    docker run --rm -it -v airflow_cache:/data jacobloe/extract_images:1.0 /data VIDEOID

    docker run --rm -it -v airflow_cache:/data jacobloe/extract_aspect_ratio:1.0 /data VIDEOID

    docker run --rm -it -v airflow_cache:/data -v /home/.keras_ndd/:/root/.keras jacobloe/extract_features:1.0 /data VIDEOID


Optical flow
------------

of::

    docker run --rm -it -v airflow_cache:/data jacobloe/optical_flow:1.0 /data /VIDEOID


Automatic speech recognition
----------------------------

asr::

    docker run --rm -it -v airflow_cache:/data jacobloe/transcribe_audio:1.0 /data 6ffaf51e5040724cd40c4411fcb872474b653710e9c88271ec98efe549c71e01

