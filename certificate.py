#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import logging, logging.config, os, pem
import subprocess
from cryptography  import x509
from cryptography.hazmat.backends import default_backend
# from tls_includes import cipher_suites
from helper import which, logger, print_h1, print_h2
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPublicKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.backends.openssl.rsa import _RSAPublicKey
from cryptography.x509 import load_pem_x509_certificate
import re
from cryptography.hazmat.primitives import serialization
import tempfile
import os

class Certificate:

    def __init__(self, cert, ca_file):
      self.cert=cert
      self.ca_file=ca_file


    def check_intermediate_certificate(self):
        print_h1("Diese Funktion überprüft ein Intermediate-Zertifikat und deckt die Anforderungen aus Kapitel 2.2 der Checkliste ab.")
        print_h2("Drucke das subject des Zertifikats. Dies dient nur der Übersicht")
        self.print_subject()
        print_h2("Überprüfe den öffentlichen Schlüssel des Zertifkats (Anforderung 2.2.1)")
        self.check_certificate_key()

        if self.is_cert_ca():
            print_h2("Überprüfe den Signaturalgorithmus (Anforderung 2.2.2)")
            self.check_signature_algorithm()

        if self.is_cert_ca():
            print_h2("Überprüfe auf Wildcards (Anforderung 2.2.3)")
            self.check_for_wildcards()

        if self.is_cert_ca():
            print_h2("Überprüfe Rückrufinformationen und AuthorityInfoAccess (Anforderung 2.1.4)")
            self.check_cert_for_crl()
            self.check_cert_for_aia()

        if self.is_cert_ca():
            print_h2("Überprüfe auf BasicConstraint Extension (Anforderung 2.2.5)")
            self.check_basic_constraint()

        if self.is_cert_ca():
            print_h2("Überprüfe keyUsageExtension (Anforderung 2.2.6)")
            self.check_cert_for_keyusage()

    def check_root_certificate(self):
        print_h1("Diese Funktion überprüft das CA-Zertifikat und deckt die Anforderungen aus Kapitel 2.2 der Checkliste ab.")
        print_h2("Drucke das subject des Zertifikats. Dies dient nur der Übersicht")
        self.print_subject()
        print_h2("Überprüfe den öffentlichen Schlüssel des Zertifkats (Anforderung 2.2.1)")
        self.check_certificate_key()

        print_h2("Überprüfe auf Wildcards (Anforderung 2.2.3)")
        self.check_for_wildcards()

        print_h2("Überprüfe auf BasicConstraint Extension (Anforderung 2.2.5)")
        self.check_basic_constraint()

        print_h2("Überprüfe keyUsageExtension (Anforderung 2.2.6)")
        self.check_cert_for_keyusage()


    def check_leaf_certificate(self):
        print_h1("Diese Funktion überprüft das Server-Zertifikat und deckt die Anforderungen aus Kapitel 2.1 der Checkliste ab.")
        print_h2("Drucke das subject des Zertifikats. Dies dient nur der Übersicht")
        self.print_subject()

        print_h2("Überprüfe den öffentlichen Schlüssel des Zertifkats (Anforderung 2.1.1)")
        self.check_certificate_key()

        print_h2("Überprüfe den Signaturalgorithmus (Anforderung 2.1.2)")
        self.check_signature_algorithm()

        print_h2("Überprüfe auf Wildcards (Anforderung 2.1.3)")
        self.check_for_wildcards()

        print_h2("Überprüfe Rückrufinformationen und AuthorityInfoAccess (Anforderung 2.1.4)")
        self.check_cert_for_crl()
        self.check_cert_for_aia()

        print_h2("Überprüfe ob das Zertifikat gesperrt ist (Anforderung 2.1.5)")
        self.check_cert_for_revocation()

        print_h2("Überprüfe keyUsageExtension (Anforderung 2.1.6)")
        self.check_cert_for_keyusage()

        print_h2("Überprüfe extendedKeyUsageExtension (Anforderung 2.1.7)")
        self.check_cert_for_extended_keyusage()

        print_h2("Überprüfe Sub-Domain Namen (Anforderung 2.1.7)")
        self.list_alternative_names()

    def check_certificate_key(self):
        if (type(self.cert.public_key()) is _RSAPublicKey):
            logger.info("This certificate has an RSA key")
            if self.cert.public_key().key_size >= 2048:
                logger.info("Die Groesse des Schluessels ist gleich oder groesser 2048. Das ist OK.")
            else:
                logger.error("Die Groesse des Schluessels ist kleiner 2048bit. Das sollte nicht der Fall sein.")

            # logger.info.("The key size is: "+str(cert.public_key().key_size))
        if (type(self.cert.public_key())==DSAPublicKey):
            logger.error("Das Zertifikat hat einen DSA key. Das sollte nicht der Fall sein. Das Skript wird hier beendet da die weiteren Tests nicht sinnvoll sind.")
            exit(1)
            #TODO: Der Fall muss noch getestet werden. Die genaue Bezeichnung des Types des public_key könnte leicht anders sein

        if (type(self.cert.public_key())==EllipticCurvePublicKey):
            #TODO: Dieser Fall ist noch recht ungetestet

            logger.info("Das Zertifikat hat einen EllipticCurvePublicKey")

            allowed_curves=["brainpoolPP256r1",
            "brainpoolP384r1",
            "brainpoolP512r1",
            "secp224r1",
            "secp256r1",
            "secp384r1",
            "secp521r1"]
            correct_curve=False

            for crv in allowed_curves:
                if str(self.cert.public_key().curve.name)==crv:
                    logger.info("Es wird folgende Kurfe verwendet:"+ str(self.cert.public_key().curve.name)+ " Das ist OK")
                    correct_curve=True
            if correct_curve:
                logger.error("Es wird eine nicht zugelassene Kurve verwendet. Und zwar: "+str(self.cert.public_key().curve.name))

    def check_signature_algorithm(self):
        logger.warning("Der verwendete Signaturalgorithmus ist : "+str(self.cert.signature_algorithm_oid._name))
        logger.warning("Die zugehörige OID lautet: "+str(self.cert.signature_algorithm_oid.dotted_string))
        logger.warning("Bitte mit Hilfe der Checkliste überprüfen")

    def check_for_wildcards(self):
        #TODO: Das ist in der Prüfung von CA Zertifkaten anders. Die Funktion hier steigt leider aus wenn es die AlternativeNames extension nich gitb und daher kann man sie eigentlich für ein CA-ZErt nicht verwenden. Und es müssen auch noch mehr Felder (subject) geprüft werden.
        for entry in self.cert.subject._attributes:
            for attr in entry:
                if attr.oid._name=="commonName":
                    logger.info("commonName im subject des Zertifikat hat den Wert: " + attr.value)
        try:
            name_extension=self.cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            logger.info("Das Zertifikat hat eine AlternativeName Extension")

            if re.search(r"\*+",str(name_extension))is not None:
                logger.error("Die AlternativeName-Extension enthält mindestens ein *. Das ist nicht OK")
            else:
                logger.info("Die AlternativeName-Extension enthält keine Wildcards. Das ist  OK")

        except Exception as err:
            logger.error("Es existiert keine AlternativeName-Extension")
            #TODO: wenn es die Extension nicht gibt, tritt vermutlich ein Fehler auf, den man hier behandeln sollte

    def check_cert_for_crl(self):
        try:
            crl_extension=self.cert.extensions.get_extension_for_class(x509.CRLDistributionPoints)
            logger.info("Das Zertifikat hat eine CRLDistributionPoint Extension")
            logger.info("Der Inhalt der CRLDistributionPoint Extension lautet:")
            logger.info(str(crl_extension))
            #TODO: Die Ausgabe der Extension könnte etwas schöner werden

        except Exception as err:
            print err
            #TODO: wenn es die Extension nicht gibt, tritt vermutlich ein Fehler auf, den man hier behandeln sollte

    def check_cert_for_aia(self):
        try:
            aia_extension=self.cert.extensions.get_extension_for_class(x509.AuthorityInformationAccess)
            logger.info("Das Zertifikat hat eine AuthorityInformationAccess Extension")
            logger.info("Der Inhalt der AuthorityInformationAccess Extension lautet:")
            logger.info(str(aia_extension))
            #TODO: Die Ausgabe der Extension könnte etwas schöner werden

        except Exception as err:
            print err
            #TODO: wenn es die Extension nicht gibt, tritt vermutlich ein Fehler auf, den man hier behandeln sollte

    def check_cert_for_revocation(self):

        tmp_file =tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write(self.cert.public_bytes(serialization.Encoding.PEM))
        tmp_file.close()

        try:
            crl_extension=self.cert.extensions.get_extension_for_class(x509.CRLDistributionPoints)
            logger.info("Das Zertifikat hat eine CRLDistributionPoint Extension")

            openssl_cmd_getcert="openssl verify -crl_check_all -CAfile "+self.ca_file+ " " + tmp_file.name

            proc = subprocess.Popen([openssl_cmd_getcert], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()

            logger.warning("Die Prüfung des Zertifikats gegen die CRL hat folgendes Ergebnis ergeben:")
            logger.warning(out)
            logger.warning(err)

        except Exception as err:
            logger.error("Fehler bei der Prüfung des Revocation status. Existiert keine CRLDistributionPoint Extension? Es folgt die Ausgabe des Fehlers")
            logger.error(err)
            #TODO: Die Fehlerbehandldung könnte man etwas schöner machen

    def check_cert_for_keyusage(self):
        try:
            keyusage_extension=self.cert.extensions.get_extension_for_class(x509.KeyUsage)
            logger.info("Das Zertifikat hat eine KeyUsage Extension mit den folgenden Eigenschaften")
            logger.warning("digital_signature: "+ str(keyusage_extension.value.digital_signature))
            logger.warning("key_cert_sign: "+ str(keyusage_extension.value.key_cert_sign))
            logger.warning("crl_sign: "+ str(keyusage_extension.value.crl_sign))

            #TODO: Man könnte die Werte auch gleich prüfen, allerdings ist das für CA Zertifkate anders und daher etwas komplizierter.

        except Exception as err:
            if "No <class 'cryptography.x509.extensions.KeyUsage'> extension was found" in str(err):
                logger.error("Es wurde keine keyUsage Extension gefunden")
            else:
                print err

    def check_cert_for_extended_keyusage(self):
        try:
            keyusage_extension=self.cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
            # logger.info("Das Zertifikat hat eine ExtendedKeyUsage Extension mit den folgenden Eigenschaften")
            # logger.warning("serverAuth: "+ str(keyusage_extension.value.SERVER_AUTH))

            for usg in keyusage_extension.value._usages:
                logger.warning("Das Zertifikat hat eine ExtendedKeyUsage Extension mit den folgenden Eigenschaften"+usg._name)

            #TODO: Ist das der richtige Wert?
        except Exception as err:
            print err
            #TODO: wenn es die Extension nicht gibt, tritt vermutlich ein Fehler auf, den man hier behandeln sollte

    def list_alternative_names(self):
        try:
            name_extension=self.cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            logger.info("Das Zertifikat hat eine AlternateiveName Extension")
            logger.info("Die Einträge für AlternativeNames lauten: ")

            for entry in name_extension._value._general_names:
                logger.info(entry._value)


        except Exception as err:
            print err
            #TODO: wenn es die Extension nicht gibt, tritt vermutlich ein Fehler auf, den man hier behandeln sollte

    def check_basic_constraint(self):
    #Anforderung 2.2.5
        try:
            basic_constraint_extension=self.cert.extensions.get_extension_for_class(x509.BasicConstraints)
            logger.info("Das Zertifikat hat eine BasicContraint Extension")
            logger.warning("Der Inhalt der BasicContraint Extension ist: "+str(basic_constraint_extension))

            #TODO: Die Extension könnte man noch nett auswerten.

        except Exception as err:
            logger.error("Das Zertifikat hat keine BasicContraint Extension")


    def is_cert_ca(self):
        try:
            basic_constraint_extension=self.cert.extensions.get_extension_for_class(x509.BasicConstraints)
            return True

        except Exception as err:
            return False

    def print_subject(self):
        for entry in self.cert.subject._attributes:
            for attr in entry:
                logger.info( attr.oid._name+ ": " + attr.value)
    #
    # def print_serial(cert):
    #         print cert.serial_number
    #         print cert.subject
    #         print cert.issuer
    #         print cert.signature_hash_algorithm
    #         print cert.signature_algorithm_oid
    #         print cert.public_key()
    #         print cert.extensions
