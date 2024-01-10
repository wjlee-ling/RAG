import { ChatOpenAI } from "langchain/chat_models/openai";
import { PromptTemplate } from "langchain/prompts";

const model = new ChatOpenAI({ temperature: 0.1, model: "gpt-4" });
const promptTemplate = PromptTemplate.fromTemplate(
  "Tell me a joke about {topic}"
);

const chain = promptTemplate.pipe(model);
const response = await chain.invoke({ topic: "Koreans" });

console.log(response);
