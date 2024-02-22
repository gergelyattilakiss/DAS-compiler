TOKEN_TYPES = [
    ("def", "\\bdef\\b"),
    ("identifier", "\\b[a-zA-Z]+\\b"),
    ("integer", "\\b[0-9]+\\b"),
    ("colon", ":"),
    ("oparent", "\\("),
    ("cparent", "\\)"),
    ("comma", ","), 
]

struct Token
    type::String
    value::String
end

struct IntegerNode
    value::Integer
end

struct CallNode
    name::String
    arg_exprs::Vector
end

struct VarRefNode
    value::String
end

struct DefinitionNode
    name::String
    arg_names::Vector
    body::CallNode
end



function tokenize(code::AbstractString)
    tokens = []
    while !isempty(code)
        token, code = tokenize_one_token(code)
        push!(tokens, token)
        code = strip(code)
    end
    return tokens
end

function tokenize_one_token(code::AbstractString)
    for type in TOKEN_TYPES
        pattern = Regex("\\A$(type[2])")
        matched = match(pattern, code)
        if matched !== nothing
            value = matched.match
            code = SubString(code, length(value)+1:length(code))
            return Token(type[1], value), code
        end
    end
end

function parse_def(tokens::Vector)
    consume(tokens,"def")
    name = consume(tokens, "identifier")
    arg_names = parse_arg_names(tokens)
    body = parse_expr(tokens)
    return DefinitionNode(name, arg_names, body)
end

function consume(tokens::Vector, expected_type::String)
    token = splice!(tokens, 1)
    if token.type == expected_type
        return token.value
    else
        error_msg = "Expected token type $expected_type but got $(token.type)."
        throw(error(error_msg))
    end
end

function parse_arg_names(tokens::Vector)
    arg_names = []
    consume(tokens, "oparent")
    if peek(tokens, "identifier")
        push!(arg_names, consume(tokens, "identifier"))
        while peek(tokens, "comma")
            consume(tokens, "comma")
            push!(arg_names, consume(tokens, "identifier"))
        end
    end
    consume(tokens, "cparent")
    consume(tokens, "colon")
    return arg_names
end

function parse_expr(tokens::Vector)
    if peek(tokens, "integer")
        return parse_integer(tokens)
    end
    if peek(tokens, "identifier") & peek(tokens, "oparent", 2)
        return parse_call(tokens)
    end
    return parse_var_ref(tokens)
end

function parse_integer(tokens::Vector)
    return IntegerNode(parse(Int,consume(tokens, "integer")))
end

function parse_call(tokens::Vector)
    name = consume(tokens, "identifier")
    arg_exprs = parse_arg_exprs(tokens)
    return CallNode(name, arg_exprs)
end

function parse_var_ref(tokens::Vector)
    return VarRefNode(consume(tokens,"identifier"))
end

function parse_arg_exprs(tokens::Vector)
    arg_exprs = []
    consume(tokens, "oparent")
    if peek(tokens, "cparent") != true
        push!(arg_exprs, parse_expr(tokens))
        while peek(tokens, "cparent") != true
            consume(tokens, "comma")
            push!(arg_exprs, parse_expr(tokens))
        end
    end
    consume(tokens, "cparent")
    return arg_exprs
end

function peek(tokens::Vector, expected_type::String, offset::Integer=1)
    return tokens[offset].type == expected_type
end

tokens = tokenize(read("test.src", String)) 
tree = parse_def(tokens)