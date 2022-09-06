from    flask               import Flask
from    www.config          import Config

app = Flask(__name__)
app.config.from_object(Config)

from www.views import api, bulletin_board, developer, home, site_admin, _skeletons

app.register_blueprint(api.bp)
app.register_blueprint(bulletin_board.bp)
app.register_blueprint(developer.bp)
app.register_blueprint(home.bp)
app.register_blueprint(site_admin.bp)
app.register_blueprint(_skeletons.bp)


 