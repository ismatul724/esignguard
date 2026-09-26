import unittest
from pathlib import Path


from crypto_utils import (
    generate_key_pair,
    create_signature_data,
    verify_document_signature,
    signature_json_bytes,
)



class TestCrypto(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        """Siapkan data uji sekali untuk semua test."""
        cls.password = "testpassword123"
        cls.document_bytes = b"Test document content for unit tests."
        cls.document_name = "test_document.txt"
        cls.signer_name = "Test User"
        cls.signer_role = "Tester"
        cls.institution = "Test Institution"


        # Generate key pair untuk semua test
        cls.private_pem, cls.public_pem = generate_key_pair(cls.password)


    def test_01_generate_key_pair(self):
        """Test 1: Generate key pair berhasil."""
        private_pem, public_pem = generate_key_pair(self.password)


        self.assertIsInstance(private_pem, bytes)
        self.assertIsInstance(public_pem, bytes)
        self.assertTrue(len(private_pem) > 0)
        self.assertTrue(len(public_pem) > 0)


    def test_02_create_signature_data(self):
        """Test 2: Create signature data berhasil."""
        signature_data, document_hash = create_signature_data(
            document_bytes=self.document_bytes,
            document_name=self.document_name,
            private_key_pem=self.private_pem,
            password=self.password,
            signer_name=self.signer_name,
            signer_role=self.signer_role,
            institution=self.institution,
        )


        self.assertIn("algorithm", signature_data)
        self.assertIn("document_sha256", signature_data)
        self.assertIn("signature_base64", signature_data)
        self.assertIn("metadata", signature_data)
        self.assertEqual(signature_data["metadata"]["signer_name"], self.signer_name)


    def test_03_verify_original_document(self):
        """Test 3: Verifikasi dokumen asli (harus VALID)."""
        # Buat signature
        signature_data, _ = create_signature_data(
            document_bytes=self.document_bytes,
            document_name=self.document_name,
            private_key_pem=self.private_pem,
            password=self.password,
            signer_name=self.signer_name,
            signer_role=self.signer_role,
            institution=self.institution,
        )


        json_bytes = signature_json_bytes(signature_data)


        # Verifikasi
        result = verify_document_signature(
            document_bytes=self.document_bytes,
            signature_json_bytes=json_bytes,
            public_key_pem=self.public_pem,
        )


        self.assertTrue(result["valid"])
        self.assertIn("verifikasi", result["reason"].lower())


    def test_04_verify_tampered_document(self):
        """Test 4: Verifikasi dokumen diubah (harus INVALID)."""
        # Buat signature dari dokumen asli
        signature_data, _ = create_signature_data(
            document_bytes=self.document_bytes,
            document_name=self.document_name,
            private_key_pem=self.private_pem,
            password=self.password,
            signer_name=self.signer_name,
            signer_role=self.signer_role,
            institution=self.institution,
        )


        json_bytes = signature_json_bytes(signature_data)


        # Ubah dokumen (tamper)
        tampered_bytes = self.document_bytes + b" extra content"


        # Verifikasi dokumen yang sudah diubah
        result = verify_document_signature(
            document_bytes=tampered_bytes,
            signature_json_bytes=json_bytes,
            public_key_pem=self.public_pem,
        )


        self.assertFalse(result["valid"])


    def test_05_verify_wrong_public_key(self):
        """Test 5: Verifikasi dengan public key salah (harus INVALID)."""
        # Generate key pair kedua (salah)
        wrong_private_pem, wrong_public_pem = generate_key_pair(self.password)


        # Buat signature dengan key pertama
        signature_data, _ = create_signature_data(
            document_bytes=self.document_bytes,
            document_name=self.document_name,
            private_key_pem=self.private_pem,
            password=self.password,
            signer_name=self.signer_name,
            signer_role=self.signer_role,
            institution=self.institution,
        )


        json_bytes = signature_json_bytes(signature_data)


        # Verifikasi dengan public key yang SALAH
        result = verify_document_signature(
            document_bytes=self.document_bytes,
            signature_json_bytes=json_bytes,
            public_key_pem=wrong_public_pem,
        )


        self.assertFalse(result["valid"])



if __name__ == "__main__":
    unittest.main()