from    flask       import Blueprint, json, redirect, request, send_file, session

from    www         import config
from    database    import __admin__ as db_admin, docs_db
from    www.modules.decorators      import permissions_required
from    www.views.developer.views   import DeveloperPageView
from    www.views.developer.widgets import ApacheAccessWidget, ActivityLogWidget, ApacheErrorWidget, ErrorAlertWidget
from    www.views.developer.widgets import DatabaseControlWidget, DatabaseStatsWidget, SqlResultsWidget, GlogbalConfigWidget
from    www.views.documentation.widgets import DocsRoutesWidget, DocsWidget

bp = Blueprint('developer', __name__)

@bp.route("/developer", methods=['GET','POST'])
#@permissions_required(config.Permissions.developer)
def developer():
    ''' Main developer page. The intention is to provide easy access to common functions 
    and simplify the db updates and restores'''
    view = DeveloperPageView(**request.args.to_dict())
    return view.html(), 200

@bp.route("/widget/database/<command>", methods=['GET'])
#@permissions_required(config.Permissions.developer)
def database_control(command):
    kwargs = request.args.to_dict()
    result = False
    if command == 'backup':
        result = db_admin.backupDb()
    elif command == 'restore':
        result = db_admin.restoreDb()
    elif command ==  'update':
        result = db_admin.updateDbFromScript()
    elif command == 'download':
        path = db_admin.returnMostRecentDbBackupPath()
        return send_file(path, as_attachment=False)
    if result == True:
        session['toast'] = {'msg': f'Database { command } successful', 'success': True}
    else:
        session['toast'] = {'msg': f'Database { command } failed', 'success': False}

    db_widget = DatabaseControlWidget(**kwargs)
    return json.jsonify(db_widget.html())


@bp.route('/widget/database/stats')
#@permissions_required(config.Permissions.developer)
def database_stats():
    kwargs = request.args.to_dict()
    db_stats_widget = DatabaseStatsWidget(**kwargs)
    return json.jsonify(db_stats_widget.html())

@bp.route('/widget/database/query')
#@permissions_required(config.Permissions.developer)
def query_db():
    kwargs = request.args.to_dict()
    sql = kwargs.pop('sql')
    results_widget = SqlResultsWidget(sql=sql, **kwargs)
    return json.jsonify(results_widget.html())

@bp.route('/widget/config/update', methods=['POST'])
#@permissions_required(config.Permissions.developer)
def update_config():
    glb_config_widget = GlogbalConfigWidget()
    glb_config_widget.writeConfig(form=request.form.to_dict())
    return redirect(request.referrer)

@bp.route('/widget/logging/<log_type>')
#@permissions_required(config.Permissions.site_admin)
def logging_widgets(log_type):
    kwargs = request.args.to_dict()
    if log_type == 'access':
        access_widget = ApacheAccessWidget(**kwargs)
        return json.jsonify(access_widget.html())
    elif log_type == 'error':
        error_widget = ApacheErrorWidget(**kwargs)
        return json.jsonify(error_widget.html())
    elif log_type == 'activity':
        activity_widget = ActivityLogWidget(**kwargs)
        return json.jsonify(activity_widget.html())
    elif log_type == 'alerts':
        error_alert_widget = ErrorAlertWidget(**kwargs)
        return json.jsonify(error_alert_widget.html())