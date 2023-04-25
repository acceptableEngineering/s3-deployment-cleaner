"""
s3_bucket_cleaner.py
Author: Mark @ https://github.com/acceptableEngineering/s3-deployment-cleaner
Usage: python3 s3_bucket_cleaner.py s3_bucket_name [keep days: int] [Really Run? True|False]
"""
import datetime
import logging
import sys
import time
import boto3

#---------------------------------------------------------------------------------------------------

def process_cli_options():
    """
    -
    """
    # Defaults
    conf = {
            'keep_days': 30, # Previous days from this run for which to keep objects
            'process': False # Do not perform any deletions without 'True' argument
        }

    # Setup console logging
    logging.basicConfig(level=logging.INFO)

    # Process user parameters
    if len(sys.argv) < 2:
        logging.error('Please see README! Usage: %s s3_bucket_name [keep_days: int|empty]'\
                      '[process: True|False|empty]', sys.argv[0])
        sys.exit(1)

    runtime_option_count = 0

    for runtime_option in sys.argv:
        if runtime_option_count == 1:
            conf['s3_bucket_name'] = runtime_option
        elif runtime_option_count == 2:
            conf['keep_days'] = runtime_option
        elif runtime_option_count == 3:
            conf['process'] = runtime_option

        runtime_option_count+=1

    logging.info('Running with the following parameters: %s', conf)

    return conf

#---------------------------------------------------------------------------------------------------

def enum_s3_objects(conf_dict):
    """
    -
    """
    boto3_s3 = boto3.client('s3')

    return boto3_s3.list_objects_v2(
        Bucket=conf_dict['s3_bucket_name']
    )

#---------------------------------------------------------------------------------------------------

def process_objects(conf_dict, s3_objects_dict):
    """
    -
    """
    purge_cutoff_seconds = int(conf_dict['keep_days']) * 86400

    for s3_object in s3_objects_dict['Contents']:
        this_date_string = s3_object['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
        this_unixtime = datetime.datetime.strptime(this_date_string, '%Y-%m-%d %H:%M:%S')
        this_unixtime = int(time.mktime(this_unixtime.timetuple()))
        this_age_seconds = int(time.time()) - this_unixtime

        if this_age_seconds >= purge_cutoff_seconds:
            logging.info('PURGE: %s (~%s days old)', s3_object['Key'],
                        str(round(this_age_seconds/86400)))
            if conf_dict['process'] is True:
                delete_object(conf_dict, s3_object['Key'])
        else:
            logging.info('KEEP : %s', s3_object['Key'])

#---------------------------------------------------------------------------------------------------

def delete_object(conf_dict, obj_key_str):
    """
    -
    """
    boto3_s3 = boto3.client('s3')
    boto3_s3.delete_object(
        Bucket=conf_dict['s3_bucket_name'],
        Key=obj_key_str
    )

#---------------------------------------------------------------------------------------------------

# Run this script's contents in a procedural manner only if it's being run as the main program
if __name__ == '__main__':
    conf_dict_result = process_cli_options()
    s3_objects = enum_s3_objects(conf_dict_result)
    process_objects(conf_dict_result, s3_objects)
