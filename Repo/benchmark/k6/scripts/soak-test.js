// soak_test.js - Test system stability over time
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 5 },    // Ramp-up to 5 users
    { duration: '10m', target: 5 },    // Stay at 5 users for 10 minutes
    { duration: '1m', target: 0 },     // Ramp-down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],     // Less than 1% failed requests
    http_req_duration: ['avg<20000'],  // Average request duration under 20000ms (20 seconds)
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:80';

export default function () {
  const payload = JSON.stringify({
    prompt: "What is the capital of France?",
    n_predict: 50,
    temperature: 0.7,
    stop: ["<|im_end|>", "</s>", "<|endoftext|>"]
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const response = http.post(`${BASE_URL}/completion`, payload, params);

  check(response, {
    'status is 200': (r) => r.status === 200,
    'has content': (r) => r.json('content') !== undefined,
  });

  sleep(1);
}