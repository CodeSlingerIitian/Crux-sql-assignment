# from sqlglot import *
import sqlglot
from sqlglot.optimizer.scope import build_scope
from sqlglot import exp

class WhereResolver():
    """
    The WhereResolver class can be used to find elements of the WHERE 
    clause for the main query. It considers the outermost query as the main query.
    """
    def __init__(self, query) -> None:
        self.query = query

        # Build an AST from the query by parsing
        self.ast = sqlglot.parse_one(query)

        # Building a scope tree from the AST
        self.root = build_scope(self.ast)

        self._where_details = []
        self._tables = []
        self.scopes = []
        for scope in self.root.traverse():
            self.scopes.append(scope)
        
        # Getting the scope of the outermost query as the main query scope
        self.main_query_scope = self.scopes[-1]

    def check_where_in_main_query(self):
        """
        Checks if there is a WHERE clause in the main query or not. Returns a corresponding
        boolean value.
        """
        pass

    def extract_where_elements(self):
        """
        Method to get the elements of the WHERE clause
        """
        where_expression = self.main_query_scope.expression.find(exp.Where)
        self._extract_where_column_details(where_expression.this)
        self._find_table(self.main_query_scope)
        response_object = {}
        response_object['table'] = self._tables
        response_object['where_details'] = self._where_details
        return response_object

    def _extract_where_column_details(self, expression):

        #We check if the expression has binary operators or logical using cases
        
        #if expression has IN Clause
        if isinstance(expression, exp.In):
            column = expression.this.name if isinstance(expression.this, exp.Column) else None
            clause = 'IN'
            value = 'CTE'
            self._where_details.append({"Column Name": column, "Clause": clause, "Value": value})

        #if expression has AND or OR operator
        elif isinstance(expression, exp.And) or isinstance(expression, exp.Or):

            #in case of logical operators, we need to evaluate both, the left and the right operands individually.
            self._extract_where_column_details(expression.left)
            self._extract_where_column_details(expression.right)

        elif isinstance(expression, exp.Binary):
            # Extract column name
            column = expression.left.name if isinstance(expression.left, exp.Column) else None
            # Extract operator
            operator = expression.__class__.__name__
            # Extract value
            value = expression.right.this if isinstance(expression.right, exp.Literal) else None
            self._where_details.append({"Column Name": column, "Operator": operator, "Value": value})

    def _find_table(self, scope):
        """
        Recursive function that traverses the scopes and finds the actual 
        underlying tables and returns a list of all the tables in the scope 
        and not the aliases.

        Working: 
        scope.selcted_source() returns a dictionary with the alias name as key, and value as a list of two elements,
        the current AST node, and the source element which is the source of this node. 
        We check that if the source node is an instance of type Table, then its an actual table in the query, otherwise
        it would be another scope element for a child sub query which has the source for this alias.
        Thus it the function calls itsef recursively till it finds a table instance.
        """
        for alias, (node, source) in scope.selected_sources.items():
            if isinstance(source, exp.Table):
                self._tables.append(source.this.this)
            else:
                return self._find_table(source)


query = """
SELECT name FROM (SELECT * FROM employees WHERE department = 'HR') AS dept_hr;
"""
w = WhereResolver(query)
print(w.extract_where_elements())