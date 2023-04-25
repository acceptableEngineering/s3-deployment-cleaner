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
python3 s3-bucket-cleaner.py my-s3-bucket-name number-of-days
```
---

## Usage / Options
Arguments:
1. S3 Bucket Name (required): the name of your S3 bucket as it exists in the AWS global namespace
2. Number of Days (required): the number of days from now backward in time for which you'd like to retain objects
3. Process (optional): by default this script will not perform any destructive actions. You must specify the positive keyword `process` as the 3rd argument for that to happen

Example run:
```
python3 s3-bucket-cleaner.py acceptable-engineering-demo-archive 30 process
```


---

## License
GPL-2.0 license, please see [LICENSE.md](https://github.com/acceptableEngineering/s3-deployment-cleaner/blob/main/LICENSE.md)