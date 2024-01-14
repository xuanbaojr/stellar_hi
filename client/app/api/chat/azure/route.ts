import { CHAT_SETTING_LIMITS } from "@/lib/chat-setting-limits"
import { checkApiKey, getServerProfile } from "@/lib/server/server-chat-helpers"
import { ChatAPIPayload } from "@/types"
import { OpenAIStream, StreamingTextResponse } from "ai"
import { da } from "date-fns/locale"
import OpenAI from "openai"
import { ChatCompletionCreateParamsBase } from "openai/resources/chat/completions.mjs"


export const runtime = "edge"

export async function POST(request: Request) {
  const json = await request.json()
  const { chatSettings, messages } = json as ChatAPIPayload

  console.log(messages[messages.length - 1].content);

  const result = await fetch('http://localhost:8000/chats/add/1', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ "role": "user",
    "content": messages[messages.length - 1].content })
  });
  const data = await result.json();
  const { chats } = data;
  console.log(chats[1].content);
  return new Response(chats[1].content);

  try {
    const profile = await getServerProfile()

    const KEY = process.env.AZURE_OPENAI_KEY
    const ENDPOINT = process.env.AZURE_OPENAI_ENDPOINT

    checkApiKey(KEY, "Azure")

    console.log("Azure OpenAI API Key:", KEY, "Endpoint:", ENDPOINT)


    let DEPLOYMENT_ID = "gpt-35-turbo"
    switch (chatSettings.model) {
      case "gpt-35-turbo":
        DEPLOYMENT_ID = "gpt-35-turbo"
        break
      default:
        return new Response(JSON.stringify({ message: "Model not found" }), {
          status: 400
        })
    }

    if (!ENDPOINT || !KEY || !DEPLOYMENT_ID) {
      return new Response(
        JSON.stringify({ message: "Azure resources not found" }),
        {
          status: 400
        }
      )
    }

    console.log("URL", `${ENDPOINT}/openai/deployments/${DEPLOYMENT_ID}`);

    const azureOpenai = new OpenAI({
      apiKey: KEY,
      baseURL: `${ENDPOINT}/openai/deployments/${DEPLOYMENT_ID}`,
      defaultQuery: { "api-version": "2023-05-15" },
      defaultHeaders: { "api-key": KEY }
    })

    const response = await azureOpenai.chat.completions.create({
      model: DEPLOYMENT_ID as ChatCompletionCreateParamsBase["model"],
      messages: messages as ChatCompletionCreateParamsBase["messages"],
      temperature: chatSettings.temperature,
      max_tokens:
        CHAT_SETTING_LIMITS[chatSettings.model].MAX_TOKEN_OUTPUT_LENGTH,
      stream: true
    })

    const stream = OpenAIStream(response)

    return new StreamingTextResponse(stream)
  } catch (error: any) {
    const errorMessage = error.error?.message || "An unexpected error occurred"
    const errorCode = error.status || 500
    return new Response(JSON.stringify({ message: errorMessage }), {
      status: errorCode
    })
  }
}
