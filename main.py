#coding:utf-8 

import clsDIO

if __name__ == "__main__":
    cIO = clsDIO.clsDIO()
    ret = cIO.Open("DIO000")
    print(f"Open : {cIO.pErrorStr}")
    print(f"{cIO.pName}")
    key = ""
    while key!="q":
        print("")
        print("1 : Input Bit")
        print("2 : Input Byte")
        print("3 : Output Bit")
        print("4 : Output Byte")
        print("q : Quit")
        key = input("Select > ")
        match key:
            case "1":
                no = input("No(0~63) > ")
                bit = cIO.pDibit[int(no)]
                print(f"No : {bit}")
            case "2":
                prt = input("Port(0~7) > ")
                byte = cIO.pDibyte[int(prt)]
                print(f"{prt} : {"{0:09_b}".format(byte)}")
            case "3":
                no = input("No(0~63) > ")
                it = input("Bit(0|1) > ")
                # cIO.pDobit(no) = (it != "0")
                cIO.pDobit[int(no)] = (it != "0")
                bak = cIO.pDobit[int(no)]
                print(f"{no} : {bak}")
            case "4":
                prt = input("Port(0~7) > ")
                it = input("Byte(00~FF) > ")
                cIO.pDobyte[int(prt)] = int(it, 16)
                bak = cIO.pDobyte[int(prt)]
                print(f"{prt} : {"{0:09_b}".format(bak)}")
            case _:
                continue
    ret = cIO.Reset()
    ret = cIO.Close()
    print(f"Close : {cIO.pErrorStr}")
    
