from google_play_scraper import app,search
import pandas as pd

def app_searcher():
    app_names, app_ids, free_apps,prices,num_of_installs = [],[],[],[],[]
    
    keyword = "Top 100 apps"
    
    results = search(
    keyword
)
    
    for app in results:
        try:
            app_names.append(app['title'])
            app_ids.append(app['appId'])
            free_apps.append(app['free'])
            prices.append(app['price'])
            num_of_installs.append(app['installs'])
            
        except Exception as e:
            app_names.append('Unknown')
            app_ids.append('Unknown')
            free_apps.append('Unknown')
            prices.append('Unknown')
            num_of_installs.append('Unknown')
        
        df = pd.DataFrame({
            'App Name': app_names,
            'App ID' : app_ids,
            'Free app' : free_apps,
            'Price' : prices,
            'Installation' : num_of_installs
        })
        
        df.to_csv(f'app_search_{keyword}_result.csv', index=False)
            
if __name__ == "__main__":
    app_searcher()
    
    
    