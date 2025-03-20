#coding:utf-8
import sys
import ctypes
import ctypes.wintypes

import cdio

__echoback__ = True     # エコーバックを使わない場合は、偽にする

class clsDIO:
    ''' clsDIO デジタル入出力クラス
            Note: 
                Contec API-DIO(WDM) Ver.10.30対応
    ''' 
    def __init__(self):
        ''' クラスコンストラクタ
                Args: 
                Returns:
                Note: 
                    property初期化
        ''' 
        self.pOpened:bool = False
        self.pName:str = ""
        self.pInpPorts:int = 0
        self.pOutPorts:int = 0
        self.pErrorStr:str = ""
        
        self.pDibit = None
        self.pDibyte = None
        self.pDobit = None
        self.pDobyte = None
        
        self._devicename:str = ""
        self._pID = ctypes.c_short()                # デバイスアクセス用ID
        self._initialized:bool = False
        self._dobuf:list = []
        
    def Open(self, deviceName:str) -> int:
        ''' ボード初期化メソッド
                Args: 
                    deviceName(str): デバイス名(exm."DIO000")
                Returns: 
                    エラーコード
                    0以外でエラー
                Note: 
        ''' 
        lret = ctypes.c_long(0)
        lret.value = cdio.DioInit(deviceName.encode(), ctypes.byref(self._pID))
        self._ErrorHandler(lret)
        if lret.value == 0:
            self.pOpened = True
            self._devicename = deviceName
            print(type(deviceName))
            lret.value = self._InitializeIO(deviceName)
            self._ErrorHandler(lret)
            if lret.value == 0:
                self._initialized = True
        return lret.value
        
    def Close(self) -> int:
        ''' ボード終了メソッド
                Args: 
                Returns: 
                    エラーコード
                    0以外でエラー
                Note: 
        ''' 
        lret = ctypes.c_long(0)
        lret.value = cdio.DioExit(self._pID)
        self._ErrorHandler(lret)
        return lret.value
        
    def Reset(self) -> int:
        ''' ボードリセットメソッド
                Args: 
                Returns: 
                    エラーコード
                    0以外でエラー
                Note: 
        ''' 
        lret = ctypes.c_long(0)
        lret.value = cdio.DioResetDevice(self._pID)
        self._ErrorHandler(lret)
        return lret.value
    
    class inpbit:
        ''' 入力Bitクラス
                Note: 
        ''' 
        def __init__(self, parent, cnt):
            ''' クラスコンストラクタ
                    Args: 
                        parent(clsDIO): 親クラス
                        cnt(int): 入力Bit数
                    Returns: 
                    Note: 
            ''' 
            self._parent = parent
            self._bit = [False] * cnt
            
        def __getitem__(self, idx:int) -> bool:
            ''' getitemメソッド
                    Args: 
                        idx(int): listインデックス
                    Returns: 
                        Bitの入力状態
                    Note: 
                        exm.print(cIO.pDibit[0])
            ''' 
            self._bit[idx] = self._InpBit(idx)
            return self._bit[idx]
            
        def _InpBit(self, no:int) -> bool:
            ''' Bit入力メソッド
                    Args: 
                        no(int): 入力論理ビット番号(0~)
                    Returns: 
                        Bit Onで真を返す
                    Note: 
            ''' 
            lret = ctypes.c_long(0)
            data = ctypes.c_ubyte()
            lret.value = cdio.DioInpBit(self._parent._pID, no, ctypes.byref(data))
            self._parent._ErrorHandler(lret)
            return data.value!=0

    class inpbyte:
        ''' 入力Byteクラス
                Note: 
        ''' 
        def __init__(self, parent, cnt):
            ''' クラスコンストラクタ
                    Args: 
                        parent(clsDIO): 親クラス
                        cnt(int): 入力Byte数
                    Returns: 
                    Note: 
            ''' 
            self._parent = parent
            self._byte = [0] * cnt
        
        def __getitem__(self, idx:int):
            ''' getitemメソッド
                    Args: 
                        idx(int): listインデックス
                    Returns: 
                        Byteの入力状態
                    Note: 
                        exm.print(cIO.pDibyte[0])
            ''' 
            self._byte[idx] = self._InpByte(idx)
            return self._byte[idx]
        
        def _InpByte(self, prt:int) -> int:  #bytes:
            ''' Byte入力メソッド
                    Args: 
                        prt(int): 入力ポート番号
                    Returns: 
                        入力値を返す(8bit分)
                    Note: 
            ''' 
            lret = ctypes.c_long(0)
            data = ctypes.c_ubyte()
            lret.value = cdio.DioInpByte(self._parent._pID, prt, ctypes.byref(data))
            self._parent._ErrorHandler(lret)
            return data.value

    class outbit:
        ''' 出力Bitクラス
                Note: 
        ''' 
        def __init__(self, parent, cnt:int):
            ''' クラスコンストラクタ
                    Args: 
                        parent(clsDIO): 親クラス
                        cnt(int): 出力Bit数
                    Returns: 
                    Note: 
            ''' 
            self._parent = parent
            self._bit = [False] * cnt
        
        def __getitem__(self, idx:int) -> bool:
            ''' getitemメソッド
                    Args: 
                        idx(int): listインデックス
                    Returns: 
                        Bitの出力状態
                    Note: 
                        __echoback__が真であればDioEchoBackBit関数を使用
                        偽の場合は_dobufの値を返す
                        exm.print(cIO.pDobit[0])
            ''' 
            if __echoback__:
                self._bit[idx] = self._OutBitEchoback(idx)
            else:
                self._bit[idx] = self._parent._dobuf[idx // 8] & (2 ** (idx % 8)) != 0
            return self._bit[idx]
            
        def _OutBitEchoback(self, no:int) -> bool:
            ''' 出力Bitエコーバックメソッド
                    Args: 
                        no(int): 出力論理ビット番号(0~)
                    Returns: 
                        Bit Onで真を返す
                    Note: 
            ''' 
            lret = ctypes.c_long()
            data = ctypes.c_ubyte(0)
            lret.value = cdio.DioEchoBackBit(self._parent._pID, no, ctypes.byref(data))
            self._parent._ErrorHandler(lret)
            return data.value != 0

        def __setitem__(self, idx:int, value:bool):
            ''' setitemメソッド
                    Args: 
                        idx(int): listインデックス
                        value(bool): 出力するBit状態
                    Returns: 
                    Note: 
                        exm.cIO.pDobit[0] = True
            ''' 
            self._OutBit(idx, value)
        
        def _OutBit(self, no:int, bit:bool) -> int:
            ''' Bit出力メソッド
                    Args: 
                        no(int): 出力論理ビット番号(0~)
                        bit(bool): True|False
                    Returns: 
                        エラーコード
                        0以外でエラー
                    Note: 
            ''' 
            lret = ctypes.c_long(0)
            data = 1 if bit else 0
            lret.value = cdio.DioOutBit(self._parent._pID, no, data)
            self._parent._ErrorHandler(lret)
            if lret.value == 0:
                # _dobufを更新
                buf = self._parent._dobuf[no // 8] & 0xff       # 念の為、8bit以上をオフ
                if bit:
                    buf |= (2 ** (no % 8))
                else:
                    buf &= (0xff ^ (2 ** (no % 8)))     # 0xffとxorで反転する(NOTは使えない…)
                self._parent._dobuf[no // 8] = buf & 0xff       # 念の為、8bit以上をオフ
            return lret.value

    class outbyte:
        ''' 出力Byteクラス
                Note: 
        ''' 
        def __init__(self, parent, cnt:int):
            ''' クラスコンストラクタ
                    Args: 
                        parent(clsDIO): 親クラス
                        cnt(int): 出力Byte数
                    Returns: 
                    Note: 
            ''' 
            self._parent = parent
            self._byte = [0] * cnt
    
        def __getitem__(self, idx:int) -> int:
            ''' getitemメソッド
                    Args: 
                        idx(int): listインデックス
                    Returns: 
                        Byteの出力状態
                    Note: 
                        exm.print(cIO.pDobyte[0])
            ''' 
            if __echoback__:
                self._byte[idx] = self._OutByteEchoback(idx)
            else:
                self._byte[idx] = self._parent._dobuf[idx]
            return self._byte[idx]
            
        def _OutByteEchoback(self, prt:int) -> int:
            ''' 出力Byteエコーバックメソッド
                    Args: 
                        prt(int): 出力ポート番号
                    Returns: 
                        出力値
                    Note: 
            ''' 
            lret = ctypes.c_long()
            data = ctypes.c_ubyte()
            lret.value = cdio.DioEchoBackByte(self._parent._pID , prt, ctypes.byref(data))
            self._parent._ErrorHandler(lret)
            return data.value
        
        def __setitem__(self, idx:int, value:int):
            ''' setitemメソッド
                    Args: 
                        idx(int): listインデックス
                        value(int): 出力値
                    Returns: 
                    Note: 
                        exm.cIO.pDobyte[0] = 0xff
            ''' 
            self._OutByte(idx, value)
            
        def _OutByte(self, prt:int, bits:int) -> int:
            ''' Byte出力メソッド
                    Args: 
                        prt(int): 出力ポート番号
                        bits(int): 出力値
                    Returns: 
                        出力値
                    Note: 
            ''' 
            lret = ctypes.c_long(0)
            data = bits & 0xff
            lret.value = cdio.DioOutByte(self._parent._pID, prt, data)
            self._parent._ErrorHandler(lret)
            if lret.value == 0:
                # _dobufを更新
                self._parent._dobuf[prt] = data
            return data
        

    def _InitializeIO(self, devnm:str) -> int:
        ''' ボード初期化メソッド
                Args: 
                    devnm(str): デバイス名(exm."DIO000")
                Returns: 
                    エラーコード
                    0以外でエラー
                Note: 
        ''' 
        lret = ctypes.c_long(0)
        deviceName = ctypes.create_string_buffer(256)   # exm."DIO000"
        device = ctypes.create_string_buffer(256)       # exm."DIO-0808LY-USB"
        
        # デバイスリセット
        lret.value = cdio.DioResetDevice(self._pID)
        # デバイス名称の取得
        if not self._initialized:       # 初回のみ
            i = 0
            while i < 255:
                # ボードが複数の場合に対応
                lret.value = cdio.DioQueryDeviceName(i,deviceName ,device )
                i += 1
                if lret.value:
                    self._ErrorHandler(lret)
                elif deviceName.value.decode('sjis') == devnm:
                    self.pName = device.value.decode('sjis')
                    break
            
            # 入出力ポート数取得
            icnt = ctypes.c_short()
            ocnt = ctypes.c_short()
            lret.value = cdio.DioGetMaxPorts(self._pID, ctypes.byref(icnt), ctypes.byref(ocnt))
            self._ErrorHandler(lret)
            if lret.value == 0:
                self.pInpPorts = icnt.value
                self.pOutPorts = ocnt.value
                self._dobuf = [0] * self.pOutPorts  # 出力バッファ
                self.pDibit = self.inpbit(self, (self.pInpPorts*8))
                self.pDibyte = self.inpbyte(self, self.pInpPorts)
                self.pDobit = self.outbit(self, (self.pOutPorts*8))
                self.pDobyte = self.outbyte(self, self.pOutPorts)
            self.pName += f"({self.pInpPorts*8}/{self.pOutPorts*8})"
            return lret.value
            
    def _ErrorHandler(self, ecode:ctypes.c_long) -> str:
        ''' エラー文字列取得メソッド
                Args: 
                    ecode(ctypes.c_long): エラーコード
                Returns: 
                    エラー文字列
                Note: 
        ''' 
        error_buf = ctypes.create_string_buffer(256)
        cdio.DioGetErrorString(ecode, error_buf)
        self.pErrorStr = f"[{ecode.value}] {error_buf.value.decode('sjis')}"
        if ecode.value != 0:
            print(self.pErrorStr, file=sys.stderr)
        return self.pErrorStr
    
