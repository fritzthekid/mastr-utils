from setuptools import setup, find_packages

setup(
    name='mastr-utils',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'seaborn',
        'gpxpy',
	'scikit-learn',
	'flask',
	'flask-cors',
	'numpy',
    ],
    entry_points={
        'console_scripts': [
            'mastrtogpx=mastr_utils.mastrtogpx:main',
        ],
    },
    author='Eduard Moser',
    author_email='eduard.moser@gmx.de',
    description='Utilities for the Marktstammdatenregister',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fritzthekid/mastr-utils',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
