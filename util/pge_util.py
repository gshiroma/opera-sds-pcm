
"""
===========
pge_util.py
===========

Contains utility functions for executing a PGE, including simulation mode.

"""

from datetime import datetime
import os
import json
import re
from typing import Dict, List

import boto3

from commons.logger import logger
from hysds.utils import get_disk_usage

from opera_chimera.constants.opera_chimera_const import OperaChimeraConstants as oc_const

DSWX_BAND_NAMES = ['WTR', 'BWTR', 'CONF', 'DIAG', 'WTR-1',
                   'WTR-2', 'LAND', 'SHAD', 'CLOUD', 'DEM']
"""
List of band identifiers for the multiple tif outputs produced by the DSWx-HLS
PGE.
"""

CSLC_BURST_IDS = ['T064-135518-IW1', 'T064-135518-IW2', 'T064-135518-IW3',
                  'T064-135519-IW1', 'T064-135519-IW2', 'T064-135519-IW3',
                  'T064-135520-IW1', 'T064-135520-IW2', 'T064-135520-IW3']
"""List of sample burst ID's to simulate CSLC-S1 multi-product output"""

RTC_BURST_IDS = ['T069-147170-IW1', 'T069-147170-IW3', 'T069-147171-IW1',
                 'T069-147171-IW2', 'T069-147171-IW3', 'T069-147172-IW1',
                 'T069-147172-IW2', 'T069-147172-IW3', 'T069-147173-IW1']
"""List of sample burst ID's to simulate RTC-S1 multi-product output"""


def get_input_hls_dataset_tile_code(context: Dict) -> str:
    product_metadata = context["product_metadata"]["metadata"]
    tile_code = product_metadata["id"].split('.')[2]  # Example id: "HLS.L30.T54PVQ.2022001T005855.v2.0"

    return tile_code


def get_product_metadata(job_json_dict: Dict) -> Dict:
    params = job_json_dict['job_specification']['params']
    for param in params:
        if param['name'] == 'product_metadata':
            return param['value']['metadata']

    raise


def download_object_from_s3(s3_bucket, s3_key, output_filepath, filetype="Ancillary"):
    """Helper function to download an arbitrary file from S3"""
    if not s3_bucket or not s3_key:
        raise RuntimeError(
            f"Incomplete S3 location for {filetype} file.\n"
            f"Values must be provided for both the '{oc_const.S3_BUCKET}' "
            f"and the '{oc_const.S3_KEY}' fields within the appropriate "
            f"section of the PGE config."
        )

    s3 = boto3.resource('s3')

    pge_metrics = {"download": [], "upload": []}

    loc_t1 = datetime.utcnow()

    try:
        logger.info(f'Downloading {filetype} file s3://{s3_bucket}/{s3_key} to {output_filepath}')
        s3.Object(s3_bucket, s3_key).download_file(output_filepath)
    except Exception as err:
        errmsg = f'Failed to download {filetype} file from S3, reason: {str(err)}'
        raise RuntimeError(errmsg)

    loc_t2 = datetime.utcnow()
    loc_dur = (loc_t2 - loc_t1).total_seconds()
    path_disk_usage = get_disk_usage(output_filepath)

    pge_metrics["download"].append(
        {
            "url": output_filepath,
            "path": output_filepath,
            "disk_usage": path_disk_usage,
            "time_start": loc_t1.isoformat() + "Z",
            "time_end": loc_t2.isoformat() + "Z",
            "duration": loc_dur,
            "transfer_rate": path_disk_usage / loc_dur,
        }
    )
    logger.info(json.dumps(pge_metrics, indent=2))

    return pge_metrics


def write_pge_metrics(metrics_path, pge_metrics):
    # Merge any existing metrics with the metrics about to be written
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as infile:
            old_pge_metrics = json.load(infile)

        pge_metrics["download"].extend(old_pge_metrics["download"])
        pge_metrics["upload"].extend(old_pge_metrics["upload"])

    # Commit the new metrics to disk
    with open(metrics_path, "w") as f:
        json.dump(pge_metrics, f, indent=2)


