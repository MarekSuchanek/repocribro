from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='repocribro',
    version='0.0.0',
    keywords='github repositories sieve projects community',
    description='Extensible sifting tool for information from GitHub repositories',
    long_description=long_description,
    author='Marek Suchánek',
    author_email='suchama4@fit.cvut.cz',
    license='MIT',
    url='https://github.com/MarekSuchanek/repocribro',
    packages=find_packages(),
    package_data={
        'repocribro': [
            'static/*',
            'templates/*'
        ]
    },
    entry_points={
        'console_scripts': [
            'repocribro = repocribro.repocribro:start',
        ],
    },
    install_requires=[
        'Flask>=0.12',
        'flask-bower',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Software Development :: Version Control',
    ],
)
