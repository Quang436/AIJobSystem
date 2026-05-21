# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, BackgroundTasks
from app.database.database import get_connection
from app.middleware.auth_middleware import require_role
from app.services.job_crawler import crawl_all_sources, TopCVCrawler, VietnamWorksCrawler, ITviecCrawler
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/crawler/run")
def run_crawler(
    keyword: str = "",
    location: str = "",
    max_pages: int = 2,
    source: str = "all",  # all, topcv, vietnamworks, itviec
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Chạy crawler để thu thập công việc từ các trang tuyển dụng"""
    
    def crawl_and_save():
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Chọn crawler
            if source == "topcv":
                crawler = TopCVCrawler()
                jobs = crawler.crawl_jobs(keyword, location, max_pages)
            elif source == "vietnamworks":
                crawler = VietnamWorksCrawler()
                jobs = crawler.crawl_jobs(keyword, location, max_pages)
            elif source == "itviec":
                crawler = ITviecCrawler()
                jobs = crawler.crawl_jobs(keyword, location, max_pages)
            else:
                jobs = crawl_all_sources(keyword, location, max_pages)
            
            # Lưu vào database
            saved_count = 0
            skipped_count = 0
            
            for job in jobs:
                try:
                    # Kiểm tra trùng lặp theo external_id
                    if job.get('external_id'):
                        cursor.execute("""
                            SELECT id FROM jobs 
                            WHERE source_name = ? AND external_id = ?
                        """, (job['source_name'], job['external_id']))
                        
                        if cursor.fetchone():
                            skipped_count += 1
                            continue
                    
                    # Insert job
                    cursor.execute("""
                        INSERT INTO jobs (
                            title, company, salary_raw, salary_min, salary_max,
                            address_raw, source_name, source_url, external_id,
                            status, job_type, scraped_at, created_by
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), ?)
                    """, (
                        job.get('title'),
                        job.get('company'),
                        job.get('salary_raw'),
                        job.get('salary_min'),
                        job.get('salary_max'),
                        job.get('address_raw'),
                        job.get('source_name'),
                        job.get('source_url'),
                        job.get('external_id'),
                        job.get('status', 'approved'),
                        job.get('job_type', 'full-time'),
                        current_user["user_id"]
                    ))
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving job: {e}")
                    continue
            
            conn.commit()
            logger.info(f"Crawler completed: {saved_count} saved, {skipped_count} skipped")
            
        except Exception as e:
            logger.error(f"Crawler error: {e}")
        finally:
            conn.close()
    
    # Chạy trong background
    if background_tasks:
        background_tasks.add_task(crawl_and_save)
        return {
            "message": "Crawler started in background",
            "source": source,
            "keyword": keyword,
            "location": location
        }
    else:
        crawl_and_save()
        return {
            "message": "Crawler completed",
            "source": source
        }

@router.get("/crawler/status")
def get_crawler_status(current_user: dict = Depends(require_role(["admin"]))):
    """Lấy thống kê crawler"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Thống kê theo nguồn
        cursor.execute("""
            SELECT source_name, COUNT(*) as total, 
                   MAX(scraped_at) as last_scraped
            FROM jobs
            WHERE source_name IN ('topcv', 'vietnamworks', 'itviec')
            GROUP BY source_name
        """)
        
        sources = []
        for row in cursor.fetchall():
            sources.append({
                "source": row[0],
                "total_jobs": row[1],
                "last_scraped": str(row[2]) if row[2] else None
            })
        
        # Tổng số job từ crawler
        cursor.execute("""
            SELECT COUNT(*) FROM jobs
            WHERE source_name IN ('topcv', 'vietnamworks', 'itviec')
        """)
        total = cursor.fetchone()[0]
        
        return {
            "total_crawled_jobs": total,
            "sources": sources
        }
    finally:
        conn.close()
