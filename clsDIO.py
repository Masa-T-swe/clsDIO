#coding:utf-8
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
        lret.value = cdio.DioInit (deviceName.encode(), ctypes.byref(self._pID))
        self._ErrorHandler(lret)
        if lret.value == 0:
            self.pOpened = True
            self._devicename = deviceName
            lret.value = self._InitializeIO()
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
        lret = ctypes.clong(0)
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
        lret = ctypes.clong(0)
        lret.value = cdio.DioResetDevice(self._pID)
        self._ErrorHandler(lret)
        return lret.value
    
    @property
    def pDibit(self, no:int) -> bool:
        ''' Bit入力Property Getter
                Args: 
                    no(int): 入力論理ビット番号(0~)
                Returns: 
                    Bit Onで真を返す
                Note: 
        ''' 
        return self._InpBit(no)

    def _InpBit(self, no:int) -> bool:
        ''' Bit入力メソッド
                Args: 
                    no(int): 入力論理ビット番号(0~)
                Returns: 
                    Bit Onで真を返す
                Note: 
        ''' 
        lret = ctypes.clong(0)
        data = ctypes.c_ubyte()
        lret.value = cdio.DioInpBit(self._pID, no, ctypes.byref(data))
        self._ErrorHandler(lret)
        return data!=0

    @property
    def pDibyte(self, prt:int) -> int:
        ''' Byte入力Property Getter
                Args: 
                    prt(int): 入力ポート番号
                Returns: 
                    入力値を返す(8bit分)
                Note: 
        ''' 
        return self._InpByte(prt)
        
    def _InpByte(self, prt:int) -> int:  #bytes:
        ''' Byte入力メソッド
                Args: 
                    prt(int): 入力ポート番号
                Returns: 
                    入力値を返す(8bit分)
                Note: 
        ''' 
        lret = ctypes.clong(0)
        data = ctypes.c_ubyte()
        lret.value = cdio.DioInpByte(self._pID, prt, ctypes.byref(data))
        self._ErrorHandler(lret)
        return data.value

    @property
    def pDobit(self, no:int) -> bool:
        ''' Bit出力Property Getter
                Args: 
                    no(int): 出力論理ビット番号(0~)
                Returns: 
                    Bit Onで真を返す
                Note: 
                    __echoback__が真であればxxxEchoBack関数を使用
                    偽の場合は_dobufの値を返す
        ''' 
        if __echoback__:    # EchoBackの値を返す
            return self._OutBitEchoback(no)
        else:               # _dobufの値を返す
            return self._dobuf[no // 8] & (2 ** (no % 8)) != 0
            
    @pDobit.setter
    def pDobit(self, no:int, bit:bool):
        ''' Bit出力Property Setter
                Args: 
                    no(int): 出力論理ビット番号(0~)
                    bit(bool): True|False
                Returns: 
                Note: 
        ''' 
        self._OutBit(no, bit)
        
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
        lret = ctypes.clong(0)
        data = 1 if bit else 0
        lret.value = cdio.DioOutBit(self._pID, no, data)
        self._ErrorHandler(lret)
        if lret.value == 0:
            # _dobufを更新
            buf = self._dobuf[no // 8] & 0xff       # 念の為、8bit以上をオフ
            if bit:
                buf |= (2 ** (no % 8))
            else:
                buf &= (0xff ^ (2 ** (no % 8)))     # 0xffとxorで反転する(NOTは使えない…)
            self._dobuf[no // 8] = buf & 0xff       # 念の為、8bit以上をオフ
        return lret.value

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
        lret.value = cdio.DioEchoBackBit(self._pID, no, ctypes.byref(data))
        self._ErrorHandler(lret)
        return data.value != 0

    @property
    def pDobyte(self, prt:int) -> int:
        ''' Byte出力property Getter
                Args: 
                    prt(int): 出力ポート番号
                Returns: 
                    出力値を返す(8bit分)
                Note: 
                    __echoback__が真であればxxxEchoBack関数を使用
                    偽の場合は_dobufの値を返す
        ''' 
        if __echoback__:
            ret = self._OutByteEchoback(prt)
        else:
            ret = self._dobuf[prt]
        return ret

    @pDobyte.setter
    def pDobyte(self, prt:int, bits:int):
        ''' Byte出力Property Setter
                Args: 
                    prt(int): 出力ポート番号
                    bits(int): 出力値
                Returns: 
                Note: 
        ''' 
        self._OutByte(prt, bits)
        
    def _OutByte(self, prt:int, bits:int) -> int:
        ''' Byte出力メソッド
                Args: 
                    prt(int): 出力ポート番号
                    bits(int): 出力値
                Returns: 
                    出力値
                Note: 
        ''' 
        lret = ctypes.clong(0)
        data = bits & 0xff
        lret.value = cdio.DioOutByte(self._pID, prt, data)
        self._ErrorHandler(lret)
        if lret.value == 0:
            # _dobufを更新
            self._dobuf[prt] = data
        return data
    
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
        lret.value = cdio.DioEchoBackByte(self._pID , prt, ctypes.byref(data))
        return data.value

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
                lret.value = cdio.DioQueryDeviceName (i,deviceName ,device )
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
                self._dobuf = [0] * self.pDutPorts  # 出力バッファ
            self.pName += f"{self.pInpPorts*8}/{self.pOutPorts*8}"
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
        self.pErrorStr = error_buf.value.decode('sjis')
        return self.pErrorStr
    
