import axios from "axios";

const BASE_URL = "https://app.berinia.com/api";

const endpoints = [
  "/stats/overview",
  "/stats/conversion?period=30d",
  "/stats/leads?period=30d",
  "/stats/campaigns?period=30d",
  "/stats/niches?period=30d",
  "/dashboard/metrics",
  "/leads",
  "/campaigns",
  "/niches",
  "/logs/recent"
];

async function checkEndpoints() {
  console.log("🔍 Checking BerinIA API endpoints (/api)...\\n");

  for (const endpoint of endpoints) {
    const url = `${BASE_URL}${endpoint}`;
    try {
      const res = await axios.get(url);
      console.log(`✅ [${res.status}] ${endpoint}`);
    } catch (error: any) {
      if (error.response) {
        console.error(`❌ [${error.response.status}] ${endpoint} - ${error.response.statusText}`);
      } else if (error.request) {
        console.error(`🚫 [NO RESPONSE] ${endpoint}`);
      } else {
        console.error(`⚠️  [ERROR] ${endpoint} - ${error.message}`);
      }
    }
  }

  console.log("\\n✅ Health check finished.");
}

checkEndpoints();