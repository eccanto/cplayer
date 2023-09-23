"""Setup CPlayer package."""

from pathlib import Path

from setuptools import find_packages, setup


setup(
    name='cplayer',
    version='1.0.0',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    description='Song player command line application',
    author='Erik Ccanto',
    author_email='ccanto.erik@gmail.com',
    url='https://github.com/eccanto/cplayer',
    license='MIT',
    long_description=Path('README.md').read_text(encoding='UTF-8'),
    long_description_content_type='text/markdown',
    install_requires=Path('requirements.txt').read_text(encoding='UTF-8').splitlines(),
    package_data={'cplayer': ['**/*.css']},
    classifiers=[
        'Environment :: Console',
        'Operating System :: Unix',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7.15, <4',
    entry_points={
        'console_scripts': [
            'cplayer = cplayer.main:main',
        ]
    },
    keywords=['music', 'songs player', 'command line'],
)
