import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

API_URL = 'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&simplified=true'

def get_proxies():
    response = requests.get(API_URL)
    if response.status_code == 200:
        proxies = response.text.split('\n')
        return [proxy.strip() for proxy in proxies if proxy.strip()]
    return []

def check_proxy(proxy):
    url = 'http://www.google.com'
    proxies = {
        'http': f'http://{proxy}'
    }

    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            return proxy, response.elapsed.total_seconds()
    except requests.RequestException:
        pass

    return None

def main():
    result_file = 'results.txt'

    proxies = get_proxies()

    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(check_proxy, proxies), total=len(proxies), desc="Sprawdzanie"))

    active_proxies = [result[0] for result in results if result is not None]
    response_times = [result[1] for result in results if result is not None]

    with open(result_file, 'w') as file:
        for proxy in active_proxies:
            file.write(proxy + '\n')

    num_active_proxies = len(active_proxies)
    avg_response_time = sum(response_times) / num_active_proxies if num_active_proxies > 0 else 0

    print(f'Sprawdzanie zakończone. Znaleziono {num_active_proxies} działających serwerów proxy.')
    print(f'Średni czas reakcji: {avg_response_time:.2f} sekundy.')
    print(f'Wyniki zapisane w pliku "results.txt".')

if __name__ == '__main__':
    main()
