import utils
import core
from codes import Type, By
from exceptions import ProfileOutOfRangerException, EmptyProfileListException


class Netflix():
    def __init__(self):
        self.driver = utils.generate_webdriver(show=False)
        self.profiles = None
        self.is_logged = False


    def login(self, email, pswd):
        self.is_logged, self.driver = core.validate_login(self, email, pswd)


    def get_profiles_list(self):
        self.profiles = core.get_profiles_list(self)


    def choose_profile(self, idx):
        if self.profiles is not None:
            if 0 <= idx < len(self.profiles):
                self.profiles[idx].click()
                return True
            
            else:
                raise ProfileOutOfRangeException
        else:
            raise EmptyProfileListException


########################## MOVIES ##############################
    def get_movies_by_id(self, ids):
        return core.get(self, Type.MOVIE , By.ID, ids)


    def get_movies_by_genre(self, genres):
        return core.get(self, Type.MOVIE , By.GENRE, genres)


    def get_movies_by_actor(self, actors):
        return core.get(self, Type.MOVIE , By.ACTOR, actors)


    def get_movies_by_mature(self, matures):
        return core.get(self, Type.MOVIE , By.MATURE, mature)


    def get_movies_by_rating(self, ratings):
        return core.get(self, Type.MOVIE , By.ratings, ratings)

########################## SERIES ##############################
    def get_series_by_id(self, ids):
        return core.get(self, Type.MOVIE , By.ID, ids)


    def get_series_by_genre(self, genres):
        return core.get(self, Type.MOVIE , By.GENRE, genres)


    def get_series_by_actor(self, actors):
        return core.get(self, Type.MOVIE , By.ACTOR, actors)


    def get_series_by_mature(self, matures):
        return core.get(self, Type.MOVIE , By.MATURE, mature)


    def get_series_by_rating(self, ratings):
        return core.get(self, Type.MOVIE , By.ratings, ratings)