Tested with Python 3.6.3 under macOS 10.12, but it should work on most platforms.

To get started, you'll need
- gcc
- CMake
- glfw3 (look for libglfw3 or glfw-x11 packages)
- python3
- virtualenv

```
virtualenv -p python3 vvv
git clone git@github.com:nhurman/dont_starve_tools
. vvv/bin/activate
cd dont_starve_tools
pip install -r requirements.txt
```

Then you're set! You can run the demo app, or use one of the file format parsers:
```
# demo opengl
./sample_app.py
# save file parser
python -m lib.save_file ../saves/saveindex
```
