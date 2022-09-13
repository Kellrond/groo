# from    functools   import wraps
# from    flask       import flash, redirect, session, url_for

# def permissions_required(permission: int) -> None:
#     ''' Python Decorator. Sets the minimum permission level required to access the resource
    
#         Usage:
#             `#@permissions_required(config.Permissions.dc_manager)
#             def function(param): ...`

#         Notes:
#             - https://peps.python.org/pep-0318/ for Python decorator docs
#     '''
#     def decorator(function):
#         @wraps(function)
#         def wrapper(*args, **kwargs):
#             if not session.get('user_id'):
#                 flash("You are not logged in", "warning")
#                 return redirect(url_for('home.home'))
#             elif not session.get('permissions', 0) >= permission:
#                 flash("You do not have permissions", "warning")
#                 return redirect(url_for('home.home'))                
#             return function(*args, **kwargs)
#         return wrapper
#     return decorator


