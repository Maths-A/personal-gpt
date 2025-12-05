// spike_test.js - Simulate sudden traffic spikes
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 30 },   // Sudden spike to 30 users
    { duration: '30s', target: 30 },  // Stay at 30 users
    { duration: '10s', target: 0 },    // Sudden drop to 0 users
  ],
  thresholds: {
    http_req_failed: ['rate<0.1'],      // Less than 10% failed requests
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