from selenium import webdriver
import unittest
import time

class FrontTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.login_true = 'charlotte.fossier@insa-lyon.fr'
        cls.pwd_true = 'aubry'

        cls.login_false = 'wrong@insa-lyon.fr'
        cls.pwd_false = 'wrong'


    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)
        
    
    def login(self):
        form = self.driver.find_element_by_id('login')
        form.find_element_by_css_selector('input[type=text]').send_keys(self.login_true)
        form.find_element_by_css_selector('input[type=password]').send_keys(self.pwd_true)
        form.find_element_by_tag_name('button').click()
        
        greeting = self.driver.find_element_by_id('loginGreeting')
        self.assertTrue(greeting is not None)

    def test_login_success(self):
        self.driver.get('localhost:8000/gestion')
        form = self.driver.find_element_by_id('login')
        form.find_element_by_css_selector('input[type=text]').send_keys(self.login_true)
        form.find_element_by_css_selector('input[type=password]').send_keys(self.pwd_true)
        form.find_element_by_tag_name('button').click()
        
        greeting = self.driver.find_element_by_id('loginGreeting')
        self.assertTrue(greeting is not None)

        
    def test_login_failure(self):
        self.driver.get('localhost:8000/gestion')
        form = self.driver.find_element_by_id('login')
        form.find_element_by_css_selector('input[type=text]').send_keys(self.login_false)
        form.find_element_by_css_selector('input[type=password]').send_keys(self.pwd_false)
        form.find_element_by_tag_name('button').click()
        
        form2 = self.driver.find_element_by_id('login')
        self.assertTrue(form2 is not None)


    def test_users(self):
        self.driver.get('localhost:8000/gestion/')
        self.login()

        self.driver.get('localhost:8000/gestion/#/users')
        modal = self.driver.find_element_by_id('user_modal')
        self.assertTrue(modal is not None)


    def test_user(self):
        self.driver.get('localhost:8000/gestion/')
        self.login()

        self.driver.get('localhost:8000/gestion/#/users')
        #modal = self.driver.find_element_by_id('user_modal')
        #self.assertTrue(modal is not None)

        users = self.driver.find_elements_by_class_name('show_user')
        print 'got users'
        self.assertTrue(users is not None)
        users[0].click()
        print 'clicked first user'
        header = self.drive.find_elements_by_class_name('modal-header')
        print 'got modal header'
        self.assertTrue(header is not None)
        

    def tearDown(self):
        self.driver.quit()

        
if __name__ == '__main__':
    unittest.main()
