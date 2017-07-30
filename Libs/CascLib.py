
from ctypes import *
import os,sys,errno

cwd = os.getcwd()
if hasattr(sys, 'frozen'):
    CascLib_DIR = os.path.join(os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding())),'Libs')
else:
    CascLib_DIR = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
if CascLib_DIR:
    os.chdir(CascLib_DIR)
FOLDER = False
try:
    _CascLib = windll.CascLib
except:
    try:
        _CascLib = CDLL("CascLib.dylib", RTLD_GLOBAL)
    except:
        FOLDER = True
os.chdir(cwd)

#-----------------------------------------------------------------------------
# Defines
CASCLIB_VERSION =        0x0100 #  Current version of CascLib (1.0)
CASCLIB_VERSION_STRING = "1.00" #  String version of CascLib version

# Values for CascOpenStorage
CASC_STOR_XXXXX = 0x00000001 #  Not used

# Values for CascOpenFile
CASC_OPEN_BY_ENCODING_KEY = 0x00000001 #  The name is just the encoding key; skip ROOT file processing

CASC_LOCALE_ALL =          0xFFFFFFFF
CASC_LOCALE_NONE =         0x00000000
CASC_LOCALE_UNKNOWN1 =     0x00000001
CASC_LOCALE_ENUS =         0x00000002
CASC_LOCALE_KOKR =         0x00000004
CASC_LOCALE_RESERVED =     0x00000008
CASC_LOCALE_FRFR =         0x00000010
CASC_LOCALE_DEDE =         0x00000020
CASC_LOCALE_ZHCN =         0x00000040
CASC_LOCALE_ESES =         0x00000080
CASC_LOCALE_ZHTW =         0x00000100
CASC_LOCALE_ENGB =         0x00000200
CASC_LOCALE_ENCN =         0x00000400
CASC_LOCALE_ENTW =         0x00000800
CASC_LOCALE_ESMX =         0x00001000
CASC_LOCALE_RURU =         0x00002000
CASC_LOCALE_PTBR =         0x00004000
CASC_LOCALE_ITIT =         0x00008000
CASC_LOCALE_PTPT =         0x00010000
CASC_LOCALE_BIT_ENUS =     0x01
CASC_LOCALE_BIT_KOKR =     0x02
CASC_LOCALE_BIT_RESERVED = 0x03
CASC_LOCALE_BIT_FRFR =     0x04
CASC_LOCALE_BIT_DEDE =     0x05
CASC_LOCALE_BIT_ZHCN =     0x06
CASC_LOCALE_BIT_ESES =     0x07
CASC_LOCALE_BIT_ZHTW =     0x08
CASC_LOCALE_BIT_ENGB =     0x09
CASC_LOCALE_BIT_ENCN =     0x0A
CASC_LOCALE_BIT_ENTW =     0x0B
CASC_LOCALE_BIT_ESMX =     0x0C
CASC_LOCALE_BIT_RURU =     0x0D
CASC_LOCALE_BIT_PTBR =     0x0E
CASC_LOCALE_BIT_ITIT =     0x0F
CASC_LOCALE_BIT_PTPT =     0x10
MAX_CASC_KEY_LENGTH =      0x10 #  Maximum length of the key (equal to MD5 hash)

MD5_HASH_SIZE =   0x10
MD5_STRING_SIZE = 0x20

SHA1_DIGEST_SIZE = 0x14 #  160 bits

LANG_NEUTRAL = 0x00 #  Neutral locale

# Return value for CascGetFileSize and CascSetFilePointer
CASC_INVALID_SIZE = 0xFFFFFFFF
CASC_INVALID_POS =  0xFFFFFFFF
CASC_INVALID_ID =   0xFFFFFFFF

# Flags for CascGetStorageInfo
CASC_FEATURE_LISTFILE = 0x00000001 #  The storage supports listfile

MAX_PATH = 1024

FILE_BEGIN =    0
FILE_CURRENT =  1
FILE_END =      2

