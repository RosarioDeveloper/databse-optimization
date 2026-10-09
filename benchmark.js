import http from 'k6/http';
import exec from 'k6/execution';
import { check, sleep } from 'k6';

const BASE_URL = "http://0.0.0.0:8000"
const RPS = 1000
const LATENCY = 200

const checkRequest = {
   'status is 200': (r) => r.status === 200,
   'latency < 500ms': (r) => r.timings.duration < 500,
}

const get_endpoints = () => {
   let userId = Math.floor(Math.random() * 300) + 1
   let offet = Math.floor(Math.random() * 20) * 100

   return [
      `/users/${userId}/orders?limit=100&offset=${offet}`,
      `/users?limit=100&offset=${offet}`,
      `/products?limit=100&offset=${offet}`,
      `/transactions?limit=100&offset=${offet}`,
      `/orders?limit=100&offset=${offet}`,
      `/orders/${userId}/items?limit=100&offset=${offet}`,
      `/orders/${userId}/items?limit=100&offset=${offet}`,
   ]
}

const INTERATION_RATE = Math.ceil(RPS / get_endpoints().length)
const MAX_VU = Math.ceil(RPS * (LATENCY / 1000))

export const options = {
   scenarios: {
      api_load: {
         executor: 'constant-arrival-rate',
         timeUnit: '1s',
         duration: '1m',
         rate: RPS,        // 1000 req/s
         preAllocatedVUs: MAX_VU * 0.5,
         maxVUs: MAX_VU
      }
   },
   thresholds: {
      http_req_duration: [`p(99)<${LATENCY}`],
      http_req_failed: ['rate<0.01'],
      http_reqs: [`rate>=${RPS}`],
      dropped_iterations: ['count==0'],
   },
};



export default function () {
   const endpoints = get_endpoints()
   const index = exec.scenario.iterationInTest % endpoints.length;

   http.get(`${BASE_URL}${endpoints.at(index)}`)
}