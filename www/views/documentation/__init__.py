from    flask       import Blueprint, json, redirect, request, send_file, session

from    www         import config

# from    database    import __admin__ as db_admin, docs_db
from    www.views.documentation.views   import DocumentationPageView
from    www.views.documentation.widgets import DocsRoutesWidget, DocsWidget, DocsAdminWidget
from    modules.documentation import py_functions

bp = Blueprint('documentation', __name__)

@bp.route("/documentation", methods=['GET','POST'])
def py_functions():
    ''' Main developer page. The intention is to provide easy access to common functions 
    and simplify the db updates and restores'''
    view = DocumentationPageView(**request.args.to_dict())
    return view.html(), 200


@bp.route('/widget/documentation/<section>')
def dev_documentation(section):
    kwargs = request.args.to_dict()
    if section == 'rebuild':
        docs_db.dropAllDocs()
        
        doc = py_functions.Docs()
        doc.update_folders_and_files_db()
        
        routes_doc = py_functions.RoutesDocs()
        routes_doc.rebuildRoutesDocs()
        classes_doc = py_functions.ClassesDocs()
        classes_doc.rebuildClassesDocs()
        functions_doc = py_functions.FunctionsDocs()
        functions_doc.rebuildFunctionsDocs()
        dependency_docs = py_functions.DependencyDocs()
        dependency_docs.rebuilddependencyDocs()

        widget = DocsAdminWidget(**kwargs)
    elif section == 'routes':
        widget = DocsRoutesWidget(**kwargs)
    else:
        widget = DocsWidget(**kwargs)

    return json.jsonify(widget.html())
