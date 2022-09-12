from    flask   import Blueprint, redirect, request, session, url_for

from    www.modules             import bulletin_board, session_control
from    database                import __admin__ as db_admin
from    modules                import logging


logger = logging.Log(py=__name__)
bp = Blueprint('api', __name__)


@bp.route("/login", methods=["POST"])
def login():
    form = request.form
    successful = session_control.login(user_id=form.get('user_id'), password=form.get('password'))

    if successful: 
        logger.write(activity='login', resource_id=session.get('user_id'), note="Employee logged in")
        bb_msgs = bulletin_board.unreadMessageCount()
        if bb_msgs >= 1:
            msg_alert_txt = 'messages' if bb_msgs > 1 else 'message'
            session['toast'] = {'header': '', 'msg': f"Login success, you have { bb_msgs } unread bulletin board { msg_alert_txt }", 'success': True}
        else:
            session['toast'] = {'header': '', 'msg': "Login success", 'success': True}
        return redirect(url_for('home_page.home'))  
    else:
        session['toast'] = {'header': 'Log in failed', 'msg': "Check fields and try again", 'success': False}
        return redirect(url_for('manifest.manifest_search'))  

@bp.route("/logout")
def logout():
    session_control.logout()
    session['toast'] = {'header': 'Logged out', 'msg': "You have been logged out", 'success': True}
    return redirect(url_for('manifest.manifest_search'))  

@bp.route("/api/backup_db", methods=['GET'])
def backup_db():
    db_admin.deleteOldBackups()
    db_admin.backupDb()
    return "OK", 200
