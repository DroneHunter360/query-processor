# Relational Algebra Query Processor
- A system capable of parsing relations and performing complex, nested relational algebra queries. 
- Provides support for the following relational algebra operations:
    - Selection
    - Projection
    - Joins
        - Inner, left-outer, right-outer, full-outer
    - Union
    - Intersection
    - Difference

# Syntax
Below is the syntax for performing queries on the query processor. Please reference the Syntax Considerations section as well for important information regarding conditions and joins.
#### $ - Selection
##### ```$(table_name)(condition)```

#### # - Projection
##### ```#(table_name)(column_1, column_2, ..., column_n)```

#### J - Inner Join
##### ```J(table1)(table2)(condition)```

#### R - Right-outer Join
##### ```R(table1)(table2)(condition)```

#### L - Left-outer Join
##### ```L(table1)(table2)(condition)```

#### F - Full-outer Join
##### ```F(table1)(table2)(condition)```

#### U - Union
##### ```U(table1)(table2)```

#### I - Intersection
##### ```I(table1)(table2)```

#### D - Difference 
##### ```D(table1)(table2)```

# Syntax Considerations
#### Condition formatting:
- A single space is required between each of the left operand, operator, and right operand as shown below:
- ```lhs operator rhs```
- Valid example: ```Age > 9```
- Invalid example: ```Age>9```
  
#### Join conditions:
- When writing join conditions, only write the attribute name itself, and not the table name
- Valid example: ```J(table1)(table2)(id == sid)```
- Invalid example: ```J(table1)(table2)(table1.id == table2.sid)```
