#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2016, Ilya Etingof <ilya@glas.net>
# License: http://pysnmp.sf.net/license.html
#
from pysnmp.proto.secmod.rfc3826.priv import aes
from pysnmp.proto.secmod.rfc3414.auth import hmacmd5, hmacsha
from pysnmp.proto.secmod.rfc3414 import localkey
from pysnmp.proto import error
from math import ceil

try:
    from hashlib import md5, sha1
except ImportError:
    import md5
    import sha

    md5 = md5.new
    sha1 = sha.new


class AbstractAes(aes.Aes):
    serviceID = ()
    keySize = 0

    # 3.1.2.1
    def localizeKey(self, authProtocol, privKey, snmpEngineID):
        if authProtocol == hmacmd5.HmacMd5.serviceID:
            localPrivKey = localkey.localizeKeyMD5(privKey, snmpEngineID)
            for count in range(1, int(ceil(self.keySize * 1.0 / len(localPrivKey)))):
                # noinspection PyDeprecation,PyCallingNonCallable
                localPrivKey += md5(localPrivKey).digest()
        elif authProtocol == hmacsha.HmacSha.serviceID:
            localPrivKey = localkey.localizeKeySHA(privKey, snmpEngineID)
            # RFC mentions this algo generates 480bit key, but only up to 256 bits are used
            for count in range(1, int(ceil(self.keySize * 1.0 / len(localPrivKey)))):
                localPrivKey += sha1(localPrivKey).digest()
        else:
            raise error.ProtocolError(
                'Unknown auth protocol %s' % (authProtocol,)
            )
        return localPrivKey[:self.keySize]
