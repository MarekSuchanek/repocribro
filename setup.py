from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='repocribro',
    version='0.1.003',
    keywords='github repositories sieve projects community',
    description='Extensible sifting tool for information from GitHub repositories',
    long_description=long_description,
    author='Marek Suchánek',
    author_email='suchama4@fit.cvut.cz',
    license='MIT',
    url='https://github.com/MarekSuchanek/repocribro',
    zip_safe=False,
    packages=find_packages(),
    package_data={
        'repocribro': [
            'static/*.js',
            'static/*.css',
            'static/fonts/*.*',
            'static/pics/*.png',
            'templates/*.html',
            'templates/admin/*.html',
            'templates/admin/tabs/*.html',
            'templates/core/*.html',
            'templates/core/org/*.html',
            'templates/core/repo/*.html',
            'templates/core/repo_owner/*.html',
            'templates/core/search/*.html',
            'templates/core/user/*.html',
            'templates/error/*.html',
            'templates/macros/*.html',
            'templates/manage/*.html',
            'templates/manage/dashboard/*.html',
        ]
    },
    entry_points={
        'console_scripts': [
            'repocribro = repocribro:cli',
        ],
        'repocribro.ext': [
            'repocribro-core = repocribro.ext_core:make_extension'
        ],
        'flask.commands': [
            'assign_role=repocribro.commands:assign_role',
            'db_create=repocribro.commands:db_create',
            'check_config=repocribro.commands:check_config',
            'repocheck=repocribro.commands:repocheck',
        ],
    },
    install_requires=[
        'configparser',
        'Flask>=0.12',
        'flask-login',
        'flask-migrate',
        'flask-principal',
        'flask-restless',
        'flask-sqlalchemy==2.1',
        'iso8601',
        'jinja2',
        'pytz',
        'python-dotenv',
        'requests',
        'sqlalchemy',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'betamax',
        'pytest'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
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
