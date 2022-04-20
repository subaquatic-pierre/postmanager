# PostManager

[![PyPI](https://img.shields.io/pypi/v/postmanager.svg)](https://pypi.python.org/pypi/postmanager)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/subaquatic-pierre/postmanager/blob/main/LICENSE)
[![Tests](https://github.com/subaquatic-pierre/postmanager/workflows/Tests/badge.svg)](https://github.com/subaquatic-pierre/postmanager/actions/workflows/1_tests.yml)
[![Linting](https://github.com/subaquatic-pierre/postmanager/workflows/Linting/badge.svg)](https://github.com/subaquatic-pierre/postmanager/actions/workflows/3_linting.yml)
[![Codecov](https://codecov.io/gh/subaquatic-pierre/postmanager/branch/main/graph/badge.svg?token=lQUanTQKRO)](https://codecov.io/gh/subaquatic-pierre/postmanager)
[![Latest Documentation](https://img.shields.io/badge/docs-latest-brightgreen)](https://subaquatic-pierre.github.io/postmanager)

Content manager for all types of content, blog posts, galleries, personal records, etc.

---

**[Features](#features)** - **[Requirements](#requirements)** - **[Installation](#installation)** - **[Quick usage](#quick-usage)** - **[Examples](#examples)**

## Features

- AWS S3 storage: This means you can store your content directly to the cloud with very little configuration out of the box.

- Local storage: Store all your content on your local system, skip cloud vulnerabilities or use for quick development purposes.

- Easy media management: Add, Delete or Update any media associated with your content. Receive media data in a browser friendly format for easy image source display.

- Control your meta data: Meta data each data point has meta data associated which can be in any shape. The user has complete control.

## Requirements

### Operating system

- Linux
- MacOS
- Windows

### Python Version

Python 3.9 or greater

### Local Storage

There is very little requirements for local storage

- User Read / Write privilege to home directory (true by default)

### Cloud Storage

It is necessary to have the following configured to use PostManager with AWS S3.

- AWS Account
- S3 Bucket with Read/Write access (not necessarily public)
- AWS CLI installed and configured

## Installation

With `pip`:

```bash
pip install postmanager
```

## Quick usage

### Setup

```python title="main.py"
from postmanager.manager import PostManager

blog_manager = PostManager.setup_local()

```

### Create

```python
meta_data = {
    "title": "Cool Blog",
    "author": "Jeff"
}

content = {
    "blocks":[
        {"Header"}:"Cool Blog"
    ],
    ...
    ...
}

new_blog = blog_manager.new_post(meta_data,content)

post_manager.save_post(new_blog)
```

### Get

```python
blog_id = 42
bog = blog_manager.get_by_id(blog_id)

return blog.to_json()
```

### Delete

```python
blog_id = 42
blog_manager.delete_post(blog_id)
```

### Add Media

!!! note "Note: Media format"
The `add_media` takes the media bytes in DataUrl format. This is the same as the value returned from JavaScript [FileReader.readAsDataURL()](https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsDataURL).

```python
media = {
    "name":"cover_photo",
    "bytes": "data:image/jpeg;base64,iV99JKH...."
}

blog_id = 42
blog = blog_manager.get_by_id(blog_id)

blog.add_media(media["name"],media["bytes"])
blog_manager.save_post(blog)
```

## Examples

- [Simple Flask](https://github.com/subaquatic-pierre/postmanager-flask-example)

## References

- [AWS CLI Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- [Media Format](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs)
- [FileReader](https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsDataURL)
