from hashlib import sha256


test_message = sha256("Hello world").digest()
afgh_pre = None
alice = None
bob = None


def init():
    global afgh_pre, alice, bob

    if afgh_pre is None:
        from zerodb.crypto.afgh_pre import afgh_pre
        alice = afgh_pre.Key.make_priv()
        bob = afgh_pre.Key.from_passphrase("Bob's passphrase")


def test_encrypt_decrypt():
    init()
    emsg = alice.encrypt(test_message)
    assert isinstance(emsg, basestring)
    assert alice.decrypt_my(emsg) == test_message


def test_reencrypt():
    init()
    emsg = alice.encrypt(test_message)
    remsg = alice.re_key(bob).reencrypt(emsg)
    assert bob.decrypt_re(remsg) == test_message


def test_load_priv():
    init()
    dump = alice.dump_priv()
    assert isinstance(dump, basestring)
    assert afgh_pre.Key.load_priv(dump).priv == alice.priv


def test_load_pub():
    init()
    dump = alice.dump_pub()
    assert isinstance(dump, basestring)
    assert afgh_pre.Key.load_pub(dump).pub == alice.pub


def test_reencryption_full():
    init()
    # Alice encrypts message and makes reencryption key fpr Bob
    emsg = alice.encrypt(test_message)
    re_key = alice.re_key(bob.dump_pub())
    re_key_dump = re_key.dump()

    # Re-encrypt for Bob
    re_key = afgh_pre.ReKey.load(re_key_dump)
    re_msg = re_key.reencrypt(emsg)

    # Bub decrypts message
    assert bob.decrypt_re(re_msg) == test_message
