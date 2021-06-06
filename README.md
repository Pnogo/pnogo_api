# pnogo_api

Pnogo API

## Requirements

To use the API you need to install the dependencies specified inside `requirements.txt`. You can quickly install them using PIP:

```bash
pip install -r requirements.txt
```

The same can be done on Windows by opening the included `install.bat` file.

## Usage

To start the API we need to first define some environment variables used by Flask. By setting the `FLASK_ENV` variable to `development` we enable some very useful functionalities, such as auto refresh on save (so we don't need to reopen Flask every time we edit the code) and the included debugger.

This can be done in Windows using `set`, while on linacs `export` must be used. For example, in Windows:

```shell
set FLASK_APP=run
set FLASK_ENV=development
```

Then, from the root of the project, we need to enter the directory `pnogo_api`, where the code is:

```bash
cd pnogo_api
```

Finally, we can start serving the API using Flask by giving the following command:

```bash
python -m flask run
```

A `start.bat` has been included to ease development when using Windows.
