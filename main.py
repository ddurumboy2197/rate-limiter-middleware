class SlidingWindowRateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def is_allowed(self, timestamp):
        self.requests = [request for request in self.requests if request['timestamp'] >= timestamp - self.time_window]
        if len(self.requests) < self.max_requests:
            self.requests.append({'timestamp': timestamp, 'allowed': True})
            return True
        else:
            self.requests.append({'timestamp': timestamp, 'allowed': False})
            return False

class RateLimiterMiddleware:
    def __init__(self, app, max_requests, time_window):
        self.app = app
        self.rate_limiter = SlidingWindowRateLimiter(max_requests, time_window)

    def __call__(self, environ, start_response):
        timestamp = int(environ.get('HTTP_X_FORWARDED_FOR', 0))
        if not self.rate_limiter.is_allowed(timestamp):
            start_response('429 Too Many Requests', [])
            return []
        return self.app(environ, start_response)
```

```python
from flask import Flask, request

app = Flask(__name__)

rate_limiter = RateLimiterMiddleware(app, max_requests=10, time_window=60)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/test')
def test():
    return 'Test request'

if __name__ == '__main__':
    rate_limiter.app.run(debug=True)
