.. _extractors:

Extractors
==========

Near duplicate detection
------------------------

# the features_path needs the static in the beginning to work with flask
docker run --rm -it -v $(pwd)/static/PATH_TO_FEATURES:/data jacobloe/shotdetect:0.1 /data videoid

# parameters:
# --trim_frames choices: yes/no default: no             decide whether to remove or keep black borders in the movies
# --frame_width default: no changes to resolution       set the width at which the frames are saved
# --file_extension choices: .jpeg/.png default: .jpeg     define the file-extension of the frames
docker run --rm -it -v $(pwd)PATH_TO_VIDEOS:/video:ro -v $(pwd)/static/PATH_TO_FEATURES:/data jacobloe/extract_images:0.1 /data /videoid

# parameters:
# --file_extension choices: .jpeg/.png default: .jpeg     use the extension in which the frames were saved
docker run --rm -it -v $(pwd)PATH_TO_VIDEOS:/video:ro -v $(pwd)/static/PATH_TO_FEATURES:/data jacobloe/extract_aspect_ratio:0.1 /data/ /video/file_mappings.tsv

# parameters:
# --file_extension choices: .jpeg/.png default: .jpeg     use the extension in which the frames were saved
docker run --rm -it -v $(pwd)/static/PATH_TO_FEATURES:/data -v /home/.keras_ndd/:/root/.keras jacobloe/extract_features:0.1 /data/

Optical flow
------------
