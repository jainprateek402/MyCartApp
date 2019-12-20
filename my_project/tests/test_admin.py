import unittest
from my_pro.admin import AdminAccount

class TestAdmin(unittest.TestCase):

    def setUp(self):
        self.admin = AdminAccount("admin", "testadmin@123")

    def test_init(self):
    	assert self.admin.login == True, "Looged in status"

    def test_logout(self):

    	self.admin.logout()        

        assert self.admin.login == False, "Looged in status"


if __name__ == '__main__':
    unittest.main()