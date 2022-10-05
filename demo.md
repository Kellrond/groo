# TEST PARSE OUTPUT


## FOLDERS
file_path: test/test_data/documentation/        split_file_path: ['test', 'test_data', 'documentation'] folder_id: 0

## FILES
file_path: test/test_data/documentation/demo.py folder_id: 0    file_id: 0      length: 215

## IMPORTS

from datetime import None as dt
from datetime import None
from config.modules import None
from config.modules import None
from datetime import None
import decimal as dec
import numbers
import time as exmpl
import  chunk


## Classes
Class1(self,param1:str,param2:dict,param3:False)
        This is an example superclass

        Usage aka code block:

            ```
            example code block
            line 2 should line up with above
                and this should in tabbed in one
                    and this indented 2
            ```

            ```example code block
            line 2 should line up with above
                and this should in tabbed in one
                    and this indented 2```

        Params:
            - param1: description with `code in it`
            - param2: this is a longer description than normal. Try to keep lines within 100 char
              if you have to go over. align it with the block above to be included.
            - param3:False to do this, True to do that

        Notes:
            This is a set of notes they may have `code` withing and that code may have `a: colon`
            and should still be rendered correctly. In fact any : in anything other than a header
            should be ignored.

        There can also be other paragraph blocks inside of this one.

        Lists:
            - there should
            - be multiple levels of indent
                - like this
                    - and this
                - and back to here
            - it should work to have : in a list
            - as well as inline code



        __init__(self, param1:str, param2:dict, param3:False) -> None:
                Heres a docstring in an __init__


        @classmethod
        c1func1(cls, param1:str):
                Example one line docstring. Also a class method


        @staticmethod
        c1func2(param1:dict, param2=False) -> str:
                Example one string with closing tag on new line. Also a static method


        nestedDef1(param1):
                This is an example of a nested function


        nestedDef2(param2, new_line='\n') -> int:
                And this is another example


        nestedDef3():


        c3func3(self, param1:list, param2:str, param3:dict) -> dict:
                Example multi line docstring with the preferred formatting style
                This is the second line




Class2(self,param1: str,param2: dict,param3: False,param4=False)   ['Class1']
        This is an example class with a super class



        __init__(self, param1: str, param2: dict, param3: False, param4=False) -> None:


        c2func1(self, param1:str) -> list:
                Example one line docstring


        c2func2(self, param1:dict, param2=False) -> str:
                Example one string with closing tag on new line


        c2func3(self, param1:list, param2:str, param3:dict) -> dict:
                Example multi line docstring with the preferred formatting style
                This is the second line




Class3(self,param1:str,param2:dict,param3:False)   ['Class1', 'Class1']




        __init__(self, param1:str, param2:dict, param3:False) -> None:


        c3func1(self, param1:str) -> list:
                Example one line docstring


        c3func2(self, param1:dict, param2=False) -> str:
                Example one string with closing tag on new line


        c3func3(self, param1:list, param2:str, param3:dict) -> dict:
                Example multi line docstring with the preferred formatting style
                This is the second line





## FUNCTIONS

testImportInFunction(param1, param2:str, param3=None):
        A single line docstring



testNestedDefInFunction():
        Example one string with closing tag on new line



returns1(param1:str) -> int:



returns2() -> int:
        As the function says returns
        two



returns3(param=3, param88=88):



@test_decorator1
@test_decorator2
decoratedAndMultiLine(param1, param2:str, param3={}) -> str:
        Example multi line docstring with the preferred formatting style
            This is the second line
