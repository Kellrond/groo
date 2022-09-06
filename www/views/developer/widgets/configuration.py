import shutil
from flask import session

from    www import config
from    www.modules import forms
from    www.modules.widget_builder   import WidgetBuilder


class GlogbalConfigWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.title = 'Global configurations'
        self.widget_id = 'global_configuration'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        file_area = forms.TextArea(_rows=25, _id="config_area")
        submit = forms.SubmitBtn()


        with open('app/config.py', 'r') as file:
            contents = file.read()

        file_area.txt = contents
        file_area.addAttributes(_style="background: #283845; color:#FFB400;font-family:courier;")


        inner_html = f'''
            <h5>{ self.title }</h5>
            <hr class="p-0 m-0" />
                <form action="/widget/config/update" method="POST">
                    <div class="col my-3">
                    { file_area.html() }
                    </div>
                    <div class="d-flex justify-content-end mt-3">
                        { submit.html() }
                    </div>
                </form>
        '''
        return inner_html
    
    ## TODO: This will not update the git and therefore config changes are lost on update. 
    # Therefore this should only really be used in development. Until a git commit can be
    # implimented  
    def writeConfig(self, form):
        shutil.copy2('app/config.py', 'app/config.py.bak')
        with open('app/config.py', 'w') as file:
            file.writelines(form.get('config_area').split('\r'))
        session['toast'] = {'msg': 'Config file written', 'success': True}

