#coding:utf-8 
from termcolor import cprint
import clsDIO

def IsHex(ss:str) -> bool:
    ''' 16進文字列判定
            Args: 
                ss(str): 文字列
            Returns: 
                16進文字列であれば真を返す
            Note: 
                "00"~"ff"の範囲内か確認
    ''' 
    ret = True
    if 0 < len(ss) <= 2:
        for s in ss:
            if s not in "0123456789abcdefABCDEF":
                ret = False
    else:
        ret = False
    return ret
    
if __name__ == "__main__":
    cIO = clsDIO.clsDIO()
    ret = cIO.Open("DIO000")
    cprint(f"Open : {cIO.pErrorStr}", "light_cyan")
    cprint(f"{cIO.pName}", "light_cyan")
    key = ""
    while key.lower()!="q":
        print("")
        print("1 : Input Bit")
        print("2 : Input Byte")
        print("3 : Output Bit")
        print("4 : Output Byte")
        print("r : Reset Board")
        print("q : Quit")
        key = input("Select > ")
        match key.lower():
            case "1":
                no = input("No(0~63) > ")
                if 0 <= int(no) < (cIO.pInpPorts * 8):
                    bit = cIO.pDibit[int(no)]
                    cprint(f"No : {bit}", "light_cyan")
            case "2":
                prt = input("Port(0~7) > ")
                if 0 <= int(prt) < cIO.pInpPorts:
                    byte = cIO.pDibyte[int(prt)]
                    cprint(f"{prt} : {"{0:09_b}".format(byte)}", "light_cyan")
            case "3":
                no = input("No(0~63) > ")
                if 0 <= int(no) < (cIO.pOutPorts * 8):
                    it = input("Bit(0|1) > ")
                    if it in "01":
                        cIO.pDobit[int(no)] = (it != "0")
                        bak = cIO.pDobit[int(no)]
                        cprint(f"{no} : {bak}", "light_cyan")
            case "4":
                prt = input("Port(0~7) > ")
                if 0 <= int(prt) < cIO.pOutPorts:
                    it = input("Byte(00~FF) > ")
                    if IsHex(it):
                        cIO.pDobyte[int(prt)] = int(it, 16)
                        bak = cIO.pDobyte[int(prt)]
                        cprint(f"{prt} : {"{0:09_b}".format(bak)}", "light_cyan")
            case "r":
                cIO.Reset()
                cprint(f"Reset : {cIO.pErrorStr}", "light_cyan")
            case _:
                continue
    ret = cIO.Reset()
    ret = cIO.Close()
    cprint(f"Close : {cIO.pErrorStr}", "light_cyan")
    
