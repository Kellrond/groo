from    flask       import Blueprint, json, request, session, redirect

from    www              import config
from    database         import bulletin_board_db as bb_db
from    www.modules.decorators import permissions_required

## New views must be added to this import
from    www.views.bulletin_board.forms     import PostForm
from    www.views.bulletin_board.views     import BulletinBoardView
from    www.views.bulletin_board.widgets   import BBMessageListWidget, BBNavWidget, BBMessageWidget, BBPostWidget
from    www.modules   import bulletin_board as bb


bp = Blueprint('bulletin_board', __name__)

@bp.route("/bulletin_board/<slug>/<post_id>", methods=['GET', 'POST'])
@bp.route("/bulletin_board/<slug>", methods=['GET', 'POST'])
@bp.route("/bulletin_board/", methods=['GET'])
@bp.route("/bulletin_board", methods=['GET'])
def bulletin_board(slug=None, post_id=None):
    if request.method == 'GET':
        # Mark message as read if currently unread
        if post_id != None and bb.isMsgRead(post_id) == False:
            bb.toggleBoardSubscriptionSatus(post_id)
        view = BulletinBoardView(slug=slug, post_id=post_id, **request.args.to_dict())
        return view.html(), 200
    elif request.method == 'POST':
        form_data = request.form.to_dict(flat=False)
        form = PostForm(submit=True)
        response  = form.submitForm(form_data=form_data)
        if response == True:   
            session['toast'] = {'msg': 'Message posted', 'success': True}  
            return redirect( request.referrer )
        else:
            session['toast'] = {'msg': 'Message failed', 'success': False}   
            return redirect( request.referrer )
    


################################
#  Bulletin board JSON and API URLs
################################
@bp.route('/api/archive_post/<slug>/<post_id>')
#@permissions_required(config.Permissions.dc_manager)
def archive_post(slug, post_id):
    bb.togglePostArchive(post_id)
    msg_widget = BBMessageWidget(slug=slug, post_id=post_id)
    return json.jsonify(msg_widget.html())

@bp.route('/api/change_board_subscription/<slug>')
#@permissions_required(config.Permissions.employee)
def change_board_subscription(slug):
    bb.toggleBoardSubscriptionSatus(slug)
    nav_widget = BBNavWidget(slug=slug)
    return json.jsonify(nav_widget.html())

@bp.route('/api/return_post_widget/<slug>/<post_type>/<post_id>')
@bp.route('/api/return_post_widget/<slug>/<post_type>')
#@permissions_required(config.Permissions.employee)
def return_post_widget(slug, post_type, post_id=None):
    post_widget = BBPostWidget(slug=slug, post_type=post_type, post_id=post_id)
    return json.jsonify(post_widget.html())

@bp.route('/api/change_unread_status/<slug>/<post_id>')
#@permissions_required(config.Permissions.employee)
def change_unread_status(slug, post_id):
    bb.toggleMessageReadStatus(post_id=post_id, slug=slug)
    nav_widget = BBNavWidget(slug=slug, post_id=post_id)
    return json.jsonify(nav_widget.html())    

@bp.route('/api/post_new_message/<board_id>', methods=['POST'])
#@permissions_required(config.Permissions.employee)
def post_new_message(board_id):
    data = request.json
    bb.postNewMessage(board_id, data.get('post_title'), data.get('post_text'), data.get('type'), post_id=data.get('post_id'))
    return json.jsonify({'status': 'OK'})

@bp.route('/api/sticky_post/<slug>/<post_id>')
#@permissions_required(config.Permissions.dc_manager)
def sticky_post(slug, post_id):
    bb.togglePostSticky(post_id)
    msg_widget = BBMessageWidget(slug=slug, post_id=post_id)
    return json.jsonify(msg_widget.html())

@bp.route('/api/update_reply_date/<post_id>')
#@permissions_required(config.Permissions.employee)
def update_reply_date(post_id):
    bb.updateLatestPostDate(post_id=post_id)
    return "OK", 200

@bp.route('/widget/bb_category/list/<slug>/<active>', methods=['GET'])
#@permissions_required(config.Permissions.supervisor)
def bb_category_list(slug, active): 
    kwargs = request.args.to_dict()
    bb_category_list = BBMessageListWidget(slug=slug, active=active, **kwargs)
    return json.jsonify(bb_category_list.html())
