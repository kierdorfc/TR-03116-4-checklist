#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# ca_file="/usr/local/etc/openssl/cert.pem" # Openssl greift auf diese Datei zu und erwartet alle gültigen Root-Zertifikate darin im PEM-Format
ca_file=""
tmp_folder="/tmp"
tmp_cert_file="/tmp/tmp.pem"
hostname=""
port=0

cipher_suites=[["TLS_DHE_RSA_WITH_AES_128_CBC_SHA256","DHE-RSA-AES128-SHA256","RSA","OPTIONAL"  ],
  ["TLS_DHE_RSA_WITH_AES_256_CBC_SHA256","DHE-RSA-AES256-SHA256", "RSA", "OPTIONAL" ],
  ["TLS_DHE_RSA_WITH_AES_128_GCM_SHA256","DHE-RSA-AES128-GCM-SHA256","RSA", "OPTIONAL"  ],
  ["TLS_DHE_RSA_WITH_AES_256_GCM_SHA384" ,"DHE-RSA-AES256-GCM-SHA384","RSA", "OPTIONAL"  ],
  ["TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256","ECDHE-RSA-AES128-SHA256","RSA","MUST"  ],
  ["TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384","ECDHE-RSA-AES256-SHA384","RSA", "SHOULD"  ],
  ["TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256","ECDHE-RSA-AES128-GCM-SHA256","RSA","MUST"  ],
  ["TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384","ECDHE-RSA-AES256-GCM-SHA384","RSA","SHOULD"  ],
  ["TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA","ECDHE-RSA-AES128-SHA","RSA","OPTIONAL"],
  ["TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA","","RSA","OPTIONAL"], #TODO: Mein Openssl unterstützt diese Cipher gar nicht.
  ["TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA","ECDHE-RSA-AES256-SHA","RSA","OPTIONAL"],
  ["TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA","","RSA","OPTIONAL"],#TODO: Mein Openssl unterstützt diese Cipher gar nicht.
  ["TLS_DHE_RSA_WITH_AES_128_CBC_SHA","DHE-RSA-AES128-SHA","RSA","OPTIONAL"],
  ["TLS_DHE_RSA_WITH_AES_256_CBC_SHA","DHE-RSA-AES256-SHA","RSA","OPTIONAL"],
  ["TLS_DHE_RSA_WITH_AES_128_GCM_SHA","","RSA","OPTIONAL"],#TODO: Mein Openssl unterstützt diese Cipher gar nicht.
  ["TLS_DHE_RSA_WITH_AES_256_GCM_SHA","","RSA","OPTIONAL"],#TODO: Mein Openssl unterstützt diese Cipher gar nicht.
  ["TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256","ECDHE-ECDSA-AES128-SHA256", "EC", "MUST"],
  ["TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384","ECDHE-ECDSA-AES256-SHA384","EC", "SHOULD"  ],
  ["TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256" ,"ECDHE-ECDSA-AES128-GCM-SHA256","EC", "MUST"  ],
  ["TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384","ECDHE-ECDSA-AES256-GCM-SHA384","EC", "SHOULD"  ],
  ["TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA","ECDHE-ECDSA-AES128-SHA","EC", "OPTIONAL"  ],
  ["TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA","ECDHE-ECDSA-AES256-SHA","EC", "OPTIONAL"  ],
  ["TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA","","EC", "OPTIONAL"  ],#TODO: Mein Openssl unterstützt diese Cipher gar nicht.
  ["TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA","","EC", "OPTIONAL"  ]]#TODO: Mein Openssl unterstützt diese Cipher gar nicht.
