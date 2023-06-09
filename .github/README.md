# s3-deployment-cleaner

<img align="left" width="160" src="https://github.com/acceptableEngineering/s3-deployment-cleaner/blob/main/.github/README-images/icon.png?raw=true">

Removes old "directories" from a given S3 bucket based on date created. S3 has no concept of
directories, only objects with slashes in them, so you'll find the word taken lightly in this
project's documentation.

Author: Mark @ https://github.com/acceptableEngineering/s3-deployment-cleaner

[![Test Status Badge](https://github.com/acceptableEngineering/s3-deployment-cleaner/actions/workflows/PR.yml/badge.svg)](https://github.com/acceptableEngineering/s3-deployment-cleaner/actions/workflows/PR.yml)

&nbsp;<br />

---

## Setup
This guide assumes that you have already:
- Installed Python 3, pip3, and virtualenv
- Configured [AWS IAM access in your environment](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- Have the following IAM permissions for your bucket(s): `iam:DeleteObject`, `iam:ListBucket`, `iam:DeleteObject`

```
# 1: Clone this git repository
git clone git@github.com:acceptableEngineering/s3-deployment-cleaner.git

# 2: Install dependencies (consider using virtualenv)
pip install -r requirements.txt
```
---

## Quick Start
Example run that will output a plan without performing deletions:
```
python3 s3_bucket_cleaner.py \
    bucket=acceptable-engineering-deployments
```
Output:
```
INFO:root:PURGE: deployment_1/ (~803 days old)
INFO:root:PURGE: deployment_2/ (~114 days old)
INFO:root:PURGE: deployment_3/ (~106 days old)
INFO:root:PURGE: deployment_4/ (~90 days old)
INFO:root:KEEP : deployment_5/ (~5 days old)
```

Example run that will delete S3 "directories" older than 90 days, but keep the 3 most recent:
```
python3 s3_bucket_cleaner.py \
    bucket=acceptable-engineering-deployments \
    keep_days=90 \
    keep_dirs=3 \
    dryrun=False
```
Output:
```
INFO:root:PURGE: deployment_1/ (~803 days old)
INFO:root:PURGE: deployment_2/ (~114 days old)
INFO:root:KEEP: deployment_3/ (~106 days old)
INFO:root:KEEP: deployment_4/ (~90 days old)
INFO:root:KEEP : deployment_5/ (~5 days old)
```

---

## Usage / Options
Required:
- `bucket=`: the name of your S3 bucket as it exists in the AWS global namespace

Optional:
- `keep_days=`: the number of days from now backward in time for which you'd like to retain objects
- `keep_dirs=`: the number of most recent S3 "directories" to keep
- `dryrun=`: By default this script will not perform any destructive actions. You must specify `dryrun=False` for it to perform deletions

---

## License
GPL-2.0 license, please see [LICENSE.md](https://github.com/acceptableEngineering/s3-deployment-cleaner/blob/main/LICENSE.md)
