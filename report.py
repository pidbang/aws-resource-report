import boto3
import json
from botocore.paginate import PageIterator


def main():
    print("loading data...")
    pagination_config = {
        'MaxItems': 1000,
        'PageSize': 10,
    }
    iam_client = boto3.client('iam')
    client = boto3.client('sts')
    response = client.get_caller_identity()
    account_id = response['Account']
    client = boto3.client('account')
    search_paginator = client.get_paginator('list_regions')
    regions_iterator = search_paginator.paginate(
        RegionOptStatusContains=['ENABLED', 'ENABLING', 'ENABLED_BY_DEFAULT'],
        PaginationConfig=pagination_config
    )
    regions = ["global"]
    for regions_page in regions_iterator:
        for region in regions_page["Regions"]:
            regions.append(region['RegionName'])
    client = boto3.client('resource-explorer-2')
    search_paginator = client.get_paginator('search')
    for region in regions:
        print(f"# {region}")
        query_items = [
            f"region:{region}",
            "resourcetype.supports:tags",
            "-tag.key:resource_group",
            "-resourcetype:resource-explorer-2:index",
            f"-id:arn:aws:athena:{region}:{account_id}:datacatalog/AwsDataCatalog",
            f"-id:arn:aws:athena:{region}:{account_id}:workgroup/primary",
            f"-id:arn:aws:cloudtrail:{region}:{account_id}:channel/aws-service-channel/resource-explorer-2/*",
            f"-id:arn:aws:ecs:{region}:{account_id}:capacity-provider/FARGATE",
            f"-id:arn:aws:ecs:{region}:{account_id}:capacity-provider/FARGATE_SPOT",
            f"-id:arn:aws:elasticache:{region}:{account_id}:parametergroup:default.*",
            f"-id:arn:aws:elasticache:{region}:{account_id}:user:default",
            f"-id:arn:aws:events:{region}:{account_id}:event-bus/default",
            f"-id:arn:aws:iam::{account_id}:mfa/root-account-mfa-device",
            f"-id:arn:aws:iam::{account_id}:role/aws-service-role/*",
            f"-id:arn:aws:memorydb:{region}:{account_id}:acl/open-access",
            f"-id:arn:aws:memorydb:{region}:{account_id}:parametergroup/default.*",
            f"-id:arn:aws:memorydb:{region}:{account_id}:user/default",
            f"-id:arn:aws:s3:{region}:{account_id}:storage-lens/default-account-dashboard",
            f"-id:arn:aws:ses:{region}:{account_id}:configuration-set/my-first-configuration-set",
        ]
        resource_page_iterator = search_paginator.paginate(
            QueryString=" ".join(query_items),
            PaginationConfig=pagination_config
        )
        for resource_page in resource_page_iterator:
            for resource in resource_page["Resources"]:
                if resource['ResourceType'] == "iam:user":
                    role_arn = resource['Arn']
                    role_name = role_arn[role_arn.index(":user/")+6:]
                    role_tags_paginator = iam_client.get_paginator('list_user_tags')
                    role_tags_page_iterator = role_tags_paginator.paginate(
                        UserName=role_name,
                        PaginationConfig=pagination_config
                    )
                    if is_tagged(role_tags_page_iterator):
                        continue
                elif resource['ResourceType'] == "iam:role":
                    role_arn = resource['Arn']
                    role_name = role_arn[role_arn.index(":role/")+6:]
                    role_tags_paginator = iam_client.get_paginator('list_role_tags')
                    role_tags_page_iterator = role_tags_paginator.paginate(
                        RoleName=role_name,
                        PaginationConfig=pagination_config
                    )
                    if is_tagged(role_tags_page_iterator):
                        continue
                print(json.dumps(resource, indent="  ", default=str))
    print("done")


def is_tagged(tags_page_iterator: PageIterator) -> bool:
    for tags_page in tags_page_iterator:
        for tag in tags_page["Tags"]:
            if tag['Key'] == "resource_group":
                return True
    return False


if __name__ == "__main__":
    main()
