try:
        from setuptools import setup
except ImportError:
        from distutils.core import setup

setup(name="test_helpers",
    version="1.1",
    packages=["test_helpers"],
    license="MIT",
    author="Hansel Dunlop",
    author_email="hansel@interpretthis.org",
    url="https://github.com/aychedee/test-helpers/",
    description="Test helpers to be used with Selenium Webdriver",
    long_description=open("README.md").read(),
    install_requires=["selenium"],
)
