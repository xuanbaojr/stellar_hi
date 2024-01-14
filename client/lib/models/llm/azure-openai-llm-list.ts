import { LLM } from "@/types"

// azure openai platform link
const OPENAI_PLATORM_LINK = "https://azure.microsoft.com/en-us/services/cognitive-services/text-analytics/"

// GPT-3.5 Turbo (UPDATED 12/18/23)
const GPT3_5Turbo: LLM = {
  modelId: "gpt-35-turbo",
  modelName: "GPT35TURBO",
  provider: "azure",
  hostedId: "gpt-3.5-turbo-1106",
  platformLink: OPENAI_PLATORM_LINK,
  imageInput: false
}

export const AZURE_OPENAI_LLM_LIST: LLM[] = [GPT3_5Turbo]
