from distutils.core import setup

setup(name='asocksimap',
    version='1.0.2',
    description='Connect to IMAP through Socks using Python asyncio',
    long_description=open('README.md', "r").read(),
    long_description_content_type='text/markdown',
    install_requires=["aioimaplib", "aiosocks"],
    author='optinsoft',
    author_email='optinsoft@gmail.com',
    keywords=['socks','imap','asyncio'],
    url='https://github.com/optinsoft/asocksimap',
    packages=['asocksimap']
)