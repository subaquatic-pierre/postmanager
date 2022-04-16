from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="postmanager",
    version="0.1.5",
    description="Post manager to manage all post types with various storage backends",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    license_file="LICENSE",
    author="Pierre du Toit",
    author_email="subaquatic.pierre@gmail.com",
    project_urls={
        "Bug Tracker": "https://github.com/subaquatic-pierre/postmanager/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={".": "postmanager"},
    packages=find_packages(exclude=["tests"]),
    test_suite="tests",
    python_requires=">=3.6,<4",
    install_requires=["boto3==1.21.38"],
)
