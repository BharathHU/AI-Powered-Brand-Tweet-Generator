
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 60000,
});

export function toGenerationPayload(form) {
  return {
    brand_name: form.brand_name || "",
    industry: form.industry || "",
    campaign_objective: form.campaign_objective,
    product_description: form.product_description || "",
    preferred_tone: form.preferred_tone || "Let AI Decide",
    target_audience: form.target_audience || "",
    additional_instructions: form.additional_instructions || "",
  };
}
