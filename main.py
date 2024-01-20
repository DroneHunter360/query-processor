import ast, random, re

tables = {}

def generate_random_string(length):
    characters = random.choices(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        k=length
    )
    random_string = ''.join(characters)
    return random_string

def helper(query):
    ctr = 0
    arg1 = ""
    for i in query:
        if i == '(':
            ctr += 1
        elif i == ')':
            ctr -= 1
            if ctr == 0:
                arg1 += ')'
                return arg1
        arg1 += i

def resolve_condition(condition):
    condition = condition.strip().split()
    lhs, op, rhs = condition[0], condition[1], condition[2]
    return [lhs, op, rhs]

def resolve(query):
    # selection
    if query[0] == '$':
        table_name = helper(query[1:])
        condition = helper(query[len(table_name)+1:])
        condition = re.sub(r'^\((.*)\)$', r'\1', condition)
        lhs = resolve_condition(condition)
        if lhs:
            lhs = lhs[0]
        
        table_name = re.sub(r'^\((.*)\)$', r'\1', table_name)
        if table_name not in tables:
            table = resolve(table_name)
            table_name = "new_table_" + generate_random_string(10)
            tables[table_name] = table
            
        # at this point, you should have a table that actually exists in tables
        result = {"relations": [], "attributes": tables[table_name]["attributes"]}
        attribute_index = tables[table_name]["attributes"].index(lhs)
        for tuple in tables[table_name]["relations"]:
            if eval(condition, {lhs: tuple[attribute_index]}):
                result["relations"].append(tuple)
        
        return result
    
    # projection
    if query[0] == '#':
        table_name = helper(query[1:])
        columns = helper(query[len(table_name)+1:]).strip('()').split(',')
        for i in range(len(columns)):
            columns[i] = columns[i].strip()
        
        table_name = re.sub(r'^\((.*)\)$', r'\1', table_name)
        if table_name not in tables:
            table = resolve(table_name)
            table_name = "new_table_" + generate_random_string(10)
            tables[table_name] = table
            
        # at this point, you should have a table that actually exists in tables
        result = {"relations": [], "attributes": columns}
        for tuple in tables[table_name]["relations"]:
            temp_tuple = []
            for col in columns:
                attribute_index = tables[table_name]["attributes"].index(col)
                temp_tuple.append(tuple[attribute_index])
            result["relations"].append(temp_tuple)
        
        return result

    
    # inner join, left/right/full outer join
    if query[0] == 'J' or query[0] == 'L':
        table_1_name = helper(query[1:])
        table_2_name = helper(query[len(table_1_name)+1:])
        condition = helper(query[len(table_1_name) + len(table_2_name) + 1:])
        condition = re.sub(r'^\((.*)\)$', r'\1', condition)
        lhs, rhs = resolve_condition(condition)[0], resolve_condition(condition)[2]

        table_1_name = re.sub(r'^\((.*)\)$', r'\1', table_1_name)
        table_2_name = re.sub(r'^\((.*)\)$', r'\1', table_2_name)
        if table_1_name not in tables:
            table = resolve(table_1_name)
            table_1_name = "new_table_" + generate_random_string(10)
            tables[table_1_name] = table

        if table_2_name not in tables:
            table = resolve(table_2_name)
            table_2_name = "new_table_" + generate_random_string(10)
            tables[table_2_name] = table
        
        result = {"relations": [], "attributes": tables[table_1_name]["attributes"] + tables[table_2_name]["attributes"]}
        attribute_index = tables[table_1_name]["attributes"].index(lhs)
        attribute_index_2 = tables[table_2_name]["attributes"].index(rhs)

        for tuple in tables[table_1_name]["relations"]:
            eval_true = False
            for tuple2 in tables[table_2_name]["relations"]:
                if lhs == rhs:
                    condition = condition.replace(lhs, lhs + '1', 1)
                    lhs += '1'

                if eval(condition, {lhs: tuple[attribute_index], rhs: tuple2[attribute_index_2]}):
                    joined_tuple = tuple + tuple2
                    result["relations"].append(joined_tuple)
                    eval_true = True

            if not eval_true:   
                if query[0] == 'L' or query[0] == 'F':
                    null_tuple = (None,) * (len(result["attributes"]) - len(tuple))
                    joined_tuple = tuple + null_tuple
                    result["relations"].append(joined_tuple)
                if query[0] == 'R' or query[0] == 'F':
                    null_tuple = (None,) * (len(result["attributes"]) - len(tuple2))
                    joined_tuple = null_tuple + tuple2
                    result["relations"].append(joined_tuple)

        return result

    # need to separate right outer join case because the nested tuple looping is swapped (i.e. loop over rhs table first and lhs is the inner nested loop)
    if query[0] == 'R':
        table_1_name = helper(query[1:])
        table_2_name = helper(query[len(table_1_name)+1:])
        condition = helper(query[len(table_1_name) + len(table_2_name) + 1:])
        condition = re.sub(r'^\((.*)\)$', r'\1', condition)
        lhs, rhs = resolve_condition(condition)[0], resolve_condition(condition)[2]

        table_1_name = re.sub(r'^\((.*)\)$', r'\1', table_1_name)
        table_2_name = re.sub(r'^\((.*)\)$', r'\1', table_2_name)
        if table_1_name not in tables:
            table = resolve(table_1_name)
            table_1_name = "new_table_" + generate_random_string(10)
            tables[table_1_name] = table

        if table_2_name not in tables:
            table = resolve(table_2_name)
            table_2_name = "new_table_" + generate_random_string(10)
            tables[table_2_name] = table
        
        result = {"relations": [], "attributes": tables[table_1_name]["attributes"] + tables[table_2_name]["attributes"]}
        attribute_index = tables[table_1_name]["attributes"].index(lhs)
        attribute_index_2 = tables[table_2_name]["attributes"].index(rhs)

        for tuple2 in tables[table_2_name]["relations"]:
            eval_true = False
            for tuple in tables[table_1_name]["relations"]:
                if lhs == rhs:
                    condition = condition.replace(lhs, lhs + '1', 1)
                    lhs += '1'

                if eval(condition, {lhs: tuple[attribute_index], rhs: tuple2[attribute_index_2]}):
                    joined_tuple = tuple + tuple2
                    result["relations"].append(joined_tuple)
                    eval_true = True

            if not eval_true:
                null_tuple = (None,) * (len(result["attributes"]) - len(tuple2))
                joined_tuple = null_tuple + tuple2
                result["relations"].append(joined_tuple)

        return result


    if query[0] == 'F':
        table_1_name = helper(query[1:])
        table_2_name = helper(query[len(table_1_name)+1:])
        condition = helper(query[len(table_1_name) + len(table_2_name) + 1:])
        condition = re.sub(r'^\((.*)\)$', r'\1', condition)
        lhs, rhs = resolve_condition(condition)[0], resolve_condition(condition)[2]

        table_1_name = re.sub(r'^\((.*)\)$', r'\1', table_1_name)
        table_2_name = re.sub(r'^\((.*)\)$', r'\1', table_2_name)
        if table_1_name not in tables:
            table = resolve(table_1_name)
            table_1_name = "new_table_" + generate_random_string(10)
            tables[table_1_name] = table

        if table_2_name not in tables:
            table = resolve(table_2_name)
            table_2_name = "new_table_" + generate_random_string(10)
            tables[table_2_name] = table
        
        result = {"relations": [], "attributes": tables[table_1_name]["attributes"] + tables[table_2_name]["attributes"]}
        relations_set = set()
        attribute_index = tables[table_1_name]["attributes"].index(lhs)
        attribute_index_2 = tables[table_2_name]["attributes"].index(rhs)

        for tuple in tables[table_1_name]["relations"]:
            eval_true = False
            for tuple2 in tables[table_2_name]["relations"]:
                if lhs == rhs:
                    condition = condition.replace(lhs, lhs + '1', 1)
                    lhs += '1'

                if eval(condition, {lhs: tuple[attribute_index], rhs: tuple2[attribute_index_2]}):
                    joined_tuple = tuple + tuple2
                    relations_set.add(joined_tuple)
                    eval_true = True

            if not eval_true:   
                if query[0] == 'L' or query[0] == 'F':
                    null_tuple = (None,) * (len(result["attributes"]) - len(tuple))
                    joined_tuple = tuple + null_tuple
                    relations_set.add(joined_tuple)
                if query[0] == 'R' or query[0] == 'F':
                    null_tuple = (None,) * (len(result["attributes"]) - len(tuple2))
                    joined_tuple = null_tuple + tuple2
                    relations_set.add(joined_tuple)

        for tuple2 in tables[table_2_name]["relations"]:
            eval_true = False
            for tuple in tables[table_1_name]["relations"]:
                if lhs == rhs:
                    condition = condition.replace(lhs, lhs + '1', 1)
                    lhs += '1'

                if eval(condition, {lhs: tuple[attribute_index], rhs: tuple2[attribute_index_2]}):
                    joined_tuple = tuple + tuple2
                    relations_set.add(joined_tuple)
                    eval_true = True

            if not eval_true:
                null_tuple = (None,) * (len(result["attributes"]) - len(tuple2))
                joined_tuple = null_tuple + tuple2
                relations_set.add(joined_tuple)

        result["relations"].append(list(relations_set))
        return result

    # union
    if query[0] == 'U' or query[0] == 'D' or query[0] == 'I':
        table_1 = helper(query[1:])
        table_2 = helper(query[len(table_1)+1:])
        table_1 = table_name = re.sub(r'^\((.*)\)$', r'\1', table_1)
        table_2 = table_name = re.sub(r'^\((.*)\)$', r'\1', table_2)

        if table_1 not in tables:
            table = resolve(table_1)
            table_1 = "new_table_" + generate_random_string(10)
            tables[table_1] = table

        if table_2 not in tables:
            table = resolve(table_2)
            table_2 = "new_table_" + generate_random_string(10)
            tables[table_2] = table

        # ensure data types of both tables are identical
        if tables[table_1]["attributes"] != tables[table_2]["attributes"]:
            return {}

        # for attributes, need to perform logic to union that too
        if query[0] == 'U':
            tuple_set = set(tables[table_1]["relations"]).union(set(tables[table_2]["relations"]))
        elif query[0] == 'D':
            tuple_set = set(tables[table_1]["relations"]).difference(set(tables[table_2]["relations"]))
        elif query[0] == 'I':
            tuple_set = set(tables[table_1]["relations"]).intersection(set(tables[table_2]["relations"]))   
        
        result = {"relations": list(tuple_set), "attributes": tables[table_1]["attributes"]}

        return result
    
