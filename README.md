# ArrasManager
repo for the files of my own arras.io save manager, documentation is not available, dm me on discord: celestial_raccoon_80621

arras.py is the main application
installer.py is the obviously installer (run when downloading)
modify.py is the settings app for the main app (run whenever, contains some sort of docs)
init.py is a system file containing all imports and data from all others

dependencies can be found in requirements.txt

extractor.py is an independent app used to extract data from any code given
runs without any need of libraries or other files

installer.py can be used to repair potentially damaged files
if a bug occurs please dm me on discord on top of this document

do `py -m pip install -r requirements.txt` upon download
or just `pip install -r requirements.txt` if you have pip on your PATH

to download dependecies you can also run the `requirements.py` file which 
will download all the dependecies for you :)

---

## HOW TO DOWNLOAD

**i wrote this program for windows only, you might have issues on linux**

green code button => local tab => download zip

locate the zip, right click the zip => "extract everything.." => "Extract"

try out `py` or `python` (`python3` on linux) in your terminal, if either work, skip the next step

### installing python

since you dont have the programming language i have wrote this in on your computer we have to download it

visit [python.org](https://www.python.org/downloads/release/python-3128/) here, scroll down, and click on the name of the install which has "Recommended" in its description, for most windows amd computers, [this](https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe) should be the install you want

run the exe and go through the installation, should be easy

### downloading requirements

next, go to the extracted folder and open `requirements.py`, if the system asks you which app to open the file with (it should), pick python launcher, if you want to for some reason, you can also type `cmd` in the directory address bar, hit enter, and write `py -m pip install -r requirements.txt`, to install the app requirements as well

after this is done, run `installer.py` with the python launcher app, if it keeps asking you, right click a python (.py) file, select "open with", and select python launcher and select "always open with ..."

after you're done, select the "full installation" option, it'll ask you for a directory to run the install in, it will create a new folder there, and move all the files there too, this could, for example, be your desktop folder, for easy access

after you're done, open up the new folder and verify that all files have been moved successfully, you may now delete the extracted folder as all files have been moved

at this point, you may now delete `requirements.py`, `requirements.txt` and `README.md`, they no longer have any purpose, of course, you may keep the README as a guide in using my software

documentation can be found in the docs folder