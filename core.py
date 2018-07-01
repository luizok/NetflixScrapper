# 3RD PACKAGES
from selenium.webdriver.remote.webdriver import WebDriver

# LOCAL PACKAGES
import utils
import config
import exceptions


def validate_login(netflixInstance, email, pswd):

    netflixInstance.driver.get(config.MAIN_URL + '/login')
    is_logged = False

    if not utils.already_logged():
        netflixInstance.driver.find_element_by_id("email").send_keys(email)
        netflixInstance.driver.find_element_by_id("password").send_keys(pswd)
        netflixInstance.driver.find_element_by_xpath(
            '//*[@id="appMountPoint"]/div/div[2]/div/div/form[1]/button'
        ).click()

    if netflixInstance.driver.current_url == config.MAIN_URL + '/browse':
        is_logged = True    

    else:
        raise exceptions.InvalidLoginException
    
    return is_logged, netflixInstance.driver


#/ProfilesGate
def get_profiles_list(netflixInstance):
    try:
        profiles = netflixInstance.driver.find_elements_by_class_name('profile')
        return profiles
        
    except:
        return None


def get(netflixInstance, type, by, params):
    pass


