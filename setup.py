#!/usr/bin/env python
from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = ""

packages = [
    "sneakysnek",
    "sneakysnek.recorders"
]

requires = []
extras_require = {
    ":sys_platform == 'darwin'": ["pyobjc-framework-Quartz"],
    ":'linux' in sys_platform": ["python-xlib"]
}

setup(
    name='sneakysnek',
    version="0.1.0",
    description="Dead simple cross-platform keyboard & mouse global input capture solution for Python 3.6+",
    long_description=long_description,
    author="Nicholas Brochu",
    author_email='nicholas@serpent.ai',
    packages=packages,
    include_package_data=True,
    install_requires=requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': ['sneakysnek = sneakysnek.recorder:demo']
    },
    license='MIT',
    url='https://github.com/SerpentAI/sneakysnek',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ]
)
