# Utility Projects

## 1. Random Variate Generator
### Generates random numbers from a specified probability distribution
a python class library which generates both discrete and continuous random variates, e.g., Bern(p), Geom(p), Exp(λ), Normal(μ,σ2), Gamma(α,β), Weibull(α,β), etc. Plots outputs generated here and compares to numpy-generated distributions.

### See further info in [RVDistributions folder]( ./RVDistributions/README.md)


![image](https://github.com/danhislop/Projects/assets/40676685/74e42baf-34de-46ae-84ec-5445485f9254)


---

## 2. Compare_Dataframes / CSV Files
### takes 2 .csv files as inputs, and finds differences
The .csv's are expected to have 1 or 2 key columns to base comparison on
This is a key<-->key compare, not a "line by line" compare. Allows for missing keys.
Use case: a list of customers and months (key columns) and 1-to-many other columns containing values.

### Usage: 
 - Enter path and file names into compare_dataframes.py
 - Specify key column. If 2 key columns, set `two_column_index = True`
 - Execute: python compare_dataframes.py     (output is on screen)  


---


## 3. NameCompare matches lists of names against each other. 
### With LDAP lookup feature, names can be fullnames or unix usernames.
Location: Projects/NameCompare folder


### Why use NameCompare?
#### This project was initiated for SOX compliance. During compliance week, we are given:
* Census list ('census') with Last, First names of all current employees
* Termination list ('terms') with Last, First names of all recently terminated employees
* We use the admin interface of any application to generate our own list of employees enabled to use that app ('users').  


### See further info in [NameCompare folder]( ./NameCompare/README.md)


