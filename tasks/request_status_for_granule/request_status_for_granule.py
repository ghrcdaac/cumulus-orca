from http import HTTPStatus
from typing import Dict, Any, List

import database
import requests_db
from cumulus_logger import CumulusLogger
from requests_db import DatabaseError

INPUT_GRANULE_ID_KEY = 'granule_id'
INPUT_JOB_ID_KEY = 'asyncOperationId'

OUTPUT_GRANULE_ID_KEY = 'granule_id'
OUTPUT_JOB_ID_KEY = 'asyncOperationId'
OUTPUT_FILES_KEY = 'files'
OUTPUT_FILENAME_KEY = 'file_name'
OUTPUT_STATUS_KEY = 'status'
OUTPUT_ERROR_MESSAGE_KEY = 'error_message'
OUTPUT_RESTORE_DESTINATION_KEY = 'restore_destination'
OUTPUT_REQUEST_TIME_KEY = 'request_time'
OUTPUT_COMPLETION_TIME_KEY = 'completion_time'

LOGGER = CumulusLogger()


def task(granule_id: str, db_connect_info: Dict, job_id: str = None) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """

    Args:
        granule_id: The unique ID of the granule to retrieve status for.
        db_connect_info: The {database}.py defined db_connect_info.
        job_id: An optional additional filter to get a specific job's entry.
    Returns: A Dict with the following keys:
        'granule_id' (str): The unique ID of the granule to retrieve status for.
        'asyncOperationId' (str): The unique ID of the asyncOperation.
        'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
            'file_name' (str): The name and extension of the file.
            'status' (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
            'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
        'restore_destination' (str): The name of the glacier bucket the granule is being copied to.
        'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
        'completion_time' (DateTime, Optional):
            The time, in UTC isoformat, when all granule_files were no longer 'pending'.

    """
    if granule_id is None or len(granule_id) == 0:
        raise ValueError("granule_id must be set to a non-empty value.")

    if job_id is None or len(job_id) == 0:
        job_id = get_most_recent_job_id_for_granule(granule_id, db_connect_info)

    job_entry = get_job_entry_for_granule(granule_id, job_id, db_connect_info)
    if job_entry[OUTPUT_COMPLETION_TIME_KEY] is None:
        del job_entry[OUTPUT_COMPLETION_TIME_KEY]

    file_entries = get_file_entries_for_granule_in_job(granule_id, job_entry[OUTPUT_JOB_ID_KEY], db_connect_info)
    for file_entry in file_entries:
        if file_entry[OUTPUT_ERROR_MESSAGE_KEY] is None:
            del file_entry[OUTPUT_ERROR_MESSAGE_KEY]

    job_entry['files'] = file_entries
    return job_entry


