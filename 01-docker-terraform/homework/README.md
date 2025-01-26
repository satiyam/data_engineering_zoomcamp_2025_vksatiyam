# Module 1 Homework: Docker & SQL

In this homework we'll prepare the environment and practice
Docker and SQL

When submitting your homework, you will also need to include
a link to your GitHub repository or other public code-hosting
site.

This repository should contain the code for solving the homework. 

When your solution has SQL or shell commands and not code
(e.g. python files) file format, include them directly in
the README file of your repository.


## Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?

**- 24.3.1**
- 24.2.1
- 23.3.1
- 23.2.1



## Solution for Question 1. Understanding docker first run

```
satiy@Satiyam MINGW64 ~/Downloads/data_engineering_zoomcamp/01-docker-terraform (main)
$ winpty docker run -it --entrypoint "bash" python:3.12.8
root@069120d01fbf:/# pip --version
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

