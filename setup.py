from setuptools import setup, find_packages

setup(
    name='pnogo_api',
    version='0.10.5',
    url='api.pnogo.dev',
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
        'setuptools',
        'Werkzeug',
        'MarkupSafe',
    ],
)