def simulate_run_pge(runconfig: Dict, pge_config: Dict, context: Dict, output_dir: str):
    pge_name: str = pge_config['pge_name']
    input_file_base_name_regexes: List[str] = pge_config['input_file_base_name_regexes']

    for input_file_base_name_regex in input_file_base_name_regexes:
        pattern = re.compile(input_file_base_name_regex)
        match = pattern.match(get_input_dataset_id(context))
        if match:
            break
    else:
        raise RuntimeError(
            f"Could not match dataset ID '{get_input_dataset_id(context)}' to any "
            f"input file base name regex in the PGE configuration yaml file."
        )

    logger.info('Simulating PGE output generation....')

    output_types = pge_config.get(oc_const.OUTPUT_TYPES)

    for output_type in output_types.keys():
        simulate_output(pge_name, pge_config, match, output_dir, output_types[output_type])


def get_input_dataset_id(context: Dict) -> str:
    params = context['job_specification']['params']
    for param in params:
        if param['name'] == 'input_dataset_id':
            return param['value']
    raise


def get_cslc_s1_simulated_output_filenames(dataset_match, pge_config, extension):
    """Generates an output filename for simulated CSLC-S1 PGE runs"""
    output_filenames = []

    base_name_template: str = pge_config['output_base_name']
    static_name_template: str = pge_config['static_output_base_name']
    ancillary_name_template: str = pge_config['ancillary_base_name']
    creation_time = get_time_for_filename()

    if extension.endswith('h5') or extension.endswith('iso.xml'):
        for burst_id in CSLC_BURST_IDS:
            base_name = base_name_template.format(
                burst_id=burst_id,
                acquisition_ts=dataset_match.groupdict()['start_ts'],
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                pol='VV',
                product_version='v0.1'
            )
            output_filenames.append(f'{base_name}.{extension}')

            static_base_name = static_name_template.format(
                burst_id=burst_id,
                validity_ts='20140403',
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                product_version='v0.1',
            )
            output_filenames.append(f'{static_base_name}.{extension}')
    elif extension.endswith('png'):
        for burst_id in CSLC_BURST_IDS:
            base_name = base_name_template.format(
                burst_id=burst_id,
                acquisition_ts=dataset_match.groupdict()['start_ts'],
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                pol='VV',
                product_version='v0.1'
            )
            output_filenames.append(f'{base_name}_BROWSE.{extension}')
    else:
        base_name = ancillary_name_template.format(
            creation_ts=creation_time,
            sensor=dataset_match.groupdict()['mission_id'],
            pol='VV',
            product_version='v0.1',
        )

        output_filenames.append(f'{base_name}.{extension}')

    return output_filenames


def get_rtc_s1_simulated_output_filenames(dataset_match, pge_config, extension):
    """Generates an output filename for simulated RTC-S1 PGE runs"""
    output_filenames = []

    base_name_template: str = pge_config['output_base_name']
    static_name_template: str = pge_config['static_output_base_name']
    ancillary_name_template: str = pge_config['ancillary_base_name']
    creation_time = get_time_for_filename()

    # Primary output image product pattern, includes burst ID, acquisition time
    # and polarization values/static layer name
    if extension.endswith('tiff') or extension.endswith('tif'):
        for burst_id in RTC_BURST_IDS:
            base_name = base_name_template.format(
                burst_id=burst_id,
                acquisition_ts=dataset_match.groupdict()['start_ts'],
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                product_version='v0.1',
            )

            output_filenames.append(f'{base_name}_VV.{extension}')
            output_filenames.append(f'{base_name}_VH.{extension}')
            output_filenames.append(f'{base_name}_mask.{extension}')

            static_base_name = static_name_template.format(
                burst_id=burst_id,
                validity_ts='20140403',
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                product_version='v0.1',
            )

            output_filenames.append(f'{static_base_name}_incidence_angle.{extension}')
            output_filenames.append(f'{static_base_name}_mask.{extension}')
            output_filenames.append(f'{static_base_name}_local_incidence_angle.{extension}')
            output_filenames.append(f'{static_base_name}_number_of_looks.{extension}')
            output_filenames.append(f'{static_base_name}_rtc_anf_gamma0_to_beta0.{extension}')
            output_filenames.append(f'{static_base_name}_rtc_anf_gamma0_to_sigma0.{extension}')
    # Primary metadata product, like image product but no polarization field
    elif extension.endswith('h5') or extension.endswith('iso.xml'):
        for burst_id in RTC_BURST_IDS:
            base_name = base_name_template.format(
                burst_id=burst_id,
                acquisition_ts=dataset_match.groupdict()['start_ts'],
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                product_version='v0.1',
            )
            output_filenames.append(f'{base_name}.{extension}')

            static_base_name = static_name_template.format(
                burst_id=burst_id,
                validity_ts='20140403',
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                product_version='v0.1',
            )
            output_filenames.append(f'{static_base_name}.{extension}')
    # PNG browse product, like image product but appended with "_BROWSE"
    elif extension.endswith('png'):
        for burst_id in RTC_BURST_IDS:
            base_name = base_name_template.format(
                burst_id=burst_id,
                acquisition_ts=dataset_match.groupdict()['start_ts'],
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                product_version='v0.1',
            )
            output_filenames.append(f'{base_name}_BROWSE.{extension}')

            static_base_name = static_name_template.format(
                burst_id=burst_id,
                validity_ts='20140403',
                creation_ts=creation_time,
                sensor=dataset_match.groupdict()['mission_id'],
                product_version='v0.1',
            )
            output_filenames.append(f'{static_base_name}_BROWSE.{extension}')
    # Ancillary output product pattern, no burst ID, acquisition time or polarization
    else:
        base_name = ancillary_name_template.format(
            creation_ts=creation_time,
            sensor=dataset_match.groupdict()['mission_id'],
            product_version='v0.1',
        )

        output_filenames.append(f'{base_name}.{extension}')

    return output_filenames


