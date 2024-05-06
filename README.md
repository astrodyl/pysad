# Python Search And Discovery
Python Search And Discovery (PYSAD) is a Python tool designed for rapid
observing of the LIGO Virgo Collaboration (LVC) localization region resulting
from a gravitational-wave event. Localizations can be poor, sometimes 
containing thousands of galaxies. Manually submitting this many observations
can be incredibly cumbersome and prone to mistakes. 

PYSAD attempts to streamline this process by leveraging the 
**[Skynet](https://skynet.unc.edu/)** 
API to schedule and modify observations of galaxies with high likelihood
of being the host galaxy of the event. These galaxies are programmatically
retrieved from the 
**[NASA/IPAC Extragalactic Database](https://ned.ipac.caltech.edu/)**.

## Setup
* Clone the `pysad` repo to a local directory.
  ```
  git clone https://github.com/astrodyl/pysad.git
  ```

* Create a Python virtual environment using Python >= 3.8.
    ```
    python -m venv location/to/create/name_of_venv
    ```

* Activate the virtual environment and change directories to the `pysad` repo 
and then install the requirements.
    ```shell
    # Omit 'source' if using cmd prompt or PowerShell on Windows
    source location/of/venv/Scripts/activate
  
    # Change directories to the repo
    cd location/of/pysad
  
    # Install all requirements
    pip install -r requirements.txt
    ```
* Store your Skynet API token. Log into **[Skynet](https://skynet.unc.edu/)** and
navigate to `My Account` under `My Observatory`. On the right side navigation
window, click on the `Settings` option. Scroll down to find your API token.
Copy and paste this token into the `pysad/config/api.ini` configuration file.
**Make sure to keep this token private**.

## Run
The entry point to run `pysad` is `__main__.py` located in 
`pysad/pysad/__main__.py`. Inside the main method, there is a 
`params` dictionary that contains and describes the required values
to run. Most of these values are pointers to the configuration files.

Since there are numerous parameters are that are required but not frequently 
changed, I make use of configuration files stored in `pysad/config`. See the 
existing configurations for examples on how to create your own.

To run using the terminal, simply run the main file: `python.exe __main__.py`