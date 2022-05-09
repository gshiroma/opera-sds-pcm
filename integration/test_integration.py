import logging
from pathlib import Path

import conftest
from int_test_util import \
    mock_cnm_r_success, \
    upload_file, \
    wait_for_cnm_s_success, \
    wait_for_cnm_r_success, \
    wait_for_l2, \
    wait_for_l3

config = conftest.config


def test_l30():
    logging.info("UPLOADING INPUT FILES")

    download_dir: Path = Path(config["L30_INPUT_DIR"]).expanduser()
    input_filepaths = [
        download_dir / "HLS.L30.T22VEQ.2021248T143156.v2.0.B02.tif",
        download_dir / "HLS.L30.T22VEQ.2021248T143156.v2.0.B03.tif",
        download_dir / "HLS.L30.T22VEQ.2021248T143156.v2.0.B04.tif",
        download_dir / "HLS.L30.T22VEQ.2021248T143156.v2.0.B05.tif",
        download_dir / "HLS.L30.T22VEQ.2021248T143156.v2.0.B06.tif",
        download_dir / "HLS.L30.T22VEQ.2021248T143156.v2.0.B07.tif",
        download_dir / "HLS.L30.T22VEQ.2021248T143156.v2.0.Fmask.tif"
    ]
    for i, input_filepath in enumerate(input_filepaths):
        logging.info(f"Uploading file {i+1} of {len(input_filepaths)}")
        upload_file(filepath=input_filepath)

    logging.info("CHECKING FOR L2 ENTRIES, INDICATING SUCCESSFUL DATA INGEST")

    response = wait_for_l2(_id="HLS.L30.T22VEQ.2021248T143156.v2.0.B02", index="grq_1_l2_hls_l30")
    assert response.hits[0]["id"] == "HLS.L30.T22VEQ.2021248T143156.v2.0.B02"

    response = wait_for_l2(_id="HLS.L30.T22VEQ.2021248T143156.v2.0.B03", index="grq_1_l2_hls_l30")
    assert response.hits[0]["id"] == "HLS.L30.T22VEQ.2021248T143156.v2.0.B03"

    response = wait_for_l2(_id="HLS.L30.T22VEQ.2021248T143156.v2.0.B04", index="grq_1_l2_hls_l30")
    assert response.hits[0]["id"] == "HLS.L30.T22VEQ.2021248T143156.v2.0.B04"

    response = wait_for_l2(_id="HLS.L30.T22VEQ.2021248T143156.v2.0.B05", index="grq_1_l2_hls_l30")
    assert response.hits[0]["id"] == "HLS.L30.T22VEQ.2021248T143156.v2.0.B05"

    response = wait_for_l2(_id="HLS.L30.T22VEQ.2021248T143156.v2.0.B06", index="grq_1_l2_hls_l30")
    assert response.hits[0]["id"] == "HLS.L30.T22VEQ.2021248T143156.v2.0.B06"

    response = wait_for_l2(_id="HLS.L30.T22VEQ.2021248T143156.v2.0.B07", index="grq_1_l2_hls_l30")
    assert response.hits[0]["id"] == "HLS.L30.T22VEQ.2021248T143156.v2.0.B07"

    response = wait_for_l2(_id="HLS.L30.T22VEQ.2021248T143156.v2.0.Fmask", index="grq_1_l2_hls_l30")
    assert response.hits[0]["id"] == "HLS.L30.T22VEQ.2021248T143156.v2.0.Fmask"

    logging.info("CHECKING FOR L3 ENTRIES, INDICATING SUCCESSFUL PGE EXECUTION")
    response = wait_for_l3(_id="OPERA_L3_DSWx_HLS_LANDSAT-8_T22VEQ_20210905T143156_v2.0", index="grq_1_l3_dswx_hls")
    assert response.hits[0]["id"] == "OPERA_L3_DSWx_HLS_LANDSAT-8_T22VEQ_20210905T143156_v2.0"

    logging.info("CHECKING FOR CNM-S SUCCESS")
    response = wait_for_cnm_s_success(_id="OPERA_L3_DSWx_HLS_LANDSAT-8_T22VEQ_20210905T143156_v2.0", index="grq_1_l3_dswx_hls")
    assert_cnm_s_success(response)

    logging.info("TRIGGER AND CHECK FOR CNM-R SUCCESS")
    mock_cnm_r_success(id="OPERA_L3_DSWx_HLS_LANDSAT-8_T22VEQ_20210905T143156_v2.0")
    response = wait_for_cnm_r_success(_id="OPERA_L3_DSWx_HLS_LANDSAT-8_T22VEQ_20210905T143156_v2.0", index="grq_1_l3_dswx_hls")

    assert_cnm_r_success(response)


