from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
from time import sleep

load_dotenv()

session = requests.Session()

login_url = 'https://qalam.nust.edu.pk/web/login'
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'lxml')

csrf_token = soup.find('input', {'name': 'csrf_token'})['value']    

payload = {
    "csrf_token": csrf_token,
    "login": os.getenv('QALAM_USERNAME'),
    "password": os.getenv('QALAM_PASSWORD'),
}

login_response = session.post(login_url, data=payload)
if login_response.status_code != 200:
    print("Login failed!")
    exit()
else:
    print("Login Successful!")

sleep(5)

dashboard_url = 'https://qalam.nust.edu.pk/student/dashboard'
dashboard_response = session.get(dashboard_url)
dashboard_soup = BeautifulSoup(dashboard_response.text, 'lxml')

courses = dashboard_soup.find_all('div', class_='card text-dark bg-light mb-1')
print("\nEnrolled Courses:")
for course in courses:
    header = course.find('div', class_='card-header bg-primary')
    course_name = header.find('span').text.strip()        
    course_link = course.find_parent('a')['href']
    print(f"\nNavigating to: {course_name}")
    
    
    course_id = course_link.split('/')[-1]  
    gradebook_url = f"https://qalam.nust.edu.pk/student/course/gradebook/{course_id}"
    
    print(f"Accessing gradebook for: {course_name}")
    gradebook_page = session.get(gradebook_url)
    
    if gradebook_page.status_code == 200:
        gradebook_soup = BeautifulSoup(gradebook_page.text, 'lxml')
        print(f"\nGradebook for {course_name}:")
        
        
        categories = {
            'Assignment': {'max': 0, 'obtained': 0, 'avg': 0},
            'Quiz': {'max': 0, 'obtained': 0, 'avg': 0},
            'Mid Term': {'max': 0, 'obtained': 0, 'avg': 0},
            'Final Term': {'max': 0, 'obtained': 0, 'avg': 0}
        }
        
        
        assessment_rows = gradebook_soup.find_all('tr')
        
        for row in assessment_rows:
            try:
                
                assessment_name = row.find('td')
                if not assessment_name:
                    continue
                    
                assessment_name = assessment_name.text.strip()
                cols = row.find_all('td')
                
                if len(cols) >= 4:
                    max_mark = float(cols[1].text.strip())
                    obtained_mark = float(cols[2].text.strip())
                    class_avg = float(cols[3].text.strip())
                    
                    
                    if assessment_name.startswith('A'):
                        category = 'Assignment'
                    elif assessment_name.startswith('Q'):
                        category = 'Quiz'
                    elif assessment_name.startswith('M'):
                        category = 'Mid Term'
                    elif assessment_name.startswith('F'):
                        category = 'Final Term'
                    else:
                        continue
                    
                    
                    categories[category]['max'] += max_mark
                    categories[category]['obtained'] += obtained_mark
                    categories[category]['avg'] += class_avg
                    
            except (ValueError, AttributeError, IndexError) as e:
                print(f"Error processing row: {e}")
                continue
        
        
        print("\nBreakdown by Category:")
        total_max = total_obtained = total_avg = 0
        
        for category, marks in categories.items():
            if marks['max'] > 0:  
                print(f"\n{category}:")
                print(f"Maximum Marks: {marks['max']:.2f}")
                print(f"Obtained Marks: {marks['obtained']:.2f}")
                print(f"Class Average: {marks['avg']:.2f}")
                percentage = (marks['obtained'] / marks['max'] * 100) if marks['max'] > 0 else 0
                print(f"Percentage: {percentage:.2f}%")
                
                total_max += marks['max']
                total_obtained += marks['obtained']
                total_avg += marks['avg']
        
        print("\nOverall Summary:")
        print(f"Total Maximum Marks: {total_max:.2f}")
        print(f"Total Obtained Marks: {total_obtained:.2f}")
        print(f"Overall Class Average: {total_avg:.2f}")
        overall_percentage = (total_obtained / total_max * 100) if total_max > 0 else 0
        print(f"Overall Percentage: {overall_percentage:.2f}%")
        print("-" * 50)
        
        sleep(2)
    else:
        print(f"Failed to load gradebook for {course_name}")
        continue
