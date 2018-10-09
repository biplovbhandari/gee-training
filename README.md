# GEE app development using webapp2
## using conda
**1: Download and install ANACONDA [(Select 2.7 python and 64 bit)](https://www.anaconda.com/download/#windows)**

**2: Add Community package management system**
start "Anaconda Prompt" with admin privileges
```
conda config --prepend channels conda-forge
```
> START HERE IF YOU HAVE ANACONDA INSTALLED

**3: Create Environment**
```
conda create -n gee_training python=2.7
conda activate gee_training
```
> (optional) remove an conda environment
> first switch to other environment, cannot remove an environment while you are into that environment
```
conda activate base
conda env remove --name gee_training
```
> verify the environment is removed
```
conda info --envs
```

**4: Install GEE API**
```
conda install earthengine-api
```
> This will install all the required dependencies for running Earth Engine library.

****Verify the installation by using****
```
python -c "from oauth2client import crypt"
python -c "import ee"
```
**5: GEE Authentication**
```
python
```
test authentication
```python 
import ee
ee.Initialize()
```

> Setup Authentication (Only needed if you received an authentication error from above)
```
earthengine authenticate
```
This will open a browser and prompt you to login to your google account once logged in, copy and paste the authorization code into your command prompt

**6: Install required dependencies**
```
pip install -r requirements.txt
```
## start the server by
```
python server.py
```
#### Also read [(this blogpost)](https://biplovbhandari.wordpress.com/2017/11/28/jrc-historical-flood-visualization-and-download-with-google-earth-engine/)
