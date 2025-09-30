JSONATA_REFERENCE = """
# JSONata Reference Guide

## Introduction
JSONata is a lightweight query and transformation language for JSON data. Inspired by the 'location path' semantics of XPath 3.1, it allows sophisticated queries to be expressed in a compact and intuitive notation. A rich complement of built-in operators and functions is provided for manipulating and combining extracted data, and the results of queries can be formatted into any JSON output structure using familiar JSON object and array syntax.

## Core Concepts

### Path Navigation
- Simple path: `Address.City` - Navigate to nested properties
- Multiple steps: `Account.Order.Product.Price` - Chain navigation steps
- Context reference: `$` - Reference to current context value
- Root reference: `$$` - Reference to root of input JSON

### JSON Value Access
- Object fields: `Address.Street` - Access object properties
- Array items: `Phone[0]` - Access array by index
- Negative index: `Phone[-1]` - Access from end of array
- All array items: `Phone.number` - Process all items implicitly

### Predicates (Filtering)
- Filter by condition: `Phone[type='mobile']` - Keep items matching condition
- Filter by index: `Phone[0]` - Select specific item
- Force array result: `Address[].City` - Return result as array
- Multiple predicates: `Phone[type='office'][number='01962 001234']` - Chain filters

## Operators

### String Operators
- Concatenation: `FirstName & " " & Surname` - Join strings

### Numeric Operators
- Addition: `+` - Add numbers
- Subtraction: `-` - Subtract numbers
- Multiplication: `*` - Multiply numbers 
- Division: `/` - Divide numbers
- Modulo: `%` - Remainder after division

### Boolean Operators
- And: `and` - Logical AND
- Or: `or` - Logical OR

### Path Operators
- Map: `.` - Apply expression to each item
- Filter: `[...]` - Select items that match condition
- Order-by: `^(...)` - Sort by expression
- Order ascending: `^(<Price)` - Sort in ascending order (default)
- Order descending: `^(>Price)` - Sort in descending order
- Multiple sort keys: `^(>Price, <Quantity)` - Sort by multiple criteria
- Reduce: `{...}` - Group and aggregate values
- Wildcard: `*` - Select all properties
- Descendants: `**` - Select all descendants
- Parent: `%` - Select parent object
- Position: `#` - Bind positional variable
- Context: `@` - Bind context variable

## Variables and Functions

### Variables
- Variable assignment: `$var := "value"` - Store value in variable
- Variable reference: `$var` - Use stored value
- Built-in variables: `$`, `$$` - Context and root reference

### Function Definition
- Define function: `function($a, $b) { $a + $b }` - Create function
- Function signature: `<params:return>` - Specify parameter types
- Type symbols:
  - Simple: `b` (boolean), `n` (number), `s` (string), `l` (null)
  - Complex: `a` (array), `o` (object), `f` (function)
  - Union: `(sao)`, `u`, `j`, `x` - Combinations of types
  - Parameterized: `a<s>` (array of strings), `a<x>` (array of any type)
  - Options: `+` (one or more), `?` (optional), `-` (use context)

### Function Application
- Standard call: `$function(arg1, arg2)` - Call function with arguments
- Function chaining: `value ~> $funcA ~> $funcB` - Pipeline functions
- Function composition: `$funcA ~> $funcB` - Create composite function
- Partial application: `$substring(?, 0, 5)` - Create specialized function

### Function Libraries

#### String Functions
- `$string(arg, prettify)` - Convert to string
- `$length(str)` - Get string length
- `$substring(str, start[, length])` - Extract substring
- `$substringBefore(str, chars)` - Get substring before match
- `$substringAfter(str, chars)` - Get substring after match
- `$uppercase(str)` - Convert to uppercase
- `$lowercase(str)` - Convert to lowercase
- `$trim(str)` - Remove whitespace
- `$pad(str, width[, char])` - Pad string to width
- `$contains(str, pattern)` - Test if string contains pattern
- `$split(str, separator[, limit])` - Split string to array
- `$join(array[, separator])` - Join array to string
- `$match(str, pattern[, limit])` - Match regex pattern
- `$replace(str, pattern, replacement[, limit])` - Replace matches
- `$eval(expr[, context])` - Evaluate JSONata expression
- `$base64encode()` - Encode to base64
- `$base64decode()` - Decode from base64
- `$encodeUrlComponent(str)` - URL encode component
- `$encodeUrl(str)` - URL encode full URL
- `$decodeUrlComponent(str)` - URL decode component
- `$decodeUrl(str)` - URL decode full URL

#### Numeric Functions
- `$number(arg)` - Convert to number
- `$abs(number)` - Absolute value
- `$floor(number)` - Round down to integer
- `$ceil(number)` - Round up to integer
- `$round(number[, precision])` - Round to precision
- `$power(base, exponent)` - Raise to power
- `$sqrt(number)` - Square root
- `$random()` - Generate random number
- `$formatNumber(number, picture[, options])` - Format as string
- `$formatBase(number[, radix])` - Format to base
- `$formatInteger(number, picture)` - Format as integer
- `$parseInteger(string, picture)` - Parse integer from string

#### Array Functions
- `$count(array)` - Count items in array
- `$append(array1, array2)` - Combine arrays
- `$sort(array[, function])` - Sort array
- `$reverse(array)` - Reverse array order
- `$shuffle(array)` - Randomize array order
- `$distinct(array)` - Remove duplicates
- `$zip(array1, array2, ...)` - Combine arrays by index

#### Aggregation Functions
- `$sum(array)` - Sum of numbers
- `$max(array)` - Maximum value
- `$min(array)` - Minimum value
- `$average(array)` - Average value

#### Higher Order Functions
- `$map(array, function)` - Transform each item
- `$filter(array, function)` - Keep matching items
- `$single(array, function)` - Find single item
- `$reduce(array, function[, init])` - Aggregate values
- `$sift(object, function)` - Filter object properties

#### Date-Time Functions
- `$now([picture[, timezone]])` - Current timestamp
- `$millis()` - Current time in milliseconds
- `$fromMillis(number[, picture[, timezone]])` - Format timestamp
- `$toMillis(timestamp[, picture])` - Parse timestamp

## Programming Constructs

### Conditional Logic
- Ternary: `condition ? expr1 : expr2` - If-then-else

### Variable Binding
- Assign value: `$var := expr` - Store result in variable
- Block scope: `(expr1; expr2; $var := expr3; expr4)` - Variables local to block

### Function Chaining
- Invocation: `value ~> $funcA ~> $funcB` - Pass results through functions
- Composition: `$funcC := $funcA ~> $funcB` - Create new function

### Recursive Functions
- Self-reference: `$factorial := function($x){ $x <= 1 ? 1 : $x * $factorial($x-1) }`
- Tail recursion: `$iter := function($x, $acc) { $x <= 1 ? $acc : $iter($x - 1, $x * $acc) }`

### Comments
- Block comments: `/* This is a comment */`

## Advanced Features

### Sequence Flattening
- Arrays are flattened automatically when returned from paths
- Force array: `Address[].City` - Return result as array

### Grouping and Aggregation
- Group by key: `Account.Order.Product{`Product Name`: Price}` - Group by name
- Aggregate: `$sum(Account.Order.Product.(Price*Quantity))` - Calculate total

### Data Formatting
- Number format: `$formatNumber(12345.6, "#,###.00")` - Format as "12,345.60"
- Date format: `$fromMillis($millis(), "[M01]/[D01]/[Y0001]")` - Format as MM/DD/YYYY

## Additional Points to Remember
- JSONata is a superset of JSON, any valid JSON is valid JSONata
- Singleton arrays and values are equivalent in expressions
- Functions are first-class values and can be passed as arguments
- Functions are closures and capture their environment
- JSONata supports tail-call optimization for recursive functions
- The context value `$` refers to the current item being processed
- We want to always force array results, so use the force array field[]. syntax
- Explicitly reference each field with full paths, e.g., use $sum(items.qty_ordered * items.price_per_unit) instead of $sum(items.(qty_ordered * price_per_unit)). Avoid using shorthand projection items.(...) for expressions involving multiple fields.
"""
