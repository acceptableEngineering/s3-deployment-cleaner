# s3-deployment-cleaner
Removes old deployments from a given S3 bucket based on date created.

Author: Mark @ https://github.com/acceptableEngineering/s3-deployment-cleaner

---

## Setup
This guide assumes that you have already:
- Installed Python 3, pip3, and virtualenv
- Configured [AWS IAM access in your environment](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

```
# 1: Clone this git repository
git clone git@github.com:acceptableEngineering/s3-deployment-cleaner.git

# 2: Install dependencies
pip install -r requirements.txt

# 3: Run the script (see options below)
python3 s3_bucket_cleaner.py my-s3-bucket-name number-of-days
```
---

## Usage / Options
Required:
- `bucket=`: the name of your S3 bucket as it exists in the AWS global namespace

Optional:
- `keep_days=`: the number of days from now backward in time for which you'd like to retain objects
- `dryrun`: By default this script will not perform any destructive actions. You must specify `dryrun=False` for it to perform deletions
- `keep_dirs=`: the number of most recent S3 "directories" to keep

Example run that will output a plan without performing deletions:
```
python3 s3_bucket_cleaner.py bucket=acceptable-engineering-demo-archive
```

Example run that will delete S3 "directories" older than 90 days, but keep the 3 most recent:
```
python3 s3_bucket_cleaner.py \
    bucket=acceptable-engineering-demo-archive \
    keep_days=90 \
    keep_dirs=3 \
    dryrun=False
```

---

## License
GPL-2.0 license, please see [LICENSE.md](https://github.com/acceptableEngineering/s3-deployment-cleaner/blob/main/LICENSE.md)