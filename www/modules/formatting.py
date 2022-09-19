from re import sub


def is_float(element) -> bool:
    ''' Checks if the parameter can be cohersed to float(element) '''
    try:
        float(element)
        return True
    except:
        return False

def stripAllHtml(text: str) -> str:
    ''' Removes all html tags from the string passed in 
    
        Notes:
            - useful when displaying part of a string that contains html tags. Prevents breaking
            - TODO: Maybe instead of stripping the html we find and close all open tags 
    '''
    return sub('<.*?>', '', text)

def htmlToPlainText(text: str) -> str:
    '''Provides a more formatted version of html with breaks and paragraphs 
    
        Notes: 
            - nested lists get colapsed to a single list
    '''
    text = text.replace('<br>', '\n')
    text = text.replace('<br />', '\n')
    text = text.replace('<li>', '• ')
    text = text.replace('</li>', '\n')
    text = sub('</p>', '\n\n', text)
    text = sub('</h.*?>', '\n', text)
    text = sub('<.*?>', '', text)
    text = text.replace('\n', '<br />')
    return text

def makeReferrerArgsSafe(referrer, keep_request_arg=True, **kwargs) -> str:
    ''' In cases where the request.referrer context variable contains the same argument as is passed failure can occur. 
    Adding a redirect( request.referrer + arg string ) would end up doubling an argument. 
    This function avoids that by writing each argument into the same dictionary by it's key. 
    
    Params:
        - referrer: the request.referrer variable is set in the Flask context
        - keep_request_arg=True: if multiple keys changing this to False will keep the arg passed into the function   

    Usage:
        `return_url = formatting.updateReferrerArg(request.referrer, example_id=...)
        return redirect( return_url )`

     '''
    arg_list = []
    if referrer.find('?') > -1:
        # Separate the args from the url
        referrer_url = referrer.split('?')

        # Move right side of list to args list and turn into list
        arg_list = referrer_url.pop(1) 
        arg_list = arg_list.split('&')

        for arg in arg_list:
            arg_split = arg.split('=')
            key = arg_split[0]
            value = arg_split[1]
            # Prevent overwriting the first value 
            if kwargs.get(key, False) == False and keep_request_arg == True:
                kwargs[key] = value
            else:
                kwargs[key] = value

        # Take the first (only) from the list
        referrer_url = referrer_url[0]    
    else: 
        referrer_url = referrer

    if len(kwargs) > 0:
        referrer_url += '?'
        referrer_url += "&".join([ f'{k}={v}' for k,v in kwargs.items() if v != None])

    return referrer_url

def plainTextToHtml(txt: str) -> str:
    ''' If no HTML closing tags are found it converts plain text to basic html
        Only new lines are converted to `<p>` and `<br>` tags. 
    '''
    if txt.find('</') > -1 or txt.find('/>') > -1:
        return txt
    else:
        txt = f'<p>{ txt }</p>'
        txt = txt.replace("\\n\\n", "</p><p>")
        txt = txt.replace('\n', '<br />')
        return txt

def prettyHtml(html: str, starting_indent=2) -> str:
    ''' Takes html and pretty prints it. The cpu overhead for this might not be worthwhile once in production, however for now it is on.
    This may change in the future in favor of a minified html

        Params:
            - html: a string of html to be pretty printed  
            - starting_indent=2: this controls the indent level when matching existing pretty html
    '''
    html = html.replace('>', '>\n').replace('<', '\n<')
    html = html.replace('  ', ' ').replace(' "', '"')
    html = html.replace('" >', '">')
    prettyHtml = []
    ## Set the default indent if the template changes and there is another parent tag before the body html
    indent = starting_indent
    indent_char = ''
    buffer = ''
    no_indent_flag = False
    inside_text_area = False
    for line in html.split('\n'):
        # If we hit the text area end we want to strip that line 
        if line.find("</textarea") >= 0:
            inside_text_area = False
        
        if inside_text_area:
            line = line.replace('  ', '    ')
        else:
            line = line.strip()

        # After we strip the text area line we want to set the inside text area flag to True so we dont strip 
        # formatting from text areas when displaying them
        if line.strip()[0:9] == "<textarea":
            inside_text_area = True 

        if line != '':    
            # Get the first line into the buffer           
            if buffer == '':
                buffer = line     
            # If line does not start with a new tag add to buffer unless the previous line does not end with a close tag
            # and buffer[-1] == '>'  fixes text area fields by stacking text in a textarea field          
            elif line[0] != '<' and buffer[-1] == '>':
                buffer += line
            # If the buffer ends with a closing tag 
            elif line[0] == '<' and buffer[-1] != '>':
                buffer += line
            # Dont add a new line if it's a text area
            elif line[0:10] == '</textarea':
                buffer += '\n' + line
            else:
                # Fix for textarea not indenting the contents like it's a tag
                if buffer[0] != '<':
                    if no_indent_flag == False:
                        indent -= 1
                        no_indent_flag = True
                    prettyHtml.append(buffer)
                else:
                    no_indent_flag = False
                    # If closing tag remove indent
                    if buffer[0:2] == '</':
                        indent -= 1
                    prettyHtml.append(indent_char * indent + buffer )
                    if buffer.find('/') == -1:
                        indent += 1
                buffer = line
        # An empty line in a text area should be considered a new line
        elif inside_text_area:
            buffer += '\n'

    # Catch the last buffer since it's once behind the loop it doesnt get appended when the loop ends
    prettyHtml.append(indent_char * indent + buffer )
    return "\n".join(prettyHtml)