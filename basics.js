// new OpenAI v4. Refer to the new changes: https://github.com/openai/openai-node/discussions/217

import { config } from "dotenv";
import { OpenAI } from "openai";

config();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function chat(input) {
  const messages = [{ role: "user", content: input }];

  const response = await openai.chat.completions.create({
    model: "gpt-3.5-turbo",
    messages: messages,
    temperature: 0.1,
  });

  return response.choices[0].message;
}

const question = "What is the meaning of life?";

// chat(question)
//   .then((response) => console.log(response))
//   .catch((error) => console.log(error));

const promptTemplate = `
  Be concise and clear like haiku in your answers.
  Question: {question}
`;

const prompt = promptTemplate.replace("{question}", question);
chat(prompt)
  .then((response) => console.log(response))
  .catch((error) => console.log(error));
