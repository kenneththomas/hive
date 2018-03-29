from setuptools import setup, find_packages
PACKAGES = find_packages()

opts = dict(name="pyengine",
            maintainer="Taylor Hemmons",
            maintainer_email="tayhemmons@protonmail.com",
            description="hive",
            long_description="hive",
            url="https://github.com/kenneththomas/hive",
            download_url="https://github.com/kenneththomas/hive",
            license="MIT",
            packages=PACKAGES)


if __name__ == '__main__':
    setup(**opts)
