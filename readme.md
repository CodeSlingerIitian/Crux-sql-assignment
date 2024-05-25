Usage - 

query = """
SELECT name FROM (SELECT * FROM employees WHERE department = 'HR') AS dept_hr;
"""

resolver = WhereResolver(query)
print(w.extract_where_elements())

Packages Used - 
sqlglot
