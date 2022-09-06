from flask import Blueprint, json,  render_template, request, session

from www                    import config
from www.modules.decorators import permissions_required
from www.views._skeletons.views   import ExampleView, ExampleTabView
from www.views._skeletons.widgets import ExampleListWidget, ExampleFormWidget
from www.views._skeletons.forms   import ExampleForm

bp = Blueprint('example', __name__) 

@bp.route("/__example", methods=['GET','POST'])
#@permissions_required(config.Permissions.employee)
def __example():
    ''' Comment string here'''
    if request.method == 'POST':
        form_data = request.form.to_dict(flat=False)
        form      = ExampleForm(submit=True)
        response  = form.submitForm(form_data=form_data)
        #-- Change this to False to test form failure
        if response == False:   
            session['toast'] = {'msg': 'Example form submitted', 'success': True}  
            form_data = None 
        else:
            session['toast'] = {'msg': 'Example form failed', 'success': False}   
    else:
        form_data = None
    view = ExampleView(form_data=form_data, **request.args.to_dict())
    return view.html(), 200

@bp.route("/__example_tabs", methods=['GET','POST'])
#@permissions_required(config.Permissions.employee)
def __example_tabs():
    ''' Comment string here'''
    if request.method == 'POST':
        form_data = request.form.to_dict(flat=False)
        form      = ExampleForm(submit=True)
        response  = form.submitForm(form_data=form_data)
        #-- Change this to False to test form failure
        if response == False:   
            session['toast'] = {'msg': 'Example form submitted', 'success': True}  
            form_data = None 
        else:
            session['toast'] = {'msg': 'Example form failed', 'success': False}   
    else:
        form_data = None
    view = ExampleTabView(form_data=form_data, **request.args.to_dict())
    return view.html(), 200


## Widget Api

@bp.route('/widget/example/list/<show_active>')
#@permissions_required(config.Permissions.employee)
def example_list(show_active):
    ''' Takes True or False. Additional arguments '''
    kwargs = request.args.to_dict()
    #-- Just an example of sending a toast through an api by tagging a launchToast() to the end of the JS
    if kwargs.get('toast'):
        session['toast'] = {'msg': kwargs.get('toast'), 'success': True}

    #-- This line is needed to convert the argument to a boolean
    show_active_response = show_active == "True"
    example_list_widget = ExampleListWidget(active=show_active_response, **kwargs)
    return json.jsonify(example_list_widget.html())

@bp.route('/widget/example/form/<example_id>')
#@permissions_required(config.Permissions.employee)
def discrepancy_edit(example_id):
    kwargs = request.args.to_dict()
    example_form_widget = ExampleFormWidget(example_id=example_id, **kwargs)
    return json.jsonify(example_form_widget.html())
