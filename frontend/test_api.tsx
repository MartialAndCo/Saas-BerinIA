// tsx script - test_api.tsx
import axios from "axios";

const baseURL = "https://app.berinia.com/api";
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

(async () => {
  console.log("🔍 Checking BerinIA API endpoints (frontend)...");
  for (const endpoint of endpoints) {
    try {
      const res = await axios.get(baseURL + endpoint);
      console.log(`✅ [${res.status}] ${endpoint}`);
    } catch (error: any) {
      if (error.response) {
        console.log(`❌ [${error.response.status}] ${endpoint}`);
      } else {
        console.log(`❌ [ERROR] ${endpoint} - ${error.message}`);
      }
    }
  }
  console.log("✅ Frontend API check complete.");
})();
