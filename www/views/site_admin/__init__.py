from    flask       import Blueprint, json, redirect, request, session

from    www import config
from    database import bulletin_board_db
from    www.modules.decorators  import permissions_required
from    www.views.site_admin.forms import BbAdminForm
## New views must be added to this import
from    www.views.site_admin.views import SiteAdminView
from    www.views.site_admin.widgets import BulletinBoardAdminWidget

bp = Blueprint('site_admin', __name__)

@bp.route("/site_admin", methods=["GET", "POST"])
#@permissions_required(config.Permissions.site_admin)
def site_admin():
    view = SiteAdminView(**request.args.to_dict())
    return view.html(), 200

@bp.route('/widget/bb_admin/category/<category_id>', methods=['GET'])
@bp.route('/widget/bb_admin/category', methods=['POST'])
#@permissions_required(config.Permissions.site_admin)
def bb_admin(category_id=None):
    if request.method == 'POST':
        form_data = request.form.to_dict(flat=False)
        form      = BbAdminForm(submit=True)
        response  = form.submitForm(form_data=form_data)
        if response == True:   
            session['toast'] = {'msg': 'Bulletin board updated', 'success': True}  
            form_data = None 
            return redirect( request.referrer )
        else:
            session['toast'] = {'msg': 'Bulletin board update failed', 'success': False}   
            return redirect( request.referrer )
    else:
        bb_category = bulletin_board_db.returnCategoryFromId(category_id=category_id)
        bb_admin = BulletinBoardAdminWidget(bb_category=bb_category)
        return json.jsonify(bb_admin.html())
