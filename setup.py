from setuptools import setup, find_packages

setup(
    name='pnogo_api',
    version='0.8.4',
    url='api.pnogo.ml',
    license='',
    author='marc0777',
    author_email='',
    description='',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-cors',
        'Pillow',
    ],
)
