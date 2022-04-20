# Configuration

## File storage structure

Below is an example of default storage locations, if you do not want to change it you will not need to make any configuration changes. The home directory differs depending on storage type, whether it is S3 storage or local storage, below is an explanation of the difference:

!!! note "Home directory difference"

- Mac/Linux: `/home/{user}/.postmanager/data`
- Windows: `C:\Users\{user}\.postmanager\data`
- AWS: `{bucket-name}`

### Set Template name

```
employee_manager = PostManager.setup_local("employees")
```

This will set the directory in which the data is stored as follows

```
  home/employees/1/....
  home/employees/2/....
```

By defualt the template name is `post`, with the following file structure.

```
📁 {home}
└─╴📁 post: {template-name}
    └─╴📁 1: {post-id}
      └─╴📁 media
        ├─╴📄 cover_photo.jpeg
        └─╴📄 media_index.json
      ├─╴📄 meta_data.json
      └─╴📄 content.json

    └─╴📁 2: {post-id}
      └─╴📁 media
        ├─╴📄 profile_photo.jpeg
        ├─╴📄 cover_photo.jpeg
        └─╴📄 media_index.json
      ├─╴📄 meta_data.json
      └─╴📄 content.json
    └─╴📁 ..
    ├─╴📄 index.json
    └─╴📄 latest_id.json
```

## Local Storage

No credentials are need to use local storage. If you choose local storage as the setup method for PostManager it is only required that the user have permission to read and write to the home directory, which is by default true.

## AWS S3 Storage

To use AWS storage you will need to configure AWS account credentials. This can be done using AWS CLI or manually add config files to your home directory.

### Manual Configuration

These files will need to be created in your home directory.

```
📁 {home}
└─╴📁 .aws
  ├─╴📄 config
  └─╴📄 credentials
```

```ini title="/home/user/.aws/config"
[default]
region = us-east-1
output = json
```

```ini title="/home/user/.aws/credentials"
[default]
aws_access_key_id = {ACCESS_KEY}
aws_secret_access_key = {SECRET_KEY}
```

### Configure with CLI

You will need to install AWS CLI. The following AWS docs will explain how to install and configure the CLI.

- [Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)

Below is the script to run if you have AWS CLI installed.

```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json
```
