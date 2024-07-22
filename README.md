# Check AWS resources that are not tagged with a `resource_group` tag

This report checks all available regions. It filters out some resources, that seem to be created in each region by default.

IAM User and Role tags seem not to be indexed in Resource Explorer.
For each found user / role, they are checked independently in IAM.

The following policy must be in place to run this report:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:ListRoleTags",
                "account:ListRegions",
                "resource-explorer-2:Search",
                "iam:ListUserTags"
            ],
            "Resource": "*"
        }
    ]
}
```