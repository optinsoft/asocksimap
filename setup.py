from distutils.core import setup
import re

s = open('asocksimap/version.py').read()
v = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", s, re.M).group(1)

setup(name='asocksimap',
    version=v,
    description='Connect to IMAP through Socks using Python asyncio',
    long_description=open('README.md', "r").read(),
    long_description_content_type='text/markdown',
    install_requires=["aioimaplib>=1.0.1", "aiosocks>=0.2.6"],
    author='optinsoft',
    author_email='optinsoft@gmail.com',
    keywords=['socks','imap','asyncio'],
    url='https://github.com/optinsoft/asocksimap',
    packages=['asocksimap']
)