def get_dswx_hls_simulated_output_filenames(dataset_match, pge_config, extension):
    """Generates the output basename for simulated DSWx-HLS PGE runs"""
    output_filenames = []

    base_name_template: str = pge_config['output_base_name']

    product_shortname = dataset_match.groupdict()['product_shortname']
    if product_shortname == 'HLS.L30':
        sensor = 'L8'
    elif product_shortname == 'HLS.S30':
        sensor = 'S2A'
    else:
        raise RuntimeError(f'Could not determine HLS sensor from product shortname "{product_shortname}"')

    acq_time = datetime.strptime(
        dataset_match.groupdict()['acquisition_ts'], '%Y%jT%H%M%S').strftime('%Y%m%dT%H%M%S')

    creation_time = get_time_for_filename()

    base_name = base_name_template.format(
        tile_id=dataset_match.groupdict()['tile_id'],
        acquisition_ts=acq_time,
        creation_ts=creation_time,
        sensor=sensor,
        product_version=dataset_match.groupdict()['collection_version']
    )

    # Simulate the multiple output tif files created by this PGE
    if extension.endswith('tiff') or extension.endswith('tif'):
        for band_idx, band_name in enumerate(DSWX_BAND_NAMES, start=1):
            output_filenames.append(f'{base_name}_B{band_idx:02}_{band_name}.tif')
    elif extension.endswith('png'):
        output_filenames.append(f'{base_name}_BROWSE.png')
        output_filenames.append(f'{base_name}_BROWSE.tif')
    else:
        output_filenames.append(f'{base_name}.{extension}')

    return output_filenames

PRODUCTION_TIME = None
def get_time_for_filename():
    """
    Creates o a time-tag string suitable for use with PGE output filenames.
    The time-tag string is cached after the first call to this function.
    """
    global PRODUCTION_TIME

    if PRODUCTION_TIME is None:
        PRODUCTION_TIME = datetime.now().strftime('%Y%m%dT%H%M%S')

    return PRODUCTION_TIME

def simulate_output(pge_name: str, pge_config: dict, dataset_match: re.Match, output_dir: str, extensions: str):
    for extension in extensions:
        # Generate the output file name(s) specific to the PGE to be simulated
        base_name_map = {
            'L2_CSLC_S1': get_cslc_s1_simulated_output_filenames,
            'L2_RTC_S1': get_rtc_s1_simulated_output_filenames,
            'L3_DSWx_HLS': get_dswx_hls_simulated_output_filenames
        }

        try:
            output_filename_function = base_name_map[pge_name]
        except KeyError as err:
            raise RuntimeError(f'No output filename function available for PGE {str(err)}')

        output_filenames = output_filename_function(dataset_match, pge_config, extension)

        for output_filename in output_filenames:
            output_file = os.path.join(output_dir, output_filename)
            logger.info(f'Simulating output {output_file}')

            # Create a realistic catalog.json file that product2dataset can parse
            if extension.endswith('catalog.json'):
                with open(output_file, 'w') as outfile:
                    json.dump(
                        {
                            "PGE_Version": "sim-pge-0.0.0",
                            "SAS_Version": "sim-sas-0.0.0"
                        },
                        outfile
                    )
            # Create a dummy file containing random data
            else:
                with open(output_file, 'wb') as outfile:
                    outfile.write(os.urandom(1024))
