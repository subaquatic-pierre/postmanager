from setuptools import setup

setup(
    name="postmanager",
    version="0.1.0",
    description="Post manager for AWS S3 bucket storage",
    url="https://github.com/subaquatic-pierre/s3-postmanager",
    author="Pierre du Toit",
    author_email="https://pierredutoit.me/contact",
    license="MIT",
    url="http://pypi.python.org/pypi/postmanger/",
    packages=["postmanager"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "boto3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)
