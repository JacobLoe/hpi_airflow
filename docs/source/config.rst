.. _extractor_configuration:

Extractor configuration
=======================

The config-file contains the following parameters (including their default values):

    * "volumes_data_path":  "airflow_cache:/data"
    * "extractor_file_extension": "jpg"
    * "shotdetection_sensitivity": "60"
    * "shotdetection_force_run": "False"
    * "image_extraction_trim_frames": "yes"
    * "image_extraction_frame_width": "299"
    * "image_extraction_force_run": "False"
    * "feature_extraction_force_run": "False"
    * "aspect_ratio_extraction_force_run": "False"
    * "optical_flow_frame_width": "129"
    * "optical_flow_step_size": "300"
    * "optical_flow_window_size": "300"
    * "optical_flow_top_percentile": "5"
    * "optical_flow_force_run": "False"
    * "get_video_force_run": "False"
    * "update_index_force_run": "False"

If a par

*volumes_data_path* maps the the docker volume that was created during the installation to a folder inside all of the docker files.
Where *airflow_cache* is the docker volume and */data* the internal volume of the docker container.

*extractor_file_extension* sets the extension with which the all images are saved and also sets the extension extractors expect.
It is advised to keep the default value of this parameter.

*EXTRATOR_force_run* has the same functionality across all extractors. If set to *True* the extractor will run regardless of any previous runs.

*shotdetection_sensitivity* sets how many distinct shots the shotdetection finds. The higher the value the less shots will be found.

*image_extraction_trim_frames* decides whether black border of images is removed before they are saved.

*image_extraction_frame_width* sets the width at which the images are saved. The heigth is computed according to the aspect ratio of the image.

*optical_flow_frame_width*

*optical_flow_step_size*

*optical_flow_window_size*

*optical_flow_top_percentile*

*get_video_force_run*

*update_index_force_run* if set to *True* forces the NDD server to create the index from scratch.

