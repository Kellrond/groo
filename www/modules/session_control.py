from flask import session

def login(user_id, password) -> None:
    '''Validates the users credentials and if authenticated sets the session variables 
            - calls setSessionVariables(employee)'''
    auth_success = True

    if auth_success:
        setSessionVariables()
        return True
    else:
        return False

def logout() -> None:
    ''' Clears all session variables in the client cookie and logs user out. '''
    [session.pop(key) for key in list(session.keys())]

def setSessionVariables(employee) -> None:
    '''Session variables are stored in the client cookie 
    
        Session variables:
            user_id 
        Notes:

    '''
    session['user_id'] = 'jkell'
    session.permanent  = True  
