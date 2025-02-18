## Setup the virtual environment:

# macOS/Linux
python3 -m venv myenv
# Windows
python -m venv myenv

1. 
# macOS/Linux
source myenv/bin/activate
# Windows
myenv\Scripts\activate

2. 
# Install required dependencies on your local machine
pip install -r requirements.txt

3. (Optional) # If you have installed or updated dependencies.
# Update requirements.txt
pip freeze > requirements.txt
