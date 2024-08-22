def list_to_string(list):
    result = ""
    for item in list:
        result += str(item) + ";"

    return result[:-1]

def string_to_list(string):
    
    string_list = string.split(";") 
    result = [0] * len(string_list)
    
    for i, item in enumerate(string_list):
        result[i] = int(item)
    
    return result

def print_update(msg, entity_name):

    final_msg = '\n'
    final_msg += '===============================================================================\n'
    final_msg += msg + '\n'
    final_msg += '===============================================================================\n' 

    print(msg)

    with open('output/' + entity_name + '.txt', 'a') as file:
        file.write(final_msg)
