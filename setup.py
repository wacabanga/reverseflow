from setuptools import setup

setup(
    name='reverseflow',
    version='0.0.1',
    description='A library for inverting tensorflow graphs',
    author='Zenna Tavares',
    author_email="zenna@mit.edu",
    packages=['reverseflow'],
    install_requires=['tensorflow>=0.11.0rc0',
                      'numpy>=1.7',
                      'overloading>=0.5.0',
                      'pqdict>=1.0.0',
                      'sympy'],
    url='https://github.com/wacabanga/reverseflow',
    license='Apache License 2.0',
    classifiers=['License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python :: 3.4'],
)
