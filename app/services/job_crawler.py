"""
Web Crawler cho TopCV, VietnamWorks, ITviec
Thu thập dữ liệu công việc từ các trang tuyển dụng
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobCrawler:
    """Base crawler class"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def clean_text(self, text: str) -> str:
        """Làm sạch text"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    def extract_salary(self, salary_text: str) -> tuple:
        """Trích xuất mức lương min, max từ text"""
        if not salary_text:
            return None, None, salary_text
        
        # Tìm số trong text
        numbers = re.findall(r'(\d+(?:[.,]\d+)?)', salary_text)
        
        if len(numbers) >= 2:
            try:
                min_sal = float(numbers[0].replace(',', '.'))
                max_sal = float(numbers[1].replace(',', '.'))
                return min_sal, max_sal, salary_text
            except:
                pass
        elif len(numbers) == 1:
            try:
                sal = float(numbers[0].replace(',', '.'))
                return sal, sal, salary_text
            except:
                pass
        
        return None, None, salary_text


class TopCVCrawler(JobCrawler):
    """Crawler cho TopCV.vn"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.topcv.vn"
    
    def crawl_jobs(self, keyword: str = "", location: str = "", max_pages: int = 3) -> List[Dict]:
        """Thu thập công việc từ TopCV"""
        jobs = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"{self.base_url}/tim-viec-lam-{keyword}-tai-{location}-trang-{page}"
                logger.info(f"Crawling TopCV page {page}: {url}")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job-item')
                
                for item in job_items:
                    try:
                        job = self._parse_job_item(item)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.error(f"Error parsing job item: {e}")
                        continue
                
                time.sleep(2)  # Delay giữa các request
        
        except Exception as e:
            logger.error(f"TopCV crawl error: {e}")
        
        return jobs
    
    def _parse_job_item(self, item) -> Optional[Dict]:
        """Parse một job item từ HTML"""
        try:
            title_elem = item.find('h3', class_='title')
            title = self.clean_text(title_elem.text) if title_elem else None
            
            link_elem = item.find('a', class_='job-link')
            job_url = self.base_url + link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
            
            company_elem = item.find('a', class_='company')
            company = self.clean_text(company_elem.text) if company_elem else None
            
            salary_elem = item.find('label', class_='salary')
            salary_text = self.clean_text(salary_elem.text) if salary_elem else "Thỏa thuận"
            
            location_elem = item.find('label', class_='address')
            location = self.clean_text(location_elem.text) if location_elem else None
            
            # Extract external ID from URL
            external_id = None
            if job_url:
                match = re.search(r'/(\d+)\.html', job_url)
                if match:
                    external_id = f"topcv_{match.group(1)}"
            
            salary_min, salary_max, salary_raw = self.extract_salary(salary_text)
            
            return {
                'title': title,
                'company': company,
                'salary_raw': salary_raw,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'address_raw': location,
                'source_name': 'topcv',
                'source_url': job_url,
                'external_id': external_id,
                'status': 'approved',
                'job_type': 'full-time',
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None


class VietnamWorksCrawler(JobCrawler):
    """Crawler cho VietnamWorks.com"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.vietnamworks.com"
    
    def crawl_jobs(self, keyword: str = "", location: str = "", max_pages: int = 3) -> List[Dict]:
        """Thu thập công việc từ VietnamWorks"""
        jobs = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"{self.base_url}/tim-viec-lam/{keyword}-tai-{location}-trang-{page}"
                logger.info(f"Crawling VietnamWorks page {page}: {url}")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job-item')
                
                for item in job_items:
                    try:
                        job = self._parse_job_item(item)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.error(f"Error parsing job item: {e}")
                        continue
                
                time.sleep(2)
        
        except Exception as e:
            logger.error(f"VietnamWorks crawl error: {e}")
        
        return jobs
    
    def _parse_job_item(self, item) -> Optional[Dict]:
        """Parse một job item từ HTML"""
        try:
            title_elem = item.find('h2', class_='job-title')
            title = self.clean_text(title_elem.text) if title_elem else None
            
            link_elem = item.find('a', class_='job-link')
            job_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
            if job_url and not job_url.startswith('http'):
                job_url = self.base_url + job_url
            
            company_elem = item.find('a', class_='company-name')
            company = self.clean_text(company_elem.text) if company_elem else None
            
            salary_elem = item.find('div', class_='salary')
            salary_text = self.clean_text(salary_elem.text) if salary_elem else "Thỏa thuận"
            
            location_elem = item.find('div', class_='location')
            location = self.clean_text(location_elem.text) if location_elem else None
            
            external_id = None
            if job_url:
                match = re.search(r'/(\d+)', job_url)
                if match:
                    external_id = f"vnw_{match.group(1)}"
            
            salary_min, salary_max, salary_raw = self.extract_salary(salary_text)
            
            return {
                'title': title,
                'company': company,
                'salary_raw': salary_raw,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'address_raw': location,
                'source_name': 'vietnamworks',
                'source_url': job_url,
                'external_id': external_id,
                'status': 'approved',
                'job_type': 'full-time',
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None


class ITviecCrawler(JobCrawler):
    """Crawler cho ITviec.com"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://itviec.com"
    
    def crawl_jobs(self, keyword: str = "python", location: str = "ho-chi-minh", max_pages: int = 3) -> List[Dict]:
        """Thu thập công việc từ ITviec"""
        jobs = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"{self.base_url}/it-jobs/{keyword}-{location}?page={page}"
                logger.info(f"Crawling ITviec page {page}: {url}")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch page {page}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job-item')
                
                for item in job_items:
                    try:
                        job = self._parse_job_item(item)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.error(f"Error parsing job item: {e}")
                        continue
                
                time.sleep(2)
        
        except Exception as e:
            logger.error(f"ITviec crawl error: {e}")
        
        return jobs
    
    def _parse_job_item(self, item) -> Optional[Dict]:
        """Parse một job item từ HTML"""
        try:
            title_elem = item.find('h3', class_='title')
            title = self.clean_text(title_elem.text) if title_elem else None
            
            link_elem = item.find('a', class_='job-link')
            job_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
            if job_url and not job_url.startswith('http'):
                job_url = self.base_url + job_url
            
            company_elem = item.find('div', class_='company-name')
            company = self.clean_text(company_elem.text) if company_elem else None
            
            salary_elem = item.find('span', class_='salary')
            salary_text = self.clean_text(salary_elem.text) if salary_elem else "Thỏa thuận"
            
            location_elem = item.find('span', class_='city')
            location = self.clean_text(location_elem.text) if location_elem else None
            
            external_id = None
            if job_url:
                match = re.search(r'/([^/]+)$', job_url)
                if match:
                    external_id = f"itviec_{match.group(1)}"
            
            salary_min, salary_max, salary_raw = self.extract_salary(salary_text)
            
            return {
                'title': title,
                'company': company,
                'salary_raw': salary_raw,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'address_raw': location,
                'source_name': 'itviec',
                'source_url': job_url,
                'external_id': external_id,
                'status': 'approved',
                'job_type': 'full-time',
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None


def crawl_all_sources(keyword: str = "", location: str = "", max_pages: int = 2) -> List[Dict]:
    """Thu thập từ tất cả các nguồn"""
    all_jobs = []
    
    # TopCV
    logger.info("Starting TopCV crawler...")
    topcv = TopCVCrawler()
    topcv_jobs = topcv.crawl_jobs(keyword, location, max_pages)
    all_jobs.extend(topcv_jobs)
    logger.info(f"TopCV: Found {len(topcv_jobs)} jobs")
    
    # VietnamWorks
    logger.info("Starting VietnamWorks crawler...")
    vnw = VietnamWorksCrawler()
    vnw_jobs = vnw.crawl_jobs(keyword, location, max_pages)
    all_jobs.extend(vnw_jobs)
    logger.info(f"VietnamWorks: Found {len(vnw_jobs)} jobs")
    
    # ITviec
    logger.info("Starting ITviec crawler...")
    itviec = ITviecCrawler()
    itviec_jobs = itviec.crawl_jobs(keyword, location, max_pages)
    all_jobs.extend(itviec_jobs)
    logger.info(f"ITviec: Found {len(itviec_jobs)} jobs")
    
    logger.info(f"Total jobs crawled: {len(all_jobs)}")
    return all_jobs
