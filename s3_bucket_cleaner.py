"""
s3_bucket_cleaner.py
Author: Mark @ https://github.com/acceptableEngineering/s3-deployment-cleaner

Please see the README's Usage section to understand what each runtime option does. Quick start, EG:

python3 s3_bucket_cleaner.py \
    bucket= (required) \
    keep_days= (optional) \
    keep_dirs= (optional) \
    dryrun= (optional)
"""
import datetime
import logging
import sys
import time
import boto3

#---------------------------------------------------------------------------------------------------

def process_cli_options():
    """
    Evaluates runtime options, massaging them into a dictionary consumed by all other functions
    """
    def parse_cli_option(value_str, remove):
        """
        Used to separate a value from a KVP, so "bucket=hello" becomes just "hello"
        """
        return value_str.split(remove)[1]

    # Defaults
    conf = {
            'keep_days': 30,  # Previous days from this run for which to keep objects
            'dryrun': True,   # Do not perform any deletions without 'True' argument
            'keep_dirs': 0    # By default, we don't exclude any number of directories from deletion
        }

    # Setup console logging
    logging.basicConfig(level=logging.INFO)

    # Process user parameters
    if len(sys.argv) < 2:
        logging.error('Please see Usage section of README. Exiting 1')
        sys.exit(1)

    runtime_option_count = 0

    for runtime_option in sys.argv:
        if 'bucket=' in runtime_option:
            conf['bucket'] = parse_cli_option(runtime_option, 'bucket=')
        elif 'keep_days' in runtime_option:
            conf['keep_days'] = int(parse_cli_option(runtime_option, 'keep_days='))
        elif 'dryrun' in runtime_option:
            conf['dryrun'] = parse_cli_option(runtime_option, 'dryrun=')
        elif 'keep_dirs' in runtime_option:
            conf['keep_dirs'] = int(parse_cli_option(runtime_option, 'keep_dirs='))

        runtime_option_count+=1

    logging.info('Running with the following parameters: %s', conf)

    return conf

#---------------------------------------------------------------------------------------------------

def enum_s3_objects(conf_dict):
    """
    Since there is no concept of directories in S3, we have boto3 enumerate all objects in the
    target S3 bucket, and process only objects with trailing slashes
    """
    list_of_s3_dirs = []
    list_added = []
    boto3_s3 = boto3.client('s3')

    for s3_object in boto3_s3.list_objects_v2(
        Bucket=conf_dict['bucket']
    )['Contents']:
        if '/' in s3_object['Key']:
            if s3_object['Key'][-1] == '/': # EG: 'files/'
                this_name = s3_object['Key']
            else: # EG: 'files/0.mp3' becomes just 'files/'
                this_name = s3_object['Key'].split('/')[0] + '/'

            # Scrappy but readable and performant way to maintain a deduplicated list
            if this_name not in list_added:
                list_added.append(this_name)

                list_of_s3_dirs.append({
                    'Key': this_name,
                    'LastModified': s3_object['LastModified']
                })

    return list_of_s3_dirs

#---------------------------------------------------------------------------------------------------

def process_objects(conf_dict, s3_objects_dict):
    """
    Evaluates the boto3-generated dictionary for objects meeting our purge criteria. Matching
    objects are sent on to delete_object() for the actual deletions
    """
    purge_cutoff_seconds = int(conf_dict['keep_days']) * 86400
    objects_with_ages = []

    # Abort if no S3 objects enumerated
    if not s3_objects_dict:
        logging.debug('No actionable S3 objects found. Nothing to do.')
        sys.exit(0)

    # Add objects older than conf['keep_days'] as candidates for deletion
    for s3_object in s3_objects_dict:
        this_date_string = s3_object['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
        this_unixtime = datetime.datetime.strptime(this_date_string, '%Y-%m-%d %H:%M:%S')
        this_unixtime = int(time.mktime(this_unixtime.timetuple()))
        this_age_seconds = int(time.time()) - this_unixtime
        s3_object['age_seconds'] = this_age_seconds

        objects_with_ages.append(s3_object)

    # Sort the list by age in seconds. Even when conf_dict['keep_dirs'] is not set, this results in
    # nice readable output
    objects_with_ages = sorted(objects_with_ages, key=lambda x: x['age_seconds'], reverse=True)

    # If the number of objects to keep equals or exceeds the number to delete, terminate script. We
    # do this with a 0 exit code because that's okay if it happens!
    if conf_dict['keep_dirs'] >= len(objects_with_ages):
        logging.info('Runtime value keep_dirs exceeded number of objects. Nothing to do.')
        sys.exit(0)
    else:
        objects_with_ages = objects_with_ages[conf_dict['keep_dirs']:]

    # Evaluate remaining objects by age since any keep_dirs have already been removed
    for object_with_age in objects_with_ages:
        this_obj_age = round(object_with_age['age_seconds']/86400)
        if object_with_age['age_seconds'] >= purge_cutoff_seconds:
            logging.info('PURGE: %s (~%s days old)', object_with_age['Key'], str(this_obj_age))
            if conf_dict['dryrun'] is False:
                delete_object(conf_dict, object_with_age['Key'])
        else:
            logging.info('KEEP : %s (~%s days old)', object_with_age['Key'], str(this_obj_age))

#---------------------------------------------------------------------------------------------------

def delete_object(conf_dict, obj_key_str):
    """
    Simple wrapper for boto3's S3.delete_object functionality
    """
    boto3_s3 = boto3.client('s3')
    boto3_s3.delete_object(
        Bucket=conf_dict['bucket'],
        Key=obj_key_str
    )

#---------------------------------------------------------------------------------------------------

# Run this script's contents in a procedural manner only if it's being run as the main program
if __name__ == '__main__':
    conf_dict_result = process_cli_options()
    s3_objects = enum_s3_objects(conf_dict_result)
    process_objects(conf_dict_result, s3_objects)
