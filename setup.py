from setuptools import setup, find_packages

setup(
    name='energie-utils',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        pandas
        matplotlib
        seaborn
    ],
    entry_points={
        'console_scripts': [
            # Füge deine Konsolen-Skripte hier hinzu
        ],
    },
    author='Eduard Moser',
    author_email='eduard.moser@gmx.de',
    description='Utilities for the Marktstammdatenregister',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fritzthekid/energie-utils',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