def test_s30():
    logging.info("UPLOADING INPUT FILES")

    download_dir: Path = Path(config["S30_INPUT_DIR"]).expanduser()
    input_filepaths = [
        download_dir / "HLS.S30.T15SXR.2021250T163901.v2.0.B02.tif",
        download_dir / "HLS.S30.T15SXR.2021250T163901.v2.0.B03.tif",
        download_dir / "HLS.S30.T15SXR.2021250T163901.v2.0.B04.tif",
        download_dir / "HLS.S30.T15SXR.2021250T163901.v2.0.B11.tif",
        download_dir / "HLS.S30.T15SXR.2021250T163901.v2.0.B12.tif",
        download_dir / "HLS.S30.T15SXR.2021250T163901.v2.0.B8A.tif",
        download_dir / "HLS.S30.T15SXR.2021250T163901.v2.0.Fmask.tif"
    ]
    for i, input_filepath in enumerate(input_filepaths):
        logging.info(f"Uploading file {i+1} of {len(input_filepaths)}")
        upload_file(filepath=input_filepath)

    logging.info("CHECKING FOR L2 ENTRIES, INDICATING SUCCESSFUL DATA INGEST")

    response = wait_for_l2(_id="HLS.S30.T15SXR.2021250T163901.v2.0.B02", index="grq_1_l2_hls_s30")
    assert response.hits[0]["id"] == "HLS.S30.T15SXR.2021250T163901.v2.0.B02"

    response = wait_for_l2(_id="HLS.S30.T15SXR.2021250T163901.v2.0.B03", index="grq_1_l2_hls_s30")
    assert response.hits[0]["id"] == "HLS.S30.T15SXR.2021250T163901.v2.0.B03"

    response = wait_for_l2(_id="HLS.S30.T15SXR.2021250T163901.v2.0.B04", index="grq_1_l2_hls_s30")
    assert response.hits[0]["id"] == "HLS.S30.T15SXR.2021250T163901.v2.0.B04"

    response = wait_for_l2(_id="HLS.S30.T15SXR.2021250T163901.v2.0.B11", index="grq_1_l2_hls_s30")
    assert response.hits[0]["id"] == "HLS.S30.T15SXR.2021250T163901.v2.0.B11"

    response = wait_for_l2(_id="HLS.S30.T15SXR.2021250T163901.v2.0.B12", index="grq_1_l2_hls_s30")
    assert response.hits[0]["id"] == "HLS.S30.T15SXR.2021250T163901.v2.0.B12"

    response = wait_for_l2(_id="HLS.S30.T15SXR.2021250T163901.v2.0.B8A", index="grq_1_l2_hls_s30")
    assert response.hits[0]["id"] == "HLS.S30.T15SXR.2021250T163901.v2.0.B8A"

    response = wait_for_l2(_id="HLS.S30.T15SXR.2021250T163901.v2.0.Fmask", index="grq_1_l2_hls_s30")
    assert response.hits[0]["id"] == "HLS.S30.T15SXR.2021250T163901.v2.0.Fmask"

    logging.info("CHECKING FOR L3 ENTRIES, INDICATING SUCCESSFUL PGE EXECUTION")
    response = wait_for_l3(_id="OPERA_L3_DSWx_HLS_SENTINEL-2A_T15SXR_20210907T163901_v2.0", index="grq_1_l3_dswx_hls")
    assert response.hits[0]["id"] == "OPERA_L3_DSWx_HLS_SENTINEL-2A_T15SXR_20210907T163901_v2.0"

    logging.info("CHECKING FOR CNM-S SUCCESS")
    response = wait_for_cnm_s_success(_id="OPERA_L3_DSWx_HLS_SENTINEL-2A_T15SXR_20210907T163901_v2.0", index="grq_1_l3_dswx_hls")
    assert_cnm_s_success(response)

    logging.info("TRIGGER AND CHECK FOR CNM-R SUCCESS")
    mock_cnm_r_success(id="OPERA_L3_DSWx_HLS_SENTINEL-2A_T15SXR_20210907T163901_v2.0")
    response = wait_for_cnm_r_success(_id="OPERA_L3_DSWx_HLS_SENTINEL-2A_T15SXR_20210907T163901_v2.0", index="grq_1_l3_dswx_hls")

    assert_cnm_r_success(response)


def assert_cnm_s_success(response):
    assert response.hits.hits[0]["_source"]["daac_CNM_S_status"] == "SUCCESS"
    assert response.hits.hits[0]["_source"]["daac_CNM_S_timestamp"] is not None


def assert_cnm_r_success(response):
    assert response.hits.hits[0]["_source"]["daac_delivery_status"] == "SUCCESS"
    assert response.hits.hits[0]["_source"]["daac_identifier"] is not None

    assert response.hits.hits[0]["_source"]["daac_received_timestamp"] is not None
    assert response.hits.hits[0]["_source"]["daac_submission_timestamp"] is not None
    assert response.hits.hits[0]["_source"]["daac_collection"] is not None
    assert response.hits.hits[0]["_source"]["daac_process_complete_timestamp"] is not None

    # CNM-R ingestion metadata
    assert response.hits.hits[0]["_source"]["daac_catalog_id"] is not None
    assert response.hits.hits[0]["_source"]["daac_catalog_url"] is not None