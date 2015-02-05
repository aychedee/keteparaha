try:
        from setuptools import setup
except ImportError:
        from distutils.core import setup

execfile("keteparaha/__init__.py")

setup(name="keteparaha",
    version=__version__,
    packages=["keteparaha"],
    license="MIT",
    author="Hansel Dunlop",
    author_email="hansel@interpretthis.org",
    url="https://github.com/aychedee/keteparaha/",
    description="Keteparaha is a collection of tools to help when functional testing",
    long_description=open("README.md").read(),
    install_requires=[
        "imapclient",
        "pyvirtualdisplay",
        "selenium"
    ],
)
