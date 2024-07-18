import boto3
import json


def main():
    print("loading data...")
    pagination_config = {
        'MaxItems': 1000,
        'PageSize': 10,
    }
    client = boto3.client('sts')
    response = client.get_caller_identity()
    account_id = response['Account']
    client = boto3.client('account')
    paginator = client.get_paginator('list_regions')
    regions_iterator = paginator.paginate(
        RegionOptStatusContains=[ 'ENABLED', 'ENABLING', 'ENABLED_BY_DEFAULT'],
        PaginationConfig=pagination_config
    )
    regions = ["global"]
    for regions_page in regions_iterator:
        for region in regions_page["Regions"]:
            regions.append(region['RegionName'])
    client = boto3.client('resource-explorer-2')
    paginator = client.get_paginator('search')
    for region in regions:
        print(f"# {region}")
        query_items = [
            f"region:{region}",
            "resourcetype.supports:tags",
            "-tag.key:resource_group",
            "-resourcetype:resource-explorer-2:index",
            f"-id:arn:aws:elasticache:{region}:{account_id}:parametergroup:default.*",
            f"-id:arn:aws:elasticache:{region}:{account_id}:user:default",
            f"-id:arn:aws:memorydb:{region}:{account_id}:parametergroup/default.*",
            f"-id:arn:aws:memorydb:{region}:{account_id}:user/default",
            f"-id:arn:aws:events:{region}:{account_id}:event-bus/default",
            f"-id:arn:aws:athena:{region}:{account_id}:workgroup/primary",
            f"-id:arn:aws:athena:{region}:{account_id}:datacatalog/AwsDataCatalog",
            f"-id:arn:aws:s3:{region}:{account_id}:storage-lens/default-account-dashboard",
            f"-id:arn:aws:iam::{account_id}:mfa/root-account-mfa-device",
        ]
        resource_page_iterator = paginator.paginate(
            QueryString=" ".join(query_items),
            PaginationConfig=pagination_config
        )
        for resource_page in resource_page_iterator:
            for resource in resource_page["Resources"]:
                print(json.dumps(resource, indent="  ", default=str))
    print("done")


if __name__ == "__main__":
    main()
