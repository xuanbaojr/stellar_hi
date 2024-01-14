import { ModelProvider } from "."

export type LLMID = AzureOpenAILLMID

// OpenAI Models (UPDATED 12/18/23)
export type AzureOpenAILLMID = "gpt-35-turbo" // Updated GPT-3.5 Turbo


export interface LLM {
  modelId: LLMID
  modelName: string
  provider: ModelProvider
  hostedId: string
  platformLink: string
  imageInput: boolean
}
