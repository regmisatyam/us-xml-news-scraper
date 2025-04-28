from flask import Flask, json, jsonify, request, render_template
from news_scraper import scrape_news

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/privacy')
def privacyPage():
    return render_template('privacy.html')

@app.route('/undefined')
def undefined():
    return "News not found!"

@app.route('/news-list', methods=['GET'])
def get_news_list():
    try:
        with open('news-list.json', 'r') as file:
            news_list = json.load(file)
        return jsonify(news_list)
    except FileNotFoundError:
        return jsonify({'error': 'news-list.json file not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON data'}), 500

@app.route('/news', methods=['GET'])
def get_news():
    # Retrieve the query parameters
    query_params = request.args.keys()
    
    # Extract URLs from the query parameters
    urls = [param for param in query_params if not param.startswith('_')]
    
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400
    
    all_news = []
    
    # List to keep track of news from each source
    news_sources = []
    
    for url in urls:
        full_url = f"https://{url}" if not url.startswith('http') else url
        news_items = scrape_news(full_url) #function that is defined in news_scraper.py
        if isinstance(news_items, list):  # Ensure news_items is a list
            news_sources.append(news_items)
        else:
            # Log error or handle specific case if necessary
            all_news.append({'error': f"Failed to fetch from {full_url}"})
    
    # Interleave news items from different sources
    while any(news_sources):
        for source in news_sources:
            if source:
                all_news.append(source.pop(0))
    
    # Prepare the response data
    response_data = {
        'fetched_news': len(all_news),
        'news': all_news
    }
    
    response = jsonify(response_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    
    return response

if __name__ == '__main__':
    app.run(debug=True)