def get_most_recent_job_id_for_granule(granule_id: str, db_connect_info: Dict[str, any]) -> str:
    sql = f"""
            SELECT
                orca_recoveryjob.job_id
            FROM
                orca_recoveryjob
            WHERE
                granule_id = %s
            ORDER BY
                 request_time DESC
            LIMIT 1"""
    try:
        rows = database.single_query(sql, db_connect_info, (granule_id,))
    except database.DbError as err:
        LOGGER.error(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    orca_recoveryjob = rows[0]
    return database.result_to_json(orca_recoveryjob)['job_id']


def get_job_entry_for_granule(
        granule_id: str,
        job_id: str,
        db_connect_info: Dict) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """
    Gets the orca_recoverfile status entries for the associated granule_id.
    If async_operation_id is non-None, then it will be used to filter results.
    Otherwise, only the item with the most recent request_time will be returned.

    Args:
        granule_id: The unique ID of the granule to retrieve status for.
        job_id: An optional additional filter to get a specific job's entry.
        db_connect_info: The {database}.py defined db_connect_info.
    Returns: A Dict with the following keys:
        'granule_id' (str): The unique ID of the granule to retrieve status for.
        'job_id' (str): The unique ID of the asyncOperation.
        'restore_destination' (str): The name of the glacier bucket the granule is being copied to.
        'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
        'completion_time' (DateTime, Optional):
            The time, in UTC isoformat, when all granule_files were no longer 'pending'.
        """
    sql = f"""
            SELECT
                orca_recoveryjob.granule_id as {OUTPUT_GRANULE_ID_KEY},
                orca_recoveryjob.job_id,
                orca_recoveryjob.restore_destination as {OUTPUT_RESTORE_DESTINATION_KEY},
                orca_recoveryjob.request_time as {OUTPUT_REQUEST_TIME_KEY},
                orca_recoveryjob.completion_time as {OUTPUT_COMPLETION_TIME_KEY}
            FROM
                orca_recoveryjob
            WHERE
                granule_id = %s AND job_id = %s"""
    try:
        rows = database.single_query(sql, db_connect_info, (granule_id, job_id,))
    except database.DbError as err:
        LOGGER.error(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    orca_recoveryjob = rows[0]
    # Can't do capitalization in a sql query, so do the 'AS' now.
    orca_recoveryjob['asyncOperationId'] = orca_recoveryjob['job_id']
    del orca_recoveryjob['job_id']
    return database.result_to_json(orca_recoveryjob)


def get_file_entries_for_granule_in_job(granule_id: str, async_operation_id: str, db_connect_info: Dict) -> List[Dict]:
    """
    Gets the individual status entries for the files for the given job+granule.

    Args:

    Returns: A Dict with the following keys:
        'file_name' (str): The name and extension of the file.
        'status' (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
        'error_message' (str): If the restoration of the file errored, the error will be stored here. Otherwise, None.
    """
    sql = f"""
            SELECT
                orca_recoverfile.filename AS {OUTPUT_FILENAME_KEY},
                orca_status.value AS {OUTPUT_STATUS_KEY},
                orca_recoverfile.error_message as {OUTPUT_ERROR_MESSAGE_KEY}
            FROM
                orca_recoverfile
            JOIN orca_status ON orca_recoverfile.status_id=orca_status.id
            WHERE
                granule_id = %s AND job_id = %s
            ORDER BY last_update desc
            """
    try:
        rows = database.single_query(sql, db_connect_info, (granule_id, async_operation_id,))
    except database.DbError as err:
        LOGGER.error(f"DbError: {str(err)}")
        raise DatabaseError(str(err))

    result = database.result_to_json(rows)
    return result


def create_http_error_dict(error_type: str, http_status_code: int, request_id: str, message: str) -> Dict[str, Any]:
    LOGGER.error(message)
    return {
        'errorType': error_type,
        'httpStatus': http_status_code,
        'requestId': request_id,
        'message': message
    }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # noinspection SpellCheckingInspection
    """
    Entry point for the request_status_for_granule Lambda.
    Args:
        event: A dict with the following keys:
            granule_id: The unique ID of the granule to retrieve status for.
            asyncOperationId (Optional): The unique ID of the asyncOperation.
                May apply to a request that covers multiple granules.
        context: An object required by AWS Lambda. Unused.

    Returns: A Dict with the following keys:
        'granule_id' (str): The unique ID of the granule to retrieve status for.
        'asyncOperationId' (str): The unique ID of the asyncOperation.
        'files' (List): Description and status of the files within the given granule. List of Dicts with keys:
            'file_name' (str): The name and extension of the file.
            'status' (str): The status of the restoration of the file. May be 'pending', 'success', or 'failed'.
            'error_message' (str, Optional): If the restoration of the file errored, the error will be stored here.
        'restore_destination' (str): The name of the glacier bucket the granule is being copied to.
        'request_time' (DateTime): The time, in UTC isoformat, when the request to restore the granule was initiated.
        'completion_time' (DateTime, Optional):
            The time, in UTC isoformat, when all granule_files were no longer 'pending'.
    """
    LOGGER.setMetadata(event, context)

    granule_id = event.get(INPUT_GRANULE_ID_KEY, None)
    if granule_id is None or len(granule_id) == 0:
        return create_http_error_dict("BadRequest", HTTPStatus.BAD_REQUEST, context.aws_request_id,
                                      f"{INPUT_GRANULE_ID_KEY} must be set to a non-empty value.")

    db_connect_info = requests_db.get_dbconnect_info()
    return task(granule_id, db_connect_info, event.get(INPUT_JOB_ID_KEY, None))


#temp_db_connect_info = {
#    'db_host': 'localhost',
#    'db_port': '5432',
#    'db_name': 'disaster_recovery',
#    'db_user': 'postgres',
#    'db_pw': 'postgres'
#}
#print(task('granule_id_0', temp_db_connect_info))
