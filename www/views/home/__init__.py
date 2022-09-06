from flask import Blueprint, request

from www.config                  import Permissions
from www.modules.decorators      import permissions_required
from www.views.home.views   import HomePageView

bp = Blueprint('home', __name__)

@bp.route("/", methods=['GET', 'POST'])
#@permissions_required(Permissions.employee)
def home():
    view = HomePageView(**request.args.to_dict())
    return view.html(), 200
