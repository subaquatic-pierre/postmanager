import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="postmanager",
    version="0.1.0",
    description="Post manager for AWS S3 bucket storage",
    url="https://github.com/subaquatic-pierre/s3-postmanager",
    author="Pierre du Toit",
    author_email="subaquatic-pierre@gmail.com",
    project_urls={
        "Bug Tracker": "https://github.com/subaquatic-pierre/s3-postmanager/issues",
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
