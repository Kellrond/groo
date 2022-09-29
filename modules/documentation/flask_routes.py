from modules.documentation import Docs
# from database import docs_db


class RoutesDocs(Docs):
    def __init__(self) -> None:
        super().__init__()
        self.routes  = []

    def rebuildRoutesDocs(self):
        self.routes = self.generateDocumentation(self.__parse_flask_routing_lines)
        self.__update_routes_db()

    def __parse_flask_routing_lines(self, file_lines, file_path) -> list:
        ''' Returns the usefull information from the flask routing definitions '''
        parsed_list = []
        def new_route() -> dict:
            return {
                'file_path': file_path,
                'route': [],
                'permissions': '',
                }

        route_dict = new_route()
        for line in file_lines:
            if line.find('@bp.route(') > -1 and file_path != 'docs/__init__.py':
                s_pos = 11
                single_quote = line[s_pos:].find("'")
                double_quote = line[s_pos:].find('"')
                comma = line[s_pos:].find(',')
                comma = comma if comma > -1 else 999
                # the comma is to catch any cases where the route and method string quotes are mismatched
                if single_quote > -1 and single_quote < comma:
                    e_pos = s_pos + single_quote
                elif double_quote > -1 and double_quote < comma:
                    e_pos = s_pos + double_quote

                url = line[s_pos:e_pos]
                #Check if method is defined or default to GET
                s_pos = line.find('methods=[')
                if s_pos > -1:
                    s_pos = s_pos + 8
                    e_pos = line.find(']') + 1
                    list_str = line[s_pos:e_pos]
                    methods = eval(list_str)
                else:
                    methods = ['GET']
                
                route_dict['route'].append({'url': url, 'methods': methods})
                prev_line = line
            else:
                if len(route_dict['route']) > 0:
                    if line.find('#@permissions_required(config.Permissions.') > -1:
                        route_dict['permissions'] = line[41:line.find(')')]
                    parsed_list.append(route_dict)
                    route_dict = new_route()
                prev_line = line
        return parsed_list

    def __update_routes_db(self) -> bool:
        return docs_db.updateDocRoutesDb(self.routes)


def parseDocstringToHtml(docstr):
    docstr = [ x.strip() for x in docstr.split('\n') if x.strip() != '' ]
    
    in_p    = False
    in_list = False
    in_code = False

    html = ''
    useage_str = ''

    for line in docstr:
        # Look for list items
        if line[:1] == '-' and not in_code:
            if in_p:
                in_p = False
                html += '</p>'
            if not in_list:
                in_list = True
                html += '<ul>'
            line = '• ' + line[1:]
            html += f'<li>{ line }</li>'
        # Code blocks
        elif line[:1] == '`' or in_code:
            if in_p:
                in_p = False
                html += '</p>'
            if in_list:
                in_list = False
                html += '</ul>'
            
            if not in_code:
                in_code = True
                useage_str = f'<code>&nbsp;&nbsp;&nbsp;&nbsp;{ line.strip()[1:] }'
            else:
                useage_str += f'<br />&nbsp;&nbsp;&nbsp;&nbsp;{ line }'

            if line.strip()[-1:] == '`':
                in_code = False
                html += f'{ useage_str.strip()[:-1] }</code><br />'

        # Look for header
        elif line.find(':') > -1 and not in_code:
            if in_p:
                in_p = False
                html += '</p>'
            if in_list:
                in_list = False
                html += '</ul>'
            html += f'<strong>{ line }</strong><br />'
        else:
            if not in_p:
                in_p = True
                html += f'<p>'

            # safety_count = 0
            while line.find('`') > -1:
                # if safety_count > 10:
                #     break
                pos = line.find('`')
                pos2 = pos + line[pos+1:].find('`') + 1

                code_str = line[pos+1: pos2].replace('<', '&lt;')

                line = line[:pos] + '<span style="font-family:courier;">&nbsp;' + code_str + '</span>' + line[pos2+1:]
                # safety_count += 1
            html += f' { line}'
    return html

