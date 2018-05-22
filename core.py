# 3RD PACKAGES
from selenium.webdriver.remote.webdriver import WebDriver

# LOCAL PACKAGES
import utils
import config


#ProfilesGate
def get_profiles_list(driver: WebDriver):
    try:
        profiles = driver.find_elements_by_class_name('profile-link')

        return list(map(
            lambda p: (
                profiles.index(p),
                p.find_element_by_class_name('profile-name').text,
                p
            ),
            profiles
        ))
    except:
        return None


def choose_profile(profile: list):
    profile[2].click()


def validate_login(email: str, pswd: str):

    driver = utils.generate_webdriver()
    driver.get(config.MAIN_URL + '/login')
    is_logged = False

    if not utils.already_logged():
        driver.find_element_by_id("email").send_keys(user)
        driver.find_element_by_id("password").send_keys(pswd)
        driver.find_element_by_xpath(
            '//*[@id="appMountPoint"]/div/div[2]/div/div/form[1]/button'
        ).click()

    if driver.current_url == config.MAIN_URL + '/browse':
        is_logged = True    

    else:
        driver.close()
        driver = None
    
    return is_logged, driver