ERROR_SUCCESS =                 0
ERROR_FILE_NOT_FOUND =          errno.ENOENT
ERROR_ACCESS_DENIED =           errno.EPERM
ERROR_INVALID_HANDLE =          errno.EBADF
ERROR_NOT_ENOUGH_MEMORY =       errno.ENOMEM
ERROR_NOT_SUPPORTED =           errno.ENOTSUP
ERROR_INVALID_PARAMETER =       errno.EINVAL
ERROR_DISK_FULL =               errno.ENOSPC
ERROR_ALREADY_EXISTS =          errno.EEXIST
ERROR_INSUFFICIENT_BUFFER =     errno.ENOBUFS
ERROR_BAD_FORMAT =              1000        # No such error code under Linux
ERROR_NO_MORE_FILES =           1001        # No such error code under Linux
ERROR_HANDLE_EOF =              1002        # No such error code under Linux
ERROR_CAN_NOT_COMPLETE =        1003        # No such error code under Linux
ERROR_FILE_CORRUPT =            1004        # No such error code under Linux
ERROR_FILE_ENCRYPTED =          1005        # Returned by encrypted stream when can't find file key

ERROR_FILE_INCOMPLETE =         1006        # The required file part is missing

#-----------------------------------------------------------------------------
# Structures

# CASC_STORAGE_INFO_CLASS
CascStorageFileCount    = 0
CascStorageFeatures     = 1
CascStorageGameInfo     = 2
CascStorageGameBuild    = 3
# CascStorageInfoClassMax = 4

class QUERY_KEY(Structure):
    _fields_ = [
        ('key',POINTER(c_byte)),
        ('size',c_ulong),
    ]

# Structure for SFileFindFirstFile and SFileFindNextFile
class CASC_FIND_DATA(Structure):
    _fields_ = [
        ('fileName', c_char * MAX_PATH),
        ('plainName', c_char_p),
        ('encodingKey', c_ubyte * MD5_HASH_SIZE),
        ('localeFlags', c_ulong),
        ('fileDataId', c_ulong),
        ('fileSize', c_ulong)
    ]

    def encodingKeyHex(self):
        h = ''
        for b in self.encodingKey:
            h += '%02X' % b
        return h

class HANDLE(c_void_p):
    @staticmethod
    def IsValid(handle):
        return isinstance(handle, HANDLE) and not handle.value in (None,0,-1,2**(8*sizeof(HANDLE))-1)

    def __repr__(self):
        return '<HANDLE object at %s: %d (%d)>' % (hex(id(self)), self.value, sizeof(self))

def CascLibGetLastError():
    # SFmpq only implements its own GetLastError on platforms other than windows
    if _CascLib.GetLastError == None:
        return GetLastError()
    return _CascLib.GetLastError()

#-----------------------------------------------------------------------------
# Functions for storage manipulation

if not FOLDER:
    try:
        _CascLib.GetLastError.restype = c_int
    except:
        _CascLib.GetLastError = None

# bool  WINAPI CascOpenStorage(const TCHAR * szDataPath, DWORD dwLocaleMask, HANDLE * phStorage);
    _CascLib.CascOpenStorage.argtypes = [c_char_p, c_ulong, POINTER(HANDLE)]
    _CascLib.CascOpenStorage.restype = c_bool
# bool  WINAPI CascGetStorageInfo(HANDLE hStorage, CASC_STORAGE_INFO_CLASS InfoClass, void * pvStorageInfo, size_t cbStorageInfo, size_t * pcbLengthNeeded);
    _CascLib.CascGetStorageInfo.argtypes = [HANDLE, c_int, c_void_p, c_size_t, POINTER(c_size_t)]
    _CascLib.CascGetStorageInfo.restype = c_bool
# bool  WINAPI CascCloseStorage(HANDLE hStorage);
    _CascLib.CascCloseStorage.argtypes = [HANDLE]
    _CascLib.CascCloseStorage.restype = c_bool

