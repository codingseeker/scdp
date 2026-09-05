// k6 Load Test — SCDP API Performance Benchmark
// Measures p50, p95, p99 latency, throughput, and error rate

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const supplierLatency = new Trend('supplier_latency');
const networkLatency = new Trend('network_latency');
const simulationLatency = new Trend('simulation_latency');

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const AUTH_USERNAME = __ENV.AUTH_USERNAME || 'analyst';
const AUTH_PASSWORD = __ENV.AUTH_PASSWORD || 'analyst123';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    errors: ['rate<0.05'],
  },
};

function getAuthToken() {
  const res = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify({
    username: AUTH_USERNAME,
    password: AUTH_PASSWORD,
  }), { headers: { 'Content-Type': 'application/json' } });

  if (res.status === 200) {
    return JSON.parse(res.body).access_token;
  }
  return null;
}

export default function () {
  // Health check
  const health = http.get(`${BASE_URL}/health`);
  check(health, { 'health OK': (r) => r.status === 200 });

  // Supplier list
  const suppliersStart = Date.now();
  const suppliers = http.get(`${BASE_URL}/api/v1/suppliers?page=1&page_size=20`);
  supplierLatency.add(Date.now() - suppliersStart);
  check(suppliers, { 'suppliers OK': (r) => r.status === 200 });
  errorRate.add(suppliers.status !== 200);

  // Network graph
  const networkStart = Date.now();
  const network = http.get(`${BASE_URL}/api/v1/network`);
  networkLatency.add(Date.now() - networkStart);
  check(network, { 'network OK': (r) => r.status === 200 });
  errorRate.add(network.status !== 200);

  // Metrics
  const metrics = http.get(`${BASE_URL}/api/v1/metrics`);
  check(metrics, { 'metrics OK': (r) => r.status === 200 });

  // Simulation (authenticated)
  const token = getAuthToken();
  if (token) {
    const simStart = Date.now();
    const sim = http.post(`${BASE_URL}/api/v1/simulations`, JSON.stringify({
      description: 'Load test scenario',
      severity: 0.5,
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });
    simulationLatency.add(Date.now() - simStart);
    check(sim, { 'simulation OK': (r) => r.status === 200 });
    errorRate.add(sim.status !== 200);
  }

  sleep(1);
}
