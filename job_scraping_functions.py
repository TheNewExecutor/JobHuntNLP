import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re


# Useful functions
class GlassdoorDriver(webdriver.Chrome):
    """ Adds some custom methods to webdriver.Chrome class to specifically scrape Glassdoor"""

    def login_glassdoor(self, username, password):
        """
        Input account info to move to next page in browser

        Parameters:
        ----------------
        username: string
            Valid glassdoor account name
        password: string
            Password corresponding to the username account

        """

        self.get('https://www.glassdoor.com/profile/login_input.htm?userOriginHook=HEADER_SIGNIN_LINK')
        user_input = self.find_element_by_xpath("""//*[@id="userEmail"]""")
        user_input.clear()
        user_input.send_keys(username)
        password_input = self.find_element_by_id('userPassword')
        password_input.send_keys(password)

        login_button = self.find_element_by_xpath("""//*[@id="InlineLoginModule"]
        /div/div/div[1]/div[4]/form/div[3]/div[1]/button""")
        login_button.click()

    def search_jobs(self, job, location):
        """
        Enters job search parameters and navigates to a results page

        Parameters:
        ----------------
        job: string
            Job title, keyword or company to enter into search
        location: string
            Name of place, must be in City, State (Country) format

        """
        job_panel = self.find_element_by_xpath("""//*[@id="sc.keyword"]""")
        location_panel = self.find_element_by_xpath("""//*[@id="sc.location"]""")
        search_button = self.find_element_by_xpath("""//*[@id="HeroSearchButton"]""")
        job_panel.clear()
        job_panel.send_keys(job)
        location_panel.clear()
        location_panel.send_keys(location)
        search_button.click()

    def get_job_links(self, xpath='//*[@id="MainCol"]/div/ul/li[.]/div[2]/a'):
        """
        Acquires a list of job description urls from Glassdoor.com from one search result page

        Parameters:
        ----------------
        xpath: string
            Xpath string to specify web elements to select

        Returns:
        ----------------
        links: list of strings
            List of urls on the current page the browser is on

        """
        links = [str(i.get_attribute('href')) for i in self.find_elements_by_xpath(xpath)]
        return links

    def find_next_page_url(self, xpath='//li[@class="next"]/a'):
        """
        Find the url to the next page in the search results

        Parameters:
        ----------------
        xpath: string
            Xpath string to specify web elements to select

        Returns:
        ----------------
        url: string
            Url of next page in the search results

        """
        next_page_element = self.find_element_by_xpath(xpath)
        url = str(next_page_element.get_attribute('href'))
        return url

    def get_all_job_links(self, job, location):
        """
        Acquires a list of job description urls from Glassdoor.com from all
        available search result pages

        Parameters:
        ----------------
        job: string
            Job title, keyword or company to enter into search
        location: string
            Name of place, must be in City, State (Country) format

        Returns:
        ----------------
        links_: list of strings
            List of all urls from search results

        """
        self.search_jobs(job, location)
        links_ = self.get_job_links()
        url = self.find_next_page_url()
        for i in range(30):
            try:
                self.get(url)
                links = self.get_job_links()
                links_.extend(links)
                url = self.find_next_page_url()
            except:

                # print out problem and revert back to the last result page
                print('Problem with page %s' % i)
                self.back()
                return links_
        return links_

    def full_search_results(self,username, password, job, locations):
        """
        Aggregate job search results from multiple locations, given a legitimate glassdoor login

        Parameters
        ----------
        uusername: string
            Valid glassdoor account name
        password: string
            Password corresponding to the username account
        job: string
            Job title, keyword or company to enter into search
        location: list of string
            Name of place, must be in City, State (Country) format

        Returns
        -------
        search_results: dict
            Dictionary of location : list of job urls key:value pairs

        """

        self.login_glassdoor(username, password)
        time.sleep(1)
        search_results = {}

        for location in locations:
            try:
                search_results[location] = self.get_all_job_links(job, location)
            except:
                print(f'Problem with {location}')
                return search_results
        return search_results


