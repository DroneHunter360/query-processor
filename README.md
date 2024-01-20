# query-processor
Relational Algebra Query Processor

# NOTE FOR CONDITIONS
- lhs, operator, rhs must be space separated
- ex. Age > 9 (VALID)
- ex. Age>9 (INVALID)

# NOTE FOR JOINS
- since we only provide support for equi and nautral joins, don't need to explicity write the table names in the condition
- ex. JOIN STUDENT, TAKES ON Student.id = Takes.sid (DON'T NEED THIS)
- rather, do this -> JOIN STUDENT, TAKES ON id = sid
- WE STILL SUPPORT NATURAL JOIN BUT IN THE FORM OF EQUI JOIN
    - i.e. ... ON id = id
