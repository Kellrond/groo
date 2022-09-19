# # This file is just here to provide fake data to the skeletons
# # Do not use as template for new files 
# from random import randrange

# def returnExampleListById(example_id) -> list:
#     ''' Returns and example list of dicts
    
#         `{'id': 1, 'ex_value': "a", 'ex_text': 'abc'}`
#     '''
#     return [
#             {'id': 1, 'ex_value': "a", 'ex_text': 'abc'},
#             {'id': 2, 'ex_value': "d", 'ex_text': 'def'},
#             {'id': 3, 'ex_value': "g", 'ex_text': 'ghi'},
#         ]

# def updateExampleDb(form_data):
#     #-- Returns True if success or False
#     return True

# def returnExamplePagination(active, page=1) -> dict:
#     page = int(page) - 1 # adjust for pagination offest to start from 1

#     stub = [] 
#     for i in range(10, randrange(50, 100)):
#         stub.append({
#             'text_field': f'text-{i}',
#             'select_field': f'select-{i}',
#             'date_field': f'20{i}-10-01',
#             'number_field': f'{i}',
#             'text_area': f'textarea-{i}',
#             'select_multiple': f'selectmultiple-{i} Something really long to demo the tables',
#             'active': True if randrange(0,2) == 1 else False
#         })

#     return { 'count': len(stub), 'results': [ x for x in stub if x.get('active') == active ][0:10] }