class LinkedInDriver(webdriver.Chrome):
    """Adds methods to webdriver.Chrome to more conveniently data mine linkedin.com jobs"""
    def search_jobs(self, job, location):
        """
        Enters job search parameters and navigates to a results page

        Parameters:
        ----------------
        job: string
            Job title, keyword or company to enter into search
        location: string
            Name of place, must be in City, State (Country) format

        """
        self.get('https://www.linkedin.com/jobs/')
        job_search_bar = self.find_element_by_xpath('//*[@id="JOBS"]/section[1]/input')
        location_search_bar = self.find_element_by_xpath('//*[@id="JOBS"]/section[2]/input')
        job_search_bar.clear()
        location_search_bar.clear()
        job_search_bar.send_keys(job)
        job_search_bar.send_keys(Keys.ENTER)
        new_location_bar_xpath = '/html/body/header/nav/section/section[2]/form/section[2]/input'
        new_location_bar = self.find_element_by_xpath(new_location_bar_xpath)
        new_location_bar.clear()
        new_location_bar.send_keys(location)
        new_location_bar.send_keys(Keys.ENTER)

    def get_job_data(self):
        """
        Gets a string containing Linkedin's job fields

        Returns
        ----------------

        data : dictionary
            Dictionary with field:data values
        """

        # Dictionary to map xpaths of useful items
        xpath = {
                 'Name': '/html/body/main/section[1]/section[1]/div/div[1]/h3[1]/span[1]/a',
                 'Description': '/html/body/main/section[1]/section[2]/div',
                 'Employment Type': '/html/body/main/section[1]/section[2]/ul/li[2]/span',
                 'Industries': '/html/body/main/section[1]/section[2]/ul/li[4]/span',
                 'Job Function': '/html/body/main/section[1]/section[2]/ul/li[3]/span',
                 'Seniority Level': '/html/body/main/section[1]/section[2]/ul/li[1]/span',
                 }
        data = {}
        for field in xpath:
            elements = self.find_elements_by_xpath(xpath[field])
            data[field] = ', '.join([i.text for i in elements])
        return data

    def get_job_links(self,  xpath="""//a[@class='result-card__full-card-link']""", delay=1):
        """
        Acquires a list of job description urls from linkedin.com from the search result page

        Parameters:
        ----------------

        xpath: string
            Xpath string to specify web elements to select
        delay: int
            Time delay in between clicking for more results (incrase for slower internet speeds)
        Returns:
        ----------------
        links: list of strings
            List of urls on the current page the browser is on

        """
        for i in range(40):
            more_jobs_button = self.find_element_by_xpath("""//button[@class='see-more-jobs']""")
            more_jobs_button.click()
            time.sleep(delay)
        links = [str(i.get_attribute('href')) for i in self.find_elements_by_xpath(xpath)]
        return links

    def full_search_results(self, job, locations, delay=1):
        """
        Aggregate job search results from multiple locations for linked.com

        Parameters
        ----------
        job: string
            Job title, keyword or company to enter into search
        location: list of string
            Name of place, must be in City, State (Country) format
        delay: int
            Time delay in between clicking for more results (incrase for slower internet speeds)
        Returns
        -------
        search_results: dict
            Dictionary of location : list of job urls key:value pairs

        """

        search_results = {}

        for location in locations:
            try:
                self.search_jobs(job, location)
                search_results[location] = self.get_job_links(delay=delay)
            except:
                print(f'Problem with {location}')
                return search_results
        return search_results

def full_search_results(username, password, job, locations):
        """
        Using a functional approach less reliant on the state of the browser,
        aggregate job search results from multiple locations

        Parameters
        ----------
        uusername: string
            Valid glassdoor account name
        password: string
            Password corresponding to the username account
        job: string
            Job title, keyword or company to enter into search
        location: list of string
            Name of place, must be in City, State, Country format

        Returns
        -------
        search_results: dict
            Dictionary of location : list of job urls key:value pairs

        """

        search_results = {}

        for location in locations:
            try:
                driver = GlassdoorDriver()
                driver.login_glassdoor(username, password)
                time.sleep(1)
                search_results[location] = driver.get_all_job_links(job, location)
                driver.close()
            except:
                print(f'Problem with {location}')
                return search_results
        return search_results

