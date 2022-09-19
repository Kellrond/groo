from flask import Blueprint, request

from www.config                  import Permissions
from www.views.home.views   import HomePageView

bp = Blueprint('home', __name__)

@bp.route("/", methods=['GET', 'POST'])
def home():
    view = HomePageView(**request.args.to_dict())
    return view.html(), 200
