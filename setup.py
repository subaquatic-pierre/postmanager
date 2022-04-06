from setuptools import setup

setup(
    name="postmanager",
    version="0.1.0",
    description="Post manager for AWS S3 bucket storage",
    url="https://github.com/codingtech/postmanager",
    author="Pierre du Toit",
    author_email="pierre@condingtech.com",
    license="MIT",
    packages=["postmanager"],
    install_requires=[
        "boto3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)
