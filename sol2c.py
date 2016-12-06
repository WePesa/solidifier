import json
import sys

"""
AST keywords
"""
class SolKeywords:
    key_source_unit = 'SourceUnit'
    key_contract = 'ContractDefinition'
    key_function = 'FunctionDefinition'
    key_param_list = 'ParameterList'
    key_var_decl = 'VariableDeclaration'
    key_var_def_stat = 'VariableDefinitionStatement'
    key_block = 'Block'
    key_return = 'Return'
    key_unary_op = 'UnaryOperation'
    key_binary_op = 'BinaryOperation'
    key_identifier = 'Identifier'
    key_literal = 'Literal'
    key_enum = 'EnumDefinition'
    key_enum_value = 'EnumValue'
    key_struct = 'StructDefinition'
    key_binary_op_exp = '**'
    key_if = 'IfStatement'
    key_expr = 'ExpressionStatement'
    key_function_call = 'FunctionCall'
    key_member_access = 'MemberAccess'
    key_assignment = 'Assignment'
    key_elem_typename_expr = 'ElementaryTypenameExpression'
    key_elem_typename = 'ElementaryTypeName'
    key_array_typename = 'ArrayTypeName'
    key_user_typename = 'UserDefinedTypeName'
    key_for = 'ForStatement'
    key_while = 'WhileStatement'
    key_idx_access = 'IndexAccess'
    key_pragma = 'PragmaDirective'
    key_mapping = 'Mapping'
    key_type_address = 'address'
    key_type_uint = 'uint'
    key_throw = 'Throw'
    key_length = 'length'
    key_storage_ptr = 'storage pointer'
    key_storage = 'storage'
    key_type_msg = 'msg'
    key_tuple_expr = 'TupleExpression'


