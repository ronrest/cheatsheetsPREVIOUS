# Headers

```
//// ###########################################################################
////                                                           New style Headers
//// ###########################################################################
```

Pattern: `\/{4} #{10,}[\s]*\/{4,}\s*.+\s\/{4} #{10,}`


```
//// ###########################################################################
                                                            **Old Style header**
//// ###########################################################################
```

pattern: `\/{4} #{10,}[\s]*\*{2}(.+)\*{2,}\s*\/{4,} #{10,}`



```
================================================================================ ####
                                                  **Old Style Header 2**
//// #######################################################################
```

pattern: `={10,} #{4}\s*\*{2}(.*)\*{2}\s\/{4} #{10,}`


# Multi-line Code - Description

## Multiline code - Single line Description


## Multiline code - Multi line Description


# Single line code-description


## Single line code - Single line Description

```
some code #### this is some description
```

regex pattern:

one of the following, still playing around with it. Note, that it needs to not clash with multi-line descriptions.

```
(.+) #### (.*)[^\\{4}]\n`
(.+) ####? (.*)[^\\{4}]
(.+) ####([^\n^\\]*)
(.+) #### (.*)[^\\{4}]\n
```


## Single line code - Multi line Description

```
some code #### this is some description \\\\
more lines of description
even more lines of description ####
```

Pattern: `(.+) #### (.+?)\\{4}([\S\s]+?)#{4}`
returns 3 groups: code, description line1, rest of description lines.

**WARNING:** Still need to test this pattern in a test case to see that it works properly and does not clash with other sections of cheatsheets. 