def parse_relation(relation):
    # Define a regular expression pattern
    pattern = re.compile(r'(\w+)\s*\(([^)]+)\)\s*=\s*{([^}]+)}', re.DOTALL)

    # Use the pattern to match the input string
    match = pattern.match(relation)

    if match:
        # Extract the three sections
        table_name = match.group(1)
        attributes = [attr.strip() for attr in match.group(2).split(',')]
        tuples = match.group(3)
        
        repeater = '[^\\n,]*,'
        for i in range(len(attributes) - 1):
            repeater += '\s*[^\\n,]*'
            if i != len(attributes) - 2:
                repeater += ','
        tuple_reg_pattern = r'(' + repeater + ')'
        
        tuples = re.findall(tuple_reg_pattern, tuples)
        for i in range(len(tuples)):
            # take in the string tuple and create an actual tuple
            # takes care of parsing/identifying which values of the tuple are strings, numbers, etc.
            temp = ast.literal_eval("(" + tuples[i] + ")")
            tuples[i] = temp
    else:
        print("No match found.")

    return [table_name, attributes, tuples]

def loadInput(filename):
    f = open(filename, "r")
    input = f.read() 

    # Define a regex pattern to match the entire relation
    pattern = re.compile(r'(\w+\s*\(.*?\)\s*=\s*{.*?})', re.DOTALL)

    # Find all matches using the regex pattern
    matches = pattern.findall(input)

    # Print the result
    for relation in matches:
        [table_name, attributes, relation] = parse_relation(relation)
        tables[table_name] = {}
        tables[table_name]["relations"] = relation
        tables[table_name]["attributes"] = attributes 

       
query = "J(Student)(takes)(id == sid)"
loadInput("input.txt")

print(tables)
print("Query: " + query)
print("\nThe result set:")
print(resolve(query))