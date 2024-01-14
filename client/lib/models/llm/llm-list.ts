import { LLM } from "@/types"
import { AZURE_OPENAI_LLM_LIST } from "./azure-openai-llm-list"

export const LLM_LIST: LLM[] = [
  ...AZURE_OPENAI_LLM_LIST
]
