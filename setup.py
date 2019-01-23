from setuptools import setup, find_packages

setup(
    name='django-joinfield',
    version='0.2',
    description='A field type for Django models that allows joins to a related model without a foreign key.',
    url='https://github.com/martsberger/django-joinfield',
    download_url='https://github.com/martsberger/django-joinfield/archive/0.2.tar.gz',
    author='Brad Martsberger',
    author_email='bmarts@procuredhealth.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(),
    install_requires=['django>=1.10']
)
