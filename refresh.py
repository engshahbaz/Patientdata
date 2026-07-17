import time
import random
from selenium import webdriver

def main():
    print("Launching Google Chrome...")
    driver = webdriver.Chrome()

    try:
        # Your specific YouTube podcast link
        url = "https://www.youtube.com/watch?v=luhF8z4WX7w"
        
        print(f"Navigating to {url} and playing the video...")
        driver.get(url)

        # Loop exactly 100 times
        for i in range(1, 101):
            # Pick a random wait time anywhere between 1 and 15 seconds
            random_wait = random.uniform(5.0, 15.0)
            
            print(f"[{i}/100] Playing... Next refresh in {random_wait:.2f} seconds.")
            time.sleep(random_wait)
            
            print("Refreshing the page now...")
            driver.refresh()
            print("Page refreshed successfully!\n")

        print("Completed all 100 loops successfully.")

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Closing the browser...")
        driver.quit()

if __name__ == "__main__":
    main()