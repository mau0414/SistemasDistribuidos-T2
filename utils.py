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
