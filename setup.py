from distutils.core import setup

setup(name='asocksimap',
    version='1.0.0',
    description='Connect to IMAP through Socks using Python asyncio',
    install_requires=["aioimaplib", "aiosocks"],
    author='optinsoft',
    author_email='optinsoft@gmail.com',
    keywords=['socks','imap','asyncio'],
    url='https://github.com/optinsoft/asocksimap',
    packages=['asocksimap']
)