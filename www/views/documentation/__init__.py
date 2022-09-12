from    flask       import Blueprint, json, redirect, request, send_file, session

from    www         import config

from    database    import __admin__ as db_admin, docs_db
from    www.modules.decorators      import permissions_required
from    www.views.documentation.views   import DocumentationPageView
from    www.views.documentation.widgets import DocsRoutesWidget, DocsWidget, DocsAdminWidget
from    modules import generate_docs

bp = Blueprint('documentation', __name__)

@bp.route("/documentation", methods=['GET','POST'])
#@permissions_required(config.Permissions.developer)
def documentation():
    ''' Main developer page. The intention is to provide easy access to common functions 
    and simplify the db updates and restores'''
    view = DocumentationPageView(**request.args.to_dict())
    return view.html(), 200


@bp.route('/widget/documentation/<section>')
#@permissions_required(config.Permissions.developer)
def dev_documentation(section):
    kwargs = request.args.to_dict()
    if section == 'rebuild':
        docs_db.dropAllDocs()
        
        doc = generate_docs.Docs()
        doc.update_folders_and_files_db()
        
        routes_doc = generate_docs.RoutesDocs()
        routes_doc.rebuildRoutesDocs()
        classes_doc = generate_docs.ClassesDocs()
        classes_doc.rebuildClassesDocs()
        functions_doc = generate_docs.FunctionsDocs()
        functions_doc.rebuildFunctionsDocs()
        dependency_docs = generate_docs.DependencyDocs()
        dependency_docs.rebuilddependencyDocs()

        widget = DocsAdminWidget(**kwargs)
    elif section == 'routes':
        widget = DocsRoutesWidget(**kwargs)
    else:
        widget = DocsWidget(**kwargs)

    return json.jsonify(widget.html())
