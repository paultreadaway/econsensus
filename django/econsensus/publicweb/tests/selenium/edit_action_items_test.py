from publicweb.tests.selenium.selenium_testcase import SeleniumTestCase
from django_dynamic_fixture import G
from publicweb.models import Decision
from organizations.models import Organization
from guardian.shortcuts import assign_perm
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from actionitems.models import ActionItem
from django.utils.formats import date_format

class EditActionItemsTest(SeleniumTestCase):
    def setUp(self):
        self.login()
        self.organization = G(Organization)
        self.organization.add_user(self.user)
        assign_perm('edit_decisions_feedback', self.user, self.organization)
            
    def test_action_item_form_replaces_feedback_item(self):
        # self.selenium is the name of the web driver for the class
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(ActionItem, origin=decision)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".edit.actionitem").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_deadline"))
        
        self.assertTrue(
            self.is_element_present(
                By.CSS_SELECTOR, ".actionitem_list > form"))
        self.assertFalse(
             self.is_element_present(
                 By.CSS_SELECTOR, ".actionitem_list > li"))
    
    def test_action_item_form_cancel_recreates_item_without_changes(self):
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        
        G(ActionItem, origin=decision)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))

        expected_text = driver.find_element_by_css_selector(
              "ol.actionitem_list > li").text
        
        driver.find_element_by_css_selector(".edit.actionitem").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_deadline"))
        
        self.selenium.find_element_by_name('description').send_keys("test")
        
        driver.find_element_by_css_selector(".actionitem_cancel").click()

        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".edit.actionitem"))
        
        actual_text = driver.find_element_by_css_selector(
              "ol.actionitem_list > li").text
              
        self.assertTrue(
             self.is_element_present(
                 By.CSS_SELECTOR, ".actionitem_list > li"))
        self.assertFalse(
            self.is_element_present(
                By.CSS_SELECTOR, ".actionitem_list > form"))
        self.assertEqual(expected_text, actual_text)
    
    def test_action_item_form_save_with_valid_form_creates_action_item(self):        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        action_item = G(ActionItem, origin=decision)
        
        expected_text = 'me is responsible for: test\nby %s\nEdit' % (
            date_format(action_item.deadline, "DATE_FORMAT"))
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".edit.actionitem").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_deadline"))
        
        self.selenium.find_element_by_name('description').clear()
        self.selenium.find_element_by_name('responsible').clear()
        self.selenium.find_element_by_name('description').send_keys("test")
        self.selenium.find_element_by_name('responsible').send_keys("me")
        
        driver.find_element_by_css_selector(".actionitem_save").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector("#actionitem_add_anchor"),
            "Check the data being submitted is valid")
        
        actual_text = driver.find_element_by_css_selector(
              "ol.actionitem_list > li").text
        
        self.assertEqual(expected_text, actual_text)

    def test_action_item_form_save_with_invalid_data_displays_errors(self):
        expected_text = ('This field is required.')
        
        decision = G(Decision, organization=self.organization, 
              author=self.user, editor=self.user)
        G(ActionItem, origin=decision)
        
        driver = self.selenium
        driver.get("%s/item/detail/%d/" % (
           self.live_server_url, decision.id))
        
        driver.find_element_by_css_selector(".edit.actionitem").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_id("id_deadline"))
        
        self.selenium.find_element_by_name('description').clear()
        
        driver.find_element_by_css_selector(".actionitem_save").click()
        
        WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_css_selector(".errorlist > li"),
            "Check the data being submitted is valid")
        
        actual_text = driver.find_element_by_css_selector(
              ".errorlist > li").text
        
        self.assertEqual(expected_text, actual_text)