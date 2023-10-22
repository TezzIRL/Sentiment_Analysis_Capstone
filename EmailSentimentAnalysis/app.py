# This is the main python file to be executed
from ESA_Modules import Interface
import webbrowser

program_interface = Interface("Sentiment Analysis")

webbrowser.get().open("http://127.0.0.1:8050")

program_interface.run()

