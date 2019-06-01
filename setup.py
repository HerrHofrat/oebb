from setuptools import setup

setup(name='oebb',
      version='1.0.3.dev',
      packages=['oebb'],
      python_requires='>=3.6',
      description='Python API client for Austrian Federal Railways',
      url='https://github.com/arahorn28/oebb',
      license='MIT',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6'
      ],
      install_requires=['requests'])