# bool  WINAPI CascOpenFileByIndexKey(HANDLE hStorage, PQUERY_KEY pIndexKey, DWORD dwFlags, HANDLE * phFile);
    _CascLib.CascOpenFileByIndexKey.argtypes = [HANDLE, POINTER(QUERY_KEY), c_ulong, POINTER(HANDLE)]
    _CascLib.CascOpenFileByIndexKey.restype = c_bool
# bool  WINAPI CascOpenFileByEncodingKey(HANDLE hStorage, PQUERY_KEY pEncodingKey, DWORD dwFlags, HANDLE * phFile);
    _CascLib.CascOpenFileByEncodingKey.argtypes = [HANDLE, POINTER(QUERY_KEY), c_ulong, POINTER(HANDLE)]
    _CascLib.CascOpenFileByEncodingKey.restype = c_bool
# bool  WINAPI CascOpenFile(HANDLE hStorage, const char * szFileName, DWORD dwLocale, DWORD dwFlags, HANDLE * phFile);
    _CascLib.CascOpenFile.argtypes = [HANDLE, c_char_p, c_ulong, c_ulong, POINTER(HANDLE)]
    _CascLib.CascOpenFile.restype = c_bool
# DWORD WINAPI CascGetFileSize(HANDLE hFile, PDWORD pdwFileSizeHigh);
    _CascLib.CascGetFileSize.argtypes = [HANDLE, POINTER(c_ulong)]
    _CascLib.CascGetFileSize.restype = c_ulong
# DWORD WINAPI CascGetFileId(HANDLE hStorage, const char * szFileName);
    _CascLib.CascGetFileId.argtypes = [HANDLE, c_char_p]
    _CascLib.CascGetFileId.restype = c_ulong
# DWORD WINAPI CascSetFilePointer(HANDLE hFile, LONG lFilePos, LONG * plFilePosHigh, DWORD dwMoveMethod);
    _CascLib.CascSetFilePointer.argtypes = [HANDLE, c_ulong, POINTER(c_ulong), c_ulong]
    _CascLib.CascSetFilePointer.restype = c_ulong
# bool  WINAPI CascReadFile(HANDLE hFile, void * lpBuffer, DWORD dwToRead, PDWORD pdwRead);
    _CascLib.CascReadFile.argtypes = [HANDLE, c_void_p, c_ulong, POINTER(c_ulong)]
    _CascLib.CascReadFile.restype = c_bool
# bool  WINAPI CascCloseFile(HANDLE hFile);
    _CascLib.CascCloseFile.argtypes = [HANDLE]
    _CascLib.CascCloseFile.restype = c_bool

# HANDLE WINAPI CascFindFirstFile(HANDLE hStorage, const char * szMask, PCASC_FIND_DATA pFindData, const TCHAR * szListFile);
    _CascLib.CascFindFirstFile.argtypes = [HANDLE, c_char_p, POINTER(CASC_FIND_DATA), c_char_p]
    _CascLib.CascFindFirstFile.restype = HANDLE
# bool  WINAPI CascFindNextFile(HANDLE hFind, PCASC_FIND_DATA pFindData);
    _CascLib.CascFindNextFile.argtypes = [HANDLE, POINTER(CASC_FIND_DATA)]
    _CascLib.CascFindNextFile.restype = c_bool
# bool  WINAPI CascFindClose(HANDLE hFind);
    _CascLib.CascFindClose.argtypes = [HANDLE]
    _CascLib.CascFindClose.restype = c_bool

def CascOpenStorage(path, localeMask=CASC_LOCALE_ALL):
    f = HANDLE()
    if _CascLib.CascOpenStorage(path, localeMask, byref(f)):
        return f
def CascGetStorageInfo(casc, infoClass):
    i = c_ulong()
    s = c_ulong()
    if _CascLib.CascGetStorageInfo(casc, infoClass, byref(i), sizeof(c_ulong), byref(s)):
        return i.value
def CascCloseStorage(casc):
    return _CascLib.CascCloseStorage(casc)

