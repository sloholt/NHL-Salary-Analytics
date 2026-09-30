# app/app.py
from dash import Dash
import os

from app.layout import layout
from app.callbacks import register_callbacks

# If any callbacks reference components not in the initial layout (tabs/pages),
# keep suppress_callback_exceptions=True.
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server 

app.title = "NHL Salary Inequality Analysis"
app.layout = layout
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8050)),
        debug=True
    )
