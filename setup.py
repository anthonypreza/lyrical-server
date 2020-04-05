from setuptools import setup

setup(
    name='lyrical_server',
    packages=['lyrical_server'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-cors',
        'nltk',
        'requests',
        'bs4',
        'python-dotenv',
    ],
)