def CascOpenFileByIndexKey(casc, indexKey, flags):
    q = QUERY_KEY()
    q.key = indexKey
    q.size = len(indexKey)
    f = HANDLE()
    if _CascLib.CascOpenFileByIndexKey(casc, byref(q), flags, byref(f)):
        return f
def CascOpenFileByEncodingKey(casc, encodingKey, flags):
    q = QUERY_KEY()
    q.key = encodingKey
    q.size = len(encodingKey)
    f = HANDLE()
    if _CascLib.CascOpenFileByIndexKey(casc, byref(q), flags, byref(f)):
        return f
def CascOpenFile(casc, filename, locale=CASC_LOCALE_ENUS, flags=0):
    f = HANDLE()
    if _CascLib.CascOpenFile(casc, filename, locale, flags, byref(f)):
        return f
def CascGetFileSize(file):
    return _CascLib.CascGetFileSize(file, None)
def CascGetFileId(casc, filename):
    return _CascLib.CascGetFileId(casc, filename)
def CascSetFilePointer(file, pos, posHigh=None, method=FILE_BEGIN):
    return _CascLib.CascSetFilePointer(file, pos, byref(posHigh), method)
def CascReadFile(file, read=None):
    all = read == None
    if all:
        read = CascGetFileSize(file)
        if read == None or read == -1:
            return
    data = create_string_buffer(read)
    r = c_ulong()
    total_read = 0
    while total_read < read:
        if _CascLib.CascReadFile(file, byref(data, total_read), read-total_read, byref(r)):
            total_read += r.value
        else:
            return
    return (data.raw[:total_read],total_read)
def CascCloseFile(file):
    return _CascLib.CascCloseFile(file)

def CascFindFirstFile(casc, search="*", listfilePath=None):
    if search == None:
        search = POINTER(c_char)()
    result = CASC_FIND_DATA()
    f = _CascLib.CascFindFirstFile(casc, search, byref(result), listfilePath)
    return (f, result)
def CascFindNextFile(find):
    result = CASC_FIND_DATA()
    if _CascLib.CascFindNextFile(find, byref(result)):
        return result
def CascFindClose(find):
    return _CascLib.CascFindClose(find)

if __name__ == '__main__':
    path = "/Users/zachzahos/Applications/Wineskin/SCRemastered.app/Contents/Resources/drive_c/Program Files/StarCraft"
    print 'Opening CASC Directory: %s' % path
    casc = CascOpenStorage(path)
    print 'CASC Handle: %s' % casc
    if not HANDLE.IsValid(casc):
        sys.exit()
    def doDetails():
        print 'FileCount: %d' % CascGetStorageInfo(casc, CascStorageFileCount)
        print 'Features: %d' % CascGetStorageInfo(casc, CascStorageFeatures)
        print 'GameInfo: %d' % CascGetStorageInfo(casc, CascStorageGameInfo)
        print 'GameBuild: %d' % CascGetStorageInfo(casc, CascStorageGameBuild)
    # doDetails()
    def doFind(search):
        filenames = []
        find,result = CascFindFirstFile(casc, search)
        print 'Find Handle: %s (%d)' % (find, CascLibGetLastError())
        print 'fileName, plainName, encodingKey, localeFlags, fileDataId, fileSize'
        if not HANDLE.IsValid(find):
            sys.exit()
        while result:
            filenames.append(result.fileName)
            print '%s\n\t%s, %s, %d, %d, %d' % (result.fileName, result.plainName, result.encodingKeyHex(), result.localeFlags, result.fileDataId, result.fileSize)
            result = CascFindNextFile(find)
        CascFindClose(find)
        return filenames
    filenames = doFind("*cmdicons*")
    def doExtract(names):
        for name in names:
            print 'Extracing file: %s' % repr(name)
            file = CascOpenFile(casc, name)
            if not HANDLE.IsValid(file):
                continue
            data,size = CascReadFile(file)
            print 'Extracted Size: %d' % size
            with open('WORKING/remastered/' + name.replace('/', '_'), 'wb') as f:
                f.write(data)
            CascCloseFile(file)
    doExtract(filenames)
    CascCloseStorage(casc)
