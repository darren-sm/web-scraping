"""
Search for all the emails in a website. This script searches the whole HTML so hidden email are also included.
Output the list of emails in a local email.csv
"""
import re, datetime, requests, json



def extract_email(html_as_str: str):
    """
    Use a regex pattern to match email in the HTML response
    """
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"    
    return re.findall(pattern, html_as_str)

def page_request(links):
    for link in links:
        try:
            r = requests.get(link)
        except requests.exceptions.MissingSchema:
            print(f"Link: {link}")
            print(f"Message: Invalid link {link}")
        except:
            print(f"ERROR: Something went wrong")
        else:
            yield {'link':link, 'response': r}
      
def link_validation(response):
    if not response.status_code == requests.codes.ok:
        raise response.raise_for_status()


if __name__ == '__main__':  
    links = set(input("Links (space separated): ").split())
    
    if len(links) == 0:
        raise Exception("ERROR: No link entered")

    with open("output.json", "r") as j:
        json_content = json.load(j)

    with open("log.txt", "a", encoding="UTF-8") as f:         
        f.write(f'[{datetime.datetime.now().strftime("%Y-%M-%d %H:%M")}] Number of Links: {len(links)}\n')
        success = 0
        for html_response in page_request(links):                 
            link = html_response['link']     
            response = html_response['response']
            html_as_str = response.text
            status_code = response.status_code
            
        
            print("  Link:", link)
            print("  Message: ", end = "")      
            
            try:
                link_validation(response)
            except requests.exceptions.HTTPError as e:
                print(f"Email Extracting failed! Get request status code {status_code}. {e}")
                continue
                
            output = extract_email(html_as_str)
            if len(output) == 0:
                print("No email found!")
                continue
            
            success += 1
            print(f"Found {len(output)}:")
            if link not in json_content.keys():
                json_content[link] = output
                with open("output.json", "w") as j:
                    json.dump(json_content, j)

            
            f.write(f"  Link: {link}\n")              
            for index, email in enumerate(output, start = 1):                
                print(f"\t{index}. {email}")
                f.write(f"\t{index}. {email}\n")            
            f.write("\n")
        f.write(f"  Extraction finished.\n\tSuccess: {success}\n\tFailed: {len(links) - success}\n\n")
        
    