"""
Translates Solidity AST to C
"""
class CTranslator:

    """
    Variable containing the translation to C
    """
    C_source = None

    """
    List of keywords
    """
    keywords = None

    """
    Assume, Assert and Nondet functions
    """
    verif_functions = None

    """
    Header of the C file
    """
    C_header = None

    """
    Custom mappings
    """
    mappings = None

    """
    Array structs
    """
    array_structs = None

    """
    Extra header
    """
    extra_header = None

    """
    Header flag
    """
    add_to_header = None

    """
    True if code inside a function call
    """
    in_fcall = None

    """
    Helper functions
    """
    def error(self, msg):
        print msg
        sys.exit(1)

    def not_supported(self, op):
        self.error('Operation not supported: ' + str(op))

    def check_type(self, data, keyword):
        if data['name'] != keyword:
            self.error('Node of type ' + keyword + ' has type ' + data['name'])

    def add_line(self, code):
        if not self.add_to_header:
            self.C_source += code + '\n'
        else:
            self.extra_header += code + '\n'

    def add(self, code):
        if not self.add_to_header:
            self.C_source += code
        else:
            self.extra_header += code

    def add_newline(self):
        if not self.add_to_header:
            self.C_source += '\n'
        else:
            self.extra_header += '\n'

    def add_commentline(self, comment):
        if not self.add_to_header:
            self.C_source += '//' + comment + '\n'
        else:
            self.extra_header += '//' + comment + '\n'

    def add_comment(self, comment):
        if not self.add_to_header:
            self.C_source += '//' + comment
        else:
            self.extra_header += '//' + comment

    def close_command(self, cname):
        return cname in ['UnaryOperation', 'Assignment', 'VariableDeclaration', 'VariableDefinitionStatement', 'FunctionCall', 'ExpressionStatement']

    def create_mapping(self, mapping, type1, type2):
        if mapping in self.mappings:
            return
        line = 'struct _' + mapping + '\n{\n\tuint id;\n\t' + type2 + ' data[NONDET_SIZE];\n};\ntypedef struct _' + mapping + ' ' + mapping + ';\n'
        self.extra_header += '\n' + line + '\n'
        self.mappings.append(mapping)

    def create_array_struct(self, atype):
        if atype in self.array_structs:
            return
        line = 'struct _array_' + atype + '\n{\n\tuint length;\n\t' + atype + ' data[NONDET_SIZE];\n};\ntypedef struct _array_' + atype + ' array_' + atype + ';\n'
        self.extra_header += '\n' + line + '\n'
        self.array_structs.append(atype)

    def create_struct_constructor(self, data):
        sname = data['attributes']['name']
        self.add(sname + '\n' + 'constructor_' + sname + '(')
        for i in range(len(data['children'])):
            if i > 0:
                self.add(',')
            self.translate(data['children'][i])
        self.add(')\n{\n\t' + sname + ' tmp_var = {')
        for i in range(len(data['children'])):
            if i > 0:
                self.add(',')
            self.add(data['children'][i]['attributes']['name'])
        self.add('};\n\treturn tmp_var;\n}')


    """
    Translators
    """
    def t_children(self, data):
        for c in data['children']:
            self.translate(c)
            if data['name'] in [self.keywords.key_block, self.keywords.key_contract, self.keywords.key_struct, self.keywords.key_for]:
                if self.close_command(c['name']):
                    self.add_line(';')

    def t_source_unit(self, data):
        self.check_type(data, self.keywords.key_source_unit)
        self.t_children(data)

    def t_contract(self, data):
        self.check_type(data, self.keywords.key_contract)
        at = data['attributes']
        self.add_commentline('Translation of contract ' + at['name'])
        self.t_children(data)

    def t_function(self, data):
        at = data['attributes']
        if at['name'] in self.verif_functions:
            return
        params_node = data['children'][0]
        ret_node = data['children'][1]
        block_node = data['children'][2]
        ret_type = 'void'
        ret_var = ''
        ret_var_node = None
        if len(ret_node['children']) > 0:
            ret_type = ret_node['children'][0]['children'][0]['attributes']['name']
            ret_var = ret_node['children'][0]['attributes']['name']
            ret_var_node = ret_node['children'][0]
        f_sig = ret_type + ' ' + at['name']
        self.add(f_sig)
        self.add('(')
        new_defs = ''
        for i in range(0, len(params_node['children'])):
            if i > 0:
                self.add(',')
            param = params_node['children'][i]
            ctype = param['attributes']['type']
            if ctype == self.keywords.key_type_address:
                cname = param['attributes']['name']
                self.add('uint ' + cname + '_real_x')
                new_defs += 'address ' + cname + ';\n' + cname + '.x = ' + cname + '_real_x;\n';
            else:
                self.translate(param)
        self.add_line(')')
        self.add_line('{')
        self.add_line(new_defs)
        if len(ret_var) > 0:
            self.add_line(ret_type + ' ' + ret_var + ';')
        self.translate(block_node)
        if len(ret_var) > 0:
            self.add_line('return ' + ret_var + ';')
        self.add_line('}')

    def t_param_list(self, data):
        if len(data['children']) == 0:
            return
        param1 = data['children'][0]
        self.translate(param1)
        for i in range(1, len(data['children'])):
            self.add(',')
            self.translate(data['children'][i])

    def t_var_decl(self, data):
        at = data['attributes']
        var_name = at['name']
        c0 = data['children'][0]
        if c0['name'] == self.keywords.key_array_typename:
            atype = c0['children'][0]['attributes']['name']
            self.create_array_struct(atype)
            new_type = 'array_' + atype
            self.add(new_type + ' ' + var_name);
        else:
            self.t_children(data)
            self.add(' ' + var_name)
        
    def t_var_def_stat(self, data):
        c = data['children'][0]
        self.translate(c)
        if len(data['children']) > 1:
            if c['attributes']['type'] == self.keywords.key_type_address:
                self.add_line(';')
                self.add(c['attributes']['name'] + '.x')
            self.add(' = ')
            self.translate(data['children'][1])

    def t_block(self, data):
        self.t_children(data)

    def t_return(self, data):
        self.add('return ')
        self.t_children(data)
        self.add_line(';')

    def t_unary_op(self, data):
        self.add(data['attributes']['operator'])
        self.t_children(data)

    def t_binary_op(self, data):
        op0 = data['children'][0]
        op1 = data['children'][1]
        self.translate(op0)
        op = data['attributes']['operator']
        if op == self.keywords.key_binary_op_exp:
            self.not_supported(op)
        self.add(op)
        self.translate(op1)

    def t_identifier(self, data):
        iname = data['attributes']['value']
        self.add(iname)
        if data['attributes']['type'] == self.keywords.key_type_address:
            self.add('.x')

    def t_literal(self, data):
        self.add(data['attributes']['value'])

    def t_enum(self, data):
        self.add('enum ' + data['attributes']['name'] + ' { ')
        if len(data['children']) > 0:
            e0 = data['children'][0]
            self.translate(e0)
            for i in range(1, len(data['children'])):
                self.add(',')
                self.translate(data['children'][i])
        self.add_line(' } ;')

    def t_enum_value(self, data):
        self.add(data['attributes']['name'])

    def t_struct(self, data):
        sname = data['attributes']['name']
        self.add_to_header = True
        self.add_line('struct ' + '_' + sname)
        self.add_line('{')
        self.t_children(data)
        self.add_newline()
        self.add_line('};')
        self.add_line('typedef struct _' + sname + ' ' + sname + ';')
        self.create_struct_constructor(data)
        self.add_to_header = False

    def t_if(self, data):
        self.add('if (')
        self.translate(data['children'][0])
        self.add_line(')')
        self.add_line('{')
        self.translate(data['children'][1])
        self.add_newline()
        self.add_line('}')
        if len(data['children']) > 2:
            self.add_line('else')
            self.add_line('{')
            self.translate(data['children'][2])
            self.add_newline()
            self.add_line('}')

    def t_expr(self, data):
        self.t_children(data)
        #for child in data['children']:
            #self.translate(child)
            #cname = child['name']
            #if self.close_command(cname):
            #    self.add_line(';')
            
    def t_function_call(self, data):
        self.in_fcall = True
        c = data['children'][0]
        if c['name'] == self.keywords.key_member_access:
            t = c['children'][0]['attributes']['type']
            n = c['children'][0]['attributes']['value']
            f = c['attributes']['member_name']
            if t == self.keywords.key_type_address:
                if f == 'send':
                    self.add('address_send(&this, &' + n + ', ')
                    self.translate(data['children'][1])
                    self.add(')')
                else:
                    self.not_supported('method ' + f + ' of type ' + self.keywords.key_type_address)
            elif self.keywords.key_storage in t:
                if f == 'push':
                    self.add(n + '.data[' + n + '.length] = ')
                    self.translate(data['children'][1])
                    self.add(';\n' + n + '.length++')
                else:
                    self.not_supported('method ' + f + ' of type ' + self.keywords.key_array_typename)
        else:
            if 'struct' in data['attributes']['type'] :
                self.add('constructor_')
            self.translate(data['children'][0])
            self.add('(')
            for i in range(1, len(data['children'])):
                if i > 1:
                    self.add(',')
                self.translate(data['children'][i])
            self.add(')')
        self.in_fcall = False

    def t_member_access(self, data):
        member_name = data['attributes']['member_name']
        self.t_children(data)
        self.add('.' + member_name)
        if data['attributes']['type'] == self.keywords.key_type_address:
            self.add('.x')

    def t_assignment(self, data):
        self.translate(data['children'][0])
        self.add(data['attributes']['operator'])
        self.translate(data['children'][1])

    def t_elem_typename_expr(self, data):
        self.add('(')
        if data['attributes']['value'] == self.keywords.key_type_address:
            self.add(self.keywords.key_type_uint)
        else:
            self.add(data['attributes']['value'])
        self.add(')')

    def t_elem_typename(self, data):
        self.add(data['attributes']['name'])

    def t_user_typename(self, data):
        self.add(data['attributes']['name'])

    def t_array_typename(self, data):
        self.translate(data['children'][0])
        #self.add('[')
        #if len(data['children']) > 1:
        #    self.translate(data['children'][1])
        #self.add(']')

    def t_for(self, data):
        self.add('for (')
        i = 0
        while i < (len(data['children']) - 1):
            if i > 0:
                self.add(';')
            self.translate(data['children'][i])
            i += 1
        self.add_line(')')
        self.add_line('{')
        self.translate(data['children'][i])
        self.add_newline()
        self.add_line('}')

    def t_while(self, data):
        self.add('while (')
        self.translate(data['children'][0])
        self.add_line(')')
        self.add_line('{')
        self.translate(data['children'][1])
        self.add_line('}')

    def t_idx_access(self, data):
        self.translate(data['children'][0])
        atype = data['children'][0]['attributes']['type']
        if 'mapping' in atype or self.keywords.key_storage in atype or 'memory' in atype:
            self.add('.data')
        self.add('[')
        self.translate(data['children'][1])
        self.add(']')

    def t_pragma(self, data):
        pass

    def t_mapping(self, data):
        c0 = data['children'][0]
        c1 = data['children'][1]
        if c0['name'] != self.keywords.key_elem_typename:
            self.not_supported(data)
        name0 = c0['attributes']['name']
        name1 = c1['attributes']['name']
        custom_mapping = 'mapping_' + name0 + '_' + name1
        if not custom_mapping in self.mappings:
            self.create_mapping(custom_mapping, name0, name1)
        self.add(custom_mapping)
        #self.add('mapping_')
        #self.translate(data['children'][0])
        #self.add('_')
        #self.translate(data['children'][1])

    def t_throw(self, data):
        self.add_line('throw();')

    def t_tuple_expr(self, data):
        self.add('(')
        self.t_children(data)
        self.add(')')
        

    """
    List of function pointers
    """
    function_list = None

    """
    Main demux
    """
    def translate(self, data):
        name = data['name']
        if not self.function_list.has_key(name):
            self.error('Solidifier:\nOperation not supported: ' + str(data))
        self.function_list[data['name']](data)

    def translate_to_C(self, fname):
        json_data = open(fname)
        data = json.load(json_data)
        self.C_source = '' 
        self.mappings = []
        self.array_structs = []
        self.extra_header = ''
        self.add_to_header = True
        self.in_fcall = False
        self.translate(data)
        json_data.close()
        return self.C_header + '\n' +  self.extra_header + '\n' + self.C_source

    """
    Constructor
    """
    def __init__(self):
        self.verif_functions = ['assume', 'assert', 'nondet_uint', 'nondet_address', 'set_msg_sender']
        self.C_header = '#include "seahorn/seahorn.h"\n#include "solidifier.h"\n'
        self.keywords = SolKeywords()
        self.function_list = {
                self.keywords.key_source_unit : self.t_source_unit,
                self.keywords.key_contract : self.t_contract,
                self.keywords.key_function : self.t_function,
                self.keywords.key_param_list : self.t_param_list,
                self.keywords.key_var_decl : self.t_var_decl,
                self.keywords.key_var_def_stat : self.t_var_def_stat,
                self.keywords.key_block : self.t_block,
                self.keywords.key_return : self.t_return,
                self.keywords.key_unary_op : self.t_unary_op,
                self.keywords.key_binary_op : self.t_binary_op,
                self.keywords.key_identifier : self.t_identifier,
                self.keywords.key_literal : self.t_literal,
                self.keywords.key_enum : self.t_enum,
                self.keywords.key_enum_value : self.t_enum_value,
                self.keywords.key_struct : self.t_struct,
                self.keywords.key_if : self.t_if,
                self.keywords.key_expr : self.t_expr,
                self.keywords.key_function_call : self.t_function_call,
                self.keywords.key_member_access : self.t_member_access,
                self.keywords.key_assignment : self.t_assignment,
                self.keywords.key_elem_typename_expr : self.t_elem_typename_expr,
                self.keywords.key_elem_typename : self.t_elem_typename,
                self.keywords.key_array_typename : self.t_array_typename,
                self.keywords.key_user_typename : self.t_user_typename,
                self.keywords.key_for : self.t_for,
                self.keywords.key_while : self.t_while,
                self.keywords.key_idx_access : self.t_idx_access,
                self.keywords.key_pragma : self.t_pragma,
                self.keywords.key_mapping : self.t_mapping,
                self.keywords.key_throw : self.t_throw,
                self.keywords.key_tuple_expr : self.t_tuple_expr,
                }

