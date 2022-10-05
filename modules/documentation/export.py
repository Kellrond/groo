import modules.documentation as documentation

def txtFile(write_path):
    ''' Writes the documentation to a plaintext file. Might get in the way of grep so perhaps 
        the file gets moved after creation? 
    '''

    with open(write_path, 'w') as file:
        file.write('MARCO')

