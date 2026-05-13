import test from "node:test";
import assert from "node:assert/strict";

import { getApiBaseUrl } from "../lib/apiConfig.js";

test("getApiBaseUrl defaults to the local backend port", () => {
  const previousValue = process.env.NEXT_PUBLIC_API_BASE_URL;
  delete process.env.NEXT_PUBLIC_API_BASE_URL;

  assert.equal(getApiBaseUrl(), "http://localhost:8000");

  if (previousValue !== undefined) {
    process.env.NEXT_PUBLIC_API_BASE_URL = previousValue;
  }
});

test("getApiBaseUrl can point the frontend at an alternate local backend port", () => {
  const previousValue = process.env.NEXT_PUBLIC_API_BASE_URL;
  process.env.NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8001";

  assert.equal(getApiBaseUrl(), "http://127.0.0.1:8001");

  if (previousValue === undefined) {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;
  } else {
    process.env.NEXT_PUBLIC_API_BASE_URL = previousValue;
  }
});
