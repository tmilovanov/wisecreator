from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

def install_nltk_data():
    import nltk
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

class PostDevelopCommand(develop):
    def run(self):
        install_nltk_data()
        develop.run(self)

class PostInstallCommand(install):
    def run(self):
        install_nltk_data()
        install.run(self)

setup(
    name='wisecreator',
    version='1.0.0',
    author='Timofey Milovanov',
    packages=['wisecreator'],
    package_data={
        'wisecreator':['data/*', 'third_party/*']
    },
    install_requires=[
        'nltk==3.4.5',
        'cursor==1.3.4',
        'six==1.12.0',
    ],
    setup_requires=[
        'nltk==3.4.5',
    ],
    cmdclass={
      'install': PostInstallCommand,
      'develop': PostDevelopCommand,
    },
    entry_points={
        'console_scripts': [
            'wisecreator = wisecreator.main:main',
        ],
    },
)