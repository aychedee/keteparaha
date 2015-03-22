from os import path
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

module = __import__('keteparaha')


if sys.argv[1] == 'document':
    # Automatically update the documentation
    import pdoc
    doc_dir = path.abspath(path.join(path.dirname(__file__), 'docs'))
    template_dir = path.join(doc_dir, 'templates')
    pdoc.tpl_lookup = pdoc.TemplateLookup(directories=[template_dir])
    pdoc._template_path = [template_dir]
    docs = pdoc.html('keteparaha', external_links=True, source=False)
    with open(path.join(doc_dir, 'index.html'), 'w') as f:
        f.write(docs)
    sys.exit(0)


setup(
    name='keteparaha',
    version=module.__version__,
    packages=['keteparaha'],
    license='MIT',
    author="Hansel Dunlop",
    author_email='hansel@interpretthis.org',
    url='https://github.com/aychedee/keteparaha/',
    description='Keteparaha is a tool for testing modern JS heavy websites',
    long_description=open('README.md').read(),
    install_requires=[
        'imapclient',
        'pyvirtualdisplay',
        'selenium'
    